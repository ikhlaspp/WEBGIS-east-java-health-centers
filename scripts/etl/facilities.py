"""Acquire/parse the approved Kemenkes snapshot into private staging output."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.facilities import EDITION, SOURCE_URL, completeness, parse_csv, parse_pdf
from gis_pipeline.etl.sources import fetch_pdf, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Read an existing archived PDF or CSV')
    parser.add_argument('--download', action='store_true', help='Download the fixed approved Kemenkes PDF')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/staging/facilities.json')
    args = parser.parse_args()
    if bool(args.input) == args.download:
        parser.error('Choose exactly one of --input or --download')
    output = args.output.resolve()
    if output.is_relative_to((ROOT / 'Archives').resolve()):
        parser.error('Archives is read-only; choose a staging output')
    if args.download:
        manifest = fetch_pdf(SOURCE_URL, ROOT / 'data/raw', 'kemkes-facilities', EDITION, {'kemkes.go.id'})
        result = parse_pdf(manifest['raw_path'], manifest)
    else:
        kind = args.input.suffix.lower()
        if kind not in ('.pdf', '.csv'):
            parser.error('Only PDF and CSV sources are supported')
        manifest = snapshot(args.input.read_bytes(), ROOT / 'data/raw', 'kemkes-facilities',
                            EDITION, SOURCE_URL if kind == '.pdf' else args.input.resolve().as_uri(),
                            'existing_archive')
        result = (parse_pdf if kind == '.pdf' else parse_csv)(manifest['raw_path'], manifest)
    report = completeness(result)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'manifest': manifest, 'report': report, **result},
                                ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
    return 0 if report['complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
