import copy
import hashlib
import json

import pytest

from gis_pipeline.etl.boundaries import collect_features, coverage, detail_line, parse_master
from gis_pipeline.etl.boundaries import candidate_links, reconcile_master, acquire_bridge


def test_official_reconciliation_retains_raw_disagreement_and_rejects_tampering(tmp_path):
    path = tmp_path / 'bridge.json'
    path.write_text(json.dumps([{'kode_bps': '3501010', 'nama_bps': 'NEW NAME'}]))
    summary = {'code': '3501010', 'name': 'NEW NAME', 'locator': 'synthetic/1'}
    master = {'rows': [{'code': '3501010', 'name': 'OLD NAME', 'raw_line': 'original'}],
              'summary_discrepancies': [summary], 'report': {'coverage_complete': True, 'summary_rows': 1}}
    receipt = {'raw_path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'edition': '2023_1.2022', 'source_url': 'https://sig.bps.go.id/rest-bridging/getwilayah?parent=3501&periode_merge=2023_1.2022'}
    decision = {'summary': summary, 'canonical_code': '3501010', 'canonical_name': 'NEW NAME', 'evidence_receipt': receipt}
    result = reconcile_master(master, [decision])
    assert result['report']['unresolved_source_conflicts'] == 0
    assert result['rows'][0]['name'] == 'NEW NAME'
    assert result['rows'][0]['raw_line'] == 'original'
    assert master['rows'][0]['name'] == 'OLD NAME'
    with pytest.raises(ValueError, match='duplicate'):
        reconcile_master(master, [decision, decision])
    path.write_text('[]')
    with pytest.raises(ValueError, match='hash'):
        reconcile_master(master, [decision])


def test_code_links_never_use_names_or_claim_historical_geometry():
    bridge = {'period': '2023_1.2022', 'records': [{'kode_dagri': '350101', 'kode_bps': '3501010', 'source_hash': 'synthetic'}]}
    collection = {'features': [{'properties': {'OBJECTID': 1, 'KDCPUM': '35.01.01', 'WADMKC': 'Unrelated name'}},
                               {'properties': {'OBJECTID': 2, 'KDCPUM': '', 'WADMKC': 'Matching name'}}]}
    result = candidate_links(collection, bridge)
    assert result['links'][0]['bps_code'] == '3501010'
    assert result['excluded'][0]['object_id'] == 2
    assert not result['historical_geometry_validated']
    assert not result['publication_allowed']
    collection['features'].append(copy.deepcopy(collection['features'][0]))
    with pytest.raises(ValueError, match='Multiple boundary'):
        candidate_links(collection, bridge)


def test_bridge_checks_parent_counts_before_use(monkeypatch):
    monkeypatch.setattr('gis_pipeline.etl.boundaries.fetch_json', lambda *args: ([], {}))
    with pytest.raises(ValueError, match='coverage'):
        acquire_bridge({'regencies': [{'code': '3501', 'expected_districts': 12}]}, 'unused')


def test_bridge_resume_verifies_receipt_without_redownloading(tmp_path, monkeypatch):
    path = tmp_path / 'cached.json'
    path.write_text(json.dumps([{'kode_bps': '3501010', 'kode_dagri': '350101', 'nama_bps': 'Synthetic'}]))
    receipt = {'raw_path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'edition': '2023_1.2022', 'source_url': 'https://sig.bps.go.id/rest-bridging/getwilayah?parent=3501&level=kecamatan&periode_merge=2023_1.2022'}
    master = {'regencies': [{'code': '3501', 'expected_districts': 1}], 'rows': [{'code': '3501010'}]}
    def unexpected(*args):
        pytest.fail('Valid cached evidence must not be redownloaded')
    monkeypatch.setattr('gis_pipeline.etl.boundaries.fetch_json', unexpected)
    result = acquire_bridge(master, tmp_path, [receipt])
    assert result['records'][0]['kode_bps'] == '3501010'
    path.write_text('[]')
    with pytest.raises(ValueError, match='hash'):
        acquire_bridge(master, tmp_path, [receipt])


def test_split_district_name_preserves_code_without_guessing():
    lines = ['SYNTHETIC NORTH', '35 01 010 35 01 010 001 SYNTHETIC VILLAGE', 'ISLAND']
    assert detail_line(lines, 1).groups() == ('35', '01', '010', 'SYNTHETIC NORTH ISLAND')
    assert detail_line(['35 01 010 001 SYNTHETIC VILLAGE'], 0) is None
    assert detail_line(['UNKNOWN', lines[1], '35 01 010 002 OTHER'], 1) is None


def test_conflicting_master_tables_remain_unapproved(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from contextlib import nullcontext
    text = ('Master File Desa Provinsi Jawa Timur 2023\nNama Kecamatan\nUrban Rural Total\n'
            '1 35 01 010 SYNTHETIC NORTH 1 1 2\n'
            '35 01 010 SYNTHETIC SOUTH 35 01 010 001 SYNTHETIC VILLAGE')
    page = SimpleNamespace(chars=[], page_number=1, extract_text=lambda: text)
    monkeypatch.setattr('gis_pipeline.etl.boundaries.pdfplumber.open', lambda path: nullcontext(SimpleNamespace(pages=[page])))
    path = tmp_path / 'synthetic.pdf'
    path.write_bytes(b'synthetic mocked PDF')
    manifest = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'edition': '2023',
                'source_url': 'https://example.test/synthetic.pdf'}
    result = parse_master(path, manifest)
    assert result['rows'][0]['code'] == '3501010'
    assert result['rows'][0]['name'] == 'SYNTHETIC SOUTH'
    assert result['summary_discrepancies'][0]['name'] == 'SYNTHETIC NORTH'
    assert result['report']['source_conflicts'] == 1
    assert result['report']['complete'] is False


def source(changed=None):
    polygons = [[[0, 0], [1, 0], [1, 1], [0, 0]]]
    features = [
        {'type': 'Feature', 'properties': {'OID': 10, 'KDCBPS': '0000010', 'WADMKK': 'Synthetic'},
         'geometry': {'type': 'Polygon', 'coordinates': polygons}},
        {'type': 'Feature', 'properties': {'OID': 11, 'KDCBPS': None, 'WADMKK': None},
         'geometry': {'type': 'MultiPolygon', 'coordinates': [polygons, [[[2, 2], [3, 2], [3, 3], [2, 2]]]]}},
    ]
    calls = []
    def query(params):
        calls.append(params)
        if 'returnCountOnly' in params:
            return {'count': 2}
        if 'returnIdsOnly' in params:
            return {'objectIdFieldName': 'OID', 'objectIds': [10, 11]}
        selected = [int(i) for i in params['objectIds'].split(',')]
        page = {'type': 'FeatureCollection',
                'features': copy.deepcopy([f for f in features if f['properties']['OID'] in selected])}
        if changed:
            changed(page)
        return page
    return query, calls, features


def test_all_pages_preserve_text_codes_and_multipolygon_islands():
    query, calls, originals = source()
    result = collect_features(query, {'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1}, 'synthetic')
    assert result['features'] == originals
    assert result['features'][0]['properties']['KDCBPS'] == '0000010'
    assert len(result['features'][1]['geometry']['coordinates']) == 2
    assert len([call for call in calls if 'objectIds' in call]) == 2


@pytest.mark.parametrize('change', [lambda p: p.update(exceededTransferLimit=True),
                                   lambda p: p['features'].clear(),
                                   lambda p: p['features'].append(copy.deepcopy(p['features'][0])),
                                   lambda p: p['features'][0].update(geometry=None)])
def test_truncated_duplicate_or_missing_geometry_fails(change):
    query, _, _ = source(change)
    with pytest.raises(ValueError):
        collect_features(query, {'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1}, 'synthetic')


def test_count_mismatch_is_not_success():
    query = lambda p: {'count': 2} if 'returnCountOnly' in p else {'objectIds': [10], 'objectIdFieldName': 'OID'}
    with pytest.raises(ValueError, match='count/ID'):
        collect_features(query, {'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1}, 'synthetic')


def test_source_drift_is_not_success():
    base, _, _ = source()
    state = {'ids': 0}
    def query(params):
        if 'returnIdsOnly' in params:
            state['ids'] += 1
            if state['ids'] == 2:
                return {'objectIds': [10, 12]}
        return base(params)
    with pytest.raises(ValueError, match='changed'):
        collect_features(query, {'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 2}, 'synthetic')


def test_missing_region_codes_do_not_become_guessed_joins():
    _, _, features = source()
    report = coverage({'features': features}, ['3501010'])
    assert report['missing_or_invalid_bps_code'] == 2
    assert report['master_codes_without_polygon'] == ['3501010']
    assert report['status'] == 'candidate_requires_edition_license_and_crosswalk_review'
