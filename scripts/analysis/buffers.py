"""Build independent AEQD reference buffers from a hash-pinned reviewed snapshot."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.analysis.buffers import build_buffers
from gis_pipeline.etl.http_client import atomic_json
from aggregates import read_pinned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists() or output.resolve() == Path(args.input).resolve():
        parser.error('Output must be a new file distinct from the input')
    atomic_json(output, build_buffers(read_pinned(args.input, args.sha256), args.sha256))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
