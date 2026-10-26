# Lifecycle implementation handoff

WF-086 is in progress and is not complete until all six checkpoints pass. C1 adds expiring operator capability issuance/revocation and a database-enforced review transition. Existing import and analysis preparation components remain in place; analysis finalization, validation, publish, rollback and complete lifecycle concurrency testing still need integration.

Review decisions are never inferred for actual Archives coordinates. Tests use isolated synthetic fixtures. No migrations, capability issuance, review or publication commands were executed against the connected Supabase project. Its TLS read/write probe succeeded previously, but PostGIS/application schema and permanent local PDO configuration remain separate deployment prerequisites.

C1 locks draft release before review/facility rows, checks expected input revision and candidate ownership, requires facility-level evidence and an explicit facility-point confirmation for acceptance, verifies point containment in the assigned district, derives actor from the token row, and writes immutable audit in the same transaction. Outside-boundary candidates cannot be forced through this path. Reviewed evidence is immutable; corrections require a new pending candidate. Operation UUID retries return the prior result only for the same actor/request.
