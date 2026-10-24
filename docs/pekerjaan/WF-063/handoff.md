# WF-063 handoff

Input: WF-062 normalized manifest/artifacts and WF-061 frozen source manifest; official reconciled master/bridge/boundaries from data/staging/acquisition-regions.json, pinned by WF-061/region-reconciliation.json. Design: WF-038. Implement scripts/etl/crosswalk.py and python/gis_pipeline/etl/crosswalk.py. No facility-code slicing, fuzzy auto-approval, aggregation of duplicate observations, or quality promotion. Technical source review by agent; no independent reviewer acceptance claimed.

Predecessor 6f7f20f5b24feb1090bee484de51e5de9e5d33fa is on origin/main; GitHub Actions 40094479019 passed. PHP 8.4.22 and Composer 2.4.1 are available; existing Boost installation/generated guidelines remain in force. Python changes only; no dependency changes.

Commands from repository root:

```powershell
.venv/Scripts/python.exe scripts/etl/crosswalk.py --normalization docs/pekerjaan/WF-062/manifest-normalisasi.json --regions docs/pekerjaan/WF-061/region-reconciliation.json --decisions docs/pekerjaan/WF-063/alias-decisions.json --supplemental docs/pekerjaan/WF-063/supplemental-receipts.json --report docs/pekerjaan/WF-063/crosswalk-terreview.json
.venv/Scripts/python.exe -m pytest tests/python -q
.venv/Scripts/python.exe -m compileall -q python scripts/etl tests/python
```

Crosswalk ran twice with identical output bytes. All 8,502 rows mapped; 973 facility codes have consistent assignments; one duplicate-observation group (Ijen/Sempol) is held for curation. All 666 master districts remain, including Pabean Cantian without assignments in the selected facility snapshot. Do not interpret that as real-world service coverage or remove the district.

Alias decisions have exact source hash/edition/period scopes and master/bridge evidence. Supplemental official Sumenep pages are private immutable HTML receipts; they corroborate Giligenting without modifying the frozen observation source set. The implementation never guesses aliases, drops historical rows, selects one of conflicting observations, or claims independent review.

Use checkpoint.json for final tests. Next: WF-064 after verified Git delivery; carry forward three additional unverified XLSX coordinates from WF-062 and the duplicate Ijen/Sempol indicator conflict.
