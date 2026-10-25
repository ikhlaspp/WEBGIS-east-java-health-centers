"""Validate frozen boundaries and write separate analysis/display artefacts."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.acquire import local_path
from gis_pipeline.etl.http_client import atomic_json
from gis_pipeline.etl.validate_boundaries import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquisition-evidence', required=True)
    parser.add_argument('--crosswalk-evidence', required=True)
    parser.add_argument('--output-dir', default='data/processed/boundaries')
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    result = run(ROOT, load(args.acquisition_evidence), load(args.crosswalk_evidence),
                 progress=lambda n: print(f'Validated {n} districts', flush=True))
    folder = local_path(ROOT, args.output_dir, 'data/processed')
    outputs = {}
    for role in ('analysis', 'display', 'excluded_water'):
        target = folder / (role + '.geojson' if role != 'excluded_water' else role + '.json')
        atomic_json(target, result[role])
        outputs[role] = {'path': target.relative_to(ROOT).as_posix(),
                         'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size}
    report = {k: v for k, v in result.items() if k not in ('analysis', 'display', 'excluded_water')}
    report['outputs'] = outputs
    atomic_json(local_path(ROOT, args.report, 'docs/pekerjaan'), report)
    print(json.dumps(result['summary']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
