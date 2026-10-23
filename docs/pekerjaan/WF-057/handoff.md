# WF-057 handoff

Status: done. Acquisition and parsing are implemented and verified against both actual source PDFs and synthetic failure fixtures. Inputs: accepted WF-037 adapter contract, the completed Python environment, approved 2024-S1 source and Archives. No original archive was changed.

Output: private raw hash-addressed snapshots and receipt manifests, staging JSON with every source locator/raw field, synthetic committed output sample and parser log. Both PDFs produce the same 973 records/38 kabupaten-kota and exact categorical counts; no duplicate/quarantined rows. Coordinates remain unverified.

Source downloads use an explicit official host allowlist, public DNS checks, bounded redirects/retries and size/type checks. The CLI cannot overwrite Archives. Tests: 16 parser/source cases passed. Git delivery and remote commit SHA are reported in the conversation; WF-056 hosted success/failure evidence is carried in this commit.

Next: WF-058 indicator acquisition/parser; do not confuse parser completeness with final research dataset acceptance.
