"""Validate a pinned analysis bundle and write immutable layers plus manifest."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.analysis.export_layers import export_bundle
from aggregates import read_pinned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    manifest = export_bundle(read_pinned(args.input, args.sha256), args.output_dir)
    print(manifest['content_hash'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
