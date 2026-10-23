import csv
import hashlib
import json
from email.message import Message
from io import BytesIO
from pathlib import Path

import pytest

from gis_pipeline.etl.facilities import FIELDS, completeness, is_watermark_glyph, parse_csv, parse_pdf, parse_rows
from gis_pipeline.etl.sources import CheckedRedirect, fetch_pdf, snapshot, validate_url

FIXTURE = json.loads((Path(__file__).parents[1] / 'data/wf-057/facility-rows.json').read_text())
MANIFEST = {'source_id': 'synthetic-facility', 'sha256': '0' * 64,
            'source_url': 'https://example.test/synthetic', 'edition': '2024-S1',
            'acquired_at': '2024-01-01T00:00:00Z'}


def test_raw_values_leading_zero_and_provenance_survive():
    result = parse_rows(FIXTURE['header'], FIXTURE['rows'], MANIFEST, 'fixture')
    assert FIXTURE['synthetic'] is True
    assert len(result['rows']) == 1
    row = result['rows'][0]
    assert row['fields']['kode_puskesmas'] == '00000000001'
    assert row['raw_fields']['alamat'] == 'Synthetic street\nBlock A'
    assert row['fields']['alamat'] == 'Synthetic street Block A'
    assert row['locator'] == 'fixture/row/2'
    assert row['source_hash'] == MANIFEST['sha256']
    assert row['status'] == 'staging_unverified'
    assert result['quarantined'][0]['reasons'] == ['invalid_facility_code']
    assert result['aggregates'][0]['raw_fields']['no'] == 'TOTAL'
    assert not completeness(result, 1, 1)['complete']


def test_missing_header_preserves_unparsed_rows():
    result = parse_rows(list(FIELDS)[1:], FIXTURE['rows'], MANIFEST, 'fixture')
    assert not result['rows']
    assert result['diagnostics'][0]['code'] == 'header_mismatch'
    assert result['diagnostics'][0]['raw_rows'] == FIXTURE['rows']


def test_duplicate_codes_block_completeness():
    result = parse_rows(FIELDS, [FIXTURE['rows'][0]] * 2, MANIFEST, 'fixture')
    assert completeness(result, 2, 1)['duplicates'] == ['00000000001']
    assert not completeness(result, 2, 1)['complete']


def test_valid_single_row_has_complete_independent_expected_counts():
    result = parse_rows(FIELDS, [FIXTURE['rows'][0]], MANIFEST, 'fixture')
    report = completeness(result, 1, 1)
    assert report['complete']
    assert report['service_types'] == {'Rawat Inap': 1}


def test_csv_snapshot_is_immutable_and_hash_checked(tmp_path):
    source = tmp_path / 'source.csv'
    with source.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        writer.writerow(FIXTURE['rows'][0])
    receipt = snapshot(source.read_bytes(), tmp_path / 'raw', 'fixture', '2024-S1',
                       'https://example.test/synthetic.csv', 'synthetic_fixture')
    assert receipt['sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert len(parse_csv(receipt['raw_path'], receipt)['rows']) == 1
    source.write_text('tampered')
    with pytest.raises(ValueError, match='hash mismatch'):
        parse_csv(source, receipt)
    assert Path(receipt['raw_path']).read_bytes().startswith(b'no,kode_puskesmas')


def test_pdf_rejects_wrong_snapshot_before_parsing(tmp_path):
    with pytest.raises(ValueError, match='approved 2024-S1'):
        parse_pdf(tmp_path / 'unused.pdf', {**MANIFEST, 'edition': '2025-S1'})


def test_watermark_filter_preserves_normal_table_characters():
    glyph = {'object_type': 'char', 'size': 56, 'matrix': (0.707, 0.707, -0.707, 0.707, 0, 0),
             'non_stroking_color': (0.85,)}
    assert is_watermark_glyph(glyph)
    assert not is_watermark_glyph({**glyph, 'size': 4.68})
    assert not is_watermark_glyph({**glyph, 'non_stroking_color': (0,)})
    assert not is_watermark_glyph({**glyph, 'matrix': (1, 0, 0, 1, 0, 0)})


@pytest.mark.parametrize('url', ['http://kemkes.go.id/file.pdf',
                               'https://unapproved.example/file.pdf',
                               'https://user:password@kemkes.go.id/file.pdf',
                               'https://kemkes.go.id:8443/file.pdf'])
def test_source_url_rejects_unapproved_destinations(url):
    with pytest.raises(ValueError, match='HTTPS'):
        validate_url(url, {'kemkes.go.id'})


def test_source_url_rejects_private_resolution(monkeypatch):
    monkeypatch.setattr('gis_pipeline.etl.sources.socket.getaddrinfo',
                        lambda *args, **kwargs: [(2, 1, 6, '', ('127.0.0.1', 443))])
    with pytest.raises(ValueError, match='non-public'):
        validate_url('https://kemkes.go.id/file.pdf', {'kemkes.go.id'})


@pytest.mark.parametrize('content_type,body,limit', [
    ('text/html', b'<html>login</html>', 100),
    ('application/pdf', b'not actually a pdf', 100),
    ('application/pdf', b'%PDF-' + b'x' * 100, 20),
])
def test_fetch_rejects_login_corrupt_and_oversized_responses(monkeypatch, tmp_path, content_type, body, limit):
    monkeypatch.setattr('gis_pipeline.etl.sources.socket.getaddrinfo',
                        lambda *args, **kwargs: [(2, 1, 6, '', ('8.8.8.8', 443))])

    class Response(BytesIO):
        headers = Message()

    response = Response(body)
    response.headers['Content-Type'] = content_type

    class Opener:
        def open(self, *args, **kwargs):
            return response

    monkeypatch.setattr('gis_pipeline.etl.sources.urllib.request.build_opener', lambda *args: Opener())
    with pytest.raises(ValueError):
        fetch_pdf('https://kemkes.go.id/file.pdf', tmp_path, 'fixture', '2024-S1',
                  {'kemkes.go.id'}, max_bytes=limit)
    assert not list(tmp_path.rglob('*.bin'))


def test_redirect_cannot_leave_source_allowlist():
    handler = CheckedRedirect({'kemkes.go.id'})
    with pytest.raises(ValueError):
        handler.redirect_request(None, None, 302, 'Found', {}, 'https://unapproved.example/file.pdf')
