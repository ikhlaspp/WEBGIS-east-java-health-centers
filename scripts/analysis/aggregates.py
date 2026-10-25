"""Aggregate a complete district snapshot using a separately hash-pinned master."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.analysis.aggregates import aggregate_regions
from gis_pipeline.etl.http_client import atomic_json
from indicators import unique_object


def read_pinned(path, expected):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Input SHA-256 mismatch')
    return json.loads(data, parse_float=str, object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON value')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--master', required=True)
    parser.add_argument('--master-sha256', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists() or output.resolve() in [Path(args.input).resolve(), Path(args.master).resolve()]:
        parser.error('Output must be a new file distinct from both inputs')
    result = aggregate_regions(read_pinned(args.input, args.sha256), read_pinned(args.master, args.master_sha256))
    result['indicator_artifact_hash'] = args.sha256
    result['master_artifact_hash'] = args.master_sha256
    atomic_json(output, result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
