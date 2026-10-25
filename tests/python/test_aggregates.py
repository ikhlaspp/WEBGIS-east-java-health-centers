import copy
from decimal import Decimal

import pytest

from gis_pipeline.analysis.aggregates import aggregate_regions
from gis_pipeline.analysis.indicators import FORMULA_VERSION, calculate, serialize


def fixture():
    rows = [{'district_id': 'd1', **serialize(calculate(30000, 1, '1', coordinate_present=1, eligible=1))},
            {'district_id': 'd2', **serialize(calculate(90000, 2, '3', coordinate_present=0, eligible=0))},
            {'district_id': 'd3', **serialize(calculate(30001, 1, '2', coordinate_present=1, eligible=0))}]
    indicators = {'release_id': 'fixture', 'boundary_hash': 'b' * 64, 'formula_version': FORMULA_VERSION,
                  'method_version': 'test', 'code_revision': 'test', 'input_hash': 'a' * 64,
                  'parameters': {'T': 30000, 'ratio_scale': 30000}, 'districts': rows}
    master = {'release_id': 'fixture', 'boundary_hash': 'b' * 64,
              'regencies': [{'id': 'r1', 'province_id': 'p1'}, {'id': 'r2', 'province_id': 'p1'}],
              'districts': [{'id': 'd1', 'regency_id': 'r1'}, {'id': 'd2', 'regency_id': 'r1'}, {'id': 'd3', 'regency_id': 'r2'}]}
    return indicators, master


def test_grouped_ratios_use_count_totals_and_local_deficits():
    result = aggregate_regions(*fixture())
    regency, province = result['regencies'][0], result['provinces'][0]
    assert Decimal(regency['ratio']) == Decimal('40000')
    assert regency['sum_deficit'] == 1
    assert province['sum_deficit'] == 2
    assert province['facility_count'] == 4
    assert province['population'] == 150001
    assert Decimal(province['ratio']) == Decimal('37500.25')
    assert Decimal(province['eligible_percentage']) == Decimal('25')
    assert regency['district_ids'] == ['d1', 'd2']
    assert regency['input_coverage']['population']['known_districts'] == 2


def test_null_population_marks_whole_group_partial_with_separate_subset():
    indicators, master = fixture()
    indicators['districts'][1]['source']['population'] = None
    result = aggregate_regions(indicators, master)['regencies'][0]
    assert result['ratio'] is None
    assert result['population'] is None
    assert result['sum_deficit'] is None
    assert result['completeness'] == 'partial'
    assert result['complete_population_subset'] == {'members': 1, 'population': 30000, 'facility_count': 1}
    assert result['input_coverage']['population']['percentage'] == '50.000000000000'


def test_marker_eligibility_never_reduces_administrative_counts():
    indicators, master = fixture()
    for row in indicators['districts']:
        row['source']['coordinate_present'] = 0
        row['source']['eligible'] = 0
    result = aggregate_regions(indicators, master)['provinces'][0]
    assert result['facility_count'] == 4
    assert result['population'] == 150001
    assert result['eligible_percentage'] == '0.000000000000'


@pytest.mark.parametrize('change', ['release', 'boundary', 'duplicate', 'missing', 'extra', 'unknown_parent', 'empty_parent', 'filter', 'mixed_row', 'scale'])
def test_rejects_incomplete_or_mixed_membership(change):
    indicators, master = fixture()
    if change == 'release':
        master['release_id'] = 'other'
    elif change == 'boundary':
        master['boundary_hash'] = 'c' * 64
    elif change == 'duplicate':
        indicators['districts'].append(copy.deepcopy(indicators['districts'][0]))
    elif change == 'missing':
        indicators['districts'].pop()
    elif change == 'extra':
        indicators['districts'].append({'district_id': 'extra'})
    elif change == 'unknown_parent':
        master['districts'][0]['regency_id'] = 'unknown'
    elif change == 'empty_parent':
        master['regencies'].append({'id': 'empty', 'province_id': 'p1'})
    elif change == 'filter':
        indicators['filters'] = {'service_type': 'Rawat Inap'}
    elif change == 'mixed_row':
        indicators['districts'][0]['release_id'] = 'other'
    else:
        indicators['parameters']['ratio_scale'] = 20000
    with pytest.raises(ValueError):
        aggregate_regions(indicators, master)


def test_missing_coordinate_counts_are_not_zero_coverage():
    indicators, master = fixture()
    indicators['districts'][0]['source']['coordinate_present'] = None
    indicators['districts'][0]['source']['eligible'] = None
    result = aggregate_regions(indicators, master)['provinces'][0]
    assert result['eligible_percentage'] is None
    assert result['input_coverage']['eligibility']['known_districts'] == 2
    assert result['input_coverage']['eligibility']['expected_districts'] == 3


def test_output_is_stable_under_member_order_and_does_not_mutate_inputs():
    indicators, master = fixture()
    before = copy.deepcopy(indicators)
    expected = aggregate_regions(indicators, master)
    assert indicators == before
    indicators['districts'].reverse()
    master['districts'].reverse()
    master['regencies'].reverse()
    assert aggregate_regions(indicators, master) == expected
