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

## Analysis checkpoint

```powershell
php artisan gis:analyze RELEASE_UUID --run-id=RUN_UUID --threshold=30000 --code-revision=FULL_GIT_COMMIT --token-file=PRIVATE_TOKEN_PATH
```

Use a token with analyze ability and the worker connection. Explicit run UUID and 40-character code commit are required. Python defaults to .venv/Scripts/python.exe on Windows and python on Linux; GIS_PYTHON_BINARY can select an installed interpreter. The command prepares a hash-pinned private input, invokes the existing Python exporter, validates file hashes and geometry/metric contents, then calls restricted database persistence. It never invokes Python from a public HTTP request.

Same-input/parameter/code retries reuse the successful analysis identity and verify its existing files. A conflicting or corrupted directory is not overwritten. Failed exports or database transactions do not create a successful run; privately generated files may remain for diagnosis. Token expiry/revocation is checked again after export. No raw capability enters the Python command, input bundle, artifact manifest or audit output.

Validation/publish/rollback commands remain pending C3–C6. Analysis does not publish data or mark files publicly sanitized.
# Release validation

`php artisan gis:validate <release-uuid> --run-id=<run-uuid> --expected-revision=<revision> --reason="Evidence-backed acceptance reason" --token-file=<private-token-path>`

The token needs `validate`. The trusted CLI database login must be allowed to assume `gis_worker` and `gis_artifact_verifier`; web/runtime logins must not receive verifier membership. The command checks private file bytes/content before finalization; sending a manifest directly as worker/publisher is denied. Missing indicators or excluded points require explicit `--allow-partial` and the recorded reason. Zero eligible points, pending review decisions, stale inputs, inconsistent method/code, unverified sources and corrupt artifacts block acceptance. A successful result means `validated`, not published; no active pointer changes. No actual dataset acceptance has been performed.
