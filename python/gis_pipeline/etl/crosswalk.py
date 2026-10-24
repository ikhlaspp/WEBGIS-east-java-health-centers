"""Evidence-bound region mapping without fuzzy approval or observation allocation."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .acquire import checked_bytes, local_path
from .normalize import digest, match_key

VERSION = 'crosswalk-1.0'


def scope(row):
    return {**{key: row[key] for key in ('dataset', 'source_id', 'source_hash', 'source_edition')},
            'observation_period': row['normalized_fields'].get('observation_year')}


def registry(master, expected_districts=None, expected_parents=None):
    if not master['report']['complete']:
        raise ValueError('Master is incomplete')
    parents = {r['code']: r for r in master['regencies']}
    districts = {r['code']: r for r in master['rows']}
    if len(parents) != len(master['regencies']) or len(districts) != len(master['rows']):
        raise ValueError('Duplicate official code')
    if expected_districts is not None and len(districts) != expected_districts:
        raise ValueError('District count mismatch')
    if expected_parents is not None and len(parents) != expected_parents:
        raise ValueError('Parent count mismatch')
    index = defaultdict(list)
    for code, row in districts.items():
        parent = row['parent_code']
        if (not isinstance(code, str) or not re.fullmatch(r'35\d{5}', code)
                or parent not in parents or code[:4] != parent
                or row['code_system'] != 'BPS' or row['edition'] != '2023'):
            raise ValueError('Invalid master code, parent, system or edition')
        index[(match_key(parents[parent]['name']), match_key(row['name']))].append(code)
    for parent, row in parents.items():
        if sum(r['parent_code'] == parent for r in districts.values()) != row['expected_districts']:
            raise ValueError('Parent subtotal mismatch')
    return parents, districts, index


def validate_decisions(decisions, parents, districts, bridge, boundary_set, supplemental):
    approved = {}
    for decision in decisions:
        if decision['status'] != 'approved':
            continue
        if (decision['master_edition'] != '2023' or decision['target_boundary_set'] != boundary_set
                or not decision.get('reviewer') or not decision.get('reviewed_at')):
            raise ValueError('Alias lacks scoped edition/boundary/review evidence')
        target = districts[decision['target_code']]
        parent_name = match_key(parents[target['parent_code']]['name'])
        parent, name = decision['source_key']
        if parent not in (parent_name, 'kabupaten ' + parent_name):
            raise ValueError('Alias crosses parent boundary')
        if decision['parent_code'] != target['parent_code']:
            raise ValueError('Alias target parent mismatch')
        evidence = decision['evidence']
        if evidence['master_locator'] != target['locator'] or evidence['master_hash'] != target['source_hash']:
            raise ValueError('Alias master evidence mismatch')
        bridged = bridge[target['code']]
        if evidence['bridge_hash'] != bridged['source_hash'] or bridged['period'] != '2023_1.2022':
            raise ValueError('Alias bridge evidence mismatch')
        basis = decision['basis']
        if basis == 'official_bridge_name':
            valid = name in {match_key(bridged['nama_bps']), match_key(bridged['nama_dagri'])}
        elif basis == 'reviewed_word_spacing':
            valid = name.replace(' ', '') == match_key(target['name']).replace(' ', '')
        elif basis == 'explicit_parent_descriptor':
            valid = parent == 'kabupaten ' + parent_name and name == match_key(target['name'])
        elif basis == 'official_giligenting_table':
            valid = (target['code'] == '3529040' and name == 'giligenting'
                     and re.search(r'040.{0,250}Giligenting', supplemental.get('table', ''), re.S)
                     and '2023' in supplemental.get('table', '')
                     and '1102001.3529040' in supplemental.get('catalog', '')
                     and 'Giligenting' in supplemental.get('catalog', '')
                     and evidence.get('supplemental_hashes') == supplemental.get('hashes'))
        else:
            valid = False
        if not valid:
            raise ValueError('Alias is not supported by the declared evidence')
        for item in decision['scopes']:
            key = (digest(item), parent, name)
            if key in approved:
                raise ValueError('Duplicate or ambiguous alias decision')
            approved[key] = decision
    return approved


def crosswalk(rows, master, bridge_rows, decisions, boundary_set, supplemental=None):
    parents, districts, names = registry(master)
    bridge = {r['kode_bps']: r for r in bridge_rows}
    if set(bridge) != set(districts) or len(bridge) != len(bridge_rows):
        raise ValueError('Bridge is not a unique complete official code set')
    aliases = validate_decisions(decisions, parents, districts, bridge, boundary_set, supplemental or {})
    mappings, unmatched, facts, facilities = [], [], defaultdict(list), defaultdict(list)
    for row in rows:
        if row['disposition'] != 'accepted':
            raise ValueError('Only normalized detail rows may be mapped')
        fields = row['normalized_fields']
        key = tuple(fields['region_match_key'])
        candidates = names.get(key, [])
        explicit = aliases.get((digest(scope(row)), *key))
        if explicit and candidates and candidates != [explicit['target_code']]:
            raise ValueError('Alias contradicts an exact official identity')
        if explicit:
            candidates = [explicit['target_code']]
        method = explicit['basis'] if explicit else 'unique_exact_official_name_with_parent'
        if 'region_code' in fields:
            target = districts.get(fields['region_code'])
            if (not target or fields.get('code_system') != 'BPS' or fields.get('region_edition') != '2023'
                    or fields.get('parent_code') != target['parent_code']
                    or key[0] != match_key(parents[target['parent_code']]['name'])):
                candidates = []
            else:
                if explicit and explicit['target_code'] != target['code']:
                    raise ValueError('Explicit source code contradicts the reviewed alias')
                candidates = [target['code']]
                method = 'exact_official_code_with_parent_and_edition'
        result = {**scope(row), 'source_locator': row['source_locator'], 'source_row_no': row['row_no'],
                  'source_key': list(key), 'master_edition': '2023', 'target_boundary_set': boundary_set,
                  'mapping_status': 'unmatched', 'region_code': None, 'data_quality_accepted': False}
        if len(candidates) != 1:
            result['reason'] = 'ambiguous_official_name' if candidates else 'no_reviewed_mapping'
            unmatched.append(result)
        else:
            target = districts[candidates[0]]
            result.update(region_code=target['code'], parent_code=target['parent_code'], mapping_status='approved',
                          basis=method,
                          evidence={'master_hash': target['source_hash'], 'master_locator': target['locator'],
                                    'bridge_hash': bridge[target['code']]['source_hash']},
                          alias_decision_id=explicit['decision_id'] if explicit else None)
            year = fields.get('observation_year')
            result['observation_period'] = year
            result['observation_allocation_verified'] = False
            result['source_name_matches_canonical'] = key[1] == match_key(target['name'])
            result['period_note'] = 'unknown_or_mixed_period' if year != 2023 else 'source_claim_requires_quality_review'
            if 'facility_code' in fields:
                result['facility_code'] = fields['facility_code']
                facilities[fields['facility_code']].append(result)
            else:
                result['fact_disposition'] = 'pending_quality_review'
                facts[(row['dataset'], target['code'])].append(result)
        mappings.append(result)
    collisions = []
    for (dataset, code), group in facts.items():
        if len(group) > 1:
            for item in group:
                item['fact_disposition'] = 'quarantined_duplicate_target'
            collisions.append({'dataset': dataset, 'region_code': code,
                               'source_rows': [{'locator': r['source_locator'], 'key': r['source_key']} for r in group],
                               'decision': 'retain_all_rows_no_sum_no_automatic_selection'})
    facility_conflicts = []
    for code, group in facilities.items():
        targets = {r['region_code'] for r in group}
        if len(targets) != 1:
            facility_conflicts.append({'facility_code': code, 'region_codes': sorted(targets)})
            for item in group:
                item['mapping_status'] = 'conflicting_facility_assignment'
    return {'pipeline_version': VERSION, 'target_boundary_set': boundary_set, 'master_edition': '2023',
            'analysis_mode': 'mixed_period_exploration', 'data_quality_accepted': False,
            'publication_allowed': False, 'strict_temporal_alignment_verified': False,
            'master': {'regencies': list(parents.values()),
                       'districts': [{k: r[k] for k in ('code', 'parent_code', 'name', 'code_system', 'edition', 'source_hash', 'locator')}
                                     for r in districts.values()]},
            'mappings': mappings, 'unmatched': unmatched, 'many_to_one_observation_conflicts': collisions,
            'facility_conflicts': facility_conflicts,
            'summary': {'input_rows': len(rows), 'mapped_rows': sum(r['mapping_status'] == 'approved' for r in mappings),
                        'unmatched_rows': len(unmatched), 'facility_codes': len(facilities),
                        'facility_conflicts': len(facility_conflicts), 'observation_collision_groups': len(collisions),
                        'mapped_districts': len({r['region_code'] for r in mappings if r['region_code']}),
                        'unknown_or_mixed_period_rows': sum(r.get('period_note') == 'unknown_or_mixed_period' for r in mappings),
                        'methods': dict(Counter(r.get('basis', 'unmatched') for r in mappings))}}


def run(root, normalization, region_evidence, decisions, supplemental_receipts):
    root = Path(root).resolve()
    evidence = region_evidence['source_output']
    regions = json.loads(checked_bytes(local_path(root, evidence['path'], 'data/staging'), evidence))
    registry(regions['master'], 666, 38)
    normalized = normalization['outputs']['accepted']
    path = local_path(root, normalized['path'], 'data/staging')
    raw = path.read_bytes()
    import hashlib
    if hashlib.sha256(raw).hexdigest() != normalized['sha256']:
        raise ValueError('Normalized source hash mismatch')
    stage = json.loads(raw)
    if stage['batch_id'] != normalization['batch_id'] or len(stage['rows']) != normalized['rows']:
        raise ValueError('Normalized batch/count mismatch')
    historical = regions['historical_boundaries']
    boundary_set = historical['receipts']['member']['sha256']
    if {r['region_code'] for r in historical['links']} != {r['code'] for r in regions['master']['rows']}:
        raise ValueError('Historical boundary linkage differs from master')
    supplemental = {'hashes': {}}
    for receipt in supplemental_receipts:
        data = checked_bytes(local_path(root, receipt['raw_path'], 'data/raw'), receipt).decode('utf-8')
        if not receipt['source_url'].startswith('https://sumenepkab.bps.go.id/'):
            raise ValueError('Supplemental evidence is not the official Sumenep source')
        if receipt['source_id'] not in ('giligenting-2023', 'giligenting-catalog'):
            raise ValueError('Unknown supplemental evidence')
        kind = 'table' if receipt['source_id'] == 'giligenting-2023' else 'catalog'
        if kind in supplemental:
            raise ValueError('Duplicate supplemental evidence')
        supplemental[kind] = data
        supplemental['hashes'][kind] = receipt['sha256']
    result = crosswalk(stage['rows'], regions['master'], regions['bridge']['records'], decisions,
                       boundary_set, supplemental)
    result['input_identity'] = {'normalization_batch': normalization['batch_id'], 'staging_sha256': normalized['sha256'],
                                'regions_sha256': evidence['sha256'], 'decisions_sha256': digest(decisions)}
    result['content_sha256'] = digest(result)
    return result
