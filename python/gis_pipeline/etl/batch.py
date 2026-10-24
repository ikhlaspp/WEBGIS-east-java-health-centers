"""Single-writer local acquisition batches with durable, verified page checkpoints."""

import hashlib
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .http_client import RetryDeferred, atomic_json


class BatchError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@contextmanager
def batch_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR)
    locked = False
    try:
        if os.fstat(descriptor).st_size == 0:
            os.write(descriptor, b'0')
        os.lseek(descriptor, 0, os.SEEK_SET)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
        yield
    finally:
        if locked:
            os.lseek(descriptor, 0, os.SEEK_SET)
            if os.name == 'nt':
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def validate_page(page, next_page, required_fields):
    if not isinstance(page, dict) or set(('rows', 'quarantined', 'aggregates', 'raw_count', 'next_page')) - page.keys():
        raise BatchError('page_schema_changed')
    groups = [page['rows'], page['quarantined'], page['aggregates']]
    if not all(isinstance(group, list) for group in groups):
        raise BatchError('page_schema_changed')
    if page['next_page'] != next_page:
        raise BatchError('pagination_end_mismatch')
    records = [row for group in groups for row in group]
    if not records or type(page['raw_count']) is not int or page['raw_count'] != len(records):
        raise BatchError('empty_or_unreconciled_page')
    if any(not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'] for row in records):
        raise BatchError('missing_source_record_id')
    if any(not set(required_fields).issubset(row) for row in page['rows']):
        raise BatchError('required_header_changed')
    ids = [row['id'] for row in records]
    if len(ids) != len(set(ids)):
        raise BatchError('duplicate_page_ids')
    return ids


def run_batch(identity, expected_pages, expected_ids, required_fields, fetch_page, checkpoint, *, resume=False,
              clock=time.monotonic, time_budget=900):
    if not 0 < time_budget <= 900:
        raise BatchError('Invalid chunk time budget')
    deadline = clock() + time_budget
    required_identity = {'source_hash', 'source_id', 'target_release_id', 'pipeline_version', 'operation'}
    if not required_identity.issubset(identity) or any(not identity[key] for key in required_identity):
        raise BatchError('Incomplete batch identity')
    if (not expected_pages or len(expected_pages) != len(set(expected_pages))
            or not expected_ids or len(expected_ids) != len(set(expected_ids))):
        raise BatchError('Explicit nonempty unique expected pages and record IDs are required')
    parameters = {'pages': expected_pages, 'ids': sorted(expected_ids), 'fields': sorted(required_fields)}
    identity = {**identity, 'parameters_hash': digest(parameters)}
    key = digest(identity)
    checkpoint = Path(checkpoint)
    with batch_lock(checkpoint.with_suffix(checkpoint.suffix + '.lock')):
        state = {'idempotency_key': key, 'identity': identity, 'status': 'pending', 'attempt': 0, 'completed': []}
        if checkpoint.exists():
            state = json.loads(checkpoint.read_text(encoding='utf-8'))
            if state['idempotency_key'] != key:
                raise BatchError('Batch input, release, version or expected parameters changed')
            if state['status'] != 'succeeded' and not resume:
                raise BatchError('Use explicit resume for an interrupted batch')
            if state['status'] == 'pending':
                if not state.get('due_at'):
                    raise BatchError('retry_schedule_requires_review')
                if datetime.fromisoformat(state['due_at']) > datetime.now(timezone.utc):
                    return state
        state.update(status='running', attempt=state['attempt'] + 1)
        state.pop('error', None)
        state.pop('due_at', None)
        state.pop('counts', None)
        state.pop('candidate_evidence', None)
        atomic_json(checkpoint, state)
        try:
            all_ids, counts = set(), {'raw': 0, 'accepted': 0, 'quarantined': 0, 'aggregates': 0}
            if len(state['completed']) > len(expected_pages):
                raise BatchError('Checkpoint contains unexpected pages')
            for index, page_id in enumerate(expected_pages):
                if clock() >= deadline:
                    raise RetryDeferred(datetime.now(timezone.utc).isoformat())
                state['active_page'] = page_id
                atomic_json(checkpoint, state)
                next_page = expected_pages[index + 1] if index + 1 < len(expected_pages) else None
                if index < len(state['completed']):
                    saved = state['completed'][index]
                    path = Path(saved['path'])
                    if saved['page_id'] != page_id or not path.resolve().is_relative_to(checkpoint.parent.resolve()):
                        raise BatchError('Checkpoint page identity changed')
                    raw = path.read_bytes()
                    if hashlib.sha256(raw).hexdigest() != saved['sha256']:
                        raise BatchError('Checkpoint page checksum mismatch')
                    page = json.loads(raw)
                else:
                    page = fetch_page(page_id)
                    candidate = checkpoint.parent / (key + '-candidate-' + str(index) + '.json')
                    atomic_json(candidate, page)
                    state['candidate_evidence'] = {'path': str(candidate), 'sha256': hashlib.sha256(candidate.read_bytes()).hexdigest()}
                ids = validate_page(page, next_page, required_fields)
                if all_ids.intersection(ids) or not set(ids).issubset(expected_ids):
                    raise BatchError('Duplicate or unexpected IDs across pages')
                all_ids.update(ids)
                counts['raw'] += page['raw_count']
                for source, target in [('rows', 'accepted'), ('quarantined', 'quarantined'), ('aggregates', 'aggregates')]:
                    counts[target] += len(page[source])
                if index >= len(state['completed']):
                    path = checkpoint.parent / (key + '-page-' + str(index) + '.json')
                    atomic_json(path, page)
                    state['completed'].append({'page_id': page_id, 'path': str(path),
                                               'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'raw_count': page['raw_count']})
                    atomic_json(checkpoint, state)
            if all_ids != set(expected_ids):
                raise BatchError('Final source ID coverage mismatch')
            if clock() >= deadline:
                raise RetryDeferred(datetime.now(timezone.utc).isoformat())
            state.update(status='succeeded', counts=counts, data_quality_accepted=False)
        except Exception as exc:
            state['status'] = 'pending' if isinstance(exc, RetryDeferred) else 'failed'
            # Arbitrary provider exception strings may contain credentials or paths.
            state['error'] = getattr(exc, 'code', type(exc).__name__)
            if isinstance(exc, RetryDeferred):
                state['due_at'] = exc.due_at
        atomic_json(checkpoint, state)
        return state
