"""Normalize declared tables from a frozen acquisition manifest."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.acquire import local_path
from gis_pipeline.etl.http_client import atomic_json
from gis_pipeline.etl.normalize import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--specs', type=Path, required=True)
    parser.add_argument('--output-root', default='data/staging/normalized')
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    target = local_path(ROOT, args.report)
    if target.is_relative_to((ROOT / 'Archives').resolve()):
        parser.error('Archives is read-only')
    report = run(ROOT, json.loads(args.manifest.read_text(encoding='utf-8')),
                 json.loads(args.specs.read_text(encoding='utf-8')), args.output_root)
    atomic_json(target, report)
    print(json.dumps({k: report[k] for k in ('batch_id', 'content_sha256', 'raw', 'counts')}))


if __name__ == '__main__':
    main()
