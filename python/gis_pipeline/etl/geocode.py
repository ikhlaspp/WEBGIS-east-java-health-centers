"""Local location-review queue. Candidate acquisition never verifies a location."""

import copy
import hashlib
import json
import math
import re
from datetime import datetime
from urllib.parse import urlencode, urlsplit

from .acquire import local_path
from .http_client import SourceClient
from .normalize import digest

VERSION = 'location-queue-1.0'
PRECISIONS = {'facility', 'street', 'village', 'district', 'regency', 'unknown'}


def point(lon, lat):
    if lon is None and lat is None:
        return None, None
    if lon is None or lat is None or isinstance(lon, bool) or isinstance(lat, bool):
        raise ValueError('Coordinates require a complete numeric pair')
    lon, lat = float(lon), float(lat)
    if not math.isfinite(lon) or not math.isfinite(lat) or not -180 <= lon <= 180 or not -90 <= lat <= 90:
        raise ValueError('Coordinates outside CRS84 bounds')
    return lon, lat


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamp requires a timezone')
    return value


def query_for(attributes):
    fields = ('nama_puskesmas', 'alamat', 'kecamatan', 'kabupaten', 'provinsi')
    if any(not isinstance(attributes.get(k), str) or not attributes[k].strip() for k in fields):
        raise ValueError('Facility name, address and complete region are required')
    return ', '.join([attributes[k].strip() for k in fields] + ['Indonesia'])


def candidate(release_id, code, source_id, query, lon, lat, provider, identity, **extra):
    lon, lat = point(lon, lat)
    return {'review_id': digest([release_id, code, source_id, identity]), 'release_id': release_id,
            'facility_code': code, 'source_id': source_id, 'provider': provider, 'query': query,
            'candidate_lon': lon, 'candidate_lat': lat, 'provider_object_id': None,
            'precision_level': 'unknown', 'centroid_candidate': None,
            'raw_response_private_path': None, 'raw_response_sha256': None,
            'retrieved_at': None, 'retrieved_at_unknown_reason': 'Historical source has no acquisition timestamp',
            'evidence_url': None, 'evidence_note': None, 'evidence_sha256': None,
            'reviewer_id': None, 'reviewed_at': None, 'observed_at': None,
            'decision_reason': None, 'result_status': 'pending', **extra}


def build_queue(master, boundary_manifest, release_id):
    if not isinstance(release_id, str) or not release_id.strip():
        raise ValueError('Explicit draft release identity required')
    if not boundary_manifest.get('geometry_validation_complete'):
        raise ValueError('Validated boundary manifest required')
    regions = {r['region_code'] for r in boundary_manifest['features']}
    entries, seen = [], set()
    for facility in sorted(master['facilities'], key=lambda f: f['facility_code']):
        code = facility['facility_code']
        if not re.fullmatch(r'\d{11}', code) or code in seen or facility['region_code'] not in regions:
            raise ValueError('Duplicate facility identity or unknown district')
        seen.add(code)
        query = query_for(facility['attributes'])
        candidates = []
        for old in facility['coordinate_candidates']:
            source = old['source']
            candidates.append(candidate(release_id, code, source['source_id'], query,
                old['longitude'], old['latitude'], 'historical_archive', source,
                source_identity=copy.deepcopy(source)))
        if len({c['review_id'] for c in candidates}) != len(candidates):
            raise ValueError('Duplicate candidate source identity')
        entries.append({'facility_code': code, 'region_code': facility['region_code'],
                        'parent_code': facility['parent_code'], 'attributes': copy.deepcopy(facility['attributes']),
                        'query': query, 'baseline_coordinate_present': facility['baseline_coordinate_present'],
                        'snapshot_status': 'unverified' if candidates else 'missing',
                        'work_status': 'pending', 'location_verified': False, 'radius_eligible': False,
                        'candidates': candidates, 'searches': [], 'decisions': []})
    if not entries:
        raise ValueError('Empty facility master')
    result = {'pipeline_version': VERSION, 'release_id': release_id, 'entries': entries,
              'provider_status': 'not_selected', 'publication_allowed': False,
              'summary': {'facilities': len(entries),
                          'baseline_candidates': sum(e['baseline_coordinate_present'] for e in entries),
                          'baseline_missing': sum(not e['baseline_coordinate_present'] for e in entries),
                          'without_any_candidate': sum(not e['candidates'] for e in entries),
                          'candidate_records': sum(len(e['candidates']) for e in entries), 'verified': 0}}
    result['input_queue_sha256'] = digest(result)
    return result


def load_inputs(root, facility_evidence, boundary_manifest, release_id):
    raw = local_path(root, facility_evidence['output_path'], 'data/processed').read_bytes()
    if hashlib.sha256(raw).hexdigest() != facility_evidence['output_sha256']:
        raise ValueError('Facility master checksum mismatch')
    for receipt in boundary_manifest['outputs'].values():
        path = local_path(root, receipt['path'], 'data/processed')
        with path.open('rb') as handle:
            actual = hashlib.file_digest(handle, 'sha256').hexdigest()
        if actual != receipt['sha256'] or path.stat().st_size != receipt['bytes']:
            raise ValueError('Boundary output checksum mismatch')
    result = build_queue(json.loads(raw), boundary_manifest, release_id)
    result['input_identity'] = {'facility_master_sha256': facility_evidence['output_sha256'],
                                'boundary_manifest_content_sha256': boundary_manifest['content_sha256']}
    result['input_queue_sha256'] = digest({k: v for k, v in result.items() if k != 'input_queue_sha256'})
    return result


class NominatimProvider:
    """Opt-in adapter for an explicitly selected, permitted Nominatim deployment."""

    endpoint_path = '/search'

    def __init__(self, root, config, client=None):
        required = ('provider_id', 'endpoint', 'edition', 'user_agent', 'terms_url',
                    'attribution', 'selection_reason', 'selected_by', 'selected_at')
        if any(not isinstance(config.get(k), str) or not config[k].strip() for k in required):
            raise ValueError('Provider selection and terms evidence required')
        timestamp(config['selected_at'])
        url = urlsplit(config['endpoint'])
        if (url.scheme != 'https' or not url.hostname or url.username or url.password
                or url.query or url.fragment or url.path.rstrip('/') != self.endpoint_path):
            raise ValueError('Explicit HTTPS provider endpoint required')
        # Public OSMF service requires a separate, informed operator choice, not a generated default.
        if url.hostname == 'nominatim.openstreetmap.org':
            raise ValueError('Public OSMF endpoint is not enabled in this workflow')
        if config.get('batch_permitted') is not True or config.get('cache_permitted') is not True:
            raise ValueError('Provider must permit this batch and private response cache')
        interval = config.get('interval_seconds')
        if type(interval) not in (int, float) or not math.isfinite(interval) or interval < 1:
            raise ValueError('Provider interval must be at least one second')
        self.config = copy.deepcopy(config)
        self.client = client or SourceClient(local_path(root, 'data/raw/geocoder', 'data/raw'),
                                             {url.hostname}, interval=interval)

    def search(self, entry, release_id):
        query = entry['query']
        url = self.config['endpoint'] + '?' + urlencode({'q': query, 'format': 'jsonv2',
                                                        'countrycodes': 'id', 'addressdetails': 1, 'limit': 5})
        response = self.client.fetch(url, self.config['provider_id'], self.config['edition'],
                                     headers={'User-Agent': self.config['user_agent']}, max_bytes=2 * 1024 * 1024)
        rows = json.loads(response['data'])
        return self.result(rows, response, entry, release_id)

    def result(self, rows, response, entry, release_id):
        query = entry['query']
        if not isinstance(rows, list) or len(rows) > 5:
            raise ValueError('Unexpected geocoder response')
        receipt = response['receipt']
        candidates = []
        for row in rows:
            lon, lat = point(row.get('lon'), row.get('lat'))
            if lon is None or row.get('osm_type') not in ('node', 'way', 'relation') or not str(row.get('osm_id', '')).isdigit():
                raise ValueError('Geocoder candidate missing coordinate/object identity')
            object_id = row['osm_type'] + '/' + str(row['osm_id'])
            kind = row.get('addresstype', row.get('type'))
            precision = {'road': 'street', 'village': 'village', 'hamlet': 'village',
                         'suburb': 'district', 'county': 'regency'}.get(kind, 'unknown')
            candidates.append(candidate(release_id, entry['facility_code'], self.config['provider_id'], query,
                lon, lat, self.config['provider_id'], [query, object_id, receipt['sha256']],
                provider_object_id=object_id, precision_level=precision,
                centroid_candidate=True if precision != 'unknown' else None,
                raw_response_private_path=receipt['raw_path'], raw_response_sha256=receipt['sha256'],
                retrieved_at=receipt['acquired_at'], retrieved_at_unknown_reason=None,
                provider_classification={'category': row.get('category'), 'type': row.get('type'),
                                         'addresstype': row.get('addresstype')},
                provider_display_name=row.get('display_name'), attribution=self.config['attribution']))
        if len({c['review_id'] for c in candidates}) != len(candidates):
            raise ValueError('Duplicate provider objects')
        return {'query': query, 'provider': self.config['provider_id'], 'receipt': receipt,
                'cache_hit': response['cache_hit'], 'candidates': candidates,
                'status': 'candidates_returned' if candidates else 'no_match'}


class PhotonProvider(NominatimProvider):
    """Photon forward search, retaining POIs as unverified even when tagged as clinics."""

    endpoint_path = '/api'

    def search(self, entry, release_id):
        url = self.config['endpoint'] + '?' + urlencode({'q': entry['query'], 'countrycode': 'ID', 'limit': 5})
        response = self.client.fetch(url, self.config['provider_id'], self.config['edition'],
                                     headers={'User-Agent': self.config['user_agent']}, max_bytes=2 * 1024 * 1024)
        document = json.loads(response['data'])
        if not isinstance(document, dict) or not isinstance(document.get('features'), list):
            raise ValueError('Unexpected Photon response')
        rows = []
        for feature in document['features']:
            geometry, props = feature.get('geometry', {}), feature.get('properties', {})
            coordinates = geometry.get('coordinates')
            if (feature.get('type') != 'Feature' or geometry.get('type') != 'Point'
                    or not isinstance(coordinates, list) or len(coordinates) != 2):
                raise ValueError('Photon candidate requires a GeoJSON point')
            rows.append({'lon': coordinates[0], 'lat': coordinates[1],
                         'osm_type': {'N': 'node', 'W': 'way', 'R': 'relation'}.get(props.get('osm_type')),
                         'osm_id': props.get('osm_id'), 'type': props.get('osm_value'),
                         'category': props.get('osm_key'), 'addresstype': props.get('type', props.get('osm_value')),
                         'display_name': props.get('name')})
        return self.result(rows, response, entry, release_id)


def validate_decision(candidate_record, decision):
    for key in ('review_id', 'release_id', 'facility_code', 'source_id'):
        if decision.get(key) != candidate_record[key]:
            raise ValueError('Review identity does not match candidate')
    status = decision.get('result_status')
    if status not in ('accepted', 'rejected'):
        raise ValueError('A review decision must be accepted or rejected')
    if any(not isinstance(decision.get(k), str) or not decision[k].strip()
           for k in ('reviewer_id', 'reviewed_at', 'decision_reason')):
        raise ValueError('Reviewer, time and reason required')
    timestamp(decision['reviewed_at'])
    if decision.get('precision_level') not in PRECISIONS:
        raise ValueError('Unknown precision level')
    if point(decision.get('candidate_lon'), decision.get('candidate_lat')) != point(
            candidate_record['candidate_lon'], candidate_record['candidate_lat']):
        raise ValueError('Review cannot relocate a candidate')
    if status == 'accepted':
        if (decision['precision_level'] != 'facility' or decision.get('centroid_candidate') is not False
                or candidate_record['candidate_lon'] is None):
            raise ValueError('Accepted location requires a facility point, not a centroid')
        url = decision.get('evidence_url')
        valid_url = isinstance(url, str) and urlsplit(url).scheme == 'https' and bool(urlsplit(url).hostname)
        note, sha = decision.get('evidence_note'), decision.get('evidence_sha256')
        valid_copy = isinstance(note, str) and bool(note.strip()) and isinstance(sha, str) and bool(re.fullmatch('[0-9a-f]{64}', sha))
        if not (valid_url or valid_copy):
            raise ValueError('Accepted location requires accessible evidence or note and copy hash')
    return copy.deepcopy(decision)
