# Basic constraint verification

2026-10-25, CI run40169928192: application and Python jobs success. All19 DatabaseConstraintsTest cases execute against the dedicated real PostGIS database (RUN_POSTGIS_TESTS=1). Local run skipped19 because local PostGIS is absent; only CI establishes the database result.

Covered: fresh schemas/PostGIS namespace/empty active pointer/queue tables/spatial index; negative population and missing provenance; nonpositive area; verified without evidence; missing with a point; out-of-range longitude; empty/self-intersecting polygons and wrong SRID; duplicate facility; parent/fact cross-boundary FKs; matching accepted review succeeds; changing selected review point fails; another facility review fails; frozen release inputs and shared boundary changes fail; draft edits increment input_revision. Constraint failures assert SQLSTATE, so an arbitrary connection failure is not treated as a successful negative test.

Authorization/RLS, token-bound lifecycle transitions, release validation and publication races are the next task, not claimed tested here. Runtime has not been provisioned or granted domain access by this migration.
