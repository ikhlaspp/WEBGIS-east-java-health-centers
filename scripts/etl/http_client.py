"""Download a declared public source with verified caching and bounded retries."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.http_client import SourceClient, atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--edition', required=True)
    parser.add_argument('--allow-host', action='append', required=True)
    parser.add_argument('--format', choices=['json', 'pdf', 'bytes'], default='json')
    parser.add_argument('--raw-root', type=Path, default=ROOT / 'data/raw')
    parser.add_argument('--receipt', type=Path, default=ROOT / 'data/staging/http-receipt.json')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    if any(path.resolve().is_relative_to((ROOT / 'Archives').resolve()) for path in (args.raw_root, args.receipt)):
        parser.error('Archives is read-only')
    def validate(data, headers):
        if args.format == 'json':
            json.loads(data)
        elif args.format == 'pdf' and not data.startswith(b'%PDF-'):
            raise ValueError('Invalid PDF response')
    result = SourceClient(args.raw_root, args.allow_host).fetch(args.url, args.source_id, args.edition,
                                                              validate=validate, refresh=args.refresh)
    atomic_json(args.receipt, result['receipt'])
    print(json.dumps({'sha256': result['receipt']['sha256'], 'bytes': len(result['data']),
                      'cache_hit': result['cache_hit'], 'attempts': result['attempts']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
