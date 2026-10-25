"""Eligibility and an independent per-point AEQD reference for metric buffers."""

import math
import re

import pyproj
import shapely
from pyproj import CRS, Geod, Transformer
from shapely.geometry import Point, mapping

from gis_pipeline.etl.geocode import point, validate_decision

RADII = (1000, 3000, 5000)
QUAD_SEGS = 32
GEOD = Geod(ellps='WGS84')
METHOD = 'python-local-aeqd-buffer-v1'


def eligibility(facility, release_id):
    if facility.get('release_id') != release_id:
        raise ValueError('Mixed release facility')
    if facility.get('coordinate_status') != 'verified':
        return 'not_verified'
    if facility.get('precision_level') != 'facility':
        return 'not_facility_precision'
    try:
        coordinates = point(facility.get('longitude'), facility.get('latitude'))
    except (ValueError, TypeError, OverflowError):
        return 'invalid_coordinates'
    if coordinates[0] is None:
        return 'missing_coordinates'
    review = facility.get('review')
    if not isinstance(review, dict):
        return 'missing_review'
    if not facility.get('selected_review_id') or not facility.get('coordinate_source_id'):
        return 'missing_review_identity'
    if any(review.get(key) != expected for key, expected in {
        'review_id': facility['selected_review_id'], 'release_id': release_id,
        'facility_code': facility['facility_code'], 'source_id': facility['coordinate_source_id'],
    }.items()):
        return 'review_identity_mismatch'
    if review.get('result_status') != 'accepted':
        return 'review_not_accepted'
    try:
        validate_decision(review, review)
        if point(review['candidate_lon'], review['candidate_lat']) != coordinates:
            return 'review_point_mismatch'
    except (ValueError, KeyError, TypeError, OverflowError):
        return 'invalid_review_evidence'
    return None


def reference_buffer(longitude, latitude, radius):
    if type(radius) is not int or radius not in RADII:
        raise ValueError('Only frozen 1000/3000/5000 metre radii are supported')
    longitude, latitude = point(longitude, latitude)
    if longitude is None or abs(latitude) >= 85:
        raise ValueError('Point is missing or outside this regional method domain')
    local = CRS.from_proj4(f'+proj=aeqd +lat_0={latitude} +lon_0={longitude} +datum=WGS84 +units=m +no_defs')
    inverse = Transformer.from_crs(local, 'EPSG:4326', always_xy=True)
    geometry = shapely.transform(Point(0, 0).buffer(radius, quad_segs=QUAD_SEGS), inverse.transform, interleaved=False)
    if geometry.is_empty or not geometry.is_valid or geometry.bounds[2] - geometry.bounds[0] > 180:
        raise ValueError('Invalid or antimeridian-crossing regional buffer')
    return geometry


def radius_check(longitude, latitude, geometry, radius):
    vertices = list(geometry.exterior.coords)[:-1]
    samples = vertices + [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                          for a, b in zip(vertices, vertices[1:] + vertices[:1])]
    errors = [abs(GEOD.inv(longitude, latitude, lon, lat)[2] - radius) for lon, lat in samples]
    maximum = max(errors)
    tolerance = max(2, 0.01 * radius)
    if not math.isfinite(maximum) or maximum > tolerance:
        raise ValueError('Buffer radius exceeds the frozen geodesic tolerance')
    return {'vertices': len(vertices), 'midpoints': len(vertices), 'max_error_m': maximum, 'tolerance_m': tolerance}


def build_buffers(document, input_hash):
    if not isinstance(document, dict) or not re.fullmatch('[0-9a-f]{64}', input_hash):
        raise ValueError('A pinned snapshot is required')
    for key in ('release_id', 'analysis_run_id', 'code_revision'):
        if not isinstance(document.get(key), str) or not document[key].strip():
            raise ValueError(f'Missing run provenance: {key}')
    facilities = document.get('facilities')
    if not isinstance(facilities, list):
        raise ValueError('Explicit facility snapshot required')
    seen, excluded, features, checks = set(), [], [], []
    for facility in facilities:
        if not isinstance(facility, dict):
            raise ValueError('Facility rows must be objects')
        code = facility.get('facility_code')
        if not isinstance(code, str) or not re.fullmatch('[0-9]{11}', code) or code in seen:
            raise ValueError('Invalid or duplicate facility code')
        seen.add(code)
        reason = eligibility(facility, document['release_id'])
        if reason:
            excluded.append({'facility_code': code, 'reason': reason})
            continue
        longitude, latitude = point(facility['longitude'], facility['latitude'])
        for radius in RADII:
            geometry = reference_buffer(longitude, latitude, radius)
            checks.append({'facility_code': code, 'radius_m': radius, **radius_check(longitude, latitude, geometry, radius)})
            features.append({'type': 'Feature', 'properties': {
                'facility_code': code, 'radius_m': radius, 'release_id': document['release_id'],
                'selected_review_id': facility['selected_review_id'], 'coordinate_source_id': facility['coordinate_source_id'],
            }, 'geometry': mapping(geometry)})
    return {
        'type': 'FeatureCollection', 'status': 'candidate_artifact', 'release_id': document['release_id'],
        'analysis_run_id': document['analysis_run_id'], 'code_revision': document['code_revision'], 'input_hash': input_hash,
        'method_version': METHOD, 'parameters': {'radii_m': list(RADII), 'quad_segs': QUAD_SEGS, 'storage_crs': 'EPSG:4326',
                                               'projection': 'per-point WGS84 azimuthal equidistant, metre units, always_xy'},
        'versions': {'pyproj': pyproj.__version__, 'proj': pyproj.proj_version_str,
                     'shapely': shapely.__version__, 'geos': shapely.geos_version_string},
        'registered_count': len(seen), 'eligible_count': len(seen) - len(excluded), 'excluded_count': len(excluded),
        'excluded': excluded, 'radius_checks': checks, 'features': features,
        'limitations': ['Straight-line distance, not travel time or routes', 'Facilities outside the province are not included'],
    }
