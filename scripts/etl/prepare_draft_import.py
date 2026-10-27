"""Package processed Archives derivatives for private draft import, never publication."""

import argparse
import hashlib
import json
import math
import subprocess
import uuid
from collections import defaultdict
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = uuid.UUID('e895c069-27de-45b4-bd83-cdb6211a12af')


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def identity(value):
    return str(uuid.uuid5(NAMESPACE, value))


def candidate_location(facility):
    candidates = [c for c in facility['coordinate_candidates'] if c['source']['dataset'] == 'coordinates_csv']
    if not facility['baseline_coordinate_present']:
        return None
    if len(candidates) != 1:
        raise ValueError('Baseline location must have exactly one CSV candidate')
    coordinates = [float(candidates[0]['longitude']), float(candidates[0]['latitude'])]
    if not all(math.isfinite(v) for v in coordinates) or abs(coordinates[0]) > 180 or abs(coordinates[1]) > 90:
        raise ValueError('Invalid candidate coordinates')
    return {'type': 'Point', 'coordinates': coordinates}


def prepare(output):
    inputs = {}
    documents = {}
    for name, relative in {
        'facilities': 'data/processed/facility-master.json',
        'indicators': 'data/processed/indicator-decisions.json',
        'crosswalk': 'data/processed/crosswalk.json',
        'boundaries': 'data/processed/boundaries/analysis.geojson',
        'display': 'data/processed/boundaries/display.geojson',
    }.items():
        contents = (ROOT / relative).read_bytes()
        digest = hashlib.sha256(contents).hexdigest()
        inputs[name] = {'path': relative, 'sha256': digest, 'bytes': len(contents)}
        documents[name] = json.loads(contents)
    snapshot = hashlib.sha256(encode(inputs)).hexdigest()
    release = identity('draft:' + snapshot)
    boundary = identity('boundary:' + inputs['boundaries']['sha256'])
    source_ids = {name: identity('source:' + value['sha256']) for name, value in inputs.items()}
    rows = []

    def row(dataset, fields, locator, raw=None):
        rows.append({'row_no': len(rows) + 1, 'dataset': dataset, 'source_locator': locator,
                     'raw_fields': raw if raw is not None else {'locator': locator},
                     'normalized_fields': fields, 'disposition': 'accepted', 'errors': []})

    for name, info in inputs.items():
        row('data_sources', {'id': source_ids[name], 'publisher': 'Local processed Archives derivative',
                            'title': info['path'], 'private_path': info['path'], 'sha256': info['sha256'],
                            'observation_period': {'facilities': '2024-S1', 'indicators': 'Mixed observation years retained per row', 'crosswalk': 'BPS 2023', 'boundaries': '2020-04-01 boundaries / BPS 2023 codes', 'display': '2020-04-01 boundaries / BPS 2023 codes'}[name],
                            'license_note': 'Original source rights apply; derivative is private pending review.',
                            'limitations': 'Draft technical compilation; not independent source or location acceptance.'}, info['path'], info)
    row('boundary_sets', {'id': boundary, 'source_id': source_ids['boundaries'],
                         'name': 'Jawa Timur — draft mixed-edition boundaries', 'version': inputs['boundaries']['sha256'],
                         'code_system': 'BPS', 'reference_year': 2023, 'source_crs': 'EPSG:4326',
                         'metadata': {'boundary_edition': '2020-04-01', 'master_edition': '2023', 'publication_allowed': False,
                                      'analysis_mode': 'mixed_period_exploration', 'input_files': inputs}}, inputs['boundaries']['path'])
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    row('dataset_releases', {'id': release, 'label': 'Archives 2024-S1 — draft, unreviewed locations',
                            'boundary_set_id': boundary, 'facility_period': '2024-S1',
                            'population_policy': 'Preserve source-checked observation years; no temporal imputation.',
                            'area_policy': 'Preserve source values and years; no substitution with polygon area.',
                            'source_manifest': {'inputs': inputs, 'publication_allowed': False},
                            'method_version': 'draft-import-v1', 'code_revision': revision}, 'draft/' + snapshot)
    for name, source in source_ids.items():
        row('release_sources', {'release_id': release, 'source_id': source, 'purpose': name}, inputs[name]['path'])
    bootstrap = rows
    rows = []
    groups = defaultdict(list)
    display = {f['properties']['region_code']: f for f in documents['display']['features']}
    districts = documents['boundaries']['features']
    for feature in districts:
        groups[feature['properties']['parent_code']].append(feature)
    master = documents['crosswalk']['master']
    if set(groups) != {r['code'] for r in master['regencies']}:
        raise ValueError('Regency coverage mismatch')
    if {f['properties']['region_code'] for f in districts} != {d['code'] for d in master['districts']}:
        raise ValueError('District coverage mismatch')
    for region in master['regencies']:
        code = region['code']
        geom = unary_union([shape(f['geometry']) for f in groups[code]])
        if not geom.is_valid or geom.is_empty:
            raise ValueError('Invalid derived regency geometry')
        row('regencies', {'id': identity(boundary + ':' + code), 'boundary_set_id': boundary,
                         'code': code, 'name': region['name'], 'kind': 'kota' if int(code[2:]) >= 71 else 'kabupaten',
                         'geom': mapping(geom)}, 'union-districts/' + code, {'master': region, 'derivation': 'union of full district geometries'})
    for feature in districts:
        props = feature['properties']; code = props['region_code']
        row('districts', {'id': identity(boundary + ':' + code), 'boundary_set_id': boundary,
                         'regency_id': identity(boundary + ':' + props['parent_code']), 'code': code,
                         'name': props['master_name'], 'geom': feature['geometry'], 'geom_display': display[code]['geometry']},
            'analysis.geojson/' + code, props)
    observations = defaultdict(dict)
    for observation in documents['indicators']['observations']:
        code = observation['region_code']; metric = observation['metric']
        if metric in observations[code] or observation['status'] != 'source_checked':
            raise ValueError('Duplicate or unchecked indicator')
        observations[code][metric] = observation
    for feature in districts:
        code = feature['properties']['region_code']; values = observations[code]
        if set(values) != {'population', 'area'}:
            raise ValueError('Incomplete indicator pair')
        fields = {'release_id': release, 'boundary_set_id': boundary, 'district_id': identity(boundary + ':' + code),
                  'quality_status': 'source_checked_pending_acceptance', 'notes': 'Source comparison retained; location/overall quality acceptance pending.'}
        for metric, prefix in [('population', 'population'), ('area', 'area')]:
            observation = values[metric]
            value = observation['value']
            fields['population' if metric == 'population' else 'area_km2'] = (int(value) if metric == 'population' else str(value)) if value is not None else None
            fields[prefix + '_year'] = observation['observation_year']
            fields[prefix + '_source_id'] = source_ids['indicators']
            fields[prefix + '_locator'] = observation['source_locator']
            fields[prefix + '_raw'] = str(observation['raw_value']) if observation['raw_value'] is not None else None
        row('district_indicators', fields, 'indicator-decisions.json/' + code, values)
    mapped = 0
    for index, facility in enumerate(documents['facilities']['facilities'], 1):
        attrs = facility['attributes']; location = candidate_location(facility); mapped += location is not None
        row('facility_snapshots', {'release_id': release, 'boundary_set_id': boundary,
                                  'district_id': identity(boundary + ':' + facility['region_code']),
                                  'facility_code': facility['facility_code'], 'name': attrs['nama_puskesmas'],
                                  'address': attrs['alamat'], 'service_type': attrs['kemampuan_pelayanan'],
                                  'area_type': attrs['karakteristik_wilayah'], 'source_id': source_ids['facilities'],
                                  'source_row': index, 'location': location, 'coordinate_status': 'unverified' if location else 'missing',
                                  'precision_level': 'unknown', 'coordinate_source_id': source_ids['facilities'] if location else None},
            'facility-master.json/' + facility['facility_code'], facility)
    output.mkdir(parents=True, exist_ok=True)
    base = {'format': 'gis-import-v1', 'source_id': source_ids['facilities'], 'target_release_id': release,
            'pipeline_version': 'prepare-draft-import-1.0', 'parameters': {'snapshot': snapshot, 'publication_allowed': False}}
    batches = []

    def save(batch_rows):
        payload = encode({**base, 'rows': batch_rows})
        if len(payload) > 20 * 1024 * 1024:
            raise ValueError('Single batch exceeds importer limit')
        path = output / f'batch-{len(batches):03d}.json'
        if path.exists() and path.read_bytes() != payload:
            raise ValueError('Refusing to replace different prepared input')
        path.write_bytes(payload)
        batches.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload), 'rows': len(batch_rows)})
    save(bootstrap)
    batch = []; size = 0
    for item in rows:
        item_size = len(encode(item)) + 1
        if batch and size + item_size > 12 * 1024 * 1024:
            save(batch); batch = []; size = 0
        batch.append(item); size += item_size
    if batch:
        save(batch)
    result = {'release_id': release, 'boundary_set_id': boundary, 'inputs': inputs, 'batches': batches,
              'counts': {'regencies': len(groups), 'districts': len(districts), 'facilities': len(documents['facilities']['facilities']), 'mapped_unverified': mapped,
                         'missing': len(documents['facilities']['facilities']) - mapped, 'verified': 0},
              'publication_allowed': False, 'database_import_performed': False}
    (output / 'manifest.json').write_bytes(encode(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'storage/app/private/imports/archives-draft')
    args = parser.parse_args()
    destination = args.output.resolve()
    if not destination.is_relative_to((ROOT / 'storage/app/private/imports').resolve()):
        parser.error('Output must stay in private import storage')
    result = prepare(destination)
    print(json.dumps({'release_id': result['release_id'], 'counts': result['counts'], 'batches': len(result['batches'])}))
