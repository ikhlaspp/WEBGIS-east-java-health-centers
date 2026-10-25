import copy
import json
from pathlib import Path

import pytest
from shapely.geometry import mapping, shape

from gis_pipeline.analysis.buffers import RADII, reference_buffer
from gis_pipeline.analysis.coverage import coverage, geodesic_area


FIXTURE = json.loads((Path(__file__).resolve().parents[2] / 'docs/pekerjaan/WF-049/contoh-spasial.json').read_text(encoding='utf-8'))


def fixture():
    features = []
    for code, lon, lat in [('35010100001', 112, -7), ('35010100002', 112.005, -7)]:
        for radius in RADII:
            features.append({'properties': {'facility_code': code, 'radius_m': radius, 'release_id': 'fixture'}, 'geometry': mapping(reference_buffer(lon, lat, radius))})
    buffers = {'release_id': 'fixture', 'analysis_run_id': 'fixture-run', 'method_version': 'python-local-aeqd-buffer-v1', 'registered_count': 2, 'eligible_count': 2, 'excluded_count': 0, 'excluded': [], 'features': features}
    buffers['parameters'] = {'radii_m': list(RADII), 'quad_segs': 32, 'storage_crs': 'EPSG:4326'}
    boundaries = {'release_id': 'fixture', 'geometry_role': 'analysis', 'features': [
        {'properties': {'district_id': 'target'}, 'geometry': FIXTURE['region']},
        {'properties': {'district_id': 'neighbour'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[111.95, -7.02], [112, -7.02], [112, -6.98], [111.95, -6.98], [111.95, -7.02]]]}}],
        'facility_assignments': [{'facility_code': '35010100001', 'district_id': 'neighbour'}, {'facility_code': '35010100002', 'district_id': 'neighbour'}]}
    return buffers, boundaries


def test_union_overlap_neighbours_islands_and_monotonic_coverage():
    buffers, boundaries = fixture()
    result = coverage(buffers, boundaries)
    target = [row for row in result['results'] if row['district_id'] == 'target']
    assert [row['radius_m'] for row in target] == [1000, 3000, 5000]
    assert all(row['registered_count'] == 0 and row['contributing_count'] == 2 for row in target)
    assert 0 < target[0]['coverage_pct'] < 100
    assert target[0]['covered_area_m2'] <= target[1]['covered_area_m2'] <= target[2]['covered_area_m2']
    region = shape(FIXTURE['region'])
    individual_sum = sum(geodesic_area(shape(f['geometry']).intersection(region)) for f in buffers['features'] if f['properties']['radius_m'] == 1000)
    assert target[0]['covered_area_m2'] < individual_sum
    assert target[0]['geometry_area_m2'] == pytest.approx(geodesic_area(region))
    assert len(region.geoms) == 2
    assert target[0]['geometry_area_m2'] > geodesic_area(region.geoms[0])


def test_no_eligible_data_is_unavailable_not_zero():
    buffers, boundaries = fixture()
    buffers.update(features=[], eligible_count=0, excluded_count=2, excluded=[{'facility_code': f'3501010000{n}', 'reason': 'not_verified'} for n in (1, 2)])
    result = coverage(buffers, boundaries)
    assert all(row['coverage_pct'] is None and row['covered_area_m2'] is None and row['geometry_area_m2'] is None for row in result['results'])
    assert all(row['completeness'] == 'unavailable' for row in result['results'])


def test_valid_empty_intersection_is_zero_with_positive_denominator():
    buffers, boundaries = fixture()
    boundaries['features'][0]['geometry'] = {'type': 'Polygon', 'coordinates': [[[115, -8], [115.1, -8], [115.1, -7.9], [115, -7.9], [115, -8]]]}
    row = next(row for row in coverage(buffers, boundaries)['results'] if row['district_id'] == 'target')
    assert row['covered_area_m2'] == row['coverage_pct'] == 0
    assert row['geometry_area_m2'] > 0
    assert row['geometry'] is None
    assert row['completeness'] == 'complete'


def test_holes_are_subtracted_independent_of_ring_orientation():
    outer = [[112, -7], [112.04, -7], [112.04, -6.96], [112, -6.96], [112, -7]]
    hole = [[112.01, -6.99], [112.03, -6.99], [112.03, -6.97], [112.01, -6.97], [112.01, -6.99]]
    polygon = shape({'type': 'Polygon', 'coordinates': [outer, hole]})
    expected = geodesic_area(shape({'type': 'Polygon', 'coordinates': [outer]})) - geodesic_area(shape({'type': 'Polygon', 'coordinates': [hole]}))
    assert geodesic_area(polygon) == pytest.approx(expected, abs=1)


@pytest.mark.parametrize('change', ['invalid', 'empty', 'display', 'release', 'missing_radius', 'duplicate', 'counts', 'unmapped'])
def test_invalid_or_incomplete_spatial_inputs_fail(change):
    buffers, boundaries = fixture()
    if change == 'invalid':
        boundaries['features'][0]['geometry'] = FIXTURE['invalid_polygon']
    elif change == 'empty':
        boundaries['features'][0]['geometry'] = {'type': 'MultiPolygon', 'coordinates': []}
    elif change == 'display':
        boundaries['geometry_role'] = 'display'
    elif change == 'release':
        boundaries['release_id'] = 'other'
    elif change == 'missing_radius':
        buffers['features'].pop()
    elif change == 'duplicate':
        buffers['features'].append(copy.deepcopy(buffers['features'][0]))
    elif change == 'counts':
        buffers['eligible_count'] = 3
    else:
        boundaries['facility_assignments'][0]['district_id'] = 'unknown'
    with pytest.raises(ValueError):
        coverage(buffers, boundaries)


def test_excluded_location_marks_partial_without_subtracting_registered_facilities():
    buffers, boundaries = fixture()
    buffers['features'] = [f for f in buffers['features'] if f['properties']['facility_code'] != '35010100002']
    buffers.update(eligible_count=1, excluded_count=1, excluded=[{'facility_code': '35010100002', 'reason': 'not_verified'}])
    result = coverage(buffers, boundaries)
    neighbour = next(row for row in result['results'] if row['district_id'] == 'neighbour')
    assert neighbour['registered_count'] == 2
    assert neighbour['eligible_count'] == neighbour['excluded_count'] == 1
    assert neighbour['completeness'] == 'partial'
    assert all(row['reason'] == 'excluded_locations_in_dataset' for row in result['results'])
