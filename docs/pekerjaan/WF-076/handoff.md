# Handoff

WF-076 is blocked by the intentionally deferred WF-071 quality report and missing WF-072 deployment credentials. Inputs are pinned in manifest-kandidat-dataset.json. No real DB rows, release identity, import success, or eligibility acceptance was invented. Continue independent formula implementation using the approved synthetic oracles. Resume this ticket after the dependencies in docs/PEKERJAAN-LOKASI-DITUNDA.txt are resolved.

## Resumed 27 October 2026

The paragraph above is historical. Supabase migrations and TLS/PostGIS checks now pass. The user explicitly continued draft preparation/import after being told that review and publication are separate. `scripts/etl/prepare_draft_import.py` packages processed derivatives into private canonical batches below the 20 MiB importer limit, preserving source locators and unverified/missing statuses. Six format/hash-checked batches are prepared under `storage/app/private/imports/archives-draft-v2/`; their manifest pins five input files and batch hashes. Derived regency polygons union full district geometry; source observation years and values are preserved.

A temporary automation actor is explicitly named as such, receives only an import capability, and is deactivated after the operation; the token is revoked in cleanup. This is not human source/location acceptance. The first attempt rolled back because source observation_period was missing; corrected immutable batch version v2 supplies explicit period descriptions. Real import is now running. Final reconciliation and counts must be recorded before claiming completion.

Six focused Python tests pass: missing CSV baseline is never filled from the workbook; coordinate order is retained; missing/duplicate/nonfinite/out-of-range baseline candidates fail closed. All canonical files passed the existing PHP importer reader. Original Archives files remain untouched.

All six database batches subsequently succeeded. Final import reconciliation matched 973 facilities, 666 districts, 38 regencies and 666 indicator rows, with zero facility identity/coordinate mismatches or indicator value/year mismatches. The source locations remain 565 unverified and 408 missing. Import credentials were revoked and the automation account disabled. See [actual reconciliation](rekonsiliasi-pasca-impor.md). A private draft analysis is running; publication remains gated by genuine source/location acceptance and the existing validation/backup requirements.


## Verified private analysis ? 28 October 2026

The database confirms analysis `b08c7a1b-426f-4658-9438-25edbb2195fe` succeeded for draft `d3ca4b39-815a-5ea5-ad44-ca7867d825be`: 666 indicator results, 1,998 coverage results, and five private (unsanitized) artifacts. All coverage results are unavailable, with no numeric coverage percentage and zero eligible locations. This preserves the distinction between unavailable coverage and zero coverage.

Post-analysis reconciliation confirms 973 facilities, 666 districts, 38 regencies, and zero identity/value/year mismatches. Coordinates remain 565 unverified and 408 missing. The temporary input was removed, automation accounts are inactive, and no live automation tokens remain. The release stays draft and the active public release remains null. Source/location acceptance and publication are not completed by this analysis.

Private evidence: `storage/app/private/imports/archives-draft-v2/analysis-result.json`, `analysis-verification.json`, and `reconciliation.json`. Implementation commit `379cb17f2a2e9cfe528e31951de6eeed36af0214` passed CI run `40482159998`. Earlier progress entries above are historical.
