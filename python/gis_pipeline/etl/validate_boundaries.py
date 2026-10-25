"""Validate historical polygons and derive a guarded, display-only geometry set."""

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import pyproj
import shapely
from pyproj import Geod, Transformer
from shapely.geometry import mapping, shape
from shapely.geometry.polygon import orient
from shapely.validation import explain_validity

from .acquire import local_path
from .normalize import digest

VERSION = 'validate-boundaries-1.0'
GEOD = Geod(ellps='WGS84')
CRS84 = 'urn:ogc:def:crs:OGC:1.3:CRS84'
MAX_AREA_CHANGE = 0.005


def parts(geometry):
    return [geometry] if geometry.geom_type == 'Polygon' else list(geometry.geoms)


def area_m2(geometry):
    # Normalize ring orientation only for measurement; never mutate source coordinates.
    return sum(abs(GEOD.geometry_area_perimeter(orient(p, sign=1))[0]) for p in parts(geometry))


def vertex_count(geometry):
    return sum(len(p.exterior.coords) + sum(len(h.coords) for h in p.interiors) for p in parts(geometry))


def checked_geometry(raw):
    if not isinstance(raw, dict) or raw.get('type') not in ('Polygon', 'MultiPolygon'):
        raise ValueError('Boundary must be Polygon or MultiPolygon')
    polygons = [raw.get('coordinates')] if raw['type'] == 'Polygon' else raw.get('coordinates')
    if not isinstance(polygons, (list, tuple)) or not polygons:
        raise ValueError('Empty boundary coordinates')
    for polygon in polygons:
        if not isinstance(polygon, (list, tuple)) or not polygon:
            raise ValueError('Empty polygon component')
        for ring in polygon:
            if (not isinstance(ring, (list, tuple)) or len(ring) < 4
                    or not isinstance(ring[0], (list, tuple))
                    or not isinstance(ring[-1], (list, tuple)) or tuple(ring[0]) != tuple(ring[-1])):
                raise ValueError('Boundary rings must be closed without implicit repair')
            for point in ring:
                if (not isinstance(point, (list, tuple)) or len(point) != 2
                        or any(type(v) not in (int, float) or not math.isfinite(v) for v in point)
                        or not -180 <= point[0] <= 180 or not -90 <= point[1] <= 90):
                    raise ValueError('Invalid CRS84 longitude/latitude coordinate')
    geometry = shape(raw)
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError('Invalid boundary; explicit repair required: ' + explain_validity(geometry))
    if area_m2(geometry) <= 0:
        raise ValueError('Boundary has no positive geodesic area')
    return geometry


def display_guard(original, candidate):
    if candidate.is_empty or not candidate.is_valid or candidate.geom_type != original.geom_type:
        return False
    old_parts, new_parts = parts(original), parts(candidate)
    if len(old_parts) != len(new_parts):
        return False
    for before, after in zip(old_parts, new_parts):
        if (len(before.interiors) != len(after.interiors)
                or not after.covers(before.representative_point())
                or abs(area_m2(after) - area_m2(before)) / area_m2(before) > MAX_AREA_CHANGE):
            return False
    return abs(area_m2(candidate) - area_m2(original)) / area_m2(original) <= MAX_AREA_CHANGE


def simplify_display(original, tolerance_m=50):
    if type(tolerance_m) not in (int, float) or not math.isfinite(tolerance_m) or not 0 < tolerance_m <= 50:
        raise ValueError('Display tolerance must be within (0, 50] metres')
    center = original.centroid
    projection = f'+proj=aeqd +lat_0={center.y:.12f} +lon_0={center.x:.12f} +datum=WGS84 +units=m +no_defs'
    forward = Transformer.from_crs('EPSG:4326', projection, always_xy=True)
    inverse = Transformer.from_crs(projection, 'EPSG:4326', always_xy=True)
    projected = shapely.transform(original, forward.transform, interleaved=False)
    attempts = []
    for divisor in (1, 2, 4, 8, 16, 32):
        tolerance = tolerance_m / divisor
        reduced = projected.simplify(tolerance, preserve_topology=True)
        candidate = shapely.transform(reduced, inverse.transform, interleaved=False)
        accepted = display_guard(original, candidate)
        attempts.append({'tolerance_m': tolerance, 'accepted': accepted})
        if accepted and vertex_count(candidate) < vertex_count(original):
            return candidate, {'method': 'local_aeqd_douglas_peucker_preserve_topology',
                               'projection': projection, 'tolerance_m': tolerance, 'attempts': attempts}
    return original, {'method': 'retain_original', 'projection': projection, 'tolerance_m': 0,
                       'attempts': attempts, 'reason': 'No smaller candidate passed the fixed island/area guards'}


def validate(historical, crosswalk, progress=None):
    collection = historical['collection']
    if (collection.get('type') != 'FeatureCollection'
            or collection.get('crs', {}).get('properties', {}).get('name') != CRS84
            or historical.get('boundary_edition') != '2020-04-01'):
        raise ValueError('Unexpected source CRS or historical edition')
    boundary_hash = historical['receipts']['member']['sha256']
    if crosswalk['target_boundary_set'] != boundary_hash or crosswalk['master_edition'] != '2023':
        raise ValueError('Crosswalk references a different boundary set or master edition')
    master = {r['code']: r for r in crosswalk['master']['districts']}
    parents = {r['code'] for r in crosswalk['master']['regencies']}
    if (not master or not parents or len(master) != len(crosswalk['master']['districts'])
            or len(parents) != len(crosswalk['master']['regencies'])
            or any(r['parent_code'] not in parents for r in master.values())):
        raise ValueError('Duplicate or invalid master identity')
    links = {r['source_pcode']: r['region_code'] for r in historical['links']}
    if (len(links) != len(historical['links']) or len(set(links.values())) != len(links)
            or set(links.values()) != set(master)):
        raise ValueError('Boundary links are duplicated or differ from the master')
    facility_counts = Counter(r['region_code'] for r in crosswalk['mappings']
                              if r['dataset'] == 'facilities_official' and r['mapping_status'] == 'approved')
    full, display, records, seen, geometry_hashes = [], [], [], set(), set()
    for feature in sorted(collection['features'], key=lambda f: f['properties']['adm3_pcode']):
        props = feature['properties']
        pcode = props['adm3_pcode']
        code = links.get(pcode)
        if (feature.get('type') != 'Feature' or code not in master or code in seen
                or pcode != 'ID' + code or props.get('adm2_pcode') != 'ID' + master[code]['parent_code']
                or props.get('adm1_pcode') != 'ID35' or props.get('valid_on') != historical['boundary_edition']):
            raise ValueError('Unexpected, duplicate or wrongly parented historical boundary')
        seen.add(code)
        original = checked_geometry(feature['geometry'])
        normalized_hash = hashlib.sha256(shapely.normalize(original).wkb).hexdigest()
        if normalized_hash in geometry_hashes:
            raise ValueError('Identical polygon geometry assigned to multiple districts')
        geometry_hashes.add(normalized_hash)
        simplified, method = simplify_display(original)
        source_area, display_area = area_m2(original), area_m2(simplified)
        common = {'region_code': code, 'parent_code': master[code]['parent_code'],
                  'master_name': master[code]['name'], 'source_name': props['adm3_name'],
                  'boundary_edition': historical['boundary_edition'], 'master_edition': '2023',
                  'source_pcode': pcode, 'boundary_set_sha256': boundary_hash,
                  'facility_assignment_count': facility_counts[code]}
        # Source geometry dict is retained exactly, including every coordinate and ring.
        full.append({'type': 'Feature', 'id': code, 'properties': {**common, 'geometry_role': 'analysis',
                     'geodesic_area_m2': source_area}, 'geometry': feature['geometry']})
        display_geometry = feature['geometry'] if method['method'] == 'retain_original' else mapping(simplified)
        display.append({'type': 'Feature', 'id': code, 'properties': {**common, 'geometry_role': 'display_only'},
                        'geometry': display_geometry})
        records.append({'region_code': code, 'source_geometry_sha256': digest(feature['geometry']),
                        'display_geometry_sha256': digest(display_geometry), 'valid': True,
                        'geometry_type': original.geom_type, 'components': len(parts(original)),
                        'display_components': len(parts(simplified)),
                        'holes': sum(len(p.interiors) for p in parts(original)),
                        'vertices': vertex_count(original), 'display_vertices': vertex_count(simplified),
                        'geodesic_area_m2': source_area, 'display_area_m2': display_area,
                        'relative_area_change': abs(display_area - source_area) / source_area,
                        'analysis_geometry_unchanged': True, 'display_operation': method})
        if progress and len(records) % 50 == 0:
            progress(len(records))
    if seen != set(master):
        raise ValueError('Missing boundary codes: ' + ', '.join(sorted(set(master) - seen)))
    excluded = historical['excluded']
    if len(excluded) != 1 or excluded[0]['feature']['properties']['adm3_pcode'] != 'ID3522888':
        raise ValueError('Unexpected excluded water-object partition')
    return {'pipeline_version': VERSION, 'analysis': {'type': 'FeatureCollection', 'features': full},
            'display': {'type': 'FeatureCollection', 'features': display}, 'excluded_water': excluded,
            'features': records, 'repairs': [], 'license': historical['license'],
            'summary': {'districts': len(seen), 'parents': len(parents), 'invalid': 0, 'empty': 0,
                        'missing_codes': [], 'extra_codes': [], 'duplicate_codes': [],
                        'components': sum(r['components'] for r in records),
                        'display_components': sum(r['display_components'] for r in records),
                        'source_vertices': sum(r['vertices'] for r in records),
                        'display_vertices': sum(r['display_vertices'] for r in records),
                        'retained_original_display': sum(r['display_operation']['method'] == 'retain_original' for r in records),
                        'max_relative_area_change': max(r['relative_area_change'] for r in records),
                        'without_facility_assignment': sorted(set(master) - set(facility_counts))},
            'methods': {'area': 'WGS84 ellipsoid; oriented rings for measurement only',
                        'display_max_relative_area_change': MAX_AREA_CHANGE, 'display_initial_tolerance_m': 50,
                        'per_component_area_and_hole_guards': True, 'analysis_geometry_modified': False,
                        'shared_edge_display_topology_claimed': False},
            'versions': {'shapely': shapely.__version__, 'geos': shapely.geos_version_string,
                         'pyproj': pyproj.__version__, 'proj': pyproj.proj_version_str},
            'geometry_validation_complete': True, 'analysis_mode': 'mixed_period_exploration',
            'strict_2023_geometry_verified': False, 'publication_allowed': False}


def run(root, acquisition_evidence, crosswalk_evidence, progress=None):
    root = Path(root).resolve()
    receipt = acquisition_evidence['source_output']
    raw = local_path(root, receipt['path'], 'data/staging').read_bytes()
    if len(raw) != receipt['bytes'] or hashlib.sha256(raw).hexdigest() != receipt['sha256']:
        raise ValueError('Acquisition artifact hash mismatch')
    acquisition = json.loads(raw)
    del raw
    raw = local_path(root, crosswalk_evidence['output_path'], 'data/processed').read_bytes()
    if hashlib.sha256(raw).hexdigest() != crosswalk_evidence['output_sha256']:
        raise ValueError('Crosswalk hash mismatch')
    crosswalk = json.loads(raw)
    historical = acquisition['historical_boundaries']
    for source in historical['receipts'].values():
        path = local_path(root, source['raw_path'], 'data/raw')
        with path.open('rb') as handle:
            actual = hashlib.file_digest(handle, 'sha256').hexdigest()
        if actual != source['sha256'] or path.stat().st_size != source['bytes']:
            raise ValueError('Boundary source receipt mismatch')
    result = validate(historical, crosswalk, progress)
    result['input_identity'] = {'acquisition_sha256': receipt['sha256'],
                                'crosswalk_sha256': crosswalk_evidence['output_sha256'],
                                'boundary_source_sha256': historical['receipts']['member']['sha256']}
    result['content_sha256'] = digest(result)
    return result
