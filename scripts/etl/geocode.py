"""Prepare private location queues and explicit, bounded provider search batches."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.acquire import local_path
from gis_pipeline.etl.batch import batch_lock
from gis_pipeline.etl.geocode import NominatimProvider, PhotonProvider, load_inputs, validate_decision
from gis_pipeline.etl.http_client import atomic_json
from gis_pipeline.etl.normalize import digest


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def immutable_json(path, value):
    if path.exists():
        if load(path) != value:
            raise ValueError('Existing artifact differs; use a new output path')
    else:
        atomic_json(path, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--facility-evidence', required=True)
    init.add_argument('--boundary-manifest', required=True)
    init.add_argument('--release-id', required=True)
    init.add_argument('--output', default='data/staging/location_queue.json')
    init.add_argument('--report', required=True)
    search = sub.add_parser('search')
    search.add_argument('--queue', default='data/staging/location_queue.json')
    search.add_argument('--provider-config', required=True)
    search.add_argument('--codes', nargs='+', required=True)
    search.add_argument('--checkpoint', required=True)
    review = sub.add_parser('review')
    review.add_argument('--candidate-file', required=True, help='One candidate record from queue or search output')
    review.add_argument('--decision-file', required=True)
    review.add_argument('--output', required=True)
    audit_parser = sub.add_parser('audit-existing')
    audit_parser.add_argument('--queue-report', required=True)
    audit_parser.add_argument('--normalization-report', required=True)
    audit_parser.add_argument('--boundary-manifest', required=True)
    audit_parser.add_argument('--output', default='data/staging/location_reviews.json')
    audit_parser.add_argument('--report', required=True)
    args = parser.parse_args()
    if args.command == 'audit-existing':
        from gis_pipeline.etl.audit_locations import audit
        queue_report, normalized, boundary = load(args.queue_report), load(args.normalization_report), load(args.boundary_manifest)
        receipts = [({'path': queue_report['output_path'], 'sha256': queue_report['output_sha256']}, 'data/staging'),
                    (normalized['outputs']['accepted'], 'data/staging'), (boundary['outputs']['analysis'], 'data/processed')]
        documents = []
        for receipt, within in receipts:
            raw = local_path(ROOT, receipt['path'], within).read_bytes()
            if hashlib.sha256(raw).hexdigest() != receipt['sha256']:
                raise ValueError('Screening input checksum mismatch')
            documents.append(json.loads(raw))
        result = audit(documents[0], documents[1]['rows'], documents[2])
        result['input_hashes'] = [receipt['sha256'] for receipt, _ in receipts]
        output = local_path(ROOT, args.output, 'data/staging')
        immutable_json(output, result)
        report = {k: v for k, v in result.items() if k != 'records'}
        report.update(output_path=args.output, output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
        atomic_json(local_path(ROOT, args.report, 'docs/pekerjaan'), report)
        print(json.dumps(result['summary']))
        return 0
    if args.command == 'init':
        result = load_inputs(ROOT, load(args.facility_evidence), load(args.boundary_manifest), args.release_id)
        output = local_path(ROOT, args.output, 'data/staging')
        immutable_json(output, result)
        report = {'pipeline_version': result['pipeline_version'], 'release_id': result['release_id'],
                  'summary': result['summary'], 'input_identity': result['input_identity'],
                  'input_queue_sha256': result['input_queue_sha256'], 'output_path': args.output,
                  'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                  'provider_status': 'not_selected', 'publication_allowed': False}
        atomic_json(local_path(ROOT, args.report, 'docs/pekerjaan'), report)
        print(json.dumps(result['summary']))
        return 0
    if args.command == 'review':
        result = validate_decision(load(local_path(ROOT, args.candidate_file, 'data/staging')),
                                   load(local_path(ROOT, args.decision_file, 'data/staging')))
        immutable_json(local_path(ROOT, args.output, 'data/staging'), result)
        print('Review recorded; snapshot verification and spatial eligibility are separate steps')
        return 0
    queue_path = local_path(ROOT, args.queue, 'data/staging')
    queue = load(queue_path)
    config = load(args.provider_config)
    codes = sorted(args.codes)
    entries = {e['facility_code']: e for e in queue['entries']}
    if not 1 <= len(codes) <= 25 or len(set(codes)) != len(codes) or not set(codes) <= set(entries):
        raise ValueError('Explicit batch requires 1-25 unique known facility codes')
    adapter = {'nominatim': NominatimProvider, 'photon': PhotonProvider}.get(config.get('adapter'))
    if adapter is None:
        raise ValueError('Unknown provider adapter')
    provider = adapter(ROOT, config)
    identity = {'queue_sha256': hashlib.sha256(queue_path.read_bytes()).hexdigest(),
                'provider_config_sha256': digest(config), 'codes': codes}
    checkpoint = local_path(ROOT, args.checkpoint, 'data/staging')
    # A single shared process lock prevents parallel provider batches on this machine.
    with batch_lock(ROOT / 'data/staging/geocoder.lock'):
        # Persist a ceiling across invocations; a small trial cannot silently become a full bulk run.
        budget_path = ROOT / 'data/staging' / ('geocoder-budget-' + digest(config) + '.json')
        budget = load(budget_path) if budget_path.exists() else {'queries': []}
        limit = config.get('max_unique_queries')
        if type(limit) is not int or not 1 <= limit <= 25:
            raise ValueError('Provider configuration requires a trial ceiling of 1-25 unique queries')
        queries = {entries[c]['query'] for c in codes}
        if len(set(budget['queries']) | queries) > limit:
            raise ValueError('Provider trial query ceiling exceeded')
        budget['queries'] = sorted(set(budget['queries']) | queries)
        atomic_json(budget_path, budget)
        state = {'identity': identity, 'completed': {}, 'blocked': {}, 'pending': codes[:]}
        if checkpoint.exists():
            state = load(checkpoint)
            if state['identity'] != identity:
                raise ValueError('Checkpoint inputs changed')
        for code, saved in state['completed'].items():
            path = local_path(ROOT, saved['path'], 'data/staging')
            if hashlib.sha256(path.read_bytes()).hexdigest() != saved['sha256']:
                raise ValueError('Completed search artifact checksum mismatch')
        atomic_json(checkpoint, state)
        for code in codes:
            if code in state['completed']:
                continue
            state['active_code'] = code
            atomic_json(checkpoint, state)
            try:
                result = provider.search(entries[code], queue['release_id'])
                result.pop('cache_hit', None)
                output = checkpoint.parent / (digest(identity) + '-' + code + '.json')
                immutable_json(output, result)
                state['completed'][code] = {'path': output.relative_to(ROOT).as_posix(),
                                            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}
                state['blocked'].pop(code, None)
            except Exception as exc:
                state['blocked'][code] = getattr(exc, 'code', type(exc).__name__)
            state['pending'] = [c for c in codes if c not in state['completed'] and c not in state['blocked']]
            state.pop('active_code', None)
            atomic_json(checkpoint, state)
            if code in state['blocked']:
                break
        print(json.dumps({k: len(state[k]) for k in ('completed', 'blocked', 'pending')}))
        return 1 if state['blocked'] or state['pending'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
