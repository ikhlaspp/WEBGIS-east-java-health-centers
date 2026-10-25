"""District indicators: exact counts, Decimal arithmetic, explicit missingness."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext

FORMULA_VERSION = 'district-indicators-v1'
BIGINT_MAX = 9223372036854775807
STORAGE_STEP = Decimal('0.000000000001')
STORAGE_MAX = Decimal('999999999999.999999999999')


def count(value, name, nullable=False, positive=False):
    if value is None and nullable:
        return None
    if type(value) is not int or not (1 if positive else 0) <= value <= BIGINT_MAX:
        raise ValueError(f'{name} must be a bounded nonnegative integer')
    return value


def area(value):
    if value is None:
        return None
    if isinstance(value, (float, bool)) or not isinstance(value, (str, int, Decimal)):
        raise ValueError('A requires an exact decimal string, integer or Decimal')
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError('Invalid A') from error
    if not result.is_finite() or result <= 0:
        raise ValueError('A must be finite and positive')
    if result > Decimal('9999999999.999999') or result < Decimal('0.000001'):
        raise ValueError('A is outside numeric(16,6) storage range')
    if result != result.quantize(Decimal('0.000001')):
        raise ValueError('A would lose source precision in numeric(16,6) storage')
    return result


def stored_decimal(value):
    if value is None:
        return None
    with localcontext() as context:
        context.prec = 60
        rounded = value.quantize(STORAGE_STEP, rounding=ROUND_HALF_UP)
    if not rounded.is_finite() or abs(rounded) > STORAGE_MAX:
        raise ValueError('Derived value overflows numeric(24,12)')
    return format(rounded, 'f')


def calculate(P, F, A, T=30000, coordinate_present=None, eligible=None):
    P, F, T, A = count(P, 'P', nullable=True), count(F, 'F'), count(T, 'T', positive=True), area(A)
    present = count(coordinate_present, 'coordinate_present', nullable=True)
    eligible = count(eligible, 'eligible', nullable=True)
    if (present is not None and present > F) or (eligible is not None and eligible > F):
        raise ValueError('Coordinate counts exceed the administrative facility count')
    if eligible is not None and (present is None or eligible > present):
        raise ValueError('Eligibility requires known coordinate presence and cannot exceed it')
    with localcontext() as context:
        context.prec = 60
        need = None if P is None else (P + T - 1) // T
        result = {
            'density': None if P is None or A is None else Decimal(P) / A,
            'ratio': None if P is None or F == 0 else Decimal(P) / F,
            'facilities_per_30000': None if P is None or P == 0 else Decimal(F) * 30000 / P,
            'need': need,
            'deficit': None if need is None else max(0, need - F),
            'without_facility': F == 0,
            'coordinate_percentage': None if present is None or F == 0 else Decimal(present) * 100 / F,
            'eligible_percentage': None if eligible is None or F == 0 else Decimal(eligible) * 100 / F,
        }
    reasons = {}
    for key in ('density', 'ratio', 'facilities_per_30000', 'need', 'deficit'):
        if result[key] is None:
            reasons[key] = ('missing_population' if P is None else 'missing_area' if key == 'density'
                            else 'no_facilities' if key == 'ratio' else 'zero_population')
    for key, value in [('coordinate_percentage', present), ('eligible_percentage', eligible)]:
        if result[key] is None:
            reasons[key] = 'missing_coordinate_count' if value is None else 'no_facilities'
    for value in result.values():
        if isinstance(value, Decimal):
            stored_decimal(value)
    return {
        'source': {'population': P, 'facility_count': F, 'area_km2': None if A is None else str(A),
                   'coordinate_present': present, 'eligible': eligible},
        'parameters': {'T': T, 'ratio_scale': 30000}, 'formula_version': FORMULA_VERSION,
        'values': result, 'reasons': reasons,
        'completeness': 'complete' if P is not None and A is not None else 'partial',
    }


def aggregate(members, T=30000):
    if not members:
        raise ValueError('An aggregate requires a nonempty explicit membership')
    rows = [calculate(**member, T=T) for member in members]
    population_complete = all(row['source']['population'] is not None for row in rows)
    area_complete = all(row['source']['area_km2'] is not None for row in rows)
    population = sum(row['source']['population'] for row in rows) if population_complete else None
    facilities = sum(row['source']['facility_count'] for row in rows)
    count(population, 'aggregate population', nullable=True)
    count(facilities, 'aggregate facility count')
    with localcontext() as context:
        context.prec = 60
        total_area = sum((Decimal(row['source']['area_km2']) for row in rows), Decimal(0)) if area_complete else None
        ratio = None if population is None or facilities == 0 else Decimal(population) / facilities
        density = None if population is None or total_area is None else Decimal(population) / total_area
    complete_subset = [row for row in rows if row['source']['population'] is not None]
    subset_population = sum(row['source']['population'] for row in complete_subset)
    subset_facilities = sum(row['source']['facility_count'] for row in complete_subset)
    return {
        'members': len(rows), 'population': population, 'facility_count': facilities,
        'ratio': ratio, 'density': density,
        'sum_deficit': sum(row['values']['deficit'] for row in rows) if population_complete else None,
        'complete_population_subset': {'members': len(complete_subset), 'population': subset_population, 'facility_count': subset_facilities},
        'coordinate_percentage': _quality_total(rows, 'coordinate_present', facilities),
        'eligible_percentage': _quality_total(rows, 'eligible', facilities),
    }


def _quality_total(rows, key, facilities):
    if facilities == 0 or any(row['source'][key] is None for row in rows):
        return None
    with localcontext() as context:
        context.prec = 60
        return Decimal(sum(row['source'][key] for row in rows)) * 100 / facilities


def serialize(value):
    if isinstance(value, Decimal):
        return stored_decimal(value)
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize(item) for item in value]
    return value


def display_decimal(value):
    if value is None:
        return None
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError('Display expects a finite Decimal')
    with localcontext() as context:
        context.prec = 60
        text = format(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), ',.2f')
    return text.translate(str.maketrans({',': '.', '.': ','}))
