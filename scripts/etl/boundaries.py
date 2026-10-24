"""Parse the verified master and acquire a private boundary candidate for review."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.boundaries import acquire_big, acquire_bridge, coverage, parse_master, reconcile_master, candidate_links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--master-receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/staging/boundaries.json')
    parser.add_argument('--download-boundaries', action='store_true')
    parser.add_argument('--resolutions', type=Path, help='Explicit identity decisions with hashed official evidence')
    parser.add_argument('--download-bridge', action='store_true')
    parser.add_argument('--bridge-receipts', type=Path, help='Previously saved official bridge receipts for resuming')
    args = parser.parse_args()
    if args.output.resolve().is_relative_to((ROOT / 'Archives').resolve()):
        parser.error('Archives is read-only')
    manifest = json.loads(args.master_receipt.read_text(encoding='utf-8'))
    master = parse_master(manifest['raw_path'], manifest)
    if args.resolutions:
        master = reconcile_master(master, json.loads(args.resolutions.read_text(encoding='utf-8')))
    result = {'master': master, 'master_receipt': manifest}
    if args.download_bridge and master['report']['complete']:
        receipts = json.loads(args.bridge_receipts.read_text(encoding='utf-8')) if args.bridge_receipts else []
        result['bridge'] = acquire_bridge(master, ROOT / 'data/raw', receipts)
    if args.download_boundaries and master['report']['complete']:
        result['boundaries'] = acquire_big(ROOT / 'data/raw')
        result['coverage'] = coverage(result['boundaries']['collection'], [row['code'] for row in master['rows']])
        if 'bridge' in result:
            result['candidate_links'] = candidate_links(result['boundaries']['collection'], result['bridge'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'master': master['report']['complete'],
                      'boundary_status': result.get('coverage', {}).get('status', 'not_requested')}))
    # A downloaded candidate is not an approved historical boundary release.
    return 2 if args.download_boundaries or not master['report']['complete'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
