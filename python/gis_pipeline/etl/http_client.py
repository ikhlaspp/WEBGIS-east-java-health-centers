"""Bounded, source-scoped HTTP retries and checksum-verified historical caches."""

import hashlib
import http.client
import json
import random
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from uuid import uuid4

from .sources import CheckedRedirect, snapshot, validate_url

HOST_LOCK = threading.Lock()
HOST_LAST = {}


class FetchError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class RetryDeferred(FetchError):
    def __init__(self, due_at):
        self.due_at = due_at
        super().__init__('retry_deferred')


class TimedConnection(http.client.HTTPSConnection):
    def connect(self):
        read_timeout = self.timeout
        self.timeout = min(10, read_timeout)
        super().connect()
        self.sock.settimeout(read_timeout)
        self.timeout = read_timeout


class TimedHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, request):
        return self.do_open(TimedConnection, request, context=self._context)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid4().hex + '.tmp')
    with temporary.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
        handle.flush()
        import os
        os.fsync(handle.fileno())
    temporary.replace(path)


class SourceClient:
    def __init__(self, raw_root, allowed_hosts, *, interval=1, deadline=900, opener=None,
                 clock=time.monotonic, sleep=time.sleep, wall_clock=time.time, jitter=random.random):
        if interval < 0 or not 0 < deadline <= 900:
            raise ValueError('Invalid HTTP pacing or deadline')
        self.root, self.hosts = Path(raw_root), set(allowed_hosts)
        self.interval, self.deadline = interval, deadline
        self.clock, self.sleep, self.wall_clock, self.jitter = clock, sleep, wall_clock, jitter
        self.opener = opener or urllib.request.build_opener(CheckedRedirect(self.hosts), TimedHTTPSHandler())

    def fetch(self, url, source_id, edition, *, headers=None, max_bytes=64 * 1024 * 1024,
              validate=None, cache=True, refresh=False, expected_status=200, persist=True):
        validate_url(url, self.hosts)
        if not source_id or not edition or not 0 < max_bytes <= 96 * 1024 * 1024:
            raise ValueError('Source, edition and bounded response size are required')
        if cache and not persist:
            raise ValueError('Caching requires a persisted response')
        headers = headers or {}
        if any(key.lower() in ('authorization', 'cookie', 'proxy-authorization') for key in headers):
            raise ValueError('This public-source client does not accept credentials')
        identity = {'source_id': source_id, 'edition': edition, 'url': url,
                    'headers': {key.lower(): value for key, value in headers.items()}, 'status': expected_status}
        key = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        index = self.root / 'http-cache' / (key + '.json')
        if cache and not refresh and index.exists():
            try:
                saved = json.loads(index.read_text(encoding='utf-8'))
                receipt = saved['receipt']
                if not Path(receipt['raw_path']).resolve().is_relative_to(self.root.resolve()):
                    raise FetchError('cache_integrity_error')
                data = Path(receipt['raw_path']).read_bytes()
                if saved['identity'] != identity or hashlib.sha256(data).hexdigest() != receipt['sha256']:
                    raise FetchError('cache_integrity_error')
            except (OSError, KeyError, json.JSONDecodeError) as exc:
                raise FetchError('cache_integrity_error') from exc
            if len(data) > max_bytes:
                raise FetchError('response_too_large')
            if validate:
                validate(data, saved['headers'])
            return {'data': data, 'headers': saved['headers'], 'receipt': receipt, 'cache_hit': True, 'attempts': 0}
        deadline = self.clock() + self.deadline
        host = urllib.parse.urlsplit(url).hostname
        request = urllib.request.Request(url, headers={'User-Agent': 'GIS-puskesmas-academic/1.0', **headers})
        for attempt in range(3):
            try:
                with HOST_LOCK:
                    wait = max(0, HOST_LAST.get(host, self.clock() - self.interval) + self.interval - self.clock())
                    if self.clock() + wait >= deadline:
                        raise RetryDeferred(datetime.fromtimestamp(self.wall_clock() + wait, timezone.utc).isoformat())
                    self.sleep(wait)
                    HOST_LAST[host] = self.clock()
                    remaining = deadline - self.clock()
                    with self.opener.open(request, timeout=min(60, remaining)) as response:
                        if getattr(response, 'status', 200) != expected_status:
                            raise FetchError('unexpected_http_status')
                        response_headers = {name.lower(): value for name, value in response.headers.items()
                                            if name.lower() in ('content-type', 'etag', 'last-modified', 'content-range')}
                        chunks, received = [], 0
                        read = getattr(response, 'read1', response.read)
                        sock = getattr(getattr(getattr(response, 'fp', None), 'raw', None), '_sock', None)
                        while True:
                            if self.clock() >= deadline:
                                raise FetchError('job_deadline_exceeded')
                            if sock is not None and sock.fileno() >= 0:
                                sock.settimeout(min(60, deadline - self.clock()))
                            chunk = read(min(65536, max_bytes + 1 - received))
                            if not chunk:
                                break
                            chunks.append(chunk)
                            received += len(chunk)
                            if received > max_bytes:
                                raise FetchError('response_too_large')
                        data = b''.join(chunks)
                if not data:
                    raise FetchError('empty_response')
                if validate:
                    validate(data, response_headers)
                receipt = snapshot(data, self.root, source_id, edition, url, 'https_download') if persist else None
                if cache:
                    atomic_json(index, {'identity': identity, 'headers': response_headers, 'receipt': receipt})
                return {'data': data, 'headers': response_headers, 'receipt': receipt, 'cache_hit': False, 'attempts': attempt + 1}
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504):
                    raise FetchError('http_' + str(exc.code)) from None
                retry_after = exc.headers.get('Retry-After') if exc.headers else None
                if retry_after:
                    try:
                        delay = float(retry_after) if retry_after.isdigit() else max(0, parsedate_to_datetime(retry_after).timestamp() - self.wall_clock())
                    except (ValueError, TypeError, OverflowError):
                        raise RetryDeferred(None) from None
                else:
                    delay = (5, 15, 15)[attempt] + self.jitter()
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                delay = (5, 15, 15)[attempt] + self.jitter()
            if attempt == 2:
                raise FetchError('retry_exhausted') from None
            if self.clock() + delay >= deadline:
                raise RetryDeferred(datetime.fromtimestamp(self.wall_clock() + delay, timezone.utc).isoformat()) from None
            self.sleep(delay)
        raise FetchError('retry_exhausted')
