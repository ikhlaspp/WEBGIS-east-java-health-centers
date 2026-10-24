import hashlib
import json
from pathlib import Path

import pytest

from gis_pipeline.etl.indicators import convert_value, parse_csv_table, parse_number, record_value, parse_workbook, save_ocr_review

FIXTURE = json.loads((Path(__file__).parents[1] / 'data/wf-058/numbers.json').read_text())


@pytest.mark.parametrize('case', FIXTURE['cases'])
def test_localized_units_against_independent_expected_values(case):
    assert FIXTURE['synthetic']
    assert convert_value(case['raw'], case['indicator'], case['unit'], case['locale']) == case['expected']


@pytest.mark.parametrize('raw,locale', [('1,234.56', 'id_ID'), ('1.23.4', 'id_ID'),
                                      ('=1+1', 'id_ID'), ('NaN', 'id_ID'),
                                      (-1, 'id_ID'), (True, 'id_ID'), (float('inf'), 'id_ID'),
                                      ('123', 'unknown')])
def test_ambiguous_invalid_negative_and_formula_values_are_rejected(raw, locale):
    with pytest.raises(ValueError):
        parse_number(raw, locale)


def test_year_cannot_be_inferred_from_a_filename():
    row = record_value('30.001', 'Synthetic district',
                       {'indicator': 'population', 'unit': 'jiwa', 'locale': 'id_ID',
                        'source_url': 'file:///source_2024.csv', 'unit_evidence': 'header'}, 'row/1')
    assert row['status'] == 'quarantined'
    assert row['value'] is None


def test_fractional_people_are_not_rounded():
    with pytest.raises(ValueError, match='whole people'):
        convert_value('0,0001', 'population', 'ribu jiwa', 'id_ID')


def test_csv_preserves_missing_zero_total_and_locator(tmp_path):
    path = tmp_path / 'synthetic.csv'
    path.write_text('district,value\nSynthetic A,0\nSynthetic B,\nTOTAL,0\n')
    manifest = {'source_id': 'synthetic', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'source_url': 'https://example.test/synthetic.csv', 'acquired_at': '2024-01-01'}
    spec = {'district_column': 'district', 'value_column': 'value', 'indicator': 'population',
            'unit': 'jiwa', 'locale': 'id_ID', 'observation_year': 2023,
            'publication_year': 2024, 'year_evidence': 'Source table: 2023', 'unit_evidence': 'jiwa'}
    parsed = parse_csv_table(path, manifest, spec)
    assert parsed['rows'][0]['value'] == 0
    assert parsed['rows'][1]['value'] is None
    assert parsed['rows'][1]['status'] == 'missing'
    assert parsed['rows'][1]['locator'] == 'csv/row/3'
    assert len(parsed['aggregates']) == 1
    assert parsed['rows'][0]['observation_year'] == 2023
    changed = parse_csv_table(path, manifest, {**spec, 'value_column': 'renamed'})
    assert changed['diagnostics'][0]['code'] == 'header_mismatch'


def test_workbook_empty_cells_and_source_footer_keep_correct_locators(tmp_path):
    from openpyxl import Workbook
    workbook = Workbook()
    notes = workbook.active
    notes.title = 'Catatan'
    notes.append(['Dalam Angka 2024; data tahun 2023'])
    sheet = workbook.create_sheet('Synthetic')
    sheet.append(['Synthetic area'])
    sheet.append(['Kecamatan', 'Luas (km2)'])
    sheet.append(['Synthetic A', None])
    sheet.append(['TOTAL', 0])
    sheet.append(['Sumber CSV BPS synthetic'])
    original = tmp_path / 'synthetic.xlsx'
    workbook.save(original)
    path = tmp_path / 'immutable-snapshot.bin'
    path.write_bytes(original.read_bytes())
    manifest = {'source_id': 'synthetic', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'source_url': 'https://example.test/synthetic.xlsx', 'acquired_at': '2024-01-01'}
    result = parse_workbook(path, manifest, 'area')
    assert len(result['rows']) == 1
    assert result['rows'][0]['status'] == 'missing'
    assert result['rows'][0]['locator'] == 'xlsx/Synthetic/B3'
    assert result['aggregates'][0]['value'] == '0'
    assert result['notes'][-1]['locator'] == 'xlsx/Synthetic/A5'


def test_ocr_keeps_low_confidence_evidence_for_review(tmp_path):
    from types import SimpleNamespace
    from PIL import Image
    page = SimpleNamespace(page_number=7,
                           to_image=lambda **kwargs: SimpleNamespace(original=Image.new('RGB', (10, 10))))
    engine = lambda image: ([[[[0, 0], [9, 0], [9, 9], [0, 9]], '1.2?4', 0.4]], [])
    path = save_ocr_review(page, {'sha256': 'a' * 64, 'source_id': 'synthetic'}, tmp_path, engine)
    evidence = json.loads(Path(path).read_text())
    assert evidence['status'] == 'requires_visual_review'
    assert evidence['tokens'][0]['text'] == '1.2?4'
    assert evidence['tokens'][0]['confidence'] == 0.4
    assert hashlib.sha256(Path(evidence['image_path']).read_bytes()).hexdigest() == evidence['image_sha256']
