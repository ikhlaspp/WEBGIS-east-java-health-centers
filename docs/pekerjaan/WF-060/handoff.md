# WF-060 handoff

Shared HTTP transport and local batch checkpoints are implemented. See hasil-uji-ketahanan-scraping.md and checkpoint.json for actual tests and live cache/range checks. Resume is explicit, hash-verified and cannot bypass future Retry-After. Live source checks remain uncached; raw snapshots and original Archives remain unchanged. Batch success is separate from data-quality or publication acceptance.

The local acquisition worker is serialized; distributed database leases/outbox/publishing remain later tasks. Next: freeze the selected source set in WF-061 after final checks and verified Git delivery. Selected boundaries are the licensed 2020 BPS/OCHA reference with mandatory mixed-period labels, not the unselected BIG 2026 candidate.
