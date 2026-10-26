# Internal operator commands — work in progress

Provisioning commands require a separate privileged connection and an active admin account. Runtime/worker/publisher roles cannot mint capabilities. Do not put raw tokens in command arguments, source control, logs or browser sessions.

```powershell
php artisan gis:issue-token admin@example.test --abilities=review --minutes=60
php artisan gis:revoke-token TOKEN_UUID
```

Issuance generates a 256-bit random capability, stores only its SHA256 in PostgreSQL, and writes the token to an exclusive private file under storage/app/private/operator-tokens. The file is restricted to its owner (POSIX mode 0600 or Windows explicit user ACL). Output contains only token ID, path, expiry and ability list. Maximum lifetime is eight hours. Revocation is idempotent.

```powershell
php artisan gis:review-location RELEASE_UUID FACILITY_CODE REVIEW_UUID accepted --reason="Evidence checked against the facility location" --expected-revision=REVISION --operation-id=OPERATION_UUID --token-file=PRIVATE_TOKEN_PATH --confirm-facility-point
```

For rejection use `rejected` and an explanatory reason; do not pass facility confirmation unless actually established. The candidate must already exist. Acceptance requires verified evidence source, facility precision, evidence URL or note+hash, and point containment in the assigned district. The command does not manufacture coordinates or evidence. Use the same operation UUID and identical arguments for a retry. A stale revision, changed operation request, expired/revoked/wrong-ability token or non-draft release is rejected atomically.

Analysis/validation/publish/rollback commands are pending C2–C6; this guide does not claim they are implemented.
