"""Reconcile normalized facilities and historical subtotals with the reviewed crosswalk."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.acquire import local_path
from gis_pipeline.etl.http_client import atomic_json
from gis_pipeline.etl.reconcile_facilities import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--normalization', required=True)
    parser.add_argument('--crosswalk-evidence', required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--output', default='data/processed/facility-master.json')
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    result = run(ROOT, load(args.normalization), load(args.crosswalk_evidence), load(args.baseline))
    atomic_json(local_path(ROOT, args.output, 'data/processed'), result)
    atomic_json(local_path(ROOT, args.report, 'docs/pekerjaan'),
                {k: v for k, v in result.items() if k not in ('facilities', 'region_master', 'district_assignment_counts')})
    print(json.dumps(result['summary']))
    return 0 if result['reconciliation_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
