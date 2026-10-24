"""Acquire region reference evidence without repairing or promoting source geometry."""

import hashlib
import copy
import json
import re
import time
import urllib.parse
from collections import Counter
from pathlib import Path

import pdfplumber

from .indicators import angled_glyph
from .sources import fetch_zip_member

BIG_SERVICE = 'https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KECAMATAN_AR/MapServer'
HDX_CATALOG = 'https://data.humdata.org/api/3/action/package_show?id=cod-ab-idn'


def select_hdx_features(collection, master):
    if not master['report']['complete']:
        raise ValueError('Resolve the master identities before selecting boundaries')
    if collection.get('type') != 'FeatureCollection' or collection.get('crs', {}).get('properties', {}).get('name') != 'urn:ogc:def:crs:OGC:1.3:CRS84':
        raise ValueError('Unexpected historical boundary schema or CRS')
    expected = {row['code'] for row in master['rows']}
    features, excluded, links, seen = [], [], [], set()
    for feature in collection['features']:
        props = feature['properties']
        if props['adm1_pcode'] != 'ID35':
            continue
        pcode = props.get('adm3_pcode')
        if not isinstance(pcode, str) or not re.fullmatch(r'ID35\d{5}', pcode):
            raise ValueError('Malformed historical source code')
        code = pcode[2:]
        if code in seen:
            raise ValueError('Duplicate historical boundary code')
        seen.add(code)
        geometry = feature.get('geometry')
        if not geometry or geometry.get('type') not in ('Polygon', 'MultiPolygon') or not geometry.get('coordinates'):
            raise ValueError('Missing historical polygon geometry')
        if props.get('valid_on') != '2020-04-01' or props.get('version') != 'v01':
            raise ValueError('Historical edition changed')
        if props.get('adm2_pcode') != 'ID' + code[:4]:
            raise ValueError('Historical boundary parent mismatch')
        if code not in expected:
            if (pcode, props.get('adm3_name')) != ('ID3522888', 'Perairan'):
                raise ValueError('Unexpected extra historical region requires review')
            excluded.append({'feature': feature, 'reason': 'Source water area, not a district in the 2023 master'})
            continue
        features.append(feature)
        links.append({'source_pcode': pcode, 'region_code': code, 'mapping': 'exact ID prefix and BPS text code'})
    if {link['region_code'] for link in links} != expected:
        raise ValueError('Historical boundaries do not cover every master district')
    return {'collection': {**collection, 'features': features}, 'excluded': excluded, 'links': links,
            'report': {'complete': True, 'districts': len(features), 'excluded_water_objects': len(excluded),
                       'parents': len({f['properties']['adm2_pcode'] for f in features}),
                       'geometry_types': dict(Counter(f['geometry']['type'] for f in features))},
            'boundary_edition': '2020-04-01', 'crs': 'OGC:CRS84',
            'analysis_mode': 'mixed_period_exploration', 'strict_2023_geometry_verified': False,
            'ready_for_public_release': False}


def parse_hdx(member_receipt, catalog_receipt, master):
    for receipt in (member_receipt, catalog_receipt):
        if hashlib.sha256(Path(receipt['raw_path']).read_bytes()).hexdigest() != receipt['sha256']:
            raise ValueError('Historical source evidence hash mismatch')
    if catalog_receipt['source_url'] != HDX_CATALOG:
        raise ValueError('Expected the official HDX catalogue receipt')
    catalog = json.loads(Path(catalog_receipt['raw_path']).read_text(encoding='utf-8'))['result']
    if catalog['license_id'] != 'cc-by-igo' or catalog['dataset_source'] != 'Badan Pusat Statistik (BPS - Statistics Indonesia)':
        raise ValueError('Historical licence or attribution changed')
    resource = next(item for item in catalog['resources'] if item['format'] == 'GeoJSON')
    if member_receipt['source_url'] != resource['url'] + '#idn_admin3.geojson':
        raise ValueError('Member receipt does not match the catalogued resource')
    collection = json.loads(Path(member_receipt['raw_path']).read_text(encoding='utf-8'))
    if len(collection['features']) != 7069:
        raise ValueError('National historical district count changed; inspect edition')
    result = select_hdx_features(collection, master)
    result['receipts'] = {'member': member_receipt, 'catalog': catalog_receipt}
    result['license'] = {'id': 'CC-BY-3.0-IGO', 'url': 'https://creativecommons.org/licenses/by/3.0/igo/',
                         'catalogue_url': 'https://data.humdata.org/dataset/cod-ab-idn',
                         'attribution': 'Indonesia - Subnational Administrative Boundaries (COD-AB v01), BPS; distributed by OCHA ROAP, OCHA FIS and HDX.',
                         'changes': 'Selected East Java districts, linked exact BPS codes, retained water object separately; source geometry unchanged.',
                         'notice': 'No endorsement by BPS, OCHA or HDX is implied.',
                         'reuse_permitted_subject_to_terms': True}
    return result


def acquire_hdx(raw_root, master):
    catalog, receipt = fetch_json(HDX_CATALOG, raw_root, 'hdx-catalog', 'cod-ab-idn-v01', {'data.humdata.org'}, cache=False)
    resource = next(item for item in catalog['result']['resources'] if item['format'] == 'GeoJSON')
    member = fetch_zip_member(resource['url'], resource['size'], 'idn_admin3.geojson', raw_root,
                              'hdx-boundary-admin3', '2020-04', {'data.humdata.org', 's3.us-east-1.amazonaws.com'})
    return parse_hdx(member, receipt, master)


def reconcile_master(master, decisions):
    """Apply explicit decisions only when the archived official bridge corroborates them."""
    result = copy.deepcopy(master)
    discrepancies = {(row['code'], row['name'], row['locator']) for row in master['summary_discrepancies']}
    seen = set()
    rows = {row['code']: row for row in result['rows']}
    for decision in decisions:
        key = tuple(decision['summary'][field] for field in ('code', 'name', 'locator'))
        if key not in discrepancies or key in seen:
            raise ValueError('Unexpected or duplicate reconciliation decision')
        receipt = decision['evidence_receipt']
        url = urllib.parse.urlsplit(receipt['source_url'])
        query = urllib.parse.parse_qs(url.query)
        if (url.scheme != 'https' or url.hostname != 'sig.bps.go.id'
                or url.path != '/rest-bridging/getwilayah'
                or receipt['edition'] != '2023_1.2022'
                or query.get('periode_merge') != ['2023_1.2022']):
            raise ValueError('Expected explicit official 2023 bridge evidence')
        raw = Path(receipt['raw_path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != receipt['sha256']:
            raise ValueError('Reconciliation evidence hash mismatch')
        code, name = decision['canonical_code'], decision['canonical_name']
        if name != decision['summary']['name']:
            raise ValueError('Reconciliation must corroborate the disputed identity, not substitute another name')
        matches = [row for row in json.loads(raw) if row.get('kode_bps') == code and row.get('nama_bps') == name]
        if len(matches) != 1 or code not in rows or query.get('parent') != [code[:4]]:
            raise ValueError('Canonical identity is not uniquely supported by evidence')
        rows[code]['name'] = name
        rows[code]['identity_evidence'] = {'source_hash': receipt['sha256'], 'source_url': receipt['source_url'],
                                         'period': receipt['edition'], 'raw_record': matches[0]}
        seen.add(key)
    result['identity_resolutions'] = copy.deepcopy(decisions)
    result['report']['unresolved_source_conflicts'] = len(discrepancies - seen)
    result['report']['complete'] = (result['report']['coverage_complete']
                                     and result['report'].get('summary_rows') == 666
                                     and not (discrepancies - seen))
    return result


def detail_line(lines, index):
    line = lines[index]
    split = re.match(r'^(35\s*\d{2}\s*\d{3})\s+(35\s*\d{2}\s*\d{3}\s*\d{3}\b.*)$', line)
    if split and 0 < index < len(lines) - 1:
        before, after = lines[index - 1], lines[index + 1]
        if all(re.fullmatch(r"[A-Z][A-Z .'-]+", value) for value in (before, after)):
            line = split[1] + ' ' + before + ' ' + after + ' ' + split[2]
    return re.match(r'^(35)\s*(\d{2})\s*(\d{3})\s+([^\d]+?)\s+35\s*\d{2}\s*\d{3}\s*\d{3}\b', line)


def fetch_json(url, raw_root, source_id, edition, allowed_hosts, *, cache=True):
    from .http_client import SourceClient

    def validate(data, headers):
        parsed = json.loads(data)
        if not isinstance(parsed, (dict, list)) or 'error' in parsed:
            raise ValueError('Source API error or unexpected JSON schema')
    result = SourceClient(raw_root, allowed_hosts).fetch(
        url, source_id, edition, headers={'Accept': 'application/json'}, validate=validate, cache=cache)
    return json.loads(result['data']), result['receipt']


def acquire_bridge(master, raw_root, resume_receipts=()):
    records, receipts = [], []
    cached = {}
    for receipt in resume_receipts:
        parsed = urllib.parse.urlsplit(receipt['source_url'])
        if parsed.scheme != 'https' or parsed.hostname != 'sig.bps.go.id' or parsed.path != '/rest-bridging/getwilayah':
            raise ValueError('Invalid resumed bridge source')
        if receipt['edition'] != '2023_1.2022':
            raise ValueError('Invalid resumed bridge period')
        key = tuple(sorted(urllib.parse.parse_qsl(parsed.query)))
        cached[key] = receipt
    for regency in master['regencies']:
        url = ('https://sig.bps.go.id/rest-bridging/getwilayah?' + urllib.parse.urlencode({
            'level': 'kecamatan', 'parent': regency['code'], 'periode_merge': '2023_1.2022'}))
        key = tuple(sorted(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query)))
        if key in cached:
            receipt = cached[key]
            raw = Path(receipt['raw_path']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != receipt['sha256']:
                raise ValueError('Resumed bridge hash mismatch')
            rows = json.loads(raw)
        else:
            time.sleep(1)
            rows, receipt = fetch_json(url, raw_root, 'bps-bridge', '2023_1.2022', {'sig.bps.go.id'})
        if not isinstance(rows, list) or len(rows) != regency['expected_districts']:
            raise ValueError('Bridge parent coverage mismatch')
        for row in rows:
            if (not isinstance(row.get('kode_bps'), str) or not re.fullmatch(regency['code'] + r'\d{3}', row['kode_bps'])
                    or not isinstance(row.get('kode_dagri'), str) or not re.fullmatch(r'35\d{4}', row['kode_dagri'])):
                raise ValueError('Invalid bridge code or parent')
            records.append({**row, 'source_hash': receipt['sha256'], 'period': receipt['edition']})
        receipts.append(receipt)
    if (len({r['kode_bps'] for r in records}) != len(records)
            or len({r['kode_dagri'] for r in records}) != len(records)
            or {r['kode_bps'] for r in records} != {r['code'] for r in master['rows']}):
        raise ValueError('Bridge duplicates or master code-set mismatch')
    return {'records': records, 'receipts': receipts, 'period': '2023_1.2022'}


def candidate_links(collection, bridge):
    lookup = {r['kode_dagri']: r for r in bridge['records']}
    if len(lookup) != len(bridge['records']):
        raise ValueError('Ambiguous bridge')
    links, excluded = [], []
    used = set()
    for feature in collection['features']:
        properties = feature['properties']
        raw = properties.get('KDCPUM')
        code = raw.replace('.', '') if isinstance(raw, str) and re.fullmatch(r'35\.\d{2}\.\d{2}', raw) else None
        if code not in lookup:
            excluded.append({'object_id': properties['OBJECTID'], 'raw_code': raw, 'reason': 'No exact official code link'})
            continue
        if code in used:
            raise ValueError('Multiple boundary objects for one bridge identity require explicit review')
        used.add(code)
        links.append({'object_id': properties['OBJECTID'], 'pum_raw': raw, 'bps_code': lookup[code]['kode_bps'],
                      'bridge_hash': lookup[code]['source_hash'], 'bridge_period': bridge['period'],
                      'boundary_edition': '2026-06', 'status': 'candidate_not_historically_validated'})
    return {'links': links, 'excluded': excluded, 'unmatched_bridge_codes': sorted(set(lookup) - used),
            'publication_allowed': False, 'historical_geometry_validated': False}


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
        parsed, receipt = fetch_json(url, raw_root, 'big-boundary', '2026-06', {'geoservices.big.go.id'}, cache=False)
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
