"""Union and clip coverage using full boundary geometry and all eligible neighbours."""

from collections import Counter
import math

import shapely
from shapely.geometry import MultiPolygon, mapping, shape
from shapely.geometry.polygon import orient

from .buffers import GEOD, RADII


def polygonal(geometry):
    if geometry.is_empty:
        return MultiPolygon([])
    if geometry.geom_type == 'Polygon':
        return MultiPolygon([geometry])
    if geometry.geom_type == 'MultiPolygon':
        return geometry
    if geometry.geom_type == 'GeometryCollection':
        return MultiPolygon([polygon for child in geometry.geoms for polygon in polygonal(child).geoms])
    return MultiPolygon([])


def geodesic_area(geometry):
    return sum(abs(GEOD.geometry_area_perimeter(orient(part, sign=1))[0]) for part in polygonal(geometry).geoms)


def checked_polygon(value):
    if not isinstance(value, dict) or value.get('type') not in ('Polygon', 'MultiPolygon') or 'crs' in value:
        raise ValueError('Canonical EPSG4326 polygon geometry required')
    geometry = shape(value)
    if geometry.is_empty or not geometry.is_valid or geometry.has_z:
        raise ValueError('Invalid, empty or non-2D polygon')
    west, south, east, north = geometry.bounds
    if not all(math.isfinite(n) for n in geometry.bounds) or not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90) or east - west > 180:
        raise ValueError('Polygon exceeds this regional geographic domain')
    return polygonal(geometry)


def coverage(buffers, boundaries):
    if not isinstance(buffers, dict) or not isinstance(boundaries, dict) or not buffers.get('release_id') or buffers['release_id'] != boundaries.get('release_id'):
        raise ValueError('Buffers and boundaries must identify the same release')
    if buffers.get('method_version') not in ('python-local-aeqd-buffer-v1', 'postgis-geography-buffer-v1'):
        raise ValueError('Unsupported buffer method')
    parameters = buffers.get('parameters', {})
    if parameters.get('radii_m') != list(RADII) or parameters.get('quad_segs') != 32 or parameters.get('storage_crs') != 'EPSG:4326':
        raise ValueError('Buffer parameters differ from the frozen method')
    if buffers.get('boundary_set_id') is not None and buffers['boundary_set_id'] != boundaries.get('boundary_set_id'):
        raise ValueError('Mixed boundary-set identity')
    if boundaries.get('geometry_role') != 'analysis' or 'crs' in boundaries:
        raise ValueError('Only full analysis geometry in EPSG4326 is permitted')
    regions = {}
    for feature in boundaries.get('features', []):
        identity = feature.get('properties', {}).get('district_id')
        if not isinstance(identity, str) or not identity or identity in regions:
            raise ValueError('Invalid or duplicate district identity')
        regions[identity] = checked_polygon(feature['geometry'])
    if not regions:
        raise ValueError('A nonempty district geometry master is required')
    assignments = {}
    for row in boundaries.get('facility_assignments', []):
        code, district = row.get('facility_code'), row.get('district_id')
        if not isinstance(code, str) or code in assignments or district not in regions:
            raise ValueError('Invalid, duplicate or unmapped administrative facility')
        assignments[code] = district
    excluded = {}
    for row in buffers.get('excluded', []):
        code = row.get('facility_code')
        if code in excluded or code not in assignments or not isinstance(row.get('reason'), str) or not row['reason']:
            raise ValueError('Invalid exclusion partition')
        excluded[code] = row['reason']
    by_radius = {radius: {} for radius in RADII}
    for feature in buffers.get('features', []):
        properties = feature.get('properties', {})
        code, radius = properties.get('facility_code'), properties.get('radius_m')
        if (code not in assignments or code in excluded or type(radius) is not int or radius not in RADII
                or code in by_radius[radius] or properties.get('release_id') != buffers['release_id']):
            raise ValueError('Invalid buffer identity, radius or partition')
        by_radius[radius][code] = checked_polygon(feature['geometry'])
    eligible = set(assignments) - set(excluded)
    if any(set(polygons) != eligible for polygons in by_radius.values()):
        raise ValueError('Every eligible facility requires all three radius buffers')
    for key, expected in [('registered_count', len(assignments)), ('eligible_count', len(eligible)), ('excluded_count', len(excluded))]:
        if type(buffers.get(key)) is not int or buffers[key] != expected:
            raise ValueError('Snapshot counts do not match administrative membership')
    unions = {radius: shapely.union_all(list(polygons.values())) for radius, polygons in by_radius.items()}
    results = []
    for identity, region in sorted(regions.items()):
        local = {code for code, district in assignments.items() if district == identity}
        local_excluded = local & set(excluded)
        denominator = geodesic_area(region)
        if not math.isfinite(denominator) or denominator <= 0:
            raise ValueError('Boundary has no positive geodesic area')
        previous = 0.0
        for radius in RADII:
            clipped = polygonal(unions[radius].intersection(region)) if eligible else MultiPolygon([])
            numerator = geodesic_area(clipped) if eligible else None
            percentage = numerator / denominator * 100 if eligible else None
            if eligible and (numerator > denominator + 1 or percentage > 100 + 1e-8 or numerator + 1 < previous):
                raise ValueError('Coverage violates area, percentage or monotonicity tolerance')
            adjustment = 0.0
            if eligible:
                adjustment = max(0, numerator - denominator)
                numerator = min(numerator, denominator)
                percentage = min(percentage, 100)
                previous = numerator
            contributors = [code for code, geometry in by_radius[radius].items()
                            if not polygonal(geometry.intersection(region)).is_empty]
            results.append({
                'district_id': identity, 'radius_m': radius,
                'covered_area_m2': numerator, 'geometry_area_m2': denominator if eligible else None,
                'coverage_pct': percentage, 'geometry': None if clipped.is_empty else mapping(clipped),
                'registered_count': len(local), 'eligible_count': len(local & eligible), 'excluded_count': len(local_excluded),
                'contributing_count': len(contributors), 'contributing_facility_codes': sorted(contributors),
                'exclusion_reasons': dict(sorted(Counter(excluded[code] for code in local_excluded).items())),
                'completeness': 'unavailable' if not eligible else 'partial' if excluded else 'complete',
                'reason': 'no_eligible_points' if not eligible else 'excluded_locations_in_dataset' if excluded else '',
                'numeric_adjustment_m2': adjustment,
            })
    return {'status': 'candidate_artifact', 'release_id': buffers['release_id'], 'analysis_run_id': buffers.get('analysis_run_id'),
            'code_revision': buffers.get('code_revision'), 'source_input_hash': buffers.get('input_hash'),
            'method_version': 'python-union-clip-geodesic-v1', 'buffer_method_version': buffers.get('method_version'),
            'parameters': buffers.get('parameters'), 'versions': buffers.get('versions'),
            'dataset_registered_count': len(assignments), 'dataset_eligible_count': len(eligible), 'dataset_excluded_count': len(excluded),
            'results': results, 'limitations': ['Facilities outside the province are not included', 'Straight-line area coverage is not travel accessibility']}
