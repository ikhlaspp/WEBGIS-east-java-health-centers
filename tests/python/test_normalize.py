import copy
import hashlib
import json

import pytest

from gis_pipeline.etl.normalize import (
    FIELDS, code, coordinate, envelope, match_key, normalize_facility, normalize_indicator,
    normalize_table, read_table, run, text,
)


RECEIPT = {'source_id': 'synthetic', 'edition': '2023', 'sha256': 'a' * 64}


def indicator(value, metric='population', unit='jiwa'):
    return {'raw_value': value, 'indicator': metric, 'unit': unit, 'locale': 'id_ID',
            'regency_raw': ' Synthetic ', 'district_raw': 'A', 'observation_year': 2023,
            'year_evidence': 'Synthetic table 2023', 'unit_evidence': 'Synthetic header'}


@pytest.mark.parametrize('raw,metric,unit,expected', [
    ('30.001', 'population', 'jiwa', 30001), ('1.234,50', 'area', 'km2', '1234.50'),
    ('181280', 'area', 'ha', '1812.80'), ('...', 'population', 'jiwa', None),
    ('0', 'population', 'jiwa', 0),
])
def test_declared_conversions_keep_raw_and_reasons(raw, metric, unit, expected):
    parsed = indicator(raw, metric, unit)
    original = copy.deepcopy(parsed)
    row = envelope(RECEIPT, 'batch', 1, 'csv/row/2', copy.deepcopy(parsed))
    result = normalize_indicator(row, parsed)
    assert result['disposition'] == 'accepted'
    assert result['normalized_fields']['value'] == expected
    assert result['raw_fields'] == original == parsed
    conversion = next(t for t in result['transform_log'] if t['field'] == 'value')
    assert conversion['before'] == raw
    assert conversion['after'] == expected
    assert result['data_quality_accepted'] is False


@pytest.mark.parametrize('raw,metric,changes', [
    ('0', 'area', {}), ('-2', 'population', {}), ('=SUM(A1:A2)', 'population', {}),
    ('1.234', 'population', {'locale': None}), ('2', 'population', {'observation_year': None}),
])
def test_invalid_observations_are_quarantined(raw, metric, changes):
    parsed = {**indicator(raw, metric, 'km2' if metric == 'area' else 'jiwa'), **changes}
    row = normalize_indicator(envelope(RECEIPT, 'b', 1, 'row/1', parsed), parsed)
    assert row['disposition'] == 'quarantined'
    assert row['errors']


def test_unicode_display_and_match_keys_do_not_change_identity():
    assert text('  Cafe\u0301   District ') == 'Caf\u00e9   District'
    assert match_key('  Cafe\u0301   District ') == 'caf\u00e9 district'
    assert code('00123', 5) == '00123'
    assert code(35010200001.0, 11, numeric_source=True) == '35010200001'
    with pytest.raises(ValueError):
        code(123, 5, numeric_source=True)
    with pytest.raises(ValueError):
        code(123, 3)


def test_coordinates_signed_missing_range_and_no_promotion():
    assert coordinate('-7.1234', 90) == '-7.1234'
    assert coordinate('', 90) is None
    assert coordinate('0', 90) == '0'
    with pytest.raises(ValueError):
        coordinate('-91', 90)


def test_source_verified_label_cannot_promote_coordinates_and_partial_pair_is_rejected():
    raw = {field: 'Synthetic' for field in FIELDS}
    raw.update(kode_puskesmas='35010200001', latitude='-7.1', longitude='112.2', status_geocoding='verified')
    row = normalize_facility(envelope(RECEIPT, 'b', 1, 'csv/row/2', raw), coordinates=True)
    assert row['normalized_fields']['location_status'] == 'candidate_unverified'
    assert row['data_quality_accepted'] is False
    incomplete = {**raw, 'longitude': ''}
    row = normalize_facility(envelope(RECEIPT, 'b', 1, 'csv/row/2', incomplete), coordinates=True)
    assert row['disposition'] == 'quarantined'
    assert 'INCOMPLETE_COORDINATE_PAIR' in row['errors']


@pytest.mark.parametrize('data', [b'name,name\na,b\n', b'other,value\na,1\n', b'name,value\n\xff,1\n'])
def test_ambiguous_header_or_encoding_fails_batch(data):
    with pytest.raises((ValueError, UnicodeError)):
        read_table(data, {'format': 'csv', 'headers': ['name', 'value']})


def test_row_width_is_counted_as_quarantine():
    spec = {'format': 'csv', 'kind': 'count', 'headers': ['kabupaten', 'kecamatan', 'jumlah_puskesmas']}
    rows, meta = normalize_table(b'kabupaten,kecamatan,jumlah_puskesmas\nA,B,2,extra\nA,C,0\n', spec, RECEIPT, 'batch')
    assert [r['disposition'] for r in rows] == ['quarantined', 'accepted']
    assert rows[0]['raw_cells'] == ['A', 'B', '2', 'extra']
    assert rows[1]['normalized_fields']['facility_count'] == 0
    assert meta['parsed_data_rows'] == 2


def test_count_totals_are_not_district_details():
    spec = {'format': 'csv', 'kind': 'count', 'headers': ['kabupaten', 'kecamatan', 'jumlah_puskesmas'],
            'total_labels': ['TOTAL']}
    rows, _ = normalize_table(b'kabupaten,kecamatan,jumlah_puskesmas\nA,B,2\nA,TOTAL,2\nTOTAL,,2\n', spec, RECEIPT, 'batch')
    assert [r['disposition'] for r in rows] == ['accepted', 'aggregate', 'aggregate']
    assert [r['normalized_fields']['facility_count'] for r in rows] == [2, 2, 2]


def test_repeat_run_same_content_and_counts_and_tampering_fails(tmp_path):
    data = b'kabupaten,kecamatan,jumlah_puskesmas\nA,Same,2\nB,Same,0\nA,B,-2\n'
    raw = tmp_path / 'data/raw/source.bin'
    raw.parent.mkdir(parents=True)
    raw.write_bytes(data)
    receipt = {**RECEIPT, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'raw_path': 'data/raw/source.bin'}
    manifest = {'availability_complete': True, 'plan_sha256': 'p', 'files': [receipt]}
    specs = [{'dataset': 'counts', 'source_id': 'synthetic', 'sha256': receipt['sha256'],
              'format': 'csv', 'kind': 'count', 'headers': ['kabupaten', 'kecamatan', 'jumlah_puskesmas']}]
    first = run(tmp_path, manifest, specs, 'data/staging/normalized')
    second = run(tmp_path, manifest, specs, 'data/staging/normalized')
    assert first == second
    assert first['raw'] == 3
    assert first['counts'] == {'accepted': 2, 'quarantined': 1, 'aggregate': 0}
    staged = json.loads((tmp_path / first['outputs']['accepted']['path']).read_text())['rows']
    assert [r['normalized_fields']['region_match_key'] for r in staged] == [['a', 'same'], ['b', 'same']]
    with pytest.raises(ValueError, match='SOURCE_ROW_COUNT_MISMATCH'):
        run(tmp_path, manifest, [{**specs[0], 'expected_rows': 4}], 'data/staging/rejected')
    assert not (tmp_path / 'data/staging/rejected').exists()
    with pytest.raises(ValueError, match='No source tables'):
        run(tmp_path, manifest, [], 'data/staging/rejected')
    raw.write_bytes(b'tampered')
    with pytest.raises(ValueError):
        run(tmp_path, manifest, specs, 'data/staging/normalized')
