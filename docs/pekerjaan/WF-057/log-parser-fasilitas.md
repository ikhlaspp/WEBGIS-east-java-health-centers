# Facility source adapter

Implemented the fixed 2024-S1 Kemenkes source adapter, immutable raw receipts, CSV derivative parser and PDF table parser. Entry point: `scripts/etl/facilities.py`; shared modules: `python/gis_pipeline/etl/facilities.py` and `sources.py`. Requirements are hash-locked; pytest adds the shared package path.

The approved source is https://kemkes.go.id/app_asset/file_content_download/1732157570673ea0828311d8.00594061.pdf linked from the official 2024-S1 publication. The download is retained under ignored `data/raw`; local Archives is unchanged. Requests use HTTPS, explicit host allowlisting, public DNS validation and redirect validation, a size cap, bounded retry, and PDF content-type/magic checks. No arbitrary source URL is accepted by the CLI. Acquisition timestamps describe the actual current read, not the historical publication date.

Both inputs were executed across all 239 pages. Twenty pages (136 through 155) contain the East Java detail rows. Both yielded 973 distinct facility codes, 38 kabupaten/kota, 616 inpatient and 357 non-inpatient facilities; area categories are 658 rural, 294 urban, 16 remote and 5 very remote. No duplicate, quarantined, or parser diagnostic rows remain. Every normalized field matches between the two PDFs, and the code set equals Archives/puskesmas_jatim_alamat.csv.

Archive SHA256: `bd07d7e79e2ebc2623174237a8faf066b2286a44785cd0a58fa84a06e9a904cd`.
Downloaded SHA256: `6acffbb1baa933b1e9f9155ec3e076ba0499670f66f3b43ebb3cdc586ed2b556`.
Different binary hashes are retained, never overwritten or assumed equal; extracted-record equality was separately checked.

Initial extraction detected rotated watermark letters contaminating region names. The parser now excludes only large rotated light-gray glyphs whose combined page text exactly matches the document watermark. It records that extraction operation per page, preserves the source PDF and all extracted raw table values, and never repairs region names with fuzzy guesses. Page 136 was visually inspected to confirm column alignment. The historical snapshot identifier is checked inside the PDF before parsing.

Verification: 16 parser/acquisition tests passed. Fixtures cover multiline fields, leading-zero codes, missing code/header, totals, duplicates, hash mismatch, wrong edition, watermark recognition, private/unapproved destinations, off-host redirects, login HTML, corrupt PDF and oversized response. The existing two GIS fixture tests also passed before the final added acquisition cases; CI runs the full suite after push.

Example output is explicitly synthetic. Actual results stay in ignored `data/staging/facilities.json` and `facilities-official.json`. Completeness here means source parsing reconciles; it does not certify facility coordinates, region-code mappings, release eligibility or field accuracy. No source rows are published automatically.
