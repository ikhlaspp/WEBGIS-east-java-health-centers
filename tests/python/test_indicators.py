"""Independent frozen examples plus missingness, overflow and aggregate regressions."""

import importlib.util
import json
from decimal import Decimal
from pathlib import Path

import pytest

from gis_pipeline.analysis.indicators import aggregate, calculate, display_decimal, serialize

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = json.loads((ROOT / 'docs/pekerjaan/WF-049/formula-fixtures.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('case', FIXTURES['cases'], ids=lambda case: case['id'])
def test_frozen_independent_oracles(case):
    result = calculate(**case['input'])['values']
    for key, expected in case['expected'].items():
        assert result[key] == (Decimal(expected) if isinstance(expected, str) else expected)


@pytest.mark.parametrize('values', FIXTURES['invalid_inputs'])
def test_reject_invalid_frozen_examples(values):
    with pytest.raises(ValueError):
        calculate(**values)


@pytest.mark.parametrize('field,value', [('P', True), ('P', 1.0), ('F', None), ('F', False), ('T', 1.5), ('A', 'NaN'), ('A', 'Infinity'), ('A', '-1'), ('A', 0.1), ('P', 2**63)])
def test_reject_ambiguous_and_nonfinite_inputs(field, value):
    values = {'P': 30000, 'F': 1, 'A': '2', 'T': 30000}
    values[field] = value
    with pytest.raises(ValueError):
        calculate(**values)


def test_threshold_does_not_change_fixed_30000_ratio_scale():
    result = calculate(60000, 2, '10', T=20000)
    assert result['values']['facilities_per_30000'] == Decimal('1')
    assert result['values']['need'] == 3


def test_zero_facilities_has_zero_scaled_ratio_but_null_people_per_facility():
    result = calculate(10000, 0, '2', coordinate_present=0, eligible=0)
    assert result['values']['facilities_per_30000'] == 0
    assert result['values']['ratio'] is None
    assert result['values']['eligible_percentage'] is None
    assert result['reasons']['ratio'] == 'no_facilities'


def test_coordinates_do_not_reduce_administrative_facility_count():
    result = calculate(60000, 3, '2', coordinate_present=1, eligible=0)
    assert result['values']['ratio'] == Decimal('20000')
    assert result['values']['deficit'] == 0
    assert result['values']['eligible_percentage'] == 0
    assert result['values']['coordinate_percentage'] > Decimal('33.333333')


@pytest.mark.parametrize('present,eligible', [(2, 3), (None, 0), (4, 0), (1, -1)])
def test_coordinate_partition_must_be_consistent(present, eligible):
    with pytest.raises(ValueError):
        calculate(60000, 3, '2', coordinate_present=present, eligible=eligible)


def test_storage_overflow_is_rejected():
    with pytest.raises(ValueError, match='overflows'):
        calculate(10**12, 1, '0.000001')


def test_display_rounding_never_changes_internal_value():
    value = Decimal('1.005')
    assert display_decimal(value) == '1,01'
    assert value == Decimal('1.005')
    assert serialize(value) == '1.005000000000'


def test_aggregate_uses_totals_and_sum_of_local_deficits():
    result = aggregate([{'P': 30000, 'F': 1, 'A': '1'}, {'P': 90000, 'F': 2, 'A': '2'}])
    assert result['ratio'] == Decimal('40000')
    result = aggregate([{'P': 30001, 'F': 1, 'A': '1'}, {'P': 29999, 'F': 1, 'A': '1'}])
    assert result['sum_deficit'] == 1


def test_incomplete_aggregate_never_borrows_facilities_from_missing_population():
    result = aggregate([{'P': 30000, 'F': 1, 'A': '1'}, {'P': None, 'F': 20, 'A': '2'}])
    assert result['ratio'] is None
    assert result['sum_deficit'] is None
    assert result['complete_population_subset'] == {'members': 1, 'population': 30000, 'facility_count': 1}


def test_quality_aggregate_uses_count_totals_not_mean_percentages():
    result = aggregate([{'P': 1, 'F': 1, 'A': '1', 'coordinate_present': 1, 'eligible': 1}, {'P': 2, 'F': 9, 'A': '1', 'coordinate_present': 0, 'eligible': 0}])
    assert result['eligible_percentage'] == Decimal('10')


def test_runner_preserves_provenance_and_rejects_duplicate_master_rows():
    spec = importlib.util.spec_from_file_location('indicator_cli', ROOT / 'scripts/analysis/indicators.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    document = {'release_id': 'synthetic-release', 'method_version': 'fixture', 'code_revision': 'fixture', 'boundary_hash': 'b' * 64, 'districts': [{'district_id': '3501010', 'P': 30001, 'F': 1, 'A': '2'}]}
    result = module.run(document, 'a' * 64, 30000)
    assert result['status'] == 'candidate_calculation'
    assert result['input_hash'] == 'a' * 64
    assert result['districts'][0]['values']['need'] == 2
    assert result['districts'][0]['source']['population'] == 30001
    document['districts'].append(document['districts'][0])
    with pytest.raises(ValueError, match='duplicate'):
        module.run(document, 'a' * 64, 30000)


def test_source_area_precision_is_not_silently_rounded():
    with pytest.raises(ValueError, match='precision'):
        calculate(30000, 1, '1.1234567')


def test_aggregate_counts_cannot_overflow_database_bigint():
    with pytest.raises(ValueError, match='aggregate facility count'):
        aggregate([{'P': None, 'F': 2**63-1, 'A': '1'}, {'P': None, 'F': 1, 'A': '1'}])
