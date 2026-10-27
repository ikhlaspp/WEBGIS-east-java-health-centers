# Operator lifecycle handoff

All six WF-086 implementation checkpoints are complete. Full CI 40413199874 succeeded on a80b9bce99bb57d053538b1087ddd758600e44e9, including application/PostGIS, Python and browser checks. Continue with WF-087, the Indonesian public dashboard and navigation. This completion covers code and synthetic verification, not acceptance or publication of actual research data.

The workflow is available through the [operator command guide](panduan-command-admin.md): evidence review, Python analysis, quality validation, backup verification, atomic publication, historical rollback and committed event delivery. Operators use expiring capability files; raw tokens never enter arguments, Python inputs, artifacts or audit records. Issuing/revoking capabilities requires the separate privileged provisioning connection.

| Checkpoint | Implemented behavior | Verification |
|---|---|---|
| C1 review | Actor/token attribution, evidence ownership and facility precision, containment, expected input revision, immutable decisions, exact operation retry | CI 40282014248 |
| C2 analysis | Hash-pinned Python input; private file verification; database recomputation; atomic successful run/results/audit; retry and failure rollback | CI 40317265675 |
| C3 validation | Current run/revision/method/code, source/eligibility checks, explicit partial-scope reason, verified private bytes, immutable quality report and candidate freeze | CI 40320631163 |
| C4 publication | Pointer-then-candidate locks, expected pointer version, report/run/artifact rechecks, atomic status/pointer/audit/outbox, exact retry | CI 40365612170 |
| C5 rollback | Restore a different previously published, non-withdrawn release; preserve both historical records; atomic pointer/audit/outbox; both publish/rollback race orders | CI 40368726652 |
| C6 integration | Actual authorized review-to-analysis-to-validation-to-publish/rollback flow, committed cache-event delivery, backup freshness and installation binding | Full CI 40413199874 passed |

## Security and deployment boundaries

- Runtime/worker/publisher roles cannot directly write trusted review, analysis, acceptance, publication or backup state. Finalizers authenticate the required capability again inside PostgreSQL.
- File acceptance requires a trusted CLI login allowed to assume both worker and the NOLOGIN artifact-verifier role. Do not give verifier membership to a web/runtime login. The database cannot inspect local files; the trusted service verifies them before calling the restricted finalizer.
- Frozen input verification uses ordinary reads because PostgreSQL applies the worker's draft-only update policy to locking reads. Draft preparation still locks inputs. Publication and rollback acquire pointer before candidate locks; domain version conflicts use P4090, not serialization/deadlock SQLSTATE 40001.
- C2 artifact records remain private and immutable with sanitized=false. C3 records the checked inventory in an immutable acceptance report. No public artifact-download route was introduced.
- New publication requires immutable backup evidence completed within 24 hours, bound to the database name and installation UUID. `gis:verify-backup --context` provides these identifiers. Verification checks actual private file sizes/hashes; it does not create backups or certify semantic completeness/restore success. Historical rollback and exact publication retries do not create a new publication.
- The outbox dispatcher requires publish capability and a standalone transaction. Claims expire after 60 seconds, stale acknowledgements are fenced by attempt number, and failures back off for 30 seconds. Release/run cache generations change only after a committed claim. Active pointer and release visibility always come from fresh database reads, including when delivery is delayed or fails.

## Evidence and remaining real-data work

Tests use the dedicated loopback gis_schema_testing database and synthetic private files. Committed concurrency fixtures are removed only in that database; the immutable installation identity is preserved. No migrations, real review decisions, data imports, backup capture, publication or rollback were run against Supabase in this checkpoint.

The previous TLS connection and temporary-table write probe succeeded, but real PostGIS/schema provisioning and dataset acceptance remain separate deployment prerequisites. Archives location review remains explicitly deferred. The single follow-up file is [PEKERJAAN-LOKASI-DITUNDA.txt](../../PEKERJAAN-LOKASI-DITUNDA.txt). Backup capture, storage retention/offsite policy and the restore drill remain deployment work; synthetic CI evidence does not satisfy them.

Code is on work/continued-implementation. Current implementation commit: a80b9bce99bb57d053538b1087ddd758600e44e9. Preserve unrelated user files such as ss.jpeg. The next ticket's expected targets are resources/views/layouts/app.blade.php, resources/views/home.blade.php and resources/css/app.css, with browser checks at 360/768/1366 pixels and no-release/API-failure states.
