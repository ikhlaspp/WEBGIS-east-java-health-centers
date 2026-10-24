"""Build the reviewed historical region crosswalk from pinned source artifacts."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.acquire import local_path
from gis_pipeline.etl.crosswalk import run
from gis_pipeline.etl.http_client import atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--normalization', required=True)
    parser.add_argument('--regions', required=True)
    parser.add_argument('--decisions', required=True)
    parser.add_argument('--supplemental', required=True)
    parser.add_argument('--output', default='data/processed/crosswalk.json')
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    result = run(ROOT, load(args.normalization), load(args.regions), load(args.decisions), load(args.supplemental))
    output = local_path(ROOT, args.output, 'data/processed')
    report = local_path(ROOT, args.report, 'docs/pekerjaan')
    atomic_json(output, result)
    atomic_json(report, {key: value for key, value in result.items() if key not in ('mappings', 'master')})
    print(json.dumps(result['summary']))
    return 2 if result['unmatched'] or result['facility_conflicts'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
