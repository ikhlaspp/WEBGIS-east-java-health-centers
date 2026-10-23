"""Parse archived indicator workbooks or a configured PDF/CSV source table."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python'))

from gis_pipeline.etl.indicators import parse_csv_table, parse_pdf_table, parse_workbook, summarize
from gis_pipeline.etl.sources import snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--indicator', choices=['population', 'area'], required=True)
    parser.add_argument('--spec', type=Path, help='Explicit metadata/table specification for PDF or CSV')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ocr', action='store_true', help='Retain scanned-page OCR evidence for visual review')
    args = parser.parse_args()
    if args.output.resolve().is_relative_to((ROOT / 'Archives').resolve()):
        parser.error('Archives is read-only')
    receipt = snapshot(args.input.read_bytes(), ROOT / 'data/raw', 'bps-' + args.indicator,
                       'source_metadata_required', args.input.resolve().as_uri(), 'existing_archive')
    if args.input.suffix.lower() == '.xlsx':
        result = parse_workbook(args.input, receipt, args.indicator)
    else:
        if not args.spec:
            parser.error('PDF/CSV inputs require an explicit table specification')
        spec = json.loads(args.spec.read_text(encoding='utf-8'))
        if spec['indicator'] != args.indicator:
            parser.error('Indicator differs from table specification')
        parsers = {'.pdf': parse_pdf_table, '.csv': parse_csv_table}
        if args.input.suffix.lower() not in parsers:
            parser.error('Unsupported file format')
        if args.input.suffix.lower() == '.pdf':
            result = parse_pdf_table(args.input, receipt, spec,
                                     ocr_directory=args.output.parent / 'ocr' if args.ocr else None)
        else:
            result = parse_csv_table(args.input, receipt, spec)
    report = summarize(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'manifest': receipt, 'report': report, **result},
                                     ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
    return 2 if result['diagnostics'] or report['statuses'].get('quarantined') else 0


if __name__ == '__main__':
    raise SystemExit(main())
