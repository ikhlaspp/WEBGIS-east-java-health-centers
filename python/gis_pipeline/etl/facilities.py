"""Parse the approved facility snapshot without promoting rows to verified data."""

import csv
import hashlib
import re
from collections import Counter
from pathlib import Path

import pdfplumber

PARSER_VERSION = 'facilities-1.0'
SOURCE_URL = 'https://kemkes.go.id/app_asset/file_content_download/1732157570673ea0828311d8.00594061.pdf'
EDITION = '2024-S1'
FIELDS = ('no', 'kode_puskesmas', 'nama_puskesmas', 'alamat', 'kecamatan',
          'kabupaten', 'provinsi', 'kemampuan_pelayanan', 'karakteristik_wilayah')
PDF_HEADERS = ('NO', 'KODE', 'NAMA PUSKESMAS', 'ALAMAT', 'KECAMATAN', 'KABUPATEN',
               'PROVINSI', 'KEMAMPUAN PELAYANAN', 'KARAKTERISTIK WILAYAH KERJA')


def clean(value):
    return ' '.join(str(value or '').split())


def is_watermark_glyph(obj):
    matrix = obj.get('matrix', (1, 0, 0, 1, 0, 0))
    color = obj.get('non_stroking_color')
    return (obj.get('object_type') == 'char' and obj.get('size', 0) > 30
            and abs(matrix[1]) > 0.5 and abs(matrix[2]) > 0.5
            and color in ((0.85,), (0.85, 0.85, 0.85)))


def parse_rows(header, rows, manifest, locator_prefix, province='Jawa Timur'):
    if tuple(header) != FIELDS:
        return {'rows': [], 'quarantined': [], 'aggregates': [], 'diagnostics': [{
            'code': 'header_mismatch', 'locator': locator_prefix, 'raw_header': header,
            'raw_rows': rows,
        }]}
    output = {'rows': [], 'quarantined': [], 'aggregates': [], 'diagnostics': []}
    for index, cells in enumerate(rows, start=2):
        raw = dict(zip(FIELDS, cells))
        normalized = {key: clean(value) for key, value in raw.items()}
        record = {
            'source_id': manifest['source_id'], 'source_hash': manifest['sha256'],
            'source_url': manifest['source_url'], 'edition': manifest['edition'],
            'acquired_at': manifest['acquired_at'], 'parser_version': PARSER_VERSION,
            'locator': f'{locator_prefix}/row/{index}', 'raw_fields': raw,
            'raw_cells': cells, 'fields': normalized,
        }
        if not any(normalized.values()):
            record['reason'] = 'empty_row'
            output['quarantined'].append(record)
            continue
        if any(value.upper() in ('TOTAL', 'JUMLAH') for value in normalized.values()):
            output['aggregates'].append(record)
            continue
        code = normalized.get('kode_puskesmas', '')
        if province and normalized.get('provinsi') != province and not code.startswith('35'):
            continue
        reasons = []
        if len(cells) != len(FIELDS):
            reasons.append('column_count')
        if not re.fullmatch(r'\d{11}', code):
            reasons.append('invalid_facility_code')
        if any(not normalized.get(field) for field in FIELDS[2:]):
            reasons.append('missing_required_field')
        if province and normalized.get('provinsi') != province:
            reasons.append('province_code_mismatch')
        if reasons:
            record['reasons'] = reasons
            output['quarantined'].append(record)
        else:
            record['status'] = 'staging_unverified'
            output['rows'].append(record)
    return output


def merge(target, part):
    for key in ('rows', 'quarantined', 'aggregates', 'diagnostics'):
        target[key].extend(part[key])


def parse_csv(path, manifest, province='Jawa Timur'):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('Source hash mismatch')
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        return parse_rows(header, list(reader), manifest, 'csv', province)


def parse_pdf(path, manifest):
    if manifest['edition'] != EDITION:
        raise ValueError('This adapter only supports the approved 2024-S1 snapshot')
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('Source hash mismatch')
    result = {'rows': [], 'quarantined': [], 'aggregates': [], 'diagnostics': [],
              'pages_scanned': 0, 'detail_pages': [], 'extraction_notes': []}
    with pdfplumber.open(path) as pdf:
        opening = '\n'.join((page.extract_text() or '') for page in pdf.pages[:3])
        if '1690/2024' not in opening or not re.search(r'SEMESTER\s+I\s+TAHUN\s+2024', opening):
            raise ValueError('PDF does not identify the approved 2024-S1 document')
        result['page_count'] = len(pdf.pages)
        for page_number, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ''
            result['pages_scanned'] += 1
            if not re.search(r'\b35\d{9}\b', text):
                page.close()
                continue
            result['detail_pages'].append(page_number)
            watermark = ''.join(char['text'] for char in page.chars if is_watermark_glyph(char))
            table_page = page
            if watermark == 'KEMENTERIAN KESEHATAN':
                table_page = page.filter(lambda obj: not is_watermark_glyph(obj))
                result['extraction_notes'].append({
                    'page': page_number, 'operation': 'exclude_rotated_gray_watermark_glyphs',
                    'text': watermark, 'source_pdf_preserved': True,
                })
            matched = False
            for table_number, table in enumerate(table_page.extract_tables(), 1):
                if not table:
                    continue
                header = [re.sub(r'\s+', '', clean(cell)).upper() for cell in table[0]]
                expected = [re.sub(r'\s+', '', cell) for cell in PDF_HEADERS]
                if header != expected:
                    result['diagnostics'].append({'code': 'header_mismatch',
                        'locator': f'pdf/page/{page_number}/table/{table_number}', 'raw_table': table})
                    continue
                matched = True
                part = parse_rows(FIELDS, table[1:], manifest,
                                  f'pdf/page/{page_number}/table/{table_number}')
                merge(result, part)
            if not matched:
                result['diagnostics'].append({'code': 'facility_table_missing', 'page': page_number})
            page.close()
    return result


def completeness(result, expected_count=973, expected_regencies=38):
    counts = Counter(row['fields']['kode_puskesmas'] for row in result['rows'])
    regencies = {row['fields']['kabupaten'] for row in result['rows']}
    duplicates = sorted(code for code, count in counts.items() if count != 1)
    complete = (len(result['rows']) == expected_count and len(regencies) == expected_regencies
                and not duplicates and not result['quarantined'] and not result['diagnostics'])
    return {'complete': complete, 'rows': len(result['rows']), 'regencies': len(regencies),
            'expected_rows': expected_count, 'expected_regencies': expected_regencies,
            'duplicates': duplicates, 'quarantined': len(result['quarantined']),
            'diagnostics': len(result['diagnostics']),
            'service_types': dict(Counter(row['fields']['kemampuan_pelayanan'] for row in result['rows'])),
            'area_types': dict(Counter(row['fields']['karakteristik_wilayah'] for row in result['rows']))}
