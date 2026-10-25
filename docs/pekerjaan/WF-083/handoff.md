# Facility API handoff

Continues the published-release context and runtime role from WF-082. Ticket instructions were read from `main:Planning/Waterfall/Tiket/04-implementasi/WF-083-WBS-4.7.2.md`; planning remains preserved on main. Existing contract: `docs/pekerjaan/WF-045/kontrak-API.md`.

Implementation: FacilityController, FacilityFilterRequest, FacilityResource, routes/api.php, and one additive column-grant migration. Runtime can read the two source reference UUIDs only on published facility rows; private source paths, source rows and review IDs remain inaccessible. Detail exposes source metadata only from the release-scoped public catalog; unavailable catalog metadata is null.

Synthetic fixtures only. No Archives edits, real data import, location acceptance, Supabase provisioning or publication was performed. Continue with WF-084 after CI verification. Deferred manual work remains in `docs/PEKERJAAN-LOKASI-DITUNDA.txt`.
