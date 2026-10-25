"""Complete administrative membership for regency and province aggregates."""

from decimal import Decimal, localcontext
import re

from .indicators import FORMULA_VERSION, aggregate, count, serialize


def _indexed(rows, key):
    if not isinstance(rows, list) or not rows:
        raise ValueError('A nonempty explicit master is required')
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(key), str) or not row[key] or row[key] in result:
            raise ValueError('Invalid or duplicate administrative identity')
        result[row[key]] = row
    return result


def _summarize(identities, rows, threshold):
    members = []
    coverage = {'population': 0, 'area': 0, 'coordinate_presence': 0, 'eligibility': 0}
    for identity in sorted(identities):
        source = rows[identity]['source']
        values = {'P': source['population'], 'F': source['facility_count'], 'A': source['area_km2'],
                  'coordinate_present': source['coordinate_present'], 'eligible': source['eligible']}
        members.append(values)
        for key, field in [('population', 'population'), ('area', 'area_km2'), ('coordinate_presence', 'coordinate_present'), ('eligibility', 'eligible')]:
            coverage[key] += source[field] is not None
    summary = aggregate(members, T=threshold)
    with localcontext() as context:
        context.prec = 60
        completeness = {key: {'known_districts': known, 'expected_districts': len(identities),
                              'percentage': Decimal(known) * 100 / len(identities)} for key, known in coverage.items()}
    summary.update({'district_ids': sorted(identities), 'input_coverage': completeness,
                    'completeness': 'complete' if all(known == len(identities) for known in coverage.values()) else 'partial',
                    'administrative_facility_scope': 'full_master'})
    return summary


def aggregate_regions(indicators, master):
    if not isinstance(indicators, dict) or not isinstance(master, dict):
        raise ValueError('Indicator and master documents must be objects')
    for key in ('release_id', 'boundary_hash'):
        if not isinstance(indicators.get(key), str) or not indicators[key] or indicators[key] != master.get(key):
            raise ValueError('Indicators and master must identify the same release and boundary')
    for key in ('boundary_hash', 'input_hash'):
        if not isinstance(indicators.get(key), str) or not re.fullmatch('[0-9a-f]{64}', indicators[key]):
            raise ValueError('Missing provenance hash')
    for key in ('method_version', 'code_revision'):
        if not isinstance(indicators.get(key), str) or not indicators[key].strip():
            raise ValueError('Missing implementation provenance')
    if indicators.get('formula_version') != FORMULA_VERSION:
        raise ValueError('Unsupported formula version')
    if indicators.get('filters') or master.get('filters'):
        raise ValueError('Filtered marker scopes cannot define administrative aggregates')
    parameters = indicators.get('parameters', {})
    threshold = count(parameters.get('T'), 'T', positive=True)
    if parameters.get('ratio_scale') != 30000:
        raise ValueError('The named ratio scale must remain 30000')
    districts = _indexed(master.get('districts'), 'id')
    regencies = _indexed(master.get('regencies'), 'id')
    rows = _indexed(indicators.get('districts'), 'district_id')
    if set(rows) != set(districts):
        raise ValueError('District results must exactly cover the administrative master')
    by_regency = {identity: [] for identity in regencies}
    by_province = {}
    for identity, row in districts.items():
        regency = row.get('regency_id')
        if regency not in regencies:
            raise ValueError('District references an unknown regency')
        province = regencies[regency].get('province_id')
        if not isinstance(province, str) or not province:
            raise ValueError('Regency requires a province identity')
        if rows[identity].get('release_id', indicators['release_id']) != indicators['release_id']:
            raise ValueError('Mixed release row')
        source = rows[identity].get('source')
        if not isinstance(source, dict) or not {'population', 'facility_count', 'area_km2', 'coordinate_present', 'eligible'} <= set(source):
            raise ValueError('District source values are incomplete')
        by_regency[regency].append(identity)
        by_province.setdefault(province, []).append(identity)
    if any(not identities for identities in by_regency.values()):
        raise ValueError('Every regency must have explicit district membership')
    return serialize({
        'status': 'candidate_calculation', 'release_id': indicators['release_id'],
        'boundary_hash': indicators['boundary_hash'], 'formula_version': FORMULA_VERSION,
        'method_version': indicators.get('method_version'), 'code_revision': indicators.get('code_revision'),
        'source_input_hash': indicators.get('input_hash'), 'parameters': parameters,
        'regencies': [{'regency_id': identity, 'province_id': regencies[identity]['province_id'],
                       **_summarize(members, rows, threshold)} for identity, members in sorted(by_regency.items())],
        'provinces': [{'province_id': identity, **_summarize(members, rows, threshold)}
                      for identity, members in sorted(by_province.items())],
    })
