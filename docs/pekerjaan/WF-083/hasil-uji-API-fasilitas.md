# Facility API validation

26 October 2026. `php artisan test --compact tests/Feature/FacilityApiValidationTest.php tests/Feature/FacilityApiTest.php`: exit 0, 15 local validation cases passed / 75 assertions; six database cases skipped locally because the disposable PostGIS test environment is CI-only. Pint and `git diff --check` passed. Database verification is pending, not claimed complete.

Database cases cover missing-coordinate list/detail, sanitized provenance and runtime privileges; filtered totals, pagination and stable ties; literal percent/underscore/escape characters and SQL-injection strings; parent mismatch; unpublished/wrong-run/not-found cases; same facility code in two published releases. Actual synthetic list/detail responses are captured to `reports/facility-api.json` and uploaded as a CI artifact.

List search uses bound parameters and explicit literal wildcard escaping across name/code/address. Sort columns come from an allowlist. All list/detail requests resolve a published release and its succeeded analysis run before querying facilities. Missing points remain represented with null location. Source references are resolved through the existing safe source catalog, not raw/private records.
