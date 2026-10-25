"""Reproducible spatial/source screening; never substitutes for facility evidence."""

from collections import Counter, defaultdict

import shapely
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

from .geocode import point
from .normalize import digest


def audit(queue, normalized_rows, boundaries):
    features = boundaries['features']
    codes = [f['properties']['region_code'] for f in features]
    if len(set(codes)) != len(codes):
        raise ValueError('Duplicate boundary code')
    geometries = [shape(f['geometry']) for f in features]
    by_code = dict(zip(codes, geometries))
    tree = STRtree(geometries)
    rows = {}
    for row in normalized_rows:
        if row['dataset'] == 'coordinates_csv':
            key = (row['source_id'], row['source_hash'], row['source_locator'])
            if key in rows:
                raise ValueError('Duplicate source row')
            rows[key] = row
    selected = sorted((e for e in queue['entries'] if e['baseline_coordinate_present']),
                      key=lambda e: (e['parent_code'], e['facility_code']))
    if len({e['facility_code'] for e in selected}) != len(selected):
        raise ValueError('Duplicate facility identity')
    records, groups = [], defaultdict(list)
    for entry in selected:
        candidates = [c for c in entry['candidates'] if c.get('source_identity', {}).get('dataset') == 'coordinates_csv']
        if len(candidates) != 1:
            raise ValueError('Exactly one CSV baseline candidate required')
        candidate = candidates[0]
        identity = candidate['source_identity']
        source = rows[(identity['source_id'], identity['source_hash'], identity['source_locator'])]
        fields = source['normalized_fields']
        expected = point(fields['longitude'], fields['latitude'])
        actual = point(candidate['candidate_lon'], candidate['candidate_lat'])
        if (expected != actual or fields['facility_code'] != entry['facility_code']
                or any(fields[k] != entry['attributes'][k] for k in ('nama_puskesmas', 'alamat', 'kecamatan', 'kabupaten'))):
            raise ValueError('Queue candidate differs from its frozen source row')
        if actual[0] is None or entry['region_code'] not in by_code:
            raise ValueError('Baseline point or assigned boundary missing')
        location = Point(*actual)
        assigned = by_code[entry['region_code']]
        covers = sorted(codes[int(i)] for i in tree.query(location, predicate='covered_by'))
        projection = f'+proj=aeqd +lat_0={actual[1]} +lon_0={actual[0]} +datum=WGS84 +units=m +no_defs'
        transform = Transformer.from_crs('EPSG:4326', projection, always_xy=True)
        boundary_distance = shapely.transform(assigned.boundary, transform.transform, interleaved=False).distance(
            shapely.transform(location, transform.transform, interleaved=False))
        raw = source['raw_fields']
        groups[actual].append(entry['facility_code'])
        records.append({'facility_code': entry['facility_code'], 'parent_code': entry['parent_code'],
            'region_code': entry['region_code'], 'review_id': candidate['review_id'],
            'candidate_lon': actual[0], 'candidate_lat': actual[1], 'source_identity': identity,
            'source_row_sha256': digest(source), 'name_address_match_frozen_master': True,
            'historical_query': raw.get('query_alamat'), 'historical_status': raw.get('status_geocoding'),
            'query_contains_full_address': entry['attributes']['alamat'].casefold() in str(raw.get('query_alamat', '')).casefold(),
            'assigned_boundary_covers': assigned.covers(location), 'covering_region_codes': covers,
            'distance_to_assigned_boundary_m': boundary_distance, 'review_near_boundary': boundary_distance <= 50,
            'boundary_edition': '2020-04-01', 'precision_level': 'unknown', 'centroid_candidate': None,
            'location_status': 'unverified', 'result_status': 'pending', 'location_verified': False,
            'evidence_available': ['frozen source row with name/address/query/coordinate', 'historical administrative geometry'],
            'missing_evidence': ['Traceable facility building or POI matching name/address and candidate point'],
            'decision_reason': 'Source identity and spatial screening do not establish a facility location; found label is not acceptance',
            'next_action': 'Review facility-specific evidence and duplicate/parent conflicts; preserve original point'})
    duplicates = [values for values in groups.values() if len(values) > 1]
    duplicates.sort()
    for record in records:
        record['same_point_facility_codes'] = groups[(record['candidate_lon'], record['candidate_lat'])]
    batches = []
    parents = sorted({e['parent_code'] for e in selected})
    for parent in parents:
        parent_records = [r for r in records if r['parent_code'] == parent]
        for start in range(0, len(parent_records), 25):
            chunk = parent_records[start:start+25]
            batches.append({'batch_id': f'{parent}-{start // 25 + 1:02d}', 'parent_code': parent,
                            'input_sha256': digest(chunk), 'codes': [r['facility_code'] for r in chunk],
                            'screened': [r['facility_code'] for r in chunk], 'completed': [],
                            'pending': [r['facility_code'] for r in chunk], 'blocked': [],
                            'reviewer': 'Codex technical source/spatial screening only'})
    return {'pipeline_version': 'location-screening-1.0', 'records': records, 'batches': batches,
            'duplicate_groups': duplicates, 'summary': {'screened': len(records), 'batches': len(batches),
                'inside_assigned_boundary': sum(r['assigned_boundary_covers'] for r in records),
                'outside_assigned_boundary': sum(not r['assigned_boundary_covers'] for r in records),
                'not_covered_by_selected_boundaries': sum(not r['covering_region_codes'] for r in records),
                'near_boundary_50m': sum(r['review_near_boundary'] for r in records),
                'duplicate_groups': len(duplicates), 'verified': 0,
                'historical_status_counts': dict(Counter(r['historical_status'] for r in records)),
                'queries_with_full_address': sum(r['query_contains_full_address'] for r in records)},
            'facility_evidence_review_complete': False, 'publication_allowed': False}
