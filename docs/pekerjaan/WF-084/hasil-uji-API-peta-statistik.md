# Map/statistics API checks

26 October 2026. Local command: `php artisan test --compact tests/Feature/MapStatisticsValidationTest.php tests/Feature/MapStatisticsApiTest.php`. Exit 0: 17 validation cases, 68 assertions; five database integration cases skipped locally, pending disposable PostGIS CI. Pint and `git diff --check` passed.

Validation covers invalid/degenerate/wrapping/out-of-range/nonfinite bbox, marker pagination rejection, invalid metric/radius/detail/run UUID, missing district parent, and rejection of marker filters by statistics.

Integration tests create synthetic district facts and 61 facilities (60 unverified points, one missing), execute the real Python exporter and immutable database persistence, and publish only the isolated test fixture. Tests cover all 60 markers beyond the table default page size, bbox versus full filtered counts, missing points, search/parent validation, stored district density, administrative totals, all three stored buffer radii, unavailable geometry, missing population, two run thresholds, cache separation and withdrawal before cache hits. Captured responses are uploaded as `reports/map-statistics-api.json`.

This is implementation verification, not real dataset acceptance or deployment evidence.

First CI run 40269685439 passed four integration cases and all local validation cases, but exposed an incorrectly scoped withdrawal assertion: the test omitted release_id, asking for the active dataset after withdrawal (correct response 503), while expecting the pinned-release 404 contract. The regression now warms and reads the same explicitly pinned release/run cache key and asserts 404 after withdrawal, plus a separate 503 NO_PUBLISHED_RELEASE assertion for the implicit active request. Application behavior and contract are unchanged; rerun required.
