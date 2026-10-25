import copy

import pytest
from shapely.geometry import Polygon, mapping

from gis_pipeline.etl.audit_locations import audit
from gis_pipeline.etl.geocode import build_queue


@pytest.fixture
def inputs():
    facilities, rows = [], []
    for n, lon in enumerate([112, 112, 113], 1):
        code = f'3501010000{n}'
        attrs = {'nama_puskesmas': 'Synthetic '+str(n), 'alamat': 'Synthetic road '+str(n),
                 'kecamatan': 'Synthetic district', 'kabupaten': 'Synthetic parent', 'provinsi': 'Jawa Timur'}
        source = {'source_id': 'fixture', 'source_hash': 'a'*64, 'source_locator': 'row/'+str(n), 'dataset': 'coordinates_csv'}
        facilities.append({'facility_code': code, 'region_code': '3501010', 'parent_code': '3501',
            'attributes': attrs, 'baseline_coordinate_present': True,
            'coordinate_candidates': [{'longitude': lon, 'latitude': -7, 'source': source}]})
        rows.append({**source, 'normalized_fields': {**attrs, 'facility_code': code, 'longitude': lon, 'latitude': -7},
            'raw_fields': {'query_alamat': 'Synthetic name only', 'status_geocoding': 'Ditemukan'}})
    queue = build_queue({'facilities': facilities}, {'geometry_validation_complete': True,
                        'features': [{'region_code': '3501010'}]}, 'fixture')
    boundaries = {'features': [{'properties': {'region_code': '3501010'},
        'geometry': mapping(Polygon([(112, -7), (112.1, -7), (112.1, -7.1), (112, -7.1)]))}]}
    return queue, rows, boundaries


def test_boundary_points_are_covered_without_auto_acceptance(inputs):
    before = copy.deepcopy(inputs)
    result = audit(*inputs)
    assert before == inputs
    assert result['summary']['inside_assigned_boundary'] == 2
    assert result['summary']['outside_assigned_boundary'] == 1
    assert result['summary']['near_boundary_50m'] == 2
    assert result['summary']['verified'] == 0
    assert result['duplicate_groups'] == [['35010100001', '35010100002']]
    assert result['facility_evidence_review_complete'] is False
    assert all(r['result_status'] == 'pending' for r in result['records'])
    assert result['batches'][0]['completed'] == []
    assert len(result['batches'][0]['pending']) == 3
    assert result == audit(*inputs)


@pytest.mark.parametrize('defect', ['point', 'name', 'code', 'duplicate', 'boundary'])
def test_rejects_changed_source_or_identity(inputs, defect):
    queue, rows, boundaries = inputs
    if defect == 'point': rows[0]['normalized_fields']['longitude'] = 114
    elif defect == 'name': rows[0]['normalized_fields']['nama_puskesmas'] = 'Different'
    elif defect == 'code': rows[0]['normalized_fields']['facility_code'] = '35010100099'
    elif defect == 'duplicate': queue['entries'].append(copy.deepcopy(queue['entries'][0]))
    else: boundaries['features'].append(copy.deepcopy(boundaries['features'][0]))
    with pytest.raises(ValueError): audit(queue, rows, boundaries)
