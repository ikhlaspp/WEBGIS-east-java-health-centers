"""Reconcile parsed source pages using a durable private batch checkpoint."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.batch import run_batch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.checkpoint.resolve().is_relative_to((ROOT / 'Archives').resolve()):
        parser.error('Archives is read-only')
    spec = json.loads(args.spec.read_text(encoding='utf-8'))
    def fetch(page_id):
        return json.loads(Path(spec['page_files'][page_id]).read_text(encoding='utf-8'))
    result = run_batch(spec['identity'], spec['expected_pages'], spec['expected_ids'], spec['required_fields'],
                       fetch, args.checkpoint, resume=args.resume)
    print(json.dumps({'status': result['status'], 'completed_pages': len(result['completed']),
                      'counts': result.get('counts'), 'error': result.get('error')}))
    return 0 if result['status'] == 'succeeded' else 2


if __name__ == '__main__':
    raise SystemExit(main())
