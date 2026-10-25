"""Validated, immutable thematic artifacts from a versioned analysis bundle."""

from datetime import datetime, timezone
from decimal import Decimal
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from shapely.geometry import mapping

from .buffers import RADII
from .coverage import checked_polygon, geodesic_area
from .indicators import calculate

LEGENDS = json.loads((Path(__file__).resolve().parents[3] / 'resources/analysis-legends.json').read_text(encoding='utf-8'))
METRICS = {key: (item['unit'], item['upper_bounds'], item['labels'], item['colors']) for key, item in LEGENDS.items()}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def number(value):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError('Boolean is not a metric value')
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError('Metrics must be finite and nonnegative')
    return result


def classify(metric, value, population, without_facility):
    if metric not in METRICS:
        raise ValueError('Unknown thematic metric')
    value = number(value)
    if value is None:
        if metric == 'population_per_facility' and population is not None and without_facility:
            return {'class': 'without_facility', 'color': '#fdae6b', 'label': 'Without facility'}
        return {'class': 'no_data', 'color': '#bdbdbd', 'label': 'No data'}
    _, limits, labels, colors = METRICS[metric]
    index = next((index for index, limit in enumerate(limits) if value <= limit), len(limits))
    return {'class': f'class_{index}', 'color': colors[index], 'label': labels[index]}


def legend(metric):
    return copy.deepcopy(LEGENDS[metric])


def validate_bundle(bundle):
    if not isinstance(bundle, dict) or bundle.get('schema_version') != 'analysis-bundle-v1':
        raise ValueError('Unsupported analysis bundle')
    for key in ('release_id', 'analysis_run_id', 'boundary_set_id', 'method_version', 'code_revision'):
        if not isinstance(bundle.get(key), str) or not bundle[key].strip():
            raise ValueError(f'Missing run identity: {key}')
    for key in ('input_hash', 'boundary_hash'):
        if not isinstance(bundle.get(key), str) or not re.fullmatch('[0-9a-f]{64}', bundle[key]):
            raise ValueError('Missing scientific input hash')
    if type(bundle.get('input_revision')) is not int or bundle['input_revision'] < 0:
        raise ValueError('Invalid input revision')
    parameters = bundle.get('parameters', {})
    if parameters.get('radii_m') != list(RADII) or parameters.get('quad_segs') != 32 or parameters.get('legend_version') != 'fixed-v1':
        raise ValueError('Unfrozen analysis parameters')
    rows, geometries, codes = {}, {}, set()
    for row in bundle.get('indicators', []):
        identity, code = row.get('district_id'), row.get('code')
        if not isinstance(identity, str) or not identity or identity in rows or not isinstance(code, str) or not code or code in codes:
            raise ValueError('Duplicate or missing district identity/code')
        if not isinstance(row.get('source_ids'), list) or not all(isinstance(item, str) for item in row['source_ids']) or not isinstance(row.get('source_periods'), dict):
            raise ValueError('Missing source provenance')
        if not isinstance(row.get('name'), str) or not isinstance(row.get('parent_code'), str):
            raise ValueError('Missing display identity')
        if any(row.get(key, bundle[key]) != bundle[key] for key in ('release_id', 'analysis_run_id', 'boundary_set_id')):
            raise ValueError('Mixed result identity')
        calculated = calculate(row['population'], row['facility_count'], row['area_km2'], parameters.get('T'))['values']
        for field, expected_key in [('density', 'density'), ('population_per_facility', 'ratio'), ('facilities_per_30000', 'facilities_per_30000'), ('indicative_need', 'need'), ('indicative_deficit', 'deficit')]:
            actual, expected = number(row.get(field)), calculated[expected_key]
            if (actual is None) != (expected is None) or (actual is not None and abs(actual - expected) > Decimal('0.000000001')):
                raise ValueError('Stored indicator disagrees with canonical formula')
        if row.get('without_facility') is not calculated['without_facility']:
            raise ValueError('Incorrect no-facility flag')
        rows[identity] = row
        codes.add(code)
    if not rows:
        raise ValueError('Empty district result set')
    for item in bundle.get('boundaries', []):
        identity = item.get('district_id')
        if identity in geometries or identity not in rows:
            raise ValueError('Duplicate or unknown boundary identity')
        geometries[identity] = checked_polygon(item['full'])
    if set(geometries) != set(rows):
        raise ValueError('Boundary and result membership differ')
    coverage_rows = {}
    previous = {}
    for row in sorted(bundle.get('coverage', []), key=lambda row: (row['district_id'], row['radius_m'])):
        identity, radius = row.get('district_id'), row.get('radius_m')
        key = (identity, radius)
        if identity not in rows or type(radius) is not int or radius not in RADII or key in coverage_rows:
            raise ValueError('Invalid coverage identity/radius')
        if any(row.get(key, bundle[key]) != bundle[key] for key in ('release_id', 'analysis_run_id', 'boundary_set_id')):
            raise ValueError('Mixed coverage identity')
        for count_key in ('registered_count', 'eligible_count', 'excluded_count', 'contributing_count'):
            if type(row.get(count_key)) is not int or row[count_key] < 0:
                raise ValueError('Invalid coverage count')
        if row['registered_count'] != rows[identity]['facility_count'] or row['eligible_count'] + row['excluded_count'] != row['registered_count']:
            raise ValueError('Coverage does not match the administrative master')
        values = [number(row.get(key)) for key in ('covered_area_m2', 'geometry_area_m2', 'coverage_pct')]
        if any(value is None for value in values):
            if values != [None, None, None] or row.get('completeness') != 'unavailable' or row.get('geometry') is not None:
                raise ValueError('Invalid unavailable coverage representation')
        else:
            covered, denominator, percentage = map(float, values)
            expected_area = geodesic_area(geometries[identity])
            if denominator <= 0 or covered > denominator + 1 or percentage > 100 or abs(percentage - covered / denominator * 100) > 1e-8:
                raise ValueError('Invalid coverage ratio')
            if abs(denominator - expected_area) > max(1, 0.01 * expected_area):
                raise ValueError('Coverage denominator is not full boundary area')
            if covered + 1 < previous.get(identity, 0):
                raise ValueError('Non-monotonic radius coverage')
            previous[identity] = covered
            geometry = None if row.get('geometry') is None else checked_polygon(row['geometry'])
            actual_area = 0 if geometry is None else geodesic_area(geometry)
            if abs(actual_area - covered) > max(1, 0.01 * covered) or (geometry is not None and geodesic_area(geometry.difference(geometries[identity])) > 1):
                raise ValueError('Coverage geometry does not match its area or region')
        coverage_rows[key] = row
    if set(coverage_rows) != {(identity, radius) for identity in rows for radius in RADII}:
        raise ValueError('Missing coverage results')
    canonical(bundle)
    return rows


def export_bundle(bundle, output):
    bundle = copy.deepcopy(bundle)
    for boundary in bundle.get('boundaries', []):
        boundary['full'] = mapping(checked_polygon(boundary['full']))
    for row in bundle.get('coverage', []):
        if row.get('geometry') is not None:
            row['geometry'] = mapping(checked_polygon(row['geometry']))
    rows = validate_bundle(bundle)
    output = Path(output)
    if output.exists():
        raise ValueError('Analysis output is immutable; choose a new run directory')
    identities = {key: bundle[key] for key in ('release_id', 'analysis_run_id', 'boundary_set_id', 'input_revision', 'input_hash', 'boundary_hash', 'method_version', 'code_revision')}
    geometries = {row['district_id']: row['full'] for row in bundle['boundaries']}
    artifacts = {'results.json': {'kind': 'analysis_results', 'data': bundle}}
    for metric in METRICS:
        features = []
        for row in sorted(rows.values(), key=lambda row: row['code']):
            value = number(row[metric])
            style = classify(metric, value, row['population'], row['without_facility'])
            reason = ('no_facilities' if style['class'] == 'without_facility' else 'missing_input') if value is None else ''
            features.append({'type': 'Feature', 'id': row['code'], 'geometry': geometries[row['district_id']], 'properties': {
                'code': row['code'], 'parent_code': row['parent_code'], 'name': row['name'], 'metric': metric,
                'value': None if value is None else float(value), 'value_exact': None if value is None else format(value, 'f'),
                'unit': METRICS[metric][0], 'completeness': 'unavailable' if value is None else 'complete', 'reason': reason,
                'without_facility': row['without_facility'], 'source_ids': row['source_ids'], 'source_periods': row['source_periods'],
                'release_id': bundle['release_id'], 'analysis_run_id': bundle['analysis_run_id'], **style,
            }})
        artifacts[metric + '.geojson'] = {'kind': 'thematic_' + metric, 'data': {'type': 'FeatureCollection', 'features': features, 'meta': {
            **identities, 'metric': metric, 'unit': METRICS[metric][0], 'legend': legend(metric),
            'geometry_detail': 'display', 'display_policy': 'full_geometry_fallback',
            'source_periods': bundle.get('source_periods', {}), 'coordinate_coverage': bundle.get('eligibility_counts', {}),
            'warnings': bundle.get('warnings', []),
        }}}
    output.mkdir(parents=True, exist_ok=False)
    receipts = []
    for filename, item in sorted(artifacts.items()):
        data = canonical(item['data']) + b'\n'
        with (output / filename).open('xb') as handle:
            handle.write(data)
            handle.flush()
        actual = (output / filename).read_bytes()
        if actual != data:
            raise OSError('Artifact verification failed')
        receipts.append({'kind': item['kind'], 'path': filename, 'bytes': len(actual), 'sha256': hashlib.sha256(actual).hexdigest()})
    content = {'schema_version': 'analysis-manifest-v1', **identities, 'parameters': bundle['parameters'],
               'validation_status': 'passed', 'artifacts': receipts, 'environment': bundle.get('environment', {}),
               'warnings': bundle.get('warnings', []), 'publication_allowed': False}
    manifest = {**content, 'content_hash': digest(content), 'generated_at': datetime.now(timezone.utc).isoformat()}
    with (output / 'manifest.json').open('xb') as handle:
        handle.write(canonical(manifest) + b'\n')
    return manifest


def verify_manifest(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    content = {key: value for key, value in manifest.items() if key not in ('content_hash', 'generated_at')}
    if manifest.get('schema_version') != 'analysis-manifest-v1' or manifest.get('validation_status') != 'passed' or digest(content) != manifest.get('content_hash'):
        raise ValueError('Invalid manifest content hash/status')
    expected_kinds = {'analysis_results'} | {'thematic_' + metric for metric in METRICS}
    if len(manifest.get('artifacts', [])) != len(expected_kinds) or {item.get('kind') for item in manifest['artifacts']} != expected_kinds:
        raise ValueError('Incomplete artifact registry')
    seen = set()
    for artifact in manifest['artifacts']:
        path = artifact['path']
        if not isinstance(path, str) or '\\' in path or ':' in path or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts or path in seen:
            raise ValueError('Unsafe or duplicate artifact path')
        seen.add(path)
        target = (root / path).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            raise ValueError('Artifact escapes root or is missing')
        data = target.read_bytes()
        if len(data) != artifact['bytes'] or hashlib.sha256(data).hexdigest() != artifact['sha256']:
            raise ValueError('Artifact hash/size mismatch')
    return manifest
