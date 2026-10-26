# Lifecycle checks — C1 progress

Local: `php artisan test --compact tests/Feature/OperatorTokenValidationTest.php tests/Feature/LocationReviewAuthorizationTest.php` passed three local cases / six assertions and skipped eight isolated database cases. Pint and whitespace checks passed.

Pending CI cases cover evidenced acceptance and exact retry, actor/token audit without raw token leakage, wrong/expired/revoked/wrong-ability/inactive credentials, stale revision, wrong facility, missing evidence, unconfirmed precision, outside-boundary point, rejected evidence immutability, runtime/publisher EXECUTE denial, worker direct-write denial, frozen release rejection, and private token issuance/revocation. No actual dataset review was performed.

C2–C6 remain pending. C1 verification alone is not full lifecycle acceptance.
