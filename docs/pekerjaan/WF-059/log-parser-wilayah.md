# Region source acquisition and parser evidence

24 October 2026. Status: blocked on source suitability; implementation and private acquisition are saved.

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
