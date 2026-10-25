# Non-owner role verification

2026-10-25. GitHub run40173430238 success: https://github.com/ikhlaspp/WEBGIS-east-java-health-centers/actions/runs/40173430238.

25 DatabaseAccessTest cases plus19 DatabaseConstraintsTest cases executed on isolated real PostgreSQL/PostGIS. Each role test uses SET LOCAL ROLE and asserts current_user, rolsuper=false and rolbypassrls=false. Tests exercise effective non-owner permissions; they do not claim independently provisioned login credentials. CI explicitly creates anon/authenticated roles so deny paths run. Fixtures are synthetic and rolled back.

Passed: runtime hides drafts and their shared geometry/source; published rows visible without recursive RLS; withdrawal immediately hides data; worker draft edits and policy edits increment revision; published inputs cannot be edited; publisher can read candidate reports. Denied with SQLSTATE42501: runtime staging/tokens/private paths/reviews/domain updates/TRUNCATE; worker publication/revision/quality-pass/review-acceptance/selected-review writes; publisher publication/pointer/audit mutations; anon domain and authenticated app-user reads. Runtime is not a member of lifecycle owner.

All application, Python and browser CI steps passed. Live development/Supabase deployment and later trusted action functions remain pending their own tasks; no location-quality gate or release acceptance was fabricated.
