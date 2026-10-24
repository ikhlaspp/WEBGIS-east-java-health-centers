"""Reconcile facility identities and totals without promoting location candidates."""

import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from .acquire import local_path
from .facilities import FIELDS
from .normalize import digest, match_key

VERSION = 'reconcile-facilities-1.0'
DATASETS = ('facilities_official', 'facilities_archive', 'facilities_csv', 'facilities_xlsx',
            'coordinates_csv', 'coordinates_xlsx')


def reference(row):
    return {k: row[k] for k in ('dataset', 'source_id', 'source_hash', 'source_locator')}


def pair(row):
    fields = row['normalized_fields']
    values = tuple(fields.get(k) for k in ('latitude', 'longitude'))
    if (values[0] is None) != (values[1] is None):
        raise ValueError('Incomplete candidate coordinate pair')
    return None if values[0] is None else tuple(Decimal(v) for v in values)


def reconcile(details, aggregates, crosswalk, baseline):
    tables = {name: {} for name in DATASETS}
    mappings = {}
    for mapping in crosswalk['mappings']:
        key = (mapping['dataset'], mapping['source_locator'], mapping['source_hash'])
        if key in mappings:
            raise ValueError('Duplicate crosswalk source row')
        mappings[key] = mapping
    districts = {r['code']: r for r in crosswalk['master']['districts']}
    parents = {r['code']: r for r in crosswalk['master']['regencies']}
    for row in details:
        if row['disposition'] != 'accepted':
            raise ValueError('Aggregate or quarantine cannot enter facility detail counts')
        dataset = row['dataset']
        if dataset not in tables:
            continue
        code = row['normalized_fields']['facility_code']
        if not isinstance(code, str) or len(code) != 11 or not code.isascii() or not code.isdigit():
            raise ValueError('Invalid facility code')
        if code in tables[dataset]:
            raise ValueError('Duplicate facility code within source')
        mapping = mappings.get((dataset, row['source_locator'], row['source_hash']))
        if (not mapping or mapping['mapping_status'] != 'approved' or mapping.get('facility_code') != code
                or mapping['region_code'] not in districts or mapping['source_id'] != row['source_id']
                or mapping['parent_code'] != districts[mapping['region_code']]['parent_code']):
            raise ValueError('Facility lacks a valid reviewed region mapping')
        tables[dataset][code] = row
    primary = tables['facilities_official']
    if len(primary) != baseline['facilities']:
        raise ValueError('Primary facility count differs from independent baseline')
    for dataset, rows in tables.items():
        if set(rows) != set(primary):
            raise ValueError('Facility code set mismatch: ' + dataset)

    def mapping_for(row):
        return mappings[(row['dataset'], row['source_locator'], row['source_hash'])]

    differences, formatting, coordinate_differences, output = [], [], [], []
    district_counts, parent_counts = Counter(), Counter()
    for code, official in sorted(primary.items()):
        mapping = mapping_for(official)
        district_counts[mapping['region_code']] += 1
        parent_counts[mapping['parent_code']] += 1
        for dataset in DATASETS[1:]:
            other = tables[dataset][code]
            if mapping_for(other)['region_code'] != mapping['region_code']:
                raise ValueError('Source copies disagree on facility district')
            for field in FIELDS[2:]:
                before, after = official['normalized_fields'][field], other['normalized_fields'][field]
                if before != after:
                    record = {'facility_code': code, 'dataset': dataset, 'field': field,
                              'official': reference(official), 'comparison': reference(other)}
                    if ' '.join(before.split()) == ' '.join(after.split()):
                        formatting.append({**record, 'decision': 'whitespace_only_preserve_originals'})
                    else:
                        differences.append({**record, 'official_value': before, 'comparison_value': after,
                                            'decision': 'retain_official_pending_explicit_review'})
        csv_row, xlsx_row = tables['coordinates_csv'][code], tables['coordinates_xlsx'][code]
        csv_pair, xlsx_pair = pair(csv_row), pair(xlsx_row)
        if csv_pair != xlsx_pair:
            coordinate_differences.append({'facility_code': code, 'csv': reference(csv_row), 'xlsx': reference(xlsx_row),
                                           'csv_present': csv_pair is not None, 'xlsx_present': xlsx_pair is not None,
                                           'decision': 'retain_both_candidates_no_automatic_replacement_or_verification'})
        candidates = [{'latitude': str(value[0]), 'longitude': str(value[1]), 'source': reference(row),
                       'status': 'candidate_unverified'}
                      for row, value in [(csv_row, csv_pair), (xlsx_row, xlsx_pair)] if value is not None]
        output.append({'facility_code': code, 'region_code': mapping['region_code'], 'parent_code': mapping['parent_code'],
                       'attributes': official['normalized_fields'], 'sources': [reference(tables[d][code]) for d in DATASETS],
                       'baseline_coordinate_present': csv_pair is not None, 'coordinate_candidates': candidates,
                       'location_verified': False, 'public_eligible': False})
    service = dict(Counter(r['normalized_fields']['kemampuan_pelayanan'] for r in primary.values()))
    area = dict(Counter(r['normalized_fields']['karakteristik_wilayah'] for r in primary.values()))
    if service != baseline['service_counts'] or area != baseline['area_counts'] or len(parent_counts) != baseline['regencies']:
        raise ValueError('Facility categories or parent coverage differ from independent baseline')
    csv_pairs = Counter(pair(r) for r in tables['coordinates_csv'].values() if pair(r) is not None)
    coordinate_counts = {'baseline_pairs': sum(csv_pairs.values()), 'baseline_missing': len(primary) - sum(csv_pairs.values()),
                         'baseline_unique_pairs': len(csv_pairs), 'baseline_duplicate_groups': sum(v > 1 for v in csv_pairs.values()),
                         'xlsx_pairs': sum(pair(r) is not None for r in tables['coordinates_xlsx'].values()),
                         'without_any_candidate': sum(not r['coordinate_candidates'] for r in output), 'verified': 0}
    for actual, expected in [('baseline_pairs', 'coordinate_pairs'), ('baseline_missing', 'missing_pairs'),
                             ('baseline_unique_pairs', 'unique_pairs'), ('baseline_duplicate_groups', 'duplicate_groups')]:
        if coordinate_counts[actual] != baseline[expected]:
            raise ValueError('Coordinate baseline mismatch: ' + actual)

    total_reports, count_differences = {}, []
    for dataset in ('counts_historical', 'combined_historical'):
        source_details = [r for r in details if r['dataset'] == dataset]
        source_aggregates = [r for r in aggregates if r['dataset'] == dataset]
        if len(source_aggregates) != baseline['recap_aggregate_rows']:
            raise ValueError('Expected separate parent and province aggregates')
        detail_sum = 0
        parent_keys = defaultdict(set)
        for row in source_details:
            fields = row['normalized_fields']
            value = fields['facility_count']
            if type(value) is not int or value < 0:
                raise ValueError('Invalid historical facility count')
            detail_sum += value  # Arithmetic check only; never creates a merged observation.
            mapping = mapping_for(row)
            if mapping['mapping_status'] != 'approved':
                raise ValueError('Unmapped historical detail')
            parent_keys[match_key(fields['regency'])].add(mapping['parent_code'])
            if mapping.get('fact_disposition') == 'quarantined_duplicate_target':
                count_differences.append({'dataset': dataset, 'source': reference(row), 'region_code': mapping['region_code'],
                                          'source_count': value, 'derived_official_count': district_counts[mapping['region_code']],
                                          'decision': 'duplicate_alias_observation_held_no_merge'})
            elif value != district_counts[mapping['region_code']]:
                count_differences.append({'dataset': dataset, 'source': reference(row), 'region_code': mapping['region_code'],
                                          'source_count': value, 'derived_official_count': district_counts[mapping['region_code']],
                                          'decision': 'unresolved_count_difference'})
        seen, province_totals, subtotal_sum = set(), [], 0
        for row in source_aggregates:
            if row['disposition'] != 'aggregate':
                raise ValueError('Historical subtotal is not classified as aggregate')
            fields = row['normalized_fields']
            parent_name = match_key(fields['regency'])
            value = fields['facility_count']
            if type(value) is not int or value < 0:
                raise ValueError('Invalid aggregate count')
            if parent_name in ('total', 'jawa timur'):
                province_totals.append(value)
                continue
            codes = parent_keys[parent_name]
            if len(codes) != 1:
                raise ValueError('Aggregate parent is missing or ambiguous')
            parent, = codes
            if parent in seen or value != parent_counts[parent]:
                raise ValueError('Duplicate or mismatching parent subtotal')
            seen.add(parent)
            subtotal_sum += value
        if seen != set(parents) or province_totals != [baseline['facilities']] or detail_sum != baseline['sum_detail']:
            raise ValueError('Historical totals do not reconcile')
        total_reports[dataset] = {'detail_rows': len(source_details), 'aggregate_rows': len(source_aggregates),
                                  'detail_sum': detail_sum, 'parent_subtotal_sum': subtotal_sum,
                                  'province_total': province_totals[0], 'naive_all_rows_sum': detail_sum + subtotal_sum + province_totals[0],
                                  'aggregates_in_master_count': 0}
    if (total_reports['counts_historical']['detail_rows'] != baseline['recap_detail_rows']
            or total_reports['counts_historical']['naive_all_rows_sum'] != baseline['sum_all']):
        raise ValueError('Historical recap differs from baseline')
    return {'pipeline_version': VERSION, 'facilities': output, 'region_master': crosswalk['master'],
            'summary': {'facilities': len(output), 'regencies': len(parent_counts), 'districts': len(districts),
                        'districts_with_assignments': len(district_counts), 'service_counts': service, 'area_counts': area,
                        'coordinate_counts': coordinate_counts, 'substantive_attribute_differences': len(differences),
                        'formatting_differences': len(formatting), 'coordinate_differences': len(coordinate_differences)},
            'attribute_differences': differences, 'formatting_differences': formatting,
            'coordinate_differences': coordinate_differences, 'count_differences': count_differences,
            'historical_totals': total_reports,
            'district_assignment_counts': {code: district_counts[code] for code in sorted(districts)},
            'reconciliation_complete': not differences and not any(d['decision'] == 'unresolved_count_difference' for d in count_differences),
            'data_quality_accepted': False, 'publication_allowed': False}


def run(root, normalization, crosswalk_evidence, baseline):
    root = Path(root).resolve()
    groups = {}
    for disposition, evidence in normalization['outputs'].items():
        data = local_path(root, evidence['path'], 'data/staging').read_bytes()
        if hashlib.sha256(data).hexdigest() != evidence['sha256']:
            raise ValueError('Staging hash mismatch')
        parsed = json.loads(data)
        if (parsed['batch_id'] != normalization['batch_id'] or len(parsed['rows']) != evidence['rows']
                or any(r['disposition'] != disposition for r in parsed['rows'])):
            raise ValueError('Staging count, batch or disposition mismatch')
        groups[disposition] = parsed['rows']
    if groups['quarantined']:
        raise ValueError('Resolve source quarantine before reconciling the full master')
    data = local_path(root, crosswalk_evidence['output_path'], 'data/processed').read_bytes()
    if hashlib.sha256(data).hexdigest() != crosswalk_evidence['output_sha256']:
        raise ValueError('Crosswalk hash mismatch')
    crosswalk = json.loads(data)
    if (crosswalk['input_identity']['normalization_batch'] != normalization['batch_id']
            or crosswalk['input_identity']['staging_sha256'] != normalization['outputs']['accepted']['sha256']):
        raise ValueError('Crosswalk is stale for this normalization batch')
    result = reconcile(groups['accepted'], groups['aggregate'], crosswalk, baseline)
    result['input_identity'] = {'normalization_batch': normalization['batch_id'],
                                'crosswalk_sha256': crosswalk_evidence['output_sha256'], 'baseline_content_sha256': digest(baseline)}
    result['content_sha256'] = digest(result)
    return result
