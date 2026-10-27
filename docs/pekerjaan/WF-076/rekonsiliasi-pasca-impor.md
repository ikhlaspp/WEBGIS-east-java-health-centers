# Historical reconciliation status — 2026-10-25

No real database import was performed. A release UUID is deliberately not allocated to imply a frozen curated snapshot: final spatial quality acceptance and the development database are still pending. The preparation manifest pins available files by actual bytes/hash; it is not a completed candidate-release manifest.

The expected master currently contains 973 facilities and 666 districts. None of the source coordinate candidates has been accepted as verified by this work. Those source counts are not database counts. After the deferred review: generate canonical bounded import files, run gis:check-database against the explicitly expected development database, import into a draft using an operator capability, and compare exact facility/district identities, source hashes, year distributions, location states and eligible counts. Record actual query results then. No reconciliation is marked passed now.

Per the user's instruction to continue independent work, WF-077 can implement and test formulas on synthetic reference fixtures. This does not complete WF-076 or authorize publication.

## Actual draft import — 27 October 2026

The historical paragraphs above are superseded for database preparation/import. Six canonical batches succeeded on Supabase for draft `d3ca4b39-815a-5ea5-ad44-ca7867d825be`. Private manifest: `storage/app/private/imports/archives-draft-v2/manifest.json`; all batch hashes and formats passed the PHP reader before import. Each batch is below 12 MiB (importer limit 20 MiB).

| Check | Expected | Actual |
|---|---:|---:|
| Regencies | 38 | 38 |
| Districts | 666 | 666 |
| Facilities | 973 | 973 |
| Unverified coordinates | 565 | 565 |
| Missing coordinates | 408 | 408 |
| Verified locations | 0 | 0 |
| District indicator rows | 666 | 666 |
| Facility code/name/district/coordinate/status mismatches | 0 | 0 |
| Missing facility IDs | 0 | 0 |
| Indicator value/year mismatches | 0 | 0 |
| Successful batches | 6 | 6 |

Reconciliation compared database rows with facility-master and all 1,332 source_checked population/area observations. Three extra workbook coordinate candidates did not fill missing CSV baseline locations. Full district polygons were unioned to derive regency geometry; boundary edition 2020 and BPS code edition 2023 remain explicit in metadata.

Database source records describe private processed derivatives, with hashes/paths and original provenance retained in staging; their status remains pending. No independent human acceptance is claimed. Original Archives files were not changed.

The importer used a clearly labelled temporary automation actor, import-only capability and SET LOCAL ROLE gis_worker. Cleanup was verified: zero active automation accounts and zero live automation tokens. An initial Windows ACL failure and a missing required observation_period stopped earlier attempts; the latter transaction rolled back. Immutable v2 batches corrected the metadata without changing source values.

GET /api/v1/releases returned HTTP 200 with active_release null and an empty list. No publication. Private evidence: `archives-draft/database-report.json` and `archives-draft-v2/reconciliation.json` under private imports. Code `379cb17f2a2e9cfe528e31951de6eeed36af0214` passed [full CI 40482159998](https://github.com/ikhlaspp/WEBGIS-east-java-health-centers/actions/runs/40482159998). Quality acceptance remains pending; private draft analysis is the next technical step.


## Verified private analysis ? 28 October 2026

The database confirms analysis `b08c7a1b-426f-4658-9438-25edbb2195fe` succeeded for draft `d3ca4b39-815a-5ea5-ad44-ca7867d825be`: 666 indicator results, 1,998 coverage results, and five private (unsanitized) artifacts. All coverage results are unavailable, with no numeric coverage percentage and zero eligible locations. This preserves the distinction between unavailable coverage and zero coverage.

Post-analysis reconciliation confirms 973 facilities, 666 districts, 38 regencies, and zero identity/value/year mismatches. Coordinates remain 565 unverified and 408 missing. The temporary input was removed, automation accounts are inactive, and no live automation tokens remain. The release stays draft and the active public release remains null. Source/location acceptance and publication are not completed by this analysis.

Private evidence: `storage/app/private/imports/archives-draft-v2/analysis-result.json`, `analysis-verification.json`, and `reconciliation.json`. Implementation commit `379cb17f2a2e9cfe528e31951de6eeed36af0214` passed CI run `40482159998`. Earlier progress entries above are historical.
