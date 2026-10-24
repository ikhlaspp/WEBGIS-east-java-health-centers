import io
import json
import urllib.error
from email.message import Message
from pathlib import Path

import pytest

from gis_pipeline.etl.batch import batch_lock, run_batch
from gis_pipeline.etl.http_client import FetchError, RetryDeferred, SourceClient, HOST_LAST

URL = 'https://example.test/data?period=2023'
IDENTITY = {'source_hash': 'synthetic-hash', 'source_id': 'synthetic', 'target_release_id': 'draft-a',
            'pipeline_version': '1', 'operation': 'acquire'}


class Clock:
    def __init__(self):
        self.value, self.waits = 0, []

    def now(self):
        return self.value

    def sleep(self, delay):
        self.waits.append(delay)
        self.value += delay


class Response(io.BytesIO):
    status = 200

    def __init__(self, data=b'{"synthetic":true}'):
        super().__init__(data)
        self.headers = {'Content-Type': 'application/json'}


class Opener:
    def __init__(self, outcomes):
        self.outcomes, self.calls = list(outcomes), []

    def open(self, request, timeout):
        self.calls.append((request.full_url, timeout))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.fixture
def client_factory(monkeypatch, tmp_path):
    monkeypatch.setattr('gis_pipeline.etl.http_client.validate_url', lambda *args: None)
    HOST_LAST.clear()
    def factory(outcomes, **options):
        clock, opener = Clock(), Opener(outcomes)
        client = SourceClient(tmp_path / 'raw', {'example.test'}, opener=opener, clock=clock.now,
                              sleep=clock.sleep, wall_clock=lambda: 0, jitter=lambda: 0, **options)
        return client, opener, clock
    return factory


def http_error(status, retry_after=None):
    headers = Message()
    if retry_after:
        headers['Retry-After'] = retry_after
    return urllib.error.HTTPError(URL + '&token=secret', status, 'sensitive provider message', headers, None)


def test_timeout_retries_are_bounded_with_required_backoff(client_factory):
    client, opener, clock = client_factory([TimeoutError(), TimeoutError(), Response()])
    result = client.fetch(URL, 'synthetic', '2023')
    assert result['attempts'] == 3
    assert [delay for delay in clock.waits if delay] == [5, 15]
    assert len(opener.calls) == 3
    assert all(timeout <= 60 for _, timeout in opener.calls)


def test_retry_exhaustion_never_creates_success_cache(client_factory):
    client, opener, _ = client_factory([TimeoutError()] * 3)
    with pytest.raises(FetchError, match='retry_exhausted'):
        client.fetch(URL, 'synthetic', '2023')
    assert len(opener.calls) == 3
    assert not list(client.root.rglob('*.bin'))


@pytest.mark.parametrize('header,expected_delay', [('7', 7), ('Thu, 01 Jan 1970 00:00:09 GMT', 9)])
def test_429_honors_seconds_and_http_date(client_factory, header, expected_delay):
    client, _, clock = client_factory([http_error(429, header), Response()])
    assert client.fetch(URL, 'synthetic', '2023')['attempts'] == 2
    assert expected_delay in clock.waits


def test_long_retry_after_is_pending_not_a_busy_loop(client_factory):
    client, opener, clock = client_factory([http_error(429, '3600')])
    with pytest.raises(RetryDeferred) as exc:
        client.fetch(URL, 'synthetic', '2023')
    assert exc.value.due_at == '1970-01-01T01:00:00+00:00'
    assert len(opener.calls) == 1
    assert not any(clock.waits)


@pytest.mark.parametrize('status', [401, 403, 404])
def test_permission_and_missing_history_errors_do_not_retry_or_leak_query(client_factory, status):
    client, opener, _ = client_factory([http_error(status)])
    with pytest.raises(FetchError) as exc:
        client.fetch(URL, 'synthetic', '2023')
    assert str(exc.value) == 'http_' + str(status)
    assert 'secret' not in str(exc.value)
    assert len(opener.calls) == 1


def test_cache_checks_checksum_and_separates_editions_and_parameters(client_factory):
    client, opener, _ = client_factory([Response(), Response(), Response()])
    first = client.fetch(URL, 'synthetic', '2023')
    assert client.fetch(URL, 'synthetic', '2023')['cache_hit']
    assert not client.fetch(URL, 'synthetic', '2024')['cache_hit']
    assert not client.fetch(URL + '&page=2', 'synthetic', '2023')['cache_hit']
    assert len(opener.calls) == 3
    Path(first['receipt']['raw_path']).write_bytes(b'tampered')
    with pytest.raises(FetchError, match='cache_integrity'):
        client.fetch(URL, 'synthetic', '2023')
    assert len(opener.calls) == 3


def test_cached_data_is_revalidated_against_current_schema(client_factory):
    client, opener, _ = client_factory([Response()])
    client.fetch(URL, 'synthetic', '2023')
    def changed(data, headers):
        if 'new_column' not in json.loads(data):
            raise ValueError('header_changed')
    with pytest.raises(ValueError, match='header_changed'):
        client.fetch(URL, 'synthetic', '2023', validate=changed)
    assert len(opener.calls) == 1


def test_buffered_response_can_finish_after_socket_has_closed(client_factory):
    from types import SimpleNamespace
    response = Response()
    response.fp = SimpleNamespace(raw=SimpleNamespace(_sock=SimpleNamespace(
        fileno=lambda: -1, settimeout=lambda _: pytest.fail('Closed socket must not be reconfigured'))))
    client, _, _ = client_factory([response])
    assert client.fetch(URL, 'synthetic', '2023')['data'] == b'{"synthetic":true}'


def test_quarantined_and_aggregate_rows_reconcile_without_quality_approval(tmp_path):
    source = {'rows': [{'id': 'a', 'value': 1}], 'quarantined': [{'id': 'b', 'reason': 'invalid value'}],
              'aggregates': [{'id': 'total', 'value': 1}], 'raw_count': 3, 'next_page': None}
    result = run_batch(IDENTITY, ['one'], ['a', 'b', 'total'], ['id', 'value'], lambda _: source, tmp_path / 'batch.json')
    assert result['status'] == 'succeeded'
    assert result['counts'] == {'raw': 3, 'accepted': 1, 'quarantined': 1, 'aggregates': 1}
    assert result['data_quality_accepted'] is False


def page(ids, next_page):
    return {'rows': [{'id': identifier, 'value': 1} for identifier in ids],
            'quarantined': [], 'aggregates': [], 'raw_count': len(ids), 'next_page': next_page}


def test_partial_batch_resumes_without_duplicate_rows(tmp_path):
    checkpoint = tmp_path / 'batch.json'
    calls = []
    def interrupted(page_id):
        calls.append(page_id)
        if page_id == 'p2':
            raise TimeoutError('token=do-not-log')
        return page(['0001'], 'p2')
    result = run_batch(IDENTITY, ['p1', 'p2'], ['0001', '0002'], ['id', 'value'], interrupted, checkpoint)
    assert result['status'] == 'failed'
    assert result['error'] == 'TimeoutError'
    assert len(result['completed']) == 1
    def resumed(page_id):
        calls.append(page_id)
        assert page_id == 'p2'
        return page(['0002'], None)
    result = run_batch(IDENTITY, ['p1', 'p2'], ['0001', '0002'], ['id', 'value'], resumed, checkpoint, resume=True)
    assert result['status'] == 'succeeded'
    assert result['counts'] == {'raw': 2, 'accepted': 2, 'quarantined': 0, 'aggregates': 0}
    assert not result['data_quality_accepted']
    assert calls == ['p1', 'p2', 'p2']
    result = run_batch(IDENTITY, ['p1', 'p2'], ['0001', '0002'], ['id', 'value'], resumed, checkpoint)
    assert result['status'] == 'succeeded'
    assert calls == ['p1', 'p2', 'p2']


@pytest.mark.parametrize('bad_page,error', [
    (page([], None), 'empty_or_unreconciled_page'),
    (page(['0001'], 'unexpected'), 'pagination_end_mismatch'),
    ({**page(['0001'], None), 'rows': [{'id': '0001'}]}, 'required_header_changed'),
    (page(['0001', '0001'], None), 'duplicate_page_ids'),
    ({**page(['0001'], None), 'raw_count': 2}, 'empty_or_unreconciled_page'),
])
def test_schema_empty_pagination_and_count_failures_are_not_success(tmp_path, bad_page, error):
    result = run_batch(IDENTITY, ['p1'], ['0001'], ['id', 'value'], lambda _: bad_page, tmp_path / 'batch.json')
    assert result['status'] == 'failed'
    assert result['error'] == error
    assert not result['completed']
    assert Path(result['candidate_evidence']['path']).exists()


def test_duplicate_ids_across_pages_and_missing_final_ids_fail(tmp_path):
    for name, final, expected in [('duplicate', ['0001'], ['0001', '0002']), ('missing', ['0002'], ['0001', '0002', '0003'])]:
        result = run_batch(IDENTITY, ['p1', 'p2'], expected, ['id', 'value'],
                           lambda key: page(['0001'], 'p2') if key == 'p1' else page(final, None), tmp_path / (name + '.json'))
        assert result['status'] == 'failed'


def test_release_change_and_tampered_checkpoint_cannot_resume(tmp_path):
    path = tmp_path / 'batch.json'
    result = run_batch(IDENTITY, ['p1'], ['0001'], ['id'], lambda _: page(['0001'], None), path)
    with pytest.raises(ValueError, match='changed'):
        run_batch({**IDENTITY, 'target_release_id': 'draft-b'}, ['p1'], ['0001'], ['id'], lambda _: None, path, resume=True)
    Path(result['completed'][0]['path']).write_text('{}')
    result = run_batch(IDENTITY, ['p1'], ['0001'], ['id'], lambda _: None, path, resume=True)
    assert result['status'] == 'failed'
    assert 'checksum' in result['error']


def test_local_worker_lock_excludes_a_second_writer(tmp_path):
    path = tmp_path / 'batch.lock'
    with batch_lock(path):
        with pytest.raises(OSError):
            with batch_lock(path):
                pytest.fail('Second writer acquired the lock')


def test_deferred_fetch_keeps_batch_pending(tmp_path, monkeypatch):
    from datetime import datetime, timezone
    class FrozenTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2024, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr('gis_pipeline.etl.batch.datetime', FrozenTime)
    def deferred(_):
        raise RetryDeferred('2030-01-01T00:00:00+00:00')
    result = run_batch(IDENTITY, ['p1'], ['0001'], ['id'], deferred, tmp_path / 'batch.json')
    assert result['status'] == 'pending'
    assert result['due_at'] == '2030-01-01T00:00:00+00:00'
    assert not result['completed']
    resumed = run_batch(IDENTITY, ['p1'], ['0001'], ['id'], lambda _: pytest.fail('Retried before Retry-After'),
                        tmp_path / 'batch.json', resume=True)
    assert resumed['attempt'] == result['attempt']
    assert resumed['status'] == 'pending'


def test_chunk_deadline_checkpoints_before_starting_another_page(tmp_path):
    clock = Clock()
    def fetch(page_id):
        assert page_id == 'p1'
        clock.value = 901
        return page(['0001'], 'p2')
    result = run_batch(IDENTITY, ['p1', 'p2'], ['0001', '0002'], ['id'], fetch,
                       tmp_path / 'batch.json', clock=clock.now)
    assert result['status'] == 'pending'
    assert len(result['completed']) == 1
