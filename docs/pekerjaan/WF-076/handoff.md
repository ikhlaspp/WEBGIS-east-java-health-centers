# Handoff

WF-076 is blocked by the intentionally deferred WF-071 quality report and missing WF-072 deployment credentials. Inputs are pinned in manifest-kandidat-dataset.json. No real DB rows, release identity, import success, or eligibility acceptance was invented. Continue independent formula implementation using the approved synthetic oracles. Resume this ticket after the dependencies in docs/PEKERJAAN-LOKASI-DITUNDA.txt are resolved.

## Resumed 27 October 2026

The paragraph above is historical. Supabase migrations and TLS/PostGIS checks now pass. The user explicitly continued draft preparation/import after being told that review and publication are separate. `scripts/etl/prepare_draft_import.py` packages processed derivatives into private canonical batches below the 20 MiB importer limit, preserving source locators and unverified/missing statuses. Six format/hash-checked batches are prepared under `storage/app/private/imports/archives-draft-v2/`; their manifest pins five input files and batch hashes. Derived regency polygons union full district geometry; source observation years and values are preserved.

A temporary automation actor is explicitly named as such, receives only an import capability, and is deactivated after the operation; the token is revoked in cleanup. This is not human source/location acceptance. The first attempt rolled back because source observation_period was missing; corrected immutable batch version v2 supplies explicit period descriptions. Real import is now running. Final reconciliation and counts must be recorded before claiming completion.

Six focused Python tests pass: missing CSV baseline is never filled from the workbook; coordinate order is retained; missing/duplicate/nonfinite/out-of-range baseline candidates fail closed. All canonical files passed the existing PHP importer reader. Original Archives files remain untouched.
