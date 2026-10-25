# Actual database grants

2026-10-25, commit5d19cbb456389ffe76275941aed4e23627539996. Runtime/worker/publisher/lifecycle roles are NOLOGIN capability groups, not provisioned deployment credentials. Runtime/worker/publisher are non-owner, non-superuser, NOBYPASSRLS, NOCREATEROLE, NOCREATEDB. Lifecycle owner owns narrowly scoped helpers only and is not granted to application roles.

Runtime: safe-column SELECT on published domain rows, successful runs and sanitized artifacts; referenced published source/boundary visibility; app auth SELECT and sessions/framework queue DML. Denied: draft rows, raw/private paths, geocode evidence, staging, operator tokens, domain writes, DDL/TRUNCATE, pointer/audit/status mutation.

Worker: reference/candidate reads, pending source/boundary/alias insertion, draft fact/facility/review/staging input edits. System trigger increments revision; direct writes to revision, passed/approved flags, review acceptance/reviewer, selected_review, analysis completion, publication and pointer are denied. Immutable evidence and frozen-input triggers remain active. Draft metadata edits also invalidate revision/report/run pointers.

Publisher: read candidate/report data; no arbitrary DML. Trusted token-bound transitions will be granted only when their controlled functions are implemented in subsequent import/lifecycle tasks. No broad substitute grants are issued now.

FORCE RLS: all gis/staging tables and active pointer. Definer helpers use pg_catalog search_path, qualified SQL, explicit owner policy and revoked PUBLIC execute. Anon/authenticated access to app/gis/staging is revoked when roles exist. Actual Supabase exposed-schema configuration and login membership must still be verified when accounts are provisioned.

Reference: PostgreSQL16 row-security and CREATE FUNCTION documentation. SQL inventory: tests/sql/role_access.sql. This access foundation does not claim completed operator-token CLI or publication functions from WF-086.
