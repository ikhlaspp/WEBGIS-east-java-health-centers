"""Bounded HTTPS acquisition and immutable local source snapshots."""

import hashlib
import io
import ipaddress
import json
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path


class RemoteZipReader(io.RawIOBase):
    """Read bounded public ZIP ranges, verifying object identity on every request."""

    def __init__(self, url, size, allowed_hosts, opener=None):
        validate_url(url, allowed_hosts)
        if not isinstance(size, int) or not 0 < size <= 512 * 1024 * 1024:
            raise ValueError('Archive size outside supported bounds')
        self.url, self.size, self.position, self.etag = url, size, 0, None
        self.opener = opener or urllib.request.build_opener(CheckedRedirect(allowed_hosts))

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        if whence not in (0, 1, 2):
            raise ValueError('Invalid seek mode')
        position = offset + (0 if whence == 0 else self.position if whence == 1 else self.size)
        if not 0 <= position <= self.size:
            raise ValueError('Seek outside archive')
        self.position = position
        return position

    def read(self, size=-1):
        size = self.size - self.position if size < 0 else min(size, self.size - self.position)
        if size == 0:
            return b''
        if size > 96 * 1024 * 1024:
            raise ValueError('ZIP range exceeds read bound')
        start, end = self.position, self.position + size - 1
        request = urllib.request.Request(self.url, headers={
            'User-Agent': 'GIS-puskesmas-academic/1.0', 'Range': f'bytes={start}-{end}'})
        with self.opener.open(request, timeout=60) as response:
            if response.status != 206 or response.headers.get('Content-Range') != f'bytes {start}-{end}/{self.size}':
                raise ValueError('Source did not honor the exact archive range')
            etag = response.headers.get('ETag')
            if not etag or (self.etag is not None and etag != self.etag):
                raise ValueError('Archive identity missing or changed during download')
            self.etag = etag
            data = response.read(size + 1)
            if len(data) != size:
                raise ValueError('Incomplete archive range')
        self.position += size
        return data


def fetch_zip_member(url, archive_size, member, raw_root, source_id, edition, allowed_hosts):
    reader = RemoteZipReader(url, archive_size, allowed_hosts)
    with zipfile.ZipFile(reader) as archive:
        info = archive.getinfo(member)
        if info.file_size > 320 * 1024 * 1024 or info.compress_size > 96 * 1024 * 1024:
            raise ValueError('Archive member exceeds acquisition bounds')
        data = archive.read(info)  # ZIP CRC is verified; no archive paths are extracted.
    receipt = snapshot(data, raw_root, source_id, edition, url + '#' + member, 'https_zip_member')
    receipt.update(archive_etag=reader.etag, archive_total_bytes=archive_size,
                   archive_member=member, archive_member_crc=info.CRC)
    return receipt


def validate_url(url, allowed_hosts):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname not in allowed_hosts
            or parsed.username or parsed.password or parsed.port not in (None, 443)):
        raise ValueError('Source URL must use HTTPS and an explicitly allowed host')
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError('Source host resolves to a non-public destination')


class CheckedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_hosts):
        self.allowed_hosts = allowed_hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl, self.allowed_hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def snapshot(data, raw_root, source_id, edition, source_url, acquired_from):
    if not re.fullmatch(r'[a-z0-9_-]+', source_id):
        raise ValueError('Invalid source identifier')
    digest = hashlib.sha256(data).hexdigest()
    folder = Path(raw_root) / source_id
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (digest + '.bin')
    try:
        with target.open('xb') as handle:
            handle.write(data)
    except FileExistsError:
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError('Existing immutable source hash mismatch')
    manifest = {
        'source_id': source_id, 'edition': edition, 'source_url': source_url,
        'acquired_from': acquired_from, 'acquired_at': datetime.now(timezone.utc).isoformat(),
        'sha256': digest, 'bytes': len(data), 'raw_path': str(target),
    }
    receipt = folder / (digest + '-' + str(time.time_ns()) + '.json')
    receipt.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def fetch_pdf(url, raw_root, source_id, edition, allowed_hosts, max_bytes=64 * 1024 * 1024):
    validate_url(url, allowed_hosts)
    opener = urllib.request.build_opener(CheckedRedirect(allowed_hosts))
    request = urllib.request.Request(url, headers={
        'User-Agent': 'GIS-puskesmas-academic/1.0 (+https://github.com/ikhlaspp/WEBGIS-east-java-health-centers)',
        'Accept': 'application/pdf',
    })
    for attempt in range(3):
        try:
            with opener.open(request, timeout=60) as response:
                content_type = response.headers.get_content_type()
                if content_type not in ('application/pdf', 'application/octet-stream'):
                    raise ValueError('Source response is not a PDF')
                data = response.read(max_bytes + 1)
                if len(data) > max_bytes or not data.startswith(b'%PDF-'):
                    raise ValueError('Source is oversized or has invalid PDF magic')
                return snapshot(data, raw_root, source_id, edition, url, 'https_download')
        except urllib.error.HTTPError as exc:
            if attempt == 2 or exc.code not in (429, 500, 502, 503, 504):
                raise
            delay = exc.headers.get('Retry-After', '')
            if delay and (not delay.isdigit() or int(delay) > 60):
                raise RuntimeError('Source retry requires a later scheduled attempt') from exc
            time.sleep(max(1, int(delay) if delay else 2 ** attempt))
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
