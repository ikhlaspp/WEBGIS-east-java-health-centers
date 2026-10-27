import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('prepare_draft_import', Path(__file__).resolve().parents[2] / 'scripts/etl/prepare_draft_import.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def candidate(dataset='coordinates_csv', longitude='112.5', latitude='-7.5'):
    return {'source': {'dataset': dataset}, 'longitude': longitude, 'latitude': latitude}


def test_missing_baseline_is_not_filled_from_an_unreviewed_workbook():
    assert module.candidate_location({'baseline_coordinate_present': False, 'coordinate_candidates': [candidate('coordinates_xlsx')]}) is None


def test_csv_baseline_keeps_geojson_order_and_ignores_other_candidates():
    result = module.candidate_location({'baseline_coordinate_present': True, 'coordinate_candidates': [candidate(), candidate('coordinates_xlsx', '113')]})
    assert result == {'type': 'Point', 'coordinates': [112.5, -7.5]}


@pytest.mark.parametrize('candidates', [[], [candidate(), candidate()], [candidate(longitude='nan')], [candidate(latitude='112.5')]])
def test_ambiguous_or_invalid_baseline_is_rejected(candidates):
    with pytest.raises(ValueError):
        module.candidate_location({'baseline_coordinate_present': True, 'coordinate_candidates': candidates})
