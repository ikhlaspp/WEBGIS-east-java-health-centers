# Region source acquisition and parser evidence

24 October 2026. Current status: done for acquisition; see the final historical-source selection below. Earlier blockers are retained as audit history. The follow-up below supersedes the initial unresolved-master status; implementation and private acquisition are saved.

Implemented python/gis_pipeline/etl/boundaries.py and scripts/etl/boundaries.py. Downloading uses the shared HTTPS allowlist/redirect checks and immutable snapshots. Every geometry page is selected by object IDs; counts, duplicates, missing IDs, transfer-limit flags and the final source ID set are checked. Geometry is not simplified, repaired or flattened. Codes remain strings or their original null values. The CLI preserves failed master diagnostics and exits 2 rather than approving an unresolved source.

## Actual master source

The official BPS MFD 2023 PDF was downloaded (415 physical pages, SHA-256 in manifest). The publication page returned HTTP 403 to the local downloader; the public BPS download link found through the official indexed publication succeeded without bypassing access controls. Full text extraction removes only the exact rotated BPS URL watermark, handles split district names and keeps raw lines/page locators. The detailed tables yield 666 districts and 38 parents; every parent count matches the province summary.

However, 16 summary rows disagree with the detail tables. Physical page 59 gives Pucang Laban as 3504061 and Rejotangan as 3504070; page 62 gives 3504070 and 3504080 respectively. These pages were rendered and visually inspected, confirming a source disagreement rather than a parser digit substitution. The Tulungagung sequence continues to differ for 13 summary rows. Bondowoso includes a malformed Sukosari summary code and Ijen versus Sempol at the same code. Mojokerto's summary uses 3676021 for Kranggan while its detail uses 3576021. Both sides remain in the manifest; neither is silently chosen as canonical. Independent official corroboration is still required.

## Actual boundary candidate

The BIG service and item metadata identify June 2026, EPSG:4326. A province-code query KDPPUM='35' returns 676 objects, all downloaded across 28 geometry pages (25 per page except the last). Initial and final object-ID sets agree. The unmodified GeoJSON has 585 Polygon and 91 MultiPolygon features, preserving separate islands. There are 38 nonempty regency/city names, plus records with absent names. All 676 KDCBPS fields are null; 10 KDCPUM fields are empty. These are source issues, not identifiers to infer from names.

BIG's item metadata has an empty licenseInfo; its XML metadata has an empty useLimit. Copyright attribution names BIG, which does not establish the missing redistribution terms. The candidate remains private and publication_allowed=false. It is not relabelled 2023. Official historical-source searches found a Pamekasan-only catalogue entry (2018-named resource, published 2023), not a verified province-wide replacement. A ministry mirror describes updates through 2025 and is not a historical 2023 substitute either. No third-party shapefile was promoted as an official historical source.

Source references: [BPS MFD publication](https://jatim.bps.go.id/id/publication/2024/07/26/d64a7ab574bdbb877d3f5665/village-master-file-of-jawa-timur-province-2023.html), [BIG service](https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KECAMATAN_AR/MapServer), [BIG item metadata](https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KECAMATAN_AR/MapServer/info/iteminfo?f=pjson), [Pamekasan catalogue](https://data.go.id/dataset/dataset/batas-administrasi-kecamatan8).

## Verification and disposition

47 Python tests passed; compileall passed. Boundary tests cover pagination, independent expected object sets, zero-prefixed strings, MultiPolygon islands, truncated/missing/duplicate geometry, source drift, missing code joins, split names and contradictory master records. Raw datasets are ignored/private; the committed manifest contains hashes, locators, counts and source metadata only. Archives was not modified.

WF-059 is not complete. WF-060 and later mandatory tickets cannot advance under the accepted finish-to-start rule while this mandatory predecessor is blocked. The next work is an evidence-backed identity reconciliation and historical boundary/terms resolution, or an explicitly accepted change allowing a specific newer boundary edition with a reviewed crosswalk. No false gate acceptance, made-up coordinates or fabricated completion is recorded.


## Follow-up: official identity corroboration

The official SIG BPS page exposes a period selector and public REST endpoint. Its period catalogue includes 2023_1.2022, explicitly 2023 Semester 1 BPS and 2022 Kemendagri. Downloaded the Tulungagung, Bondowoso and Mojokerto city tables and preserved source hashes. All 16 disputed PDF identities have exact corroborating BPS code/name records: the Tulungagung detail sequence, Sukosari 3511060, Kranggan 3576021 and Ijen 3511151. Ijen is retained as the corroborated name while the original Sempol detail text is preserved. These are explicit source-backed decisions in identity-resolutions.json, not fuzzy matches or invented reviewer acceptance.

The reconciliation function verifies the evidence host, path, selected period, parent, SHA-256 and unique exact code/name record before applying a decision. Duplicate/unsupported decisions fail. The master retains all 666 codes and 38 parents; unresolved identity conflicts are now zero. This evidence has the stated semester, not an invented effective date range.

A full bridge acquisition was then attempted to resolve the null BPS fields in the boundary candidate via its PUM codes. The initial download saved 20 parent tables before TLS resets. Retrying outside the sandbox reproduced the same remote failure. Resuming recovered six more tables, and a later resumed attempt completed the remaining twelve. All 38 tables now reconcile to 666 unique BPS/PUM pairs, linking exactly 666 candidate geometry objects. Ten objects without a usable PUM code remain explicitly excluded from joins; all original geometries are preserved. bridge-progress.json records complete counts; bridge-resume-receipts.json allows recovery without redownloading verified snapshots. Candidate links use exact dotted PUM-code normalization only; absent codes remain excluded, with no name guessing. Successful code linkage does not validate June 2026 geometry for 2023.

Added CLI options --resolutions, --download-bridge and --bridge-receipts. Resume using the existing master receipt and the two JSON files beside this log. No source archive or source geometry was modified. Verification: 51 Python tests passed and compileall passed. The preceding hosted run 40026052844 also completed successfully. The remaining blockers are boundary edition and reuse terms. Master identities and full code bridging are now corroborated; historical geometry validity remains unestablished.

Official reference: https://sig.bps.go.id/bridging-kode/index. The exact query URLs, periods and hashed downloads are recorded in the evidence receipts.


## Final source selection: licensed historical BPS/OCHA reference

The official HDX metadata API returned an explicit CC BY-IGO licence and BPS source attribution for COD-AB Indonesia v01. The 2020-04-01 district member was acquired from the catalogue's GeoJSON ZIP using bounded HTTP ranges and stable ETag checks; ZIP CRC and a complete member SHA-256 were verified. The parser checks the catalogue receipt, licence/source identity, national count 7069, exact CRS, feature dates, parent identities, complete district-code coverage and unexpected duplicates/extras. Actual selection: 666 districts, 38 parents, 603 Polygon and 63 MultiPolygon; one water object is preserved outside district joins.

The historical reference is selected for explicitly labelled mixed-period exploration under the existing accepted scope. It is not relabelled 2023 or certified ready for publication. source-selection.md and selected-boundary-source.json preserve the rationale, attribution, licence and required date labels. The unapproved BIG 2026 candidate is superseded, not silently accepted. This resolves the acquisition blocker without changing the proposed feature scope or inventing permission from BIG.

63 Python tests pass, including ZIP range/identity failure cases and historical code/parent/date/geometry/coverage checks. Real source hashes and reports are in the manifest. WF-060 may proceed after verified Git delivery; downstream data-quality and release checks remain mandatory.
