import copy
import json

import pytest

from gis_pipeline.etl.geocode import NominatimProvider, build_queue, candidate, point, validate_decision


@pytest.fixture
def inputs():
    attrs = {'nama_puskesmas': 'Synthetic', 'alamat': 'Synthetic road', 'kecamatan': 'Island',
             'kabupaten': 'Synthetic regency', 'provinsi': 'Jawa Timur'}
    facilities = []
    for number in (1, 2):
        facilities.append({'facility_code': f'3501010000{number}', 'region_code': '3501010',
            'parent_code': '3501', 'attributes': attrs, 'baseline_coordinate_present': number == 1,
            'coordinate_candidates': [] if number == 2 else [{'longitude': '112', 'latitude': '-7',
                'source': {'source_id': 'archive', 'source_hash': 'a'*64, 'source_locator': 'row/1'}}]})
    return {'facilities': facilities}, {'geometry_validation_complete': True, 'features': [{'region_code': '3501010'}]}


def test_queue_preserves_missing_and_never_promotes(inputs):
    before = copy.deepcopy(inputs)
    result = build_queue(*inputs, 'synthetic-release')
    assert inputs == before
    assert result == build_queue(*inputs, 'synthetic-release')
    assert result['summary'] == {'facilities': 2, 'baseline_candidates': 1, 'baseline_missing': 1,
                                 'without_any_candidate': 1, 'candidate_records': 1, 'verified': 0}
    assert [e['snapshot_status'] for e in result['entries']] == ['unverified', 'missing']
    assert not any(e['radius_eligible'] for e in result['entries'])
    assert result['entries'][0]['candidates'][0]['retrieved_at'] is None
    assert result['entries'][1]['candidates'] == []
    assert 'Island' in result['entries'][1]['query']


def test_additional_spreadsheet_candidate_does_not_change_csv_baseline(inputs):
    master, boundaries = inputs
    master['facilities'][1]['coordinate_candidates'] = copy.deepcopy(master['facilities'][0]['coordinate_candidates'])
    result = build_queue(master, boundaries, 'draft')
    assert result['summary']['baseline_missing'] == 1
    assert result['summary']['without_any_candidate'] == 0
    assert len({e['candidates'][0]['review_id'] for e in result['entries']}) == 2


@pytest.mark.parametrize('defect', ['duplicate', 'unknown_region', 'empty', 'address'])
def test_queue_rejects_bad_inputs(inputs, defect):
    master, boundaries = inputs
    if defect == 'duplicate': master['facilities'].append(copy.deepcopy(master['facilities'][0]))
    elif defect == 'unknown_region': master['facilities'][0]['region_code'] = 'unknown'
    elif defect == 'empty': master['facilities'] = []
    else: master['facilities'][0]['attributes']['alamat'] = ''
    with pytest.raises(ValueError): build_queue(master, boundaries, 'draft')


@pytest.mark.parametrize('lon,lat', [(None, -7), (112, None), (float('nan'), -7), (112, 100), (True, -7)])
def test_bad_coordinate_pair(lon, lat):
    with pytest.raises(ValueError): point(lon, lat)


@pytest.fixture
def config():
    return {'provider_id': 'synthetic-provider', 'endpoint': 'https://geocoder.example/search',
            'edition': 'fixture', 'user_agent': 'SyntheticFixture/1.0', 'terms_url': 'https://geocoder.example/terms',
            'attribution': 'Synthetic fixture', 'selection_reason': 'Test only', 'selected_by': 'fixture',
            'selected_at': '2026-10-25T00:00:00Z', 'batch_permitted': True, 'cache_permitted': True,
            'interval_seconds': 1}


@pytest.mark.parametrize('defect', ['public', 'no_permission', 'no_cache', 'no_identity', 'too_fast', 'credentials'])
def test_provider_requires_explicit_permitted_configuration(tmp_path, config, defect):
    if defect == 'public': config['endpoint'] = 'https://nominatim.openstreetmap.org/search'
    elif defect == 'no_permission': config['batch_permitted'] = False
    elif defect == 'no_cache': config['cache_permitted'] = False
    elif defect == 'no_identity': del config['selected_by']
    elif defect == 'too_fast': config['interval_seconds'] = 0
    else: config['endpoint'] = 'https://secret:token@geocoder.example/search'
    with pytest.raises(ValueError): NominatimProvider(tmp_path, config)


def test_provider_records_exact_query_receipt_and_centroid(tmp_path, config, inputs):
    calls = []
    class Client:
        def fetch(self, url, *args, **kwargs):
            calls.append((url, kwargs))
            return {'data': json.dumps([{'lon': '112', 'lat': '-7', 'osm_type': 'relation', 'osm_id': 123,
                'addresstype': 'village', 'display_name': 'Synthetic village'}]).encode(),
                'receipt': {'sha256': 'a'*64, 'raw_path': 'data/raw/fixture.bin', 'acquired_at': '2026-10-25T00:00:00Z'},
                'cache_hit': True}
    entry = build_queue(*inputs, 'draft')['entries'][1]
    result = NominatimProvider(tmp_path, config, client=Client()).search(entry, 'draft')
    item = result['candidates'][0]
    assert result['cache_hit'] is True
    assert item['query'] == entry['query']
    assert item['provider_object_id'] == 'relation/123'
    assert item['centroid_candidate'] is True
    assert item['precision_level'] == 'village'
    assert item['result_status'] == 'pending'
    assert item['raw_response_sha256'] == 'a'*64
    assert 'countrycodes=id' in calls[0][0]
    assert 'bounded=' not in calls[0][0]


@pytest.fixture
def decision_pair():
    record = candidate('draft', '35010100001', 'source', 'Synthetic address', 112, -7, 'fixture', '1')
    decision = {**record, 'result_status': 'accepted', 'precision_level': 'facility', 'centroid_candidate': False,
                'reviewer_id': 'fixture-reviewer', 'reviewed_at': '2026-10-25T00:00:00Z',
                'decision_reason': 'Synthetic facility identity evidence', 'evidence_url': 'https://example.org/fixture'}
    return record, decision


def test_valid_decision_does_not_mutate_candidate(decision_pair):
    record, decision = decision_pair
    assert validate_decision(record, decision) == decision
    assert record['result_status'] == 'pending'


@pytest.mark.parametrize('field,value', [('facility_code', '35010100002'), ('release_id', 'other'),
    ('source_id', 'other'), ('candidate_lon', 113), ('precision_level', 'village'), ('centroid_candidate', True),
    ('reviewer_id', ''), ('reviewed_at', '2026-10-25'), ('evidence_url', None)])
def test_unproven_or_mismatched_acceptance_is_rejected(decision_pair, field, value):
    record, decision = decision_pair
    decision[field] = value
    with pytest.raises(ValueError): validate_decision(record, decision)


def test_photon_poi_is_not_automatically_facility_precision(tmp_path, config, inputs):
    from gis_pipeline.etl.geocode import PhotonProvider
    config['endpoint'] = 'https://geocoder.example/api'
    class Client:
        def fetch(self, url, *args, **kwargs):
            assert 'countrycode=ID' in url
            return {'data': json.dumps({'features': [{'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [112, -7]},
                'properties': {'osm_type': 'N', 'osm_id': 12, 'osm_key': 'amenity', 'osm_value': 'clinic',
                               'name': 'Synthetic clinic'}}]}).encode(),
                'receipt': {'sha256': 'b'*64, 'raw_path': 'data/raw/fixture.bin', 'acquired_at': '2026-10-25T00:00:00Z'},
                'cache_hit': False}
    entry = build_queue(*inputs, 'draft')['entries'][0]
    item = PhotonProvider(tmp_path, config, client=Client()).search(entry, 'draft')['candidates'][0]
    assert item['provider_object_id'] == 'node/12'
    assert item['precision_level'] == 'unknown'
    assert item['centroid_candidate'] is None
    assert item['result_status'] == 'pending'


def test_cli_checkpoint_resumes_without_repeating_completed_search(tmp_path, monkeypatch, config, inputs):
    import importlib.util
    import sys
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('geocode_cli', Path(__file__).resolve().parents[2] / 'scripts/etl/geocode.py')
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    monkeypatch.setattr(cli, 'ROOT', tmp_path)
    folder = tmp_path / 'data/staging'
    folder.mkdir(parents=True)
    (folder / 'location_queue.json').write_text(json.dumps(build_queue(*inputs, 'draft')))
    config.update(adapter='photon', endpoint='https://geocoder.example/api', max_unique_queries=2)
    config_path = tmp_path / 'provider.json'
    config_path.write_text(json.dumps(config))
    calls = []
    class Provider:
        def __init__(self, *args): pass
        def search(self, entry, release):
            calls.append(entry['facility_code'])
            if len(calls) == 2: raise ValueError('Synthetic interruption')
            return {'query': entry['query'], 'candidates': [], 'status': 'no_match', 'cache_hit': False}
    monkeypatch.setattr(cli, 'PhotonProvider', Provider)
    monkeypatch.setattr(sys, 'argv', ['geocode.py', 'search', '--provider-config', str(config_path),
        '--codes', '35010100001', '35010100002', '--checkpoint', 'data/staging/checkpoint.json'])
    assert cli.main() == 1
    state = json.loads((folder / 'checkpoint.json').read_text())
    assert len(state['completed']) == 1 and len(state['blocked']) == 1 and not state['pending']
    assert cli.main() == 0
    assert calls == ['35010100001', '35010100002', '35010100002']
    assert cli.main() == 0
    assert len(calls) == 3
    saved = next(iter(json.loads((folder / 'checkpoint.json').read_text())['completed'].values()))
    (tmp_path / saved['path']).write_text('{}')
    with pytest.raises(ValueError, match='checksum'): cli.main()
