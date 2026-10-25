import copy

import pytest
from shapely.geometry import Polygon, MultiPolygon, mapping

from gis_pipeline.etl.validate_boundaries import (
    CRS84, area_m2, checked_geometry, display_guard, simplify_display, validate,
)


@pytest.fixture
def inputs():
    geometry = mapping(Polygon([(112, -7), (112.01, -7), (112.01, -7.01), (112, -7.01)]))
    historical = {'collection': {'type': 'FeatureCollection',
        'crs': {'properties': {'name': CRS84}}, 'features': [{'type': 'Feature',
        'properties': {'adm3_pcode': 'ID3501010', 'adm2_pcode': 'ID3501',
        'adm1_pcode': 'ID35', 'valid_on': '2020-04-01', 'adm3_name': 'Synthetic'},
        'geometry': geometry}]}, 'boundary_edition': '2020-04-01',
        'receipts': {'member': {'sha256': 'frozen'}},
        'links': [{'source_pcode': 'ID3501010', 'region_code': '3501010'}],
        'excluded': [{'feature': {'properties': {'adm3_pcode': 'ID3522888'}}}], 'license': {}}
    crosswalk = {'target_boundary_set': 'frozen', 'master_edition': '2023', 'master': {
        'districts': [{'code': '3501010', 'parent_code': '3501', 'name': 'Synthetic'}],
        'regencies': [{'code': '3501'}]}, 'mappings': []}
    return historical, crosswalk


def test_analysis_unchanged_and_unserved_district_retained(inputs):
    before = copy.deepcopy(inputs)
    result = validate(*inputs)
    assert inputs == before
    assert result['analysis']['features'][0]['geometry'] == before[0]['collection']['features'][0]['geometry']
    assert result['summary']['without_facility_assignment'] == ['3501010']
    assert result['repairs'] == []
    assert result['publication_allowed'] is False
    assert validate(*inputs) == result


@pytest.mark.parametrize('raw', [
    {'type': 'Point', 'coordinates': [112, -7]},
    {'type': 'Polygon', 'coordinates': []},
    {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1]]]},
    {'type': 'Polygon', 'coordinates': [[0, 1, 2, 0]]},
    {'type': 'Polygon', 'coordinates': [[[112, -7], [113, -8], [112, -8], [113, -7], [112, -7]]]},
    {'type': 'Polygon', 'coordinates': [[[-7, 112], [-8, 112], [-8, 113], [-7, 112]]]},
    {'type': 'Polygon', 'coordinates': [[[0, 0], [float('nan'), 0], [1, 1], [0, 0]]]},
])
def test_rejects_invalid_without_silent_repair(raw):
    with pytest.raises(ValueError):
        checked_geometry(raw)


@pytest.mark.parametrize('defect', ['parent', 'duplicate', 'missing', 'crs', 'edition', 'crosswalk', 'empty_master'])
def test_rejects_identity_defects(inputs, defect):
    historical, crosswalk = inputs
    feature = historical['collection']['features'][0]
    if defect == 'parent':
        feature['properties']['adm2_pcode'] = 'ID3599'
    elif defect == 'duplicate':
        historical['collection']['features'].append(copy.deepcopy(feature))
    elif defect == 'missing':
        historical['collection']['features'] = []
    elif defect == 'crs':
        historical['collection']['crs']['properties']['name'] = 'EPSG:3857'
    elif defect == 'edition':
        historical['boundary_edition'] = '2023-01-01'
    elif defect == 'crosswalk':
        crosswalk['target_boundary_set'] = 'different'
    else:
        crosswalk['master']['districts'] = []
    with pytest.raises(ValueError):
        validate(historical, crosswalk)


def test_islands_holes_and_area_guards():
    main = Polygon([(112, -7), (112.1, -7), (112.1, -7.1), (112, -7.1)],
                   [[(112.02, -7.02), (112.04, -7.02), (112.04, -7.04), (112.02, -7.04)]])
    island = Polygon([(113, -7), (113.001, -7), (113.001, -7.001), (113, -7.001)])
    original = MultiPolygon([main, island])
    candidate, _ = simplify_display(original)
    assert len(candidate.geoms) == 2
    assert len(candidate.geoms[0].interiors) == 1
    assert display_guard(original, candidate)
    assert not display_guard(original, MultiPolygon([main]))
    assert not display_guard(original, MultiPolygon([Polygon(main.exterior), island]))
    assert not display_guard(original, MultiPolygon([main, island.buffer(-0.0002)]))
    assert area_m2(main) < area_m2(Polygon(main.exterior))


@pytest.mark.parametrize('tolerance', [0, -1, 51, float('nan'), True])
def test_display_tolerance_is_bounded(tolerance):
    with pytest.raises(ValueError):
        simplify_display(Polygon([(112, -7), (113, -7), (113, -8)]), tolerance)
