# WF-061 handoff

Started from ae0077083e2d905800f4fea4620135286f3a281a (WF-060, pushed; GitHub Actions 40058253468 passed). Accepted G2/G3 decisions remain in force: all original Archives are retained, free official sources may be selected during acquisition, and mixed-period exploration must display actual source dates.

Implementation maps `scripts/etl/acquire.py` to shared `python/gis_pipeline/etl/acquire.py`. The explicit source plan pins the original WF-017 inventory, 42 downloaded receipts and source-selection/identity decisions by hash. It never executes the archived notebook or edits Archives. Hash-addressed workbook snapshots are read as bytes so their `.bin` extension does not prevent parsing.

Run from the repository root with `.venv/Scripts/python.exe`:

```powershell
.venv/Scripts/python.exe scripts/etl/acquire.py --plan docs/pekerjaan/WF-061/source-plan.json --reconcile-output docs/pekerjaan/WF-061/reconciliation.json
.venv/Scripts/python.exe -m pytest tests/python -q
.venv/Scripts/python.exe -m compileall -q python scripts/etl tests/python
```

The regional adapter was also rerun successfully with:

```powershell
.venv/Scripts/python.exe scripts/etl/boundaries.py --master-receipt .tools/mfd-receipt.json --resolutions docs/pekerjaan/WF-059/identity-resolutions.json --hdx-member-receipt docs/pekerjaan/WF-059/hdx-member-receipt.json --hdx-catalog-receipt docs/pekerjaan/WF-059/hdx-catalog-receipt.json --download-bridge --bridge-receipts docs/pekerjaan/WF-059/bridge-resume-receipts.json --output data/staging/acquisition-regions.json
```

The temporary master receipt is the `bps-mfd` entry in source-plan.json; its source hash is 64389efb56742edcd495bfd95cf8dcb40bba881209d0172448b7d4e75cf68e3f. All 38 bridge responses were reused after hash verification. Public summary: region-reconciliation.json; large source rows/geometry remain private in data/staging. The later freeze-only invocation and eight acquisition tests verified the final manifest-target safeguards without repeating unchanged PDF parsing.

The manifest is published atomically only after inventory, hash, size and configuration checks. Raw files are immutable by procedure: never edit or overwrite them; changed source bytes require a new snapshot and explicit source-plan review. This is not an operating-system ACL guarantee. Missing, changed, extra, duplicate or escaping inputs fail; no partial download is selected. Old successful manifests remain historical evidence if a later invocation fails and must not be mistaken for a successful new run.

Availability is separate from numeric, spatial and release approval. Indicator derivative claims, OCR review, historical name differences and missing coordinates remain downstream curation work. Technical self-review does not claim independent review, lecturer acceptance or UAT.

See checkpoint.json and laporan-akuisisi-sumber.md for final execution results and the next task.
