# Revised requirements decisions for acceptance

Status: accepted by the project owner on 2026-10-23T18:28:39+07:00. Read with SRS-baseline.md and the earlier requirements package. No data completion, external review, or historical approval is claimed.

## Concrete scope

- Preserve the proposal's 973 registered facilities for Semester I 2024 across 38 East Java kabupaten/kota. Archives remains the primary input collection, with originals unchanged.
- Deliver the facility register, population/area indicators, verified-location map, choropleth, geometric radius analysis, Colab notebook and interactive HTML/WebGIS. Keep the agreed Laravel/Leaflet and Supabase implementation, guest access, and authenticated administrative commands.
- The proposal explicitly requires a kabupaten/kota choropleth. Retain the more detailed kecamatan-level contracts already designed under WF-G3; do not silently remove their tests or substitute kabupaten boundaries for kecamatan analysis. Acquire suitable boundaries at the levels actually used.
- Defer the four optional release features individually: batch dashboard (WF-097), review/publish graphical interface (WF-098), public CSV download (WF-099), and ranking (WF-100). Administrative commands, review evidence, published tables, and research exports remain required. These deferrals are effective; downstream checkpoints record deferred rather than completed implementation.
- Keep routing, travel-time analysis, patient data, and automated siting recommendations outside this release. Radius means geometric distance, not measured travel access or population served.

## Data requirements and implementation actions

| Item | Accepted decision | Completion condition and owner |
|---|---|---|
| Initial records | Reuse Archives; retain missing-location facilities in the administrative register | Implementation/owner reconcile counts, names, source identifiers, and duplicates |
| Boundary geometry and region codes | Research and obtain suitable free official datasets; prefer an edition compatible with the historical snapshot | Before dependent spatial implementation, document source, edition, usage terms, codes, island coverage, and joins; a newer edition requires an explicit documented mapping and limitation |
| Coordinates | Verify the 565 existing candidate pairs and investigate the 408 missing pairs | Implementation/owner retain evidence and status per facility; never replace a missing facility with a region centroid |
| Geocoding | Start with official location evidence and manual candidate review; no paid or unrestricted bulk provider is assumed | Select a batch service only if its usage terms, limits, and zero-cost constraint permit the intended use; otherwise keep manual review and missing statuses |
| Population and area | Reconcile existing spreadsheets with their BPS tables; retain true observation years and units | Target the existing 2023 reference where supported; declare mixed-year observations and unresolved mappings; never relabel file year as observation year |
| Coverage | Permit a labelled partial demonstration while data is incomplete | Only verified eligible points enter buffers; show the eligible/total count; complete coverage may be claimed only when supported by actual data |

Partial demonstrations do not automatically satisfy a requirement for a complete 973-facility final analysis. Retain that completion objective. Any final reduction of academic coverage must be explicitly recorded and, where required by the college, agreed with the lecturer. Missing mandatory boundary geometry still blocks the first implementation task that needs it; do not skip that task.

## Accepted process revision

This accepted supplement freezes the required outcomes and data acceptance rules while allowing the exact boundary download/edition, code reconciliation, and coordinate evidence to be completed during the existing data-acquisition/curation tickets. This explicitly changes the earlier gate rule that required those source decisions before WF-G2 acceptance. It does not declare the datasets ready, waive source permissions, or alter the accepted geometry contracts without a later reviewed change.

This acceptance authorizes reconciling the SRS/scope registers, affected checkpoint blockers, and manifests against this decision. Preserve the history of the earlier pending gates and the already recorded WF-G3 acceptance; do not backdate approvals.

## Recorded decision

The owner approved applying the revised packages with "ok push it, then make change of it", following presentation at commit 68ca3b9b5667f640d66df2e6e39f8871690de0f7. Project-owner acceptance is recorded now; lecturer approval is not claimed.
