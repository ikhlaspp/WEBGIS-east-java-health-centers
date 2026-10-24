import copy

import pytest

from gis_pipeline.etl.crosswalk import crosswalk, registry, scope


@pytest.fixture
def sources():
    master = {'report': {'complete': True},
              'regencies': [{'code': '3501', 'name': 'First', 'expected_districts': 2},
                            {'code': '3502', 'name': 'Second', 'expected_districts': 1}],
              'rows': [{'code': code, 'parent_code': parent, 'name': name, 'code_system': 'BPS',
                        'edition': '2023', 'source_hash': 'master-hash', 'locator': 'pdf/' + code}
                       for code, parent, name in [('3501010', '3501', 'Same'), ('3501020', '3501', 'New Name'),
                                                  ('3502010', '3502', 'Same')]]}
    bridge = [{'kode_bps': r['code'], 'nama_bps': r['name'],
               'nama_dagri': 'Old Name' if r['code'] == '3501020' else r['name'],
               'source_hash': 'bridge-hash', 'period': '2023_1.2022'} for r in master['rows']]
    return master, bridge


def row(name='same', parent='first', number=1, **fields):
    return {'dataset': 'population', 'source_id': 'source', 'source_hash': 'input-hash',
            'source_edition': 'archive-baseline', 'source_locator': f'csv/row/{number}',
            'row_no': number, 'disposition': 'accepted',
            'normalized_fields': {'region_match_key': [parent, name], 'observation_year': 2023, **fields}}


def decision(source):
    return {'decision_id': 'alias-1', 'status': 'approved', 'source_key': ['first', 'old name'],
            'target_code': '3501020', 'parent_code': '3501', 'master_edition': '2023',
            'target_boundary_set': 'boundary-hash', 'reviewer': 'Technical test review', 'reviewed_at': '2026-10-24',
            'basis': 'official_bridge_name', 'scopes': [scope(source)],
            'evidence': {'master_hash': 'master-hash', 'master_locator': 'pdf/3501020', 'bridge_hash': 'bridge-hash'}}


def test_identical_names_in_different_parents_never_merge(sources):
    result = crosswalk([row(), row(parent='second', number=2)], *sources, [], 'boundary-hash')
    assert [r['region_code'] for r in result['mappings']] == ['3501010', '3502010']
    assert result['many_to_one_observation_conflicts'] == []


def test_reviewed_rename_retains_both_observations_without_sum(sources):
    old = row('old name')
    current = row('new name', number=2)
    result = crosswalk([old, current], *sources, [decision(old)], 'boundary-hash')
    assert result['summary']['mapped_rows'] == 2
    assert result['summary']['observation_collision_groups'] == 1
    assert all(r['fact_disposition'] == 'quarantined_duplicate_target' for r in result['mappings'])
    assert old['normalized_fields']['region_match_key'] == ['first', 'old name']
    assert all(not r['observation_allocation_verified'] for r in result['mappings'])


@pytest.mark.parametrize('mutation', ['pending', 'hash', 'edition', 'dataset', 'period'])
def test_alias_only_applies_to_reviewed_source_scope(sources, mutation):
    old = row('old name')
    approved = decision(old)
    if mutation == 'pending':
        approved['status'] = 'pending'
    elif mutation == 'period':
        old['normalized_fields']['observation_year'] = 2019
    else:
        old[{'hash': 'source_hash', 'edition': 'source_edition', 'dataset': 'dataset'}[mutation]] = 'changed'
    result = crosswalk([old], *sources, [approved], 'boundary-hash')
    assert result['summary']['unmatched_rows'] == 1


@pytest.mark.parametrize('mutation', ['parent', 'boundary', 'proof', 'duplicate'])
def test_invalid_or_ambiguous_alias_evidence_fails(sources, mutation):
    old = row('old name')
    approved = decision(old)
    decisions = [approved]
    if mutation == 'parent':
        approved['parent_code'] = '3502'
    elif mutation == 'boundary':
        approved['target_boundary_set'] = 'different'
    elif mutation == 'proof':
        approved['evidence']['bridge_hash'] = 'different'
    else:
        decisions.append(copy.deepcopy(approved))
    with pytest.raises(ValueError):
        crosswalk([old], *sources, decisions, 'boundary-hash')


def test_similar_names_are_not_fuzzy_approved_or_sliced_from_facility_code(sources):
    result = crosswalk([row('sme', facility_code='35010100001')], *sources, [], 'boundary-hash')
    assert result['summary']['unmatched_rows'] == 1
    assert result['mappings'][0]['region_code'] is None


def test_official_code_requires_matching_parent_and_edition(sources):
    source = row('different spelling', region_code='3501010', parent_code='3501', code_system='BPS', region_edition='2023')
    result = crosswalk([source], *sources, [], 'boundary-hash')
    assert result['mappings'][0]['region_code'] == '3501010'
    source['normalized_fields']['region_edition'] = '2019'
    assert crosswalk([source], *sources, [], 'boundary-hash')['summary']['unmatched_rows'] == 1


def test_conflicting_facility_assignments_are_not_publishable(sources):
    result = crosswalk([row(facility_code='00123456789'), row(parent='second', number=2, facility_code='00123456789')],
                       *sources, [], 'boundary-hash')
    assert result['facility_conflicts'] == [{'facility_code': '00123456789', 'region_codes': ['3501010', '3502010']}]
    assert all(r['mapping_status'] == 'conflicting_facility_assignment' for r in result['mappings'])


def test_duplicate_official_code_and_wrong_parent_fail(sources):
    master, _ = sources
    master['rows'].append(copy.deepcopy(master['rows'][0]))
    with pytest.raises(ValueError):
        registry(master)
    master['rows'].pop()
    master['rows'][0]['parent_code'] = '3502'
    with pytest.raises(ValueError):
        registry(master)


def test_repeat_is_deterministic_and_does_not_mutate_sources(sources):
    rows = [row(), row('new name', number=2)]
    before = copy.deepcopy((rows, sources))
    first = crosswalk(rows, *sources, [], 'boundary-hash')
    assert first == crosswalk(rows, *sources, [], 'boundary-hash')
    assert (rows, sources) == before


def test_supplemental_alias_requires_bound_code_and_both_source_hashes():
    source = row('giligenting', 'sumenep')
    master = {'report': {'complete': True},
              'regencies': [{'code': '3529', 'name': 'Sumenep', 'expected_districts': 1}],
              'rows': [{'code': '3529040', 'parent_code': '3529', 'name': 'Giligenteng',
                        'code_system': 'BPS', 'edition': '2023', 'source_hash': 'master-hash', 'locator': 'pdf/3529040'}]}
    bridge = [{'kode_bps': '3529040', 'nama_bps': 'Giligenteng', 'nama_dagri': 'Giliginting',
               'source_hash': 'bridge-hash', 'period': '2023_1.2022'}]
    approved = decision(source)
    approved.update(source_key=['sumenep', 'giligenting'], target_code='3529040', parent_code='3529',
                    basis='official_giligenting_table')
    approved['evidence'].update(master_locator='pdf/3529040', supplemental_hashes={'table': 't', 'catalog': 'c'})
    supplemental = {'table': '2023: 040 Giligenting', 'catalog': '1102001.3529040 Giligenting',
                    'hashes': {'table': 't', 'catalog': 'c'}}
    assert crosswalk([source], master, bridge, [approved], 'boundary-hash', supplemental)['summary']['mapped_rows'] == 1
    supplemental['hashes']['table'] = 'changed'
    with pytest.raises(ValueError):
        crosswalk([source], master, bridge, [approved], 'boundary-hash', supplemental)
