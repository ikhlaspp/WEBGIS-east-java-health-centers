"""Verify and freeze all inputs in an explicit acquisition plan."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.acquire import freeze, local_path, reconcile
from gis_pipeline.etl.http_client import atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', default='data/raw/manifest.json')
    parser.add_argument('--reconcile-output', help='Run source adapters and save comparison evidence')
    args = parser.parse_args()
    manifest = freeze(ROOT, json.loads(args.plan.read_text(encoding='utf-8')), args.output)
    if args.reconcile_output:
        target = local_path(ROOT, args.reconcile_output)
        if target.is_relative_to((ROOT / 'Archives').resolve()):
            parser.error('Archives is read-only')
        atomic_json(target, reconcile(ROOT, manifest))
    print(json.dumps({key: manifest[key] for key in
                      ('availability_complete', 'data_quality_accepted', 'archive_files', 'external_files')}))


if __name__ == '__main__':
    main()
