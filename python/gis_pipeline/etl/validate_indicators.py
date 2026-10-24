"""Bind indicator decisions to inspected sources; never infer approval from totals."""

import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

from .acquire import local_path
from .indicators import convert_value
from .normalize import digest

VERSION = 'validate-indicators-1.0'


def source_key(row):
    return tuple(row[k] for k in ('dataset', 'source_id', 'source_hash', 'source_locator'))


def reconcile_total(values, printed, precision, total_precision):
    """Report a rounding envelope, not a repaired or redistributed total."""
    numbers = [Decimal(str(v)) for v in values if v is not None]
    quantum, total_quantum = Decimal(precision), Decimal(total_precision)
    if not quantum.is_finite() or not total_quantum.is_finite() or min(quantum, total_quantum) < 0:
        raise ValueError('Invalid source precision')
    subtotal = sum(numbers, Decimal(0))
    target = Decimal(str(printed))
    if not target.is_finite() or target < 0:
        raise ValueError('Invalid printed total')
    delta = subtotal - target
    tolerance = (len(numbers) * quantum + total_quantum) / 2
    complete = len(numbers) == len(values)
    status = ('incomplete' if not complete else 'exact' if delta == 0
              else 'within_rounding_envelope' if abs(delta) <= tolerance else 'unresolved_difference')
    return {'detail_sum': str(subtotal), 'printed_total': str(target), 'difference': str(delta),
            'rounding_envelope': str(tolerance), 'missing_rows': len(values) - len(numbers),
            'status': status, 'values_adjusted': False}


def validate(details, crosswalk, reviews):
    candidates = {}
    for row in details:
        if row['dataset'] not in ('population', 'area'):
            continue
        key = source_key(row)
        if row['disposition'] != 'accepted' or key in candidates:
            raise ValueError('Duplicate or non-detail indicator candidate')
        candidates[key] = row
    mappings = {}
    for mapping in crosswalk['mappings']:
        key = source_key(mapping)
        if key in mappings:
            raise ValueError('Duplicate source mapping')
        mappings[key] = mapping
    districts = {r['code']: r for r in crosswalk['master']['districts']}
    decisions, used, totals, reviewed_groups = {}, set(), [], set()
    for table in reviews['tables']:
        metric, year, unit = table['metric'], table['observation_year'], table['source_unit']
        group = (table['regency'], metric)
        if group in reviewed_groups:
            raise ValueError('Multiple selected tables for the same indicator and regency')
        reviewed_groups.add(group)
        if (type(year) is not int or not 1900 <= year <= 2100 or not table.get('year_evidence')
                or not table.get('unit_decision') or not table.get('reviewer') or not table.get('review_date')
                or not table.get('table_id') or type(table.get('pdf_page')) is not int
                or table['pdf_page'] < 1 or not table.get('rows')):
            raise ValueError('Incomplete original-source review metadata')
        if not table.get('source', {}).get('sha256') or not table['source'].get('source_id'):
            raise ValueError('Original source identity is required')
        values, region_codes = [], set()
        for reviewed in table['rows']:
            key = source_key(reviewed['candidate'])
            if key in used or key not in candidates:
                raise ValueError('Duplicate or stale reviewed candidate')
            used.add(key)
            candidate = candidates[key]
            fields, mapping = candidate['normalized_fields'], mappings.get(key)
            if (reviewed['review_status'] not in ('visually_checked', 'text_layer_compared') or not reviewed.get('row_locator')
                    or not reviewed.get('identity_review') or candidate['dataset'] != metric
                    or fields['regency'] != table['regency']
                    or fields['district'] != reviewed['candidate_district_label']):
                raise ValueError('Review is not bound to the candidate district and metric')
            if (not mapping or mapping['mapping_status'] != 'approved'
                    or mapping.get('fact_disposition') == 'quarantined_duplicate_target'
                    or mapping['region_code'] != reviewed['region_code']
                    or mapping['parent_code'] != reviewed['parent_code']
                    or mapping['region_code'] not in districts
                    or districts[mapping['region_code']]['parent_code'] != mapping['parent_code']
                    or mapping['region_code'] in region_codes):
                raise ValueError('Missing, ambiguous or duplicate reviewed region identity')
            region_codes.add(mapping['region_code'])
            value = convert_value(reviewed['raw_value'], metric, unit, table['locale'])
            if metric == 'area' and value is not None and Decimal(value) <= 0:
                raise ValueError('Statistical area must be positive')
            if value is None and not reviewed.get('missing_reason'):
                raise ValueError('Missing original value requires an explicit reason')
            values.append(value)
            original = fields['value']
            changed = ((value is None) != (original is None)
                       or (value is not None and original is not None and Decimal(str(value)) != Decimal(str(original))))
            factor = '1000' if unit == 'ribu jiwa' else '0.01' if unit in ('ha', 'hektar') else '1'
            decisions[key] = {'value': value, 'unit': 'jiwa' if metric == 'population' else 'km2',
                              'observation_year': year, 'status': 'source_checked' if value is not None else 'unavailable',
                              'missing_reason': reviewed.get('missing_reason'), 'value_changed': changed,
                              'year_changed': year != fields['observation_year'], 'review_id': table['review_id'],
                              'source': table['source'], 'source_locator': reviewed['row_locator'],
                              'raw_value': reviewed['raw_value'], 'source_unit': unit, 'factor': factor,
                              'unit_decision': table['unit_decision'], 'reviewer': table['reviewer'],
                              'review_date': table['review_date']}
        printed = convert_value(table['printed_total'], metric, unit, table['locale'])
        if printed is None:
            raise ValueError('Selected table requires a printed total')
        totals.append({'review_id': table['review_id'], 'regency': table['regency'], 'metric': metric,
                       'observation_year': year, **reconcile_total(values, printed,
                           str(Decimal(table['precision']) * Decimal(factor)),
                           str(Decimal(table['total_precision']) * Decimal(factor)))})
    observations, seen_targets = [], set()
    for key, row in sorted(candidates.items()):
        mapping = mappings.get(key)
        if (not mapping or mapping['mapping_status'] != 'approved' or mapping['region_code'] not in districts
                or mapping['parent_code'] != districts[mapping['region_code']]['parent_code']
                or mapping.get('fact_disposition') == 'quarantined_duplicate_target'):
            raise ValueError('Indicator requires an unambiguous reviewed crosswalk')
        target = (row['dataset'], mapping['region_code'])
        if target in seen_targets:
            raise ValueError('Multiple indicator observations target the same district')
        seen_targets.add(target)
        decision = decisions.get(key, {'value': None, 'unit': None, 'observation_year': None,
                                       'status': 'unavailable', 'missing_reason': 'original_source_review_pending',
                                       'value_changed': False, 'year_changed': False})
        observations.append({'metric': row['dataset'], 'region_code': mapping['region_code'],
                             'parent_code': mapping['parent_code'], 'candidate': dict(zip(
                                 ('dataset', 'source_id', 'source_hash', 'source_locator'), key)),
                             'candidate_fields': row['normalized_fields'], **decision,
                             'publication_allowed': False})
    expected_targets = {(metric, code) for metric in ('population', 'area') for code in districts}
    if seen_targets != expected_targets:
        raise ValueError('Primary indicator coverage differs from the reviewed district master')
    checklist = []
    for risk in reviews['risk_checklist']:
        matching = [t for t in reviews['tables'] if t['review_id'] == risk['review_id']
                    and t['metric'] == risk['metric'] and t['regency'] == risk['regency']]
        actual = len(matching[0]['rows']) if len(matching) == 1 else 0
        checklist.append({**risk, 'actual_rows': actual, 'checked': actual == risk['expected_rows']})
    held = []
    for row in details:
        if row['dataset'] != 'combined_historical':
            continue
        mapping = mappings.get(source_key(row))
        if mapping and mapping.get('fact_disposition') == 'quarantined_duplicate_target':
            fields = row['normalized_fields']
            held.append({'source': {k: row[k] for k in ('dataset', 'source_id', 'source_hash', 'source_locator')},
                         'district_label': fields['district'], 'region_code': mapping['region_code'],
                         'raw_population': fields.get('population'), 'raw_area': fields.get('area'),
                         'population': None, 'area': None, 'promoted': False,
                         'reason': 'Historical duplicate alias and unverified period; no merging or imputation'})
    return {'pipeline_version': VERSION, 'observations': observations, 'source_totals': totals,
            'held_historical_aliases': held, 'historical_derivative_promoted': False,
            'changes': [{'metric': row['metric'], 'region_code': row['region_code'],
                         'regency': row['candidate_fields']['regency'], 'district': row['candidate_fields']['district'],
                         'previous_value': row['candidate_fields']['value'], 'selected_value': row['value'],
                         'previous_year': row['candidate_fields']['observation_year'],
                         'selected_year': row['observation_year'], 'review_id': row['review_id'],
                         'source_locator': row['source_locator']}
                        for row in observations if row['value_changed'] or row['year_changed']],
            'risk_checklist': checklist, 'risk_review_complete': bool(checklist) and all(r['checked'] for r in checklist),
            'summary': {'observations': len(observations), 'reviewed_rows': len(decisions),
                        'source_checked': sum(d['value'] is not None for d in decisions.values()),
                        'unreviewed': len(candidates) - len(decisions),
                        'value_changes': sum(d['value_changed'] for d in decisions.values()),
                        'year_changes': sum(d['year_changed'] for d in decisions.values()),
                        'total_statuses': dict(Counter(t['status'] for t in totals))},
            'all_sources_reviewed': len(decisions) == len(candidates),
            'data_quality_accepted': False, 'publication_allowed': False}


def run(root, normalization, crosswalk_evidence, reviews):
    root = Path(root).resolve()
    evidence = normalization['outputs']['accepted']
    data = local_path(root, evidence['path'], 'data/staging').read_bytes()
    if hashlib.sha256(data).hexdigest() != evidence['sha256']:
        raise ValueError('Staging hash mismatch')
    staging = json.loads(data)
    if staging['batch_id'] != normalization['batch_id'] or len(staging['rows']) != evidence['rows']:
        raise ValueError('Staging batch or count mismatch')
    data = local_path(root, crosswalk_evidence['output_path'], 'data/processed').read_bytes()
    if hashlib.sha256(data).hexdigest() != crosswalk_evidence['output_sha256']:
        raise ValueError('Crosswalk hash mismatch')
    crosswalk = json.loads(data)
    if (crosswalk['input_identity']['normalization_batch'] != normalization['batch_id']
            or crosswalk['input_identity']['staging_sha256'] != evidence['sha256']):
        raise ValueError('Crosswalk is stale')
    for table in reviews['tables']:
        for source in [table['source'], *table.get('additional_sources', [])]:
            raw = local_path(root, source['raw_path'], 'data/raw').read_bytes()
            if hashlib.sha256(raw).hexdigest() != source['sha256'] or len(raw) != source['bytes']:
                raise ValueError('Reviewed original source hash mismatch')
        for image in [table['image'], *table.get('additional_images', [])]:
            raw = local_path(root, image['path'], 'data/staging').read_bytes()
            if hashlib.sha256(raw).hexdigest() != image['sha256']:
                raise ValueError('Reviewed page image hash mismatch')
        texts = {}
        for text in table.get('text_evidence', []):
            raw = local_path(root, text['path'], 'data/staging').read_bytes()
            if hashlib.sha256(raw).hexdigest() != text['sha256']:
                raise ValueError('Reviewed text hash mismatch')
            texts[text['pdf_page']] = raw.decode('utf-8')
        for row in table['rows']:
            if row['review_status'] == 'text_layer_compared':
                text = texts.get(row.get('pdf_page'), '')
                if not row.get('source_line') or ' '.join(row['source_line'].split()) not in ' '.join(text.split()):
                    raise ValueError('Reviewed row lacks its original text evidence')
    result = validate(staging['rows'], crosswalk, reviews)
    result['input_identity'] = {'normalization_batch': normalization['batch_id'],
                                'staging_sha256': evidence['sha256'],
                                'crosswalk_sha256': crosswalk_evidence['output_sha256'],
                                'reviews_content_sha256': digest(reviews)}
    result['content_sha256'] = digest(result)
    return result
