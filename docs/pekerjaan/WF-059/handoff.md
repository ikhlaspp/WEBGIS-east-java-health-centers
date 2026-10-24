# WF-059 handoff

Status: done for source acquisition. Selected boundary: licensed BPS/OCHA HDX COD-AB v01, actual geometry reference 2020-04-01, used only with explicit mixed-period labels. Read source-selection.md and selected-boundary-source.json. All 666 master district codes and 38 parents are present; one Perairan water object remains separate. Geometry and original names/properties are unchanged. The BIG 2026 candidate is unselected.

The 16 original master identity conflicts have exact 2023 Semester 1 BPS corroboration. The complete 38-parent BPS/PUM bridge also remains available. Historical source reuse terms, attribution, change notice and date labels are recorded; topology, coordinate validation and public release remain pending later work. Strictly aligned 2023 geometry is not claimed.

Private outputs: data/staging/historical-boundaries.json and data/staging/selected-boundaries.json. Reproduce using scripts/etl/boundaries.py --master-receipt <saved MFD receipt> --resolutions docs/pekerjaan/WF-059/identity-resolutions.json --hdx-member-receipt docs/pekerjaan/WF-059/hdx-member-receipt.json --hdx-catalog-receipt docs/pekerjaan/WF-059/hdx-catalog-receipt.json --output data/staging/selected-boundaries.json. --download-hdx performs a fresh bounded source acquisition. Keep raw data private.

63 Python tests pass. Identity-reconciliation commit 4fa5c2cd021db2c990d107dd6a9b72f45b84c184 passed hosted run 40052974836. This is a technical self-review, with no fabricated independent reviewer or owner acceptance. Next: WF-060 after this commit is pushed and verified.
