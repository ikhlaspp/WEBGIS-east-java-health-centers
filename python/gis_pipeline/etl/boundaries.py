"""Acquire region reference evidence without repairing or promoting source geometry."""

import hashlib
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import pdfplumber

from .indicators import angled_glyph
from .sources import CheckedRedirect, snapshot, validate_url

BIG_SERVICE = 'https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KECAMATAN_AR/MapServer'


def detail_line(lines, index):
    line = lines[index]
    split = re.match(r'^(35\s*\d{2}\s*\d{3})\s+(35\s*\d{2}\s*\d{3}\s*\d{3}\b.*)$', line)
    if split and 0 < index < len(lines) - 1:
        before, after = lines[index - 1], lines[index + 1]
        if all(re.fullmatch(r"[A-Z][A-Z .'-]+", value) for value in (before, after)):
            line = split[1] + ' ' + before + ' ' + after + ' ' + split[2]
    return re.match(r'^(35)\s*(\d{2})\s*(\d{3})\s+([^\d]+?)\s+35\s*\d{2}\s*\d{3}\s*\d{3}\b', line)


def fetch_json(url, raw_root, source_id, edition, allowed_hosts):
    validate_url(url, allowed_hosts)
    opener = urllib.request.build_opener(CheckedRedirect(allowed_hosts))
    request = urllib.request.Request(url, headers={'User-Agent': 'GIS-puskesmas-academic/1.0',
                                                  'Accept': 'application/json'})
    with opener.open(request, timeout=60) as response:
        data = response.read(64 * 1024 * 1024 + 1)
    if len(data) > 64 * 1024 * 1024:
        raise ValueError('Oversized JSON response')
    parsed = json.loads(data)
    if not isinstance(parsed, dict) or 'error' in parsed:
        raise ValueError('Source API error or unexpected JSON schema')
    receipt = snapshot(data, raw_root, source_id, edition, url, 'https_download')
    return parsed, receipt


def parse_master(path, manifest):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('Source hash mismatch')
    rows, regencies, diagnostics = [], [], []
    detail_codes = {}
    edition_seen = False
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            glyphs = [c for c in page.chars if angled_glyph(c)]
            filtered = page
            if ''.join(c['text'] for c in glyphs) == 'https://jatim.bps.go.id':
                filtered = page.filter(lambda obj: not angled_glyph(obj))
            text = filtered.extract_text() or ''
            edition_seen |= 'Master File Desa Provinsi Jawa Timur 2023' in text
            lines = text.splitlines()
            for number, line in enumerate(lines, 1):
                detail = detail_line(lines, number - 1)
                if detail:
                    province, regency, suffix, name = detail.groups()
                    code = province + regency + suffix
                    row = {'code': code, 'parent_code': province + regency, 'name': name.strip(),
                           'code_system': 'BPS', 'edition': '2023', 'source_hash': manifest['sha256'],
                           'source_url': manifest['source_url'],
                           'locator': f'pdf/page/{page.page_number}/line/{number}', 'raw_line': line,
                           'raw_context': lines[max(0, number - 2):number + 1]}
                    if code in detail_codes and detail_codes[code]['name'] != row['name']:
                        diagnostics.append({'code': 'conflicting_detail_name', 'variants': [detail_codes[code], row]})
                    else:
                        detail_codes[code] = row
            is_regency = 'Jumlah Kecamatan' in text and 'Nama Kabupaten/Kota' in text
            is_district = 'Nama Kecamatan' in text and 'Urban Rural Total' in text
            if not (is_regency or is_district):
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if is_regency:
                    match = re.fullmatch(r'\d+\s+(35)\s+(\d{2})\s+(.+?)\s+(\d+)', line)
                    if match:
                        province, suffix, name, expected = match.groups()
                        regencies.append({'code': province + suffix, 'parent_code': province,
                                          'name': name, 'expected_districts': int(expected),
                                          'locator': f'pdf/page/{page.page_number}/line/{number}', 'raw_line': line})
                else:
                    match = re.match(r'^\d+\s+(\d{1,2})\s*(\d{2})\s*(\d{3})\s+([^\d]+?)\s+(?=[\d\-\ufffd\u2013])', line)
                    if match:
                        province, regency, suffix, name = match.groups()
                        rows.append({'code': province + regency + suffix, 'parent_code': province + regency,
                                     'name': name.strip(), 'code_system': 'BPS', 'edition': '2023',
                                     'source_hash': manifest['sha256'], 'source_url': manifest['source_url'],
                                     'locator': f'pdf/page/{page.page_number}/line/{number}', 'raw_line': line})
                    elif re.match(r'^\d+\s+35\s+', line):
                        diagnostics.append({'code': 'unparsed_master_row', 'raw_line': line,
                                            'page': page.page_number})
    summary_rows = rows
    rows = list(detail_codes.values())
    counts = Counter(row['parent_code'] for row in rows)
    codes = [row['code'] for row in rows]
    expected = {row['code']: row['expected_districts'] for row in regencies}
    coverage_complete = (edition_seen and manifest.get('edition') == '2023'
                and len(regencies) == 38 and len(expected) == 38 and len(rows) == 666
                and len(set(codes)) == len(codes) and dict(counts) == expected and not diagnostics)
    summary_mismatches = [row for row in summary_rows if row['code'] not in detail_codes
                          or detail_codes[row['code']]['name'] != row['name']]
    return {'rows': rows, 'regencies': regencies, 'diagnostics': diagnostics,
            'summary_discrepancies': summary_mismatches,
            'report': {'complete': coverage_complete and len(summary_rows) == 666 and not summary_mismatches,
                       'coverage_complete': coverage_complete, 'source_conflicts': len(summary_mismatches),
                       'summary_rows': len(summary_rows),
                       'districts': len(rows), 'regencies': len(regencies),
                       'expected_by_parent': expected, 'actual_by_parent': dict(counts)}}


def collect_features(query, metadata, where, batch_size=25):
    """Use explicit IDs and reconcile every page; never trust a transfer-limit count."""
    if metadata.get('geometryType') != 'esriGeometryPolygon':
        raise ValueError('Expected polygon layer')
    count = query({'where': where, 'returnCountOnly': 'true', 'f': 'json'})['count']
    ids = query({'where': where, 'returnIdsOnly': 'true', 'f': 'json'})
    object_ids = ids.get('objectIds') or []
    if not object_ids or len(object_ids) != count or len(set(object_ids)) != count:
        raise ValueError('Source count/ID list mismatch or empty coverage')
    object_field = ids['objectIdFieldName']
    features = []
    batch_size = min(batch_size, metadata['maxRecordCount'])
    if batch_size < 1:
        raise ValueError('Invalid source page size')
    for offset in range(0, len(object_ids), batch_size):
        selected = object_ids[offset:offset + batch_size]
        page = query({'objectIds': ','.join(map(str, selected)), 'outFields': '*',
                      'returnGeometry': 'true', 'outSR': '4326', 'f': 'geojson'})
        if page.get('type') != 'FeatureCollection' or page.get('exceededTransferLimit'):
            raise ValueError('Incomplete or unexpected geometry response')
        returned = [feature['properties'][object_field] for feature in page['features']]
        if len(returned) != len(selected) or set(returned) != set(selected):
            raise ValueError('Missing, duplicate or unexpected IDs in geometry page')
        for feature in page['features']:
            geometry = feature.get('geometry')
            if not geometry or geometry.get('type') not in ('Polygon', 'MultiPolygon') or not geometry.get('coordinates'):
                raise ValueError('Missing or unsupported source geometry')
            features.append(feature)
    final_ids = query({'where': where, 'returnIdsOnly': 'true', 'f': 'json'}).get('objectIds') or []
    if len(final_ids) != count or set(final_ids) != set(object_ids):
        raise ValueError('Source changed during acquisition')
    return {'type': 'FeatureCollection', 'features': features}


def coverage(collection, master_codes):
    features = collection['features']
    codes = [feature['properties'].get('KDCBPS') for feature in features]
    present = {code for code in codes if isinstance(code, str) and re.fullmatch(r'35\d{5}', code)}
    return {'objects': len(features), 'valid_bps_codes': len(present),
            'missing_or_invalid_bps_code': sum(not isinstance(code, str) or not re.fullmatch(r'35\d{5}', code) for code in codes),
            'master_codes_without_polygon': sorted(set(master_codes) - present),
            'polygon_codes_outside_master': sorted(present - set(master_codes)),
            'geometry_types': dict(Counter(f['geometry']['type'] for f in features)),
            'regency_names': sorted({f['properties']['WADMKK'] for f in features if f['properties'].get('WADMKK')}),
            'status': 'candidate_requires_edition_license_and_crosswalk_review'}


def acquire_big(raw_root):
    receipts = []
    def get(url):
        parsed, receipt = fetch_json(url, raw_root, 'big-boundary', '2026-06', {'geoservices.big.go.id'})
        receipts.append(receipt)
        return parsed
    service = get(BIG_SERVICE + '?f=pjson')
    if 'Juni 2026' not in service.get('serviceDescription', ''):
        raise ValueError('Source edition changed; review metadata before acquisition')
    metadata = get(BIG_SERVICE + '/0?f=pjson')
    item = get(BIG_SERVICE + '/info/iteminfo?f=pjson')
    if metadata.get('extent', {}).get('spatialReference', {}).get('wkid') != 4326:
        raise ValueError('Unexpected source CRS')
    query = lambda params: get(BIG_SERVICE + '/0/query?' + urllib.parse.urlencode(params))
    collection = collect_features(query, metadata, "KDPPUM='35'")
    return {'collection': collection, 'service_metadata': service, 'layer_metadata': metadata,
            'item_metadata': item,
            'receipts': receipts, 'edition': '2026-06', 'crs': 'EPSG:4326',
            'license_status': 'requires_review' if item.get('licenseInfo') else 'not_established',
            'publication_allowed': False,
            'harmonization_required': True}
