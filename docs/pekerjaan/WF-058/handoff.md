# WF-058 handoff

Status: done for the parser implementation. Inputs: completed WF-057, accepted adapter/data contracts and archived BPS sources. Shared code is python/gis_pipeline/etl/indicators.py; CLI is scripts/etl/indicators.py. Requirements lock includes openpyxl and RapidOCR; original sources are unchanged.

Real XLSX and PDF executions and scanned-page OCR are recorded in checkpoint.json and log-parser-indikator.md. OCR and derivative workbook records are unverified evidence, not certified research data. Preserve the mixed area years and Bangkalan total discrepancy through later validation. Technical self-review only; no external acceptance fabricated.

Next: acquire and reconcile the region-code and polygon sources in WF-059 after verifying this commit on origin/main. Git delivery is reported separately to avoid a self-referencing commit hash.
