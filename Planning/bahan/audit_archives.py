"""Audit read-only Archives dan ekspor bahan staging, memakai pustaka standar Python.

Jalankan dari root: python Planning/bahan/audit_archives.py
Tidak mengoreksi nama, mengisi koordinat, atau mengubah berkas sumber.
"""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter, defaultdict
from decimal import Decimal
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ARCHIVES = ROOT / "Archives"
OUT = ROOT / "Planning" / "bahan"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name, rows, fields=None):
    fields = fields or list(rows[0])
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_xlsx(path):
    """Baca nilai tersimpan OOXML; tidak menghitung formula atau mengubah workbook."""
    with ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(n.text or "" for n in x.findall(".//s:t", NS))
                      for x in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in
                ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        result = {}
        for sheet in ET.fromstring(archive.read("xl/workbook.xml")).findall("s:sheets/s:sheet", NS):
            rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = rels[rid]
            target = target.lstrip("/") if target.startswith("/") else "xl/" + target
            rows = []
            for row in ET.fromstring(archive.read(target)).findall("s:sheetData/s:row", NS):
                cells = {}
                for cell in row:
                    value = cell.find("s:v", NS)
                    value = value.text if value is not None and value.text is not None else ""
                    if cell.get("t") == "s":
                        value = shared[int(value)] if value else ""
                    elif cell.get("t") == "inlineStr":
                        value = "".join(n.text or "" for n in cell.findall(".//s:t", NS))
                    cells[re.sub(r"\d", "", cell.attrib["r"])] = value
                if any(v != "" for v in cells.values()):
                    rows.append({"_row": int(row.attrib["r"]), **cells})
            result[sheet.attrib["name"]] = rows
        return result


def key(row):
    return row["kabupaten"], row["kecamatan"]


def integer(value):
    return int(Decimal(value)) if value else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    addresses = read_csv(ARCHIVES / "puskesmas_jatim_alamat.csv")
    coords = read_csv(ARCHIVES / "puskesmas_jatim_koordinat.csv")
    counts = read_csv(ARCHIVES / "jumlah_puskesmas_per_kecamatan.csv")
    details = [r for r in counts if r["kabupaten"].upper() != "TOTAL" and r["kecamatan"].upper() != "TOTAL"]
    totals = [r for r in counts if r not in details]
    workbook = read_xlsx(ARCHIVES / "Data_Gabungan_Kecamatan_Jawa_Timur.xlsx")
    sheet_name, sheet_rows = next((n, rows) for n, rows in workbook.items()
                                  if any(r.get("D") == "Jumlah Penduduk" for r in rows))
    merged = []
    aggregate_rows = []
    for r in sheet_rows:
        if r.get("C", "").upper() == "TOTAL" or r.get("B", "").upper() == "TOTAL":
            aggregate_rows.append(r)
        elif r.get("B") and r.get("C") and r.get("D") != "Jumlah Penduduk":
            merged.append({"source_row": r["_row"], "kabupaten": r["B"], "kecamatan": r["C"],
                           "jumlah_penduduk": integer(r.get("D", "")),
                           "luas_km2": r.get("E", ""), "jumlah_puskesmas": integer(r.get("F", ""))})
    by_pair = defaultdict(list)
    staged = []
    for i, row in enumerate(coords, 2):
        found = bool(row["latitude"] and row["longitude"])
        if found:
            by_pair[(row["latitude"], row["longitude"])].append(row)
        staged.append({"source_row": i, **row, "periode_fasilitas": "2024-S1",
                       "coordinate_review_status": "unverified" if found else "missing",
                       "precision_level": "unknown", "eligible_for_buffer": "false"})
    issues = []
    for row in staged:
        if row["coordinate_review_status"] == "missing":
            issues.append({"kode_puskesmas": row["kode_puskesmas"], "nama_puskesmas": row["nama_puskesmas"],
                           "kabupaten": row["kabupaten"], "kecamatan": row["kecamatan"],
                           "issue": "MISSING_COORDINATES", "latitude": row["latitude"], "longitude": row["longitude"]})
        elif len(by_pair[(row["latitude"], row["longitude"])] ) > 1:
            issues.append({"kode_puskesmas": row["kode_puskesmas"], "nama_puskesmas": row["nama_puskesmas"],
                           "kabupaten": row["kabupaten"], "kecamatan": row["kecamatan"],
                           "issue": "DUPLICATE_COORDINATE_REVIEW", "latitude": row["latitude"], "longitude": row["longitude"]})
    from_master = Counter(key(r) for r in addresses)
    merged_keys = {key(r) for r in merged}
    reconciliation = []
    for k in sorted(merged_keys | set(from_master)):
        record = next((r for r in merged if key(r) == k), None)
        actual = from_master.get(k, 0)
        reported = record["jumlah_puskesmas"] if record else None
        if record is None or reported != actual or record["jumlah_penduduk"] is None or not record["luas_km2"]:
            reconciliation.append({"kabupaten": k[0], "kecamatan": k[1],
                                   "master_count_exact_name": actual,
                                   "merged_count": reported,
                                   "in_merged": record is not None,
                                   "population_missing": record is not None and record["jumlah_penduduk"] is None,
                                   "area_missing": record is not None and not record["luas_km2"],
                                   "review_status": "pending_name_and_code_reconciliation"})
    write_csv("staging_puskesmas_2024_s1.csv", staged)
    write_csv("staging_kecamatan_gabungan.csv", merged)
    write_csv("jumlah_puskesmas_tanpa_total.csv", details)
    write_csv("antrean_review_koordinat.csv", issues)
    write_csv("rekonsiliasi_nama_kecamatan.csv", reconciliation)
    notes = {}
    workbook_inventory = []
    for path in sorted(ARCHIVES.rglob("*.xlsx")):
        sheets = read_xlsx(path)
        workbook_inventory.append({"path": path.relative_to(ROOT).as_posix(),
                                   "sheets": {n: len(rows) for n, rows in sheets.items()}})
        for n, rows in sheets.items():
            if "catatan" in n.lower() or "note" in n.lower():
                notes[path.name + " / " + n] = [" ".join(str(v) for k, v in r.items() if k != "_row") for r in rows]
    (OUT / "catatan_workbook.json").write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    inventory = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                 for p in sorted(ARCHIVES.rglob("*")) if p.is_file()]
    write_csv("inventaris_sumber.csv", inventory)
    report = {
        "audit_date": "2026-10-22", "method": "CSV and stored OOXML values; no geospatial or source PDF validation",
        "source_file_count": len(inventory), "source_pdf_count": len(list(ARCHIVES.rglob("*.pdf"))),
        "puskesmas": {"rows": len(addresses), "unique_codes": len({r["kode_puskesmas"] for r in addresses}),
                      "kabupaten_kota": len({r["kabupaten"] for r in addresses}), "raw_kecamatan_keys": len(from_master),
                      "service_types": dict(Counter(r["kemampuan_pelayanan"] for r in addresses)),
                      "area_types": dict(Counter(r["karakteristik_wilayah"] for r in addresses)),
                      "master_vs_coordinate_code_sets_equal": {r["kode_puskesmas"] for r in addresses} == {r["kode_puskesmas"] for r in coords}},
        "coordinates": {"rows": len(coords), "found": sum(len(v) for v in by_pair.values()),
                        "missing": sum(not r["latitude"] or not r["longitude"] for r in coords),
                        "found_percentage": round(sum(len(v) for v in by_pair.values()) / len(coords) * 100, 2),
                        "unique_pairs": len(by_pair), "duplicate_groups": sum(len(v) > 1 for v in by_pair.values()),
                        "duplicate_rows": sum(len(v) for v in by_pair.values() if len(v) > 1),
                        "review_queue_rows": len(issues), "verified_for_analysis": 0,
                        "duplicate_examples": [[r["kode_puskesmas"] + " " + r["nama_puskesmas"] for r in v] for v in by_pair.values() if len(v) > 1]},
        "counts_csv": {"all_rows": len(counts), "detail_rows": len(details), "aggregate_rows": len(totals),
                       "sum_all_rows": sum(int(r["jumlah_puskesmas"]) for r in counts),
                       "sum_detail_rows": sum(int(r["jumlah_puskesmas"]) for r in details),
                       "detail_matches_raw_master": {key(r): int(r["jumlah_puskesmas"]) for r in details} == dict(from_master)},
        "merged_workbook": {"sheet": sheet_name, "detail_rows": len(merged), "aggregate_rows": len(aggregate_rows),
                            "kabupaten_kota": len({r["kabupaten"] for r in merged}),
                            "unique_keys": len(merged_keys),
                            "missing_population": [{"kabupaten": r["kabupaten"], "kecamatan": r["kecamatan"]} for r in merged if r["jumlah_penduduk"] is None],
                            "missing_area": [{"kabupaten": r["kabupaten"], "kecamatan": r["kecamatan"]} for r in merged if not r["luas_km2"]],
                            "sum_facilities": sum(r["jumlah_puskesmas"] or 0 for r in merged),
                            "zero_facility_rows": [{"kabupaten": r["kabupaten"], "kecamatan": r["kecamatan"]} for r in merged if r["jumlah_puskesmas"] == 0],
                            "exact_name_reconciliation_rows": len(reconciliation)},
        "workbooks": workbook_inventory,
    }
    (OUT / "hasil_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "workbooks"}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
