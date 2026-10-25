import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from gis_pipeline.analysis.coverage import checked_polygon, geodesic_area
from gis_pipeline.analysis.export_layers import classify, digest, export_bundle, verify_manifest


def bundle():
    geometry = {'type': 'MultiPolygon', 'coordinates': [[[[112, -7], [112.01, -7], [112.01, -6.99], [112, -6.99], [112, -7]]]]}
    denominator = geodesic_area(checked_polygon(geometry))
    coverage = [{'district_id': 'district', 'radius_m': radius, 'covered_area_m2': 0, 'geometry_area_m2': denominator,
                 'coverage_pct': 0, 'geometry': None, 'registered_count': 1, 'eligible_count': 1, 'excluded_count': 0,
                 'contributing_count': 0, 'completeness': 'complete', 'reason': ''} for radius in (1000, 3000, 5000)]
    return {'schema_version': 'analysis-bundle-v1', 'release_id': 'fixture-release', 'analysis_run_id': 'fixture-run',
            'boundary_set_id': 'fixture-boundary', 'input_revision': 1, 'input_hash': 'a' * 64, 'boundary_hash': 'b' * 64,
            'method_version': 'fixture', 'code_revision': 'c' * 40,
            'parameters': {'T': 30000, 'radii_m': [1000, 3000, 5000], 'quad_segs': 32, 'legend_version': 'fixed-v1'},
            'indicators': [{'district_id': 'district', 'code': '3501010', 'parent_code': '3501', 'name': 'Synthetic',
                            'population': 30001, 'facility_count': 1, 'area_km2': '2', 'density': '15000.5',
                            'population_per_facility': '30001', 'facilities_per_30000': '0.999966667778',
                            'indicative_need': 2, 'indicative_deficit': 1, 'without_facility': False,
                            'source_ids': ['synthetic-source'], 'source_periods': {'population': '2023', 'facilities': '2024', 'area': '2023'}}],
            'boundaries': [{'district_id': 'district', 'full': geometry}], 'coverage': coverage,
            'eligibility_counts': {'registered': 1, 'eligible': 1, 'excluded': 0}, 'warnings': ['Synthetic fixture only']}


@pytest.mark.parametrize('metric,value,expected', [
    ('population_per_facility', 29999, 'class_0'), ('population_per_facility', 30000, 'class_0'),
    ('population_per_facility', 30001, 'class_1'), ('population_per_facility', 60000, 'class_1'),
    ('population_per_facility', 60001, 'class_2'),
    *[('facility_count', value, expected) for value, expected in [(0, 'class_0'), (1, 'class_1'), (2, 'class_1'), (3, 'class_2'), (5, 'class_2'), (6, 'class_3'), (10, 'class_3'), (11, 'class_4')]],
    ('density', 0, 'class_0'), ('density', 1000, 'class_1'), ('density', 5000, 'class_2'),
    ('indicative_deficit', 0, 'class_0'), ('indicative_deficit', 1, 'class_1'), ('indicative_deficit', 3, 'class_2'), ('indicative_deficit', 4, 'class_3'),
])
def test_frozen_class_boundaries(metric, value, expected):
    assert classify(metric, value, 30000, False)['class'] == expected


def test_null_and_without_facility_are_distinct_from_zero():
    assert classify('population_per_facility', None, 30000, True)['class'] == 'without_facility'
    assert classify('population_per_facility', None, None, True)['class'] == 'no_data'
    assert classify('facility_count', 0, None, True)['class'] == 'class_0'


def test_complete_bundle_writes_verifiable_immutable_artifacts(tmp_path):
    source = bundle()
    original = copy.deepcopy(source)
    manifest = export_bundle(source, tmp_path / 'run')
    assert source == original
    assert manifest['publication_allowed'] is False
    assert verify_manifest(tmp_path / 'run') == manifest
    layer = json.loads((tmp_path / 'run/density.geojson').read_text(encoding='utf-8'))
    assert layer['features'][0]['id'] == '3501010'
    assert layer['features'][0]['properties']['value'] == 15000.5
    assert layer['meta']['legend']['version'] == 'fixed-v1'
    assert layer['meta']['display_policy'] == 'full_geometry_fallback'
    with pytest.raises(ValueError, match='immutable'):
        export_bundle(source, tmp_path / 'run')


@pytest.mark.parametrize('change', ['formula', 'identity', 'missing_geometry', 'missing_radius', 'counts', 'coverage_area', 'nan'])
def test_failed_validation_never_writes_success_manifest(tmp_path, change):
    source = bundle()
    if change == 'formula':
        source['indicators'][0]['indicative_need'] = 1
    elif change == 'identity':
        source['indicators'][0]['release_id'] = 'other'
    elif change == 'missing_geometry':
        source['boundaries'] = []
    elif change == 'missing_radius':
        source['coverage'].pop()
    elif change == 'counts':
        source['coverage'][0]['registered_count'] = 2
    elif change == 'coverage_area':
        source['coverage'][0]['geometry_area_m2'] = 1
    else:
        source['indicators'][0]['density'] = 'NaN'
    with pytest.raises(ValueError):
        export_bundle(source, tmp_path / 'run')
    assert not (tmp_path / 'run/manifest.json').exists()


def test_content_hash_excludes_generation_time_and_output_directory(tmp_path):
    first = export_bundle(bundle(), tmp_path / 'first')
    second = export_bundle(bundle(), tmp_path / 'second')
    assert first['content_hash'] == second['content_hash']
    assert first['artifacts'] == second['artifacts']


def test_artifact_tampering_and_path_traversal_fail(tmp_path):
    manifest = export_bundle(bundle(), tmp_path / 'run')
    path = tmp_path / 'run/density.geojson'
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='hash/size'):
        verify_manifest(tmp_path / 'run')
    manifest['artifacts'][0]['path'] = '../outside.json'
    manifest['content_hash'] = digest({key: value for key, value in manifest.items() if key not in ('content_hash', 'generated_at')})
    (tmp_path / 'run/manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match='Unsafe'):
        verify_manifest(tmp_path / 'run')


def test_cli_preserves_numeric_geojson_coordinates(tmp_path):
    path = tmp_path / 'input.json'
    path.write_text(json.dumps(bundle()), encoding='utf-8')
    script = Path(__file__).resolve().parents[2] / 'scripts/analysis/export_layers.py'
    result = subprocess.run([sys.executable, str(script), '--input', str(path), '--sha256', hashlib.sha256(path.read_bytes()).hexdigest(), '--output-dir', str(tmp_path / 'run')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    layer = json.loads((tmp_path / 'run/density.geojson').read_text(encoding='utf-8'))
    assert isinstance(layer['features'][0]['geometry']['coordinates'][0][0][0][0], (int, float))
