"""Clip unioned eligible buffers to full-precision administrative boundaries."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.analysis.coverage import coverage
from gis_pipeline.etl.http_client import atomic_json
from aggregates import read_pinned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--buffers', required=True)
    parser.add_argument('--buffers-sha256', required=True)
    parser.add_argument('--boundaries', required=True)
    parser.add_argument('--boundaries-sha256', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists() or output.resolve() in [Path(args.buffers).resolve(), Path(args.boundaries).resolve()]:
        parser.error('Output must be new and distinct from the inputs')
    result = coverage(read_pinned(args.buffers, args.buffers_sha256), read_pinned(args.boundaries, args.boundaries_sha256))
    result['buffer_artifact_hash'] = args.buffers_sha256
    result['boundary_artifact_hash'] = args.boundaries_sha256
    atomic_json(output, result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
