# Fresh database migration verification

2026-10-25. Commit57e9ce05066007656dbd61e86c51b9aee6e61f4b, branch work/continued-implementation. GitHub run40169928192 completed successfully: https://github.com/ikhlaspp/WEBGIS-east-java-health-centers/actions/runs/40169928192.

CI created gis_schema_testing from template0 inside its disposable PostgreSQL16/PostGIS3.4 service. Laravel migrations ran on that empty database, installed PostGIS in extensions, created app/gis/staging tables, composite FKs, checks, deferred selected-review enforcement, revision/freeze/immutable-evidence triggers and spatial/filter indexes. Existing framework jobs/job_batches/failed_jobs moved to app using the same Laravel migration history. No source data imported and no Supabase/production database changed.

Original gis_testing remains independent for the connection smoke tests. Domain tests use synthetic fixture rows inside rolled-back transactions. Migration refuses an existing PostGIS extension in a different schema rather than silently moving provider-managed objects. Destructive down is intentionally disabled; reconstruction uses a new disposable database. The ordinary public starter auth tables remain legacy scaffold until application auth integration; domain auth tables are app.users/sessions/operator_tokens.

Live development provisioning is still pending actual private credentials. CI proof does not claim Supabase deployment, location review, quality acceptance or public release.
