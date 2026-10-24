import copy
import hashlib
import json

import pytest

from gis_pipeline.etl.validate_indicators import reconcile_total, run, validate


@pytest.fixture
def inputs():
    details, mappings, tables = [], [], []
    for metric, values in [('population', [1200, 3400]), ('area', ['128.39', '143.09'])]:
        reviewed = []
        for index, value in enumerate(values):
            identity = {'dataset': metric, 'source_id': metric, 'source_hash': 'candidate-hash',
                        'source_locator': f'row/{index}'}
            fields = {'regency': 'Example', 'district': str(index), 'value': value,
                      'observation_year': 2025}
            details.append({**identity, 'disposition': 'accepted', 'normalized_fields': fields})
            mappings.append({**identity, 'mapping_status': 'approved', 'region_code': str(index), 'parent_code': 'parent'})
            reviewed.append({'candidate': identity, 'region_code': str(index), 'parent_code': 'parent',
                             'district_label': str(index), 'candidate_district_label': str(index),
                             'identity_review': 'Same source district', 'row_locator': f'pdf/1/row/{index}',
                             'review_status': 'visually_checked',
                             'raw_value': str(value) if metric == 'population' else ['143.09', '128.39'][index]})
        tables.append({'review_id': metric, 'regency': 'Example', 'metric': metric, 'observation_year': 2023,
                       'year_evidence': 'Explicit table title', 'source_unit': 'jiwa' if metric == 'population' else 'km2',
                       'locale': 'en_US', 'unit_decision': 'Explicit original table header', 'reviewer': 'Technical review',
                       'review_date': '2026-10-25', 'pdf_page': 1, 'table_id': '1',
                       'source': {'source_id': 'original', 'sha256': 'original-hash'}, 'rows': reviewed,
                       'printed_total': '4600' if metric == 'population' else '271.48',
                       'precision': '0' if metric == 'population' else '0.01',
                       'total_precision': '0' if metric == 'population' else '0.01'})
    return details, {'mappings': mappings, 'master': {'districts': [
        {'code': str(i), 'parent_code': 'parent'} for i in range(2)]}}, {
        'tables': tables, 'risk_checklist': [{'regency': 'Example', 'metric': t['metric'],
                                            'review_id': t['review_id'], 'expected_rows': 2} for t in tables]}


def test_matching_total_does_not_hide_swapped_district_values(inputs):
    result = validate(*inputs)
    areas = [r for r in result['observations'] if r['metric'] == 'area']
    assert [r['value'] for r in areas] == ['143.09', '128.39']
    assert [r['candidate_fields']['value'] for r in areas] == ['128.39', '143.09']
    assert result['summary']['value_changes'] == 2
    assert result['summary']['year_changes'] == 4
    assert all(t['status'] == 'exact' for t in result['source_totals'])
    assert result['all_sources_reviewed'] is True
    assert result['publication_allowed'] is False


def test_unreviewed_is_null_not_zero_or_automatic_workbook_approval(inputs):
    inputs[2]['tables'].pop()
    result = validate(*inputs)
    assert result['all_sources_reviewed'] is False
    assert result['risk_review_complete'] is False
    areas = [r for r in result['observations'] if r['metric'] == 'area']
    assert all(r['value'] is None and r['missing_reason'] == 'original_source_review_pending' for r in areas)


def test_explicit_thousands_and_hectares_convert_totals_and_precision_once(inputs):
    population, area = inputs[2]['tables']
    population.update(source_unit='ribu jiwa', printed_total='4.60', precision='0.01', total_precision='0.01')
    population['rows'][0]['raw_value'] = '1.20'
    population['rows'][1]['raw_value'] = '3.40'
    area.update(source_unit='ha', printed_total='27148', precision='1', total_precision='1')
    area['rows'][0]['raw_value'] = '14309'
    area['rows'][1]['raw_value'] = '12839'
    result = validate(*inputs)
    assert [r['value'] for r in result['observations']] == ['143.09', '128.39', 1200, 3400]
    assert [t['status'] for t in result['source_totals']] == ['exact', 'exact']
    assert result['source_totals'][0]['rounding_envelope'] == '15.00'


@pytest.mark.parametrize('damage', ['duplicate_review', 'stale_source', 'wrong_district', 'wrong_parent',
                                   'duplicate_target', 'unknown_unit', 'missing_year', 'zero_area', 'negative', 'nan'])
def test_unsafe_reviews_fail_closed(inputs, damage):
    rows, crosswalk, reviews = inputs
    table = reviews['tables'][1]
    row = table['rows'][0]
    if damage == 'duplicate_review':
        table['rows'].append(copy.deepcopy(row))
    elif damage == 'stale_source':
        row['candidate']['source_hash'] = 'changed'
    elif damage == 'wrong_district':
        row['candidate_district_label'] = 'Other'
    elif damage == 'wrong_parent':
        row['parent_code'] = 'other'
    elif damage == 'duplicate_target':
        crosswalk['mappings'][2]['fact_disposition'] = 'quarantined_duplicate_target'
    elif damage == 'unknown_unit':
        table['source_unit'] = 'unknown'
    elif damage == 'missing_year':
        table['observation_year'] = None
    else:
        row['raw_value'] = {'zero_area': '0', 'negative': '-1', 'nan': 'NaN'}[damage]
    with pytest.raises(ValueError):
        validate(rows, crosswalk, reviews)


def test_missing_original_is_retained_and_not_used_to_reconcile_total(inputs):
    row = inputs[2]['tables'][0]['rows'][0]
    row.update(raw_value=None, missing_reason='Not published in source')
    result = validate(*inputs)
    population = [r for r in result['observations'] if r['metric'] == 'population']
    assert population[0]['value'] is None
    assert result['source_totals'][0]['status'] == 'incomplete'


def test_precision_reports_discrepancies_without_adjustment():
    exact_counts = reconcile_total([50, 51], 100, '0', '0')
    assert exact_counts['status'] == 'unresolved_difference'
    rounded = reconcile_total(['12.75', '13.62', '10.98', '8.66', '10.65'], '56.67', '0.01', '0.01')
    assert rounded['difference'] == '-0.01'
    assert rounded['status'] == 'within_rounding_envelope'
    assert rounded['values_adjusted'] is False


def test_historical_sempol_null_and_ijen_duplicate_are_never_promoted(inputs):
    rows, crosswalk, reviews = inputs
    for index, label, population, area in [(10, 'Ijen', 12277, '207.2'), (11, 'Sempol', None, None)]:
        identity = {'dataset': 'combined_historical', 'source_id': 'historical', 'source_hash': 'old',
                    'source_locator': f'row/{index}'}
        rows.append({**identity, 'disposition': 'accepted', 'normalized_fields': {
            'district': label, 'population': population, 'area': area, 'observation_year': None}})
        crosswalk['mappings'].append({**identity, 'mapping_status': 'approved', 'region_code': '0',
                                     'parent_code': 'parent', 'fact_disposition': 'quarantined_duplicate_target'})
    result = validate(*inputs)
    assert len(result['observations']) == 4
    assert len(result['held_historical_aliases']) == 2
    assert all(r['population'] is None and r['area'] is None and not r['promoted']
               for r in result['held_historical_aliases'])
    assert result['held_historical_aliases'][1]['raw_population'] is None


@pytest.fixture
def files(tmp_path, inputs):
    rows, crosswalk, reviews = inputs

    def save(path, value):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(json.dumps(value).encode())
        return hashlib.sha256(target.read_bytes()).hexdigest()

    staging_path = 'data/staging/candidates.json'
    staging_sha = save(staging_path, {'batch_id': 'batch', 'rows': rows})
    normalization = {'batch_id': 'batch', 'outputs': {'accepted': {
        'path': staging_path, 'sha256': staging_sha, 'rows': len(rows)}}}
    crosswalk['input_identity'] = {'normalization_batch': 'batch', 'staging_sha256': staging_sha}
    crosswalk_path = 'data/processed/crosswalk.json'
    evidence = {'output_path': crosswalk_path, 'output_sha256': save(crosswalk_path, crosswalk)}
    source_path, image_path = 'data/raw/original.bin', 'data/staging/page.png'
    source_sha = save(source_path, 'original source bytes')
    image_sha = save(image_path, 'reviewed page image')
    for table in reviews['tables']:
        table['source'].update(raw_path=source_path, sha256=source_sha, bytes=(tmp_path / source_path).stat().st_size)
        table['image'] = {'path': image_path, 'sha256': image_sha}
    return tmp_path, normalization, evidence, reviews


def test_repeat_run_is_deterministic_and_bound_to_inputs(files):
    first, second = run(*files), run(*files)
    assert first == second
    assert first['all_sources_reviewed'] is True
    assert first['input_identity']['normalization_batch'] == 'batch'


@pytest.mark.parametrize('path', ['data/staging/candidates.json', 'data/processed/crosswalk.json',
                                 'data/raw/original.bin', 'data/staging/page.png'])
def test_changed_evidence_is_rejected(files, path):
    (files[0] / path).write_bytes(b'changed')
    with pytest.raises(ValueError, match='hash mismatch'):
        run(*files)


def test_text_review_requires_hash_verified_original_line(files):
    root, _, _, reviews = files
    table = reviews['tables'][0]
    table['rows'][0].update(review_status='text_layer_compared', pdf_page=1, source_line='Missing source line')
    text = root / 'data/staging/page.txt'
    text.write_text('Different text', encoding='utf-8')
    table['text_evidence'] = [{'path': 'data/staging/page.txt', 'pdf_page': 1,
                               'sha256': hashlib.sha256(text.read_bytes()).hexdigest()}]
    with pytest.raises(ValueError, match='original text evidence'):
        run(*files)
