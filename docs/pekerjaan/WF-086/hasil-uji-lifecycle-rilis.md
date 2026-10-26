# Lifecycle checks — C1 progress

Local: `php artisan test --compact tests/Feature/OperatorTokenValidationTest.php tests/Feature/LocationReviewAuthorizationTest.php` passed three local cases / six assertions and skipped eight isolated database cases. Pint and whitespace checks passed.

Pending CI cases cover evidenced acceptance and exact retry, actor/token audit without raw token leakage, wrong/expired/revoked/wrong-ability/inactive credentials, stale revision, wrong facility, missing evidence, unconfirmed precision, outside-boundary point, rejected evidence immutability, runtime/publisher EXECUTE denial, worker direct-write denial, frozen release rejection, and private token issuance/revocation. No actual dataset review was performed.

C2–C6 remain pending. C1 verification alone is not full lifecycle acceptance.

Initial CI 40281498309 passed 161 application cases but exposed use of SQLSTATE 40001 for a logical stale-revision conflict. Laravel treats 40001 as a serialization/deadlock error and changes nested transaction handling. Review conflicts now use explicit domain SQLSTATE P4090; the regression retains the expected rejection and verifies subsequent reads/requests see unchanged state. Retest required. This migration has not been applied to the real Supabase database.

C1 retest: full CI 40282014248 succeeded on 7f4b9f4; revision conflict correctly rolls back and does not invoke deadlock handling.

## C2 analysis verification

Local `php artisan test --compact tests/Feature/OperatorAnalysisValidationTest.php tests/Feature/OperatorAnalysisTest.php`: two validation cases passed / five assertions, nine database integration cases skipped locally. Pint and whitespace checks passed. Pending isolated CI covers real Python export followed by restricted persistence, same/different run-ID idempotency, audited actor identity, private artifact registration, valid-point monotonic coverage, wrong ability before export, Python executable failure, tampered artifact retry, direct function recomputation despite forged submitted result values, forbidden runtime/publisher calls, stale revision, and injected midway failure with complete database rollback.

Tests use synthetic data and isolated storage paths, removed after each case. No live Supabase schema/data or actual review decision was changed.

C2 retest: application and Python jobs in CI 40317265675 succeeded on f6b6df88d9fe0ca24d462ab88d2d779b2945069d. The integration run covers all nine operator analysis cases listed above. Corrections explicitly qualify the PostGIS overlap operator under the restricted search path and grant the lifecycle function owner SELECT on regency id/code only. The adversarial recomputation fixture supplies distinct unverified artifact hashes so the existing uniqueness constraint does not prevent exercising its intended recomputation assertion; its artifacts must still remain unsanitized. No production constraint or expected scientific result was relaxed.

C1 and C2 are verified. C3 validation, C4 publication, C5 rollback and C6 lifecycle integration remain pending; WF-086 is not complete.
# C3 validation verification

C4 full retest: CI 40365612170 succeeded on 616f33c9bf22a8e626c72f3f92aeb2a0c9799d1b, including application/PostGIS, Python and browser checks. Frozen verification no longer requests draft-only locking reads; draft preparation still locks inputs.

C5 local verification: three lifecycle input/CLI tests passed; ten rollback DB cases plus nine publication regressions skipped locally pending CI. Rollback tests cover two actual synthetic release versions, historical immutability, implicit/explicit context, retries, invalid targets/capabilities/files/version, atomic outbox failure, direct-role denial and both orders of a publish/rollback race with a second PDO connection. No actual Supabase data was changed.

C4 local checks: two publication input/CLI tests passed; nine PostGIS cases skipped locally pending isolated CI. Cases cover atomic publish and exact retry, fresh public context, artifact tampering, wrong ability, stale pointer, missing acceptance, injected outbox failure, conflicting operation reuse, repeat publication, role denial and a competing PDO connection blocked on the pointer lock. Pint and whitespace checks passed. No production publication was attempted.

Local targeted tests: two input/CLI tests passed, nine PostGIS cases skipped locally, Pint and whitespace checks passed. Isolated CI pending: real Python files plus explicit partial scope freeze; atomic report/audit; frozen input denial; tampered file, stale revision, wrong ability, zero eligible points, missing explicit partial acceptance, wrong run, injected audit failure; runtime/worker/publisher direct attestation denial. No live Supabase schema or research data was changed.

C3 retest: application and Python jobs succeeded in CI 40320631163 on 74e659d085c838a3cbb80dd3f1a255a3987a410a. All nine isolated DB cases above passed, including injected audit failure rolling back the quality report and candidate status. C1-C3 are verified; C4-C6 remain pending.
