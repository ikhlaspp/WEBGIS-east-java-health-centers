"""Parse the verified master and acquire a private boundary candidate for review."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.boundaries import acquire_big, acquire_bridge, coverage, parse_master, reconcile_master, candidate_links
from gis_pipeline.etl.boundaries import acquire_hdx, parse_hdx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--master-receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/staging/boundaries.json')
    parser.add_argument('--download-boundaries', action='store_true')
    parser.add_argument('--resolutions', type=Path, help='Explicit identity decisions with hashed official evidence')
    parser.add_argument('--download-bridge', action='store_true')
    parser.add_argument('--bridge-receipts', type=Path, help='Previously saved official bridge receipts for resuming')
    parser.add_argument('--download-hdx', action='store_true', help='Acquire licensed 2020 historical reference')
    parser.add_argument('--hdx-member-receipt', type=Path)
    parser.add_argument('--hdx-catalog-receipt', type=Path)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to((ROOT / 'Archives').resolve()):
        parser.error('Archives is read-only')
    manifest = json.loads(args.master_receipt.read_text(encoding='utf-8'))
    master = parse_master(manifest['raw_path'], manifest)
    if args.resolutions:
        master = reconcile_master(master, json.loads(args.resolutions.read_text(encoding='utf-8')))
    result = {'master': master, 'master_receipt': manifest}
    if args.download_hdx and master['report']['complete']:
        result['historical_boundaries'] = acquire_hdx(ROOT / 'data/raw', master)
    elif args.hdx_member_receipt or args.hdx_catalog_receipt:
        if not (args.hdx_member_receipt and args.hdx_catalog_receipt):
            parser.error('Both historical receipts are required')
        result['historical_boundaries'] = parse_hdx(
            json.loads(args.hdx_member_receipt.read_text(encoding='utf-8')),
            json.loads(args.hdx_catalog_receipt.read_text(encoding='utf-8')), master)
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
                      'historical_boundaries': result.get('historical_boundaries', {}).get('report'),
                      'boundary_status': result.get('coverage', {}).get('status', 'not_requested')}))
    # A downloaded candidate is not an approved historical boundary release.
    return 2 if args.download_boundaries or not master['report']['complete'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
