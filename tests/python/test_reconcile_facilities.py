import copy
import hashlib
import json

import pytest

from gis_pipeline.etl.facilities import FIELDS
from gis_pipeline.etl.reconcile_facilities import DATASETS, reconcile, run


@pytest.fixture
def inputs():
    rows, aggregates, mappings = [], [], []

    def source(dataset, number, fields, disposition='accepted', target='3501010'):
        row = {'dataset': dataset, 'source_id': dataset, 'source_hash': 'hash-' + dataset,
               'source_locator': 'row/' + str(number), 'disposition': disposition, 'normalized_fields': fields}
        if disposition == 'accepted':
            mappings.append({'dataset': dataset, 'source_id': dataset, 'source_hash': row['source_hash'],
                             'source_locator': row['source_locator'], 'mapping_status': 'approved',
                             'region_code': target, 'parent_code': '3501',
                             **({'facility_code': fields['facility_code']} if 'facility_code' in fields else {})})
        return row

    for dataset in DATASETS:
        for number in (1, 2):
            fields = {name: 'Synthetic' for name in FIELDS[2:]}
            fields.update(facility_code=f'3501010000{number}', kemampuan_pelayanan='Rawat Inap',
                          karakteristik_wilayah='Perdesaan')
            if dataset.startswith('coordinates_'):
                present = number == 1 or dataset == 'coordinates_xlsx'
                fields.update(latitude='-7.1' if present else None, longitude='112.2' if present else None)
            rows.append(source(dataset, number, fields))
    for dataset in ('counts_historical', 'combined_historical'):
        rows.append(source(dataset, 1, {'regency': 'First', 'district': 'One', 'facility_count': 2}))
        if dataset == 'combined_historical':
            rows.append(source(dataset, 2, {'regency': 'First', 'district': 'Two', 'facility_count': 0}, target='3501020'))
        aggregates.extend([source(dataset, 3, {'regency': 'First', 'district': 'TOTAL', 'facility_count': 2}, 'aggregate'),
                           source(dataset, 4, {'regency': 'TOTAL', 'district': '', 'facility_count': 2}, 'aggregate')])
    crosswalk = {'mappings': mappings, 'master': {'districts': [{'code': c, 'parent_code': '3501'} for c in ('3501010', '3501020')],
                                                'regencies': [{'code': '3501', 'name': 'First'}]}}
    baseline = {'facilities': 2, 'regencies': 1, 'service_counts': {'Rawat Inap': 2}, 'area_counts': {'Perdesaan': 2},
                'coordinate_pairs': 1, 'missing_pairs': 1, 'unique_pairs': 1, 'duplicate_groups': 0,
                'recap_aggregate_rows': 2, 'recap_detail_rows': 1, 'sum_detail': 2, 'sum_all': 6}
    return rows, aggregates, crosswalk, baseline


def test_master_retains_missing_locations_and_empty_districts_and_excludes_totals(inputs):
    result = reconcile(*inputs)
    assert result['reconciliation_complete'] is True
    assert len(result['facilities']) == 2
    assert result['district_assignment_counts'] == {'3501010': 2, '3501020': 0}
    assert result['historical_totals']['counts_historical']['detail_sum'] == 2
    assert result['historical_totals']['counts_historical']['naive_all_rows_sum'] == 6
    assert result['historical_totals']['counts_historical']['aggregates_in_master_count'] == 0
    second = result['facilities'][1]
    assert second['baseline_coordinate_present'] is False
    assert len(second['coordinate_candidates']) == 1
    assert second['location_verified'] is second['public_eligible'] is False
    assert result['summary']['coordinate_counts']['baseline_missing'] == 1


@pytest.mark.parametrize('damage', ['duplicate', 'missing', 'unmapped', 'aggregate_in_details', 'subtotal', 'category'])
def test_identity_or_total_damage_cannot_pass(inputs, damage):
    rows, aggregates, crosswalk, baseline = inputs
    if damage == 'duplicate':
        rows.append(copy.deepcopy(rows[0]))
    elif damage == 'missing':
        rows.pop(0)
    elif damage == 'unmapped':
        crosswalk['mappings'][0]['mapping_status'] = 'unmatched'
    elif damage == 'aggregate_in_details':
        rows[0]['disposition'] = 'aggregate'
    elif damage == 'subtotal':
        aggregates[0]['normalized_fields']['facility_count'] = 3
    else:
        baseline['service_counts'] = {'Non Rawat Inap': 2}
    with pytest.raises(ValueError):
        reconcile(*inputs)


def test_attribute_difference_requires_review_and_does_not_overwrite_official(inputs):
    rows, _, _, _ = inputs
    rows[2]['normalized_fields']['nama_puskesmas'] = 'Different source name'
    result = reconcile(*inputs)
    assert result['reconciliation_complete'] is False
    assert result['attribute_differences'][0]['field'] == 'nama_puskesmas'
    assert result['facilities'][0]['attributes']['nama_puskesmas'] == 'Synthetic'


def test_shared_coordinates_do_not_merge_facility_identities(inputs):
    rows, _, _, baseline = inputs
    for row in rows:
        if row['dataset'] == 'coordinates_csv':
            row['normalized_fields'].update(latitude='-7.1', longitude='112.2')
    baseline.update(coordinate_pairs=2, missing_pairs=0, unique_pairs=1, duplicate_groups=1)
    result = reconcile(*inputs)
    assert len(result['facilities']) == 2
    assert result['summary']['coordinate_counts']['baseline_duplicate_groups'] == 1
    assert result['summary']['coordinate_counts']['verified'] == 0


def test_duplicate_alias_counts_are_held_instead_of_promoted(inputs):
    rows, _, crosswalk, _ = inputs
    combined = [r for r in rows if r['dataset'] == 'combined_historical']
    combined[1]['normalized_fields']['district'] = 'Old Name'
    for mapping in crosswalk['mappings']:
        if mapping['dataset'] == 'combined_historical':
            mapping['region_code'] = '3501010'
            mapping['fact_disposition'] = 'quarantined_duplicate_target'
    result = reconcile(*inputs)
    assert len(result['count_differences']) == 2
    assert all(d['decision'] == 'duplicate_alias_observation_held_no_merge' for d in result['count_differences'])
    assert result['data_quality_accepted'] is False


def test_repeat_and_hash_protection(tmp_path, inputs):
    rows, aggregates, crosswalk, baseline = inputs
    normalization = {'batch_id': 'batch', 'outputs': {}}
    for disposition, items in [('accepted', rows), ('aggregate', aggregates), ('quarantined', [])]:
        path = tmp_path / 'data/staging' / (disposition + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps({'batch_id': 'batch', 'rows': items}).encode()
        path.write_bytes(data)
        normalization['outputs'][disposition] = {'path': path.relative_to(tmp_path).as_posix(),
                                                  'sha256': hashlib.sha256(data).hexdigest(), 'rows': len(items)}
    crosswalk['input_identity'] = {'normalization_batch': 'batch',
                                   'staging_sha256': normalization['outputs']['accepted']['sha256']}
    path = tmp_path / 'data/processed/crosswalk.json'
    path.parent.mkdir(parents=True)
    data = json.dumps(crosswalk).encode()
    path.write_bytes(data)
    evidence = {'output_path': path.relative_to(tmp_path).as_posix(), 'output_sha256': hashlib.sha256(data).hexdigest()}
    first = run(tmp_path, normalization, evidence, baseline)
    assert first == run(tmp_path, normalization, evidence, baseline)
    path.write_bytes(b'changed')
    with pytest.raises(ValueError, match='Crosswalk hash mismatch'):
        run(tmp_path, normalization, evidence, baseline)
