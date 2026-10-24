# WF-064 handoff

Predecessor 5d71479d9a10872e64578554629ca802737b55b8 verified on origin/main. Inputs: WF-062 normalization manifest/artifacts, WF-063 crosswalk/output-verification, WF-017 audit baseline. Reuse normalized row dispositions and reviewed crosswalk; do not reparse or change Archives. Implement scripts/etl/reconcile_facilities.py and python/gis_pipeline/etl/reconcile_facilities.py. Retain 973 facilities, including missing coordinates, and all 666 official districts. Supplemental XLSX locations remain unverified; combined Ijen/Sempol observations cannot be silently merged. Technical self-review only.

Commands from repository root:

```powershell
.venv/Scripts/python.exe scripts/etl/reconcile_facilities.py --normalization docs/pekerjaan/WF-062/manifest-normalisasi.json --crosswalk-evidence docs/pekerjaan/WF-063/output-verification.json --baseline docs/pekerjaan/WF-017/audit-readonly.json --report docs/pekerjaan/WF-064/daftar-perbedaan-master.json
.venv/Scripts/python.exe -m pytest tests/python -q
.venv/Scripts/python.exe -m compileall -q python scripts/etl tests/python
```

All exited 0; 142 tests passed. Actual source run repeated byte-identically. Six code/attribute sets agree, 973 identities/38 parents, all 666 districts retained. Historical 39-row aggregate partitions reconcile separately and never enter master counts. No attribute corrections; three XLSX-only coordinate candidates and the two combined Ijen/Sempol rows retain explicit decisions.

Private master path/hash: output-verification.json. No coordinates verified or publication eligibility granted. Baseline 565 present/408 absent remains separate from supplemental XLSX evidence. Read rekonsiliasi-master-fasilitas.md and daftar-perbedaan-master.json before WF-065 indicator curation; proceed only after verified Git delivery.
