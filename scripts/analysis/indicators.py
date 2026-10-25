"""Calculate draft district indicators from a hash-pinned administrative snapshot."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.analysis.indicators import FORMULA_VERSION, aggregate, calculate, serialize
from gis_pipeline.etl.http_client import atomic_json


def run(document, input_hash, threshold):
    if not isinstance(document, dict) or not re.fullmatch('[0-9a-f]{64}', input_hash):
        raise ValueError('A document and its SHA-256 are required')
    for key in ('release_id', 'method_version', 'code_revision'):
        if not isinstance(document.get(key), str) or not document[key].strip():
            raise ValueError(f'Missing provenance: {key}')
    if not re.fullmatch('[0-9a-f]{64}', document.get('boundary_hash', '')):
        raise ValueError('Missing boundary hash')
    districts = document.get('districts')
    if not isinstance(districts, list) or not districts:
        raise ValueError('An explicit nonempty administrative district master is required')
    seen, results, members = set(), [], []
    for row in districts:
        if not isinstance(row, dict):
            raise ValueError('District rows must be objects')
        district = row.get('district_id')
        if not isinstance(district, str) or not district or district in seen:
            raise ValueError('Invalid/duplicate district identity')
        seen.add(district)
        if set(row) - {'district_id', 'P', 'F', 'A', 'coordinate_present', 'eligible'}:
            raise ValueError('Unexpected district field; filtered facility counts are not supported')
        values = {key: row[key] for key in ('P', 'F', 'A')}
        values.update({key: row[key] for key in ('coordinate_present', 'eligible') if key in row})
        members.append(values)
        results.append({'district_id': district, **calculate(**values, T=threshold)})
    return serialize({
        'status': 'candidate_calculation', 'release_id': document['release_id'],
        'method_version': document['method_version'], 'formula_version': FORMULA_VERSION,
        'code_revision': document['code_revision'], 'input_hash': input_hash,
        'boundary_hash': document['boundary_hash'], 'parameters': {'T': threshold, 'ratio_scale': 30000},
        'districts': results, 'aggregate': aggregate(members, T=threshold),
    })


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--threshold', type=int, default=30000)
    args = parser.parse_args()
    source, output = Path(args.input), Path(args.output)
    if source.resolve() == output.resolve() or output.exists():
        parser.error('Output must be a new file distinct from the input')
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != args.sha256:
        parser.error('Input SHA-256 mismatch')
    document = json.loads(data, parse_float=str, object_pairs_hook=unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON value')))
    atomic_json(output, run(document, digest, args.threshold))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
