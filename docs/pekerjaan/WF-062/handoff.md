# WF-062 handoff

Started from 39b01a32bfc9cadd661b0838676e10464ea58faa, verified on origin/main. Input: WF-061 frozen manifest and raw snapshots; contracts: WF-038 normalization and WF-040 staging. Implementation: scripts/etl/normalize.py delegates to python/gis_pipeline/etl/normalize.py.

Produce deterministic row envelopes, separate accepted/quarantined/aggregate dispositions, raw values and conversion logs. Accepted means syntactically normalized, never verified or published. All historical combined rows are retained; no alias merges or duplicate deletion. Coordinate values remain unverified candidates. PDF table certification, crosswalk, geometry validation and quality acceptance retain their downstream controls.

Technical self-review only; no independent reviewer or lecturer acceptance claimed.

Final commands from the repository root:

```powershell
.venv/Scripts/python.exe scripts/etl/normalize.py --manifest docs/pekerjaan/WF-061/manifest-input-mentah.json --specs docs/pekerjaan/WF-062/source-specs.json --report docs/pekerjaan/WF-062/manifest-normalisasi.json
.venv/Scripts/python.exe -m pytest tests/python -q
.venv/Scripts/python.exe -m compileall -q python scripts/etl tests/python
```

All final commands exited 0. Actual raw=8656, accepted=8502, aggregate=154, quarantine=0; 114 tests passed. Read laporan-parse-dan-reject.md for the caught subtotal expectation error and successful retest. Batch/content/output hashes are in manifest-normalisasi.json; output-verification.json independently reconciles saved outputs. Synthetic full-run repetition produced identical report/content/file hashes and counts.

Repository JSON evidence verification now permits only Git LF/CRLF representation changes, while raw hashes remain byte-exact. This prerequisite correction was tested against actual Git blobs and against source tampering.

Carry three additional XLSX coordinate candidates into later review (35770200004/5/6); do not promote them automatically. Keep all 667 historical combined detail rows and the separate 39 aggregate rows. Next: WF-063 crosswalk after verified commit/push. Predecessor CI 40091927753 passed.
