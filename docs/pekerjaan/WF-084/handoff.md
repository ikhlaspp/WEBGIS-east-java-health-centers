# Map and statistics API handoff

Implements WF-084 from the ticket preserved on main and the WF-045 API contract. PublicMapData reads stored results using the published release/run context. MapController, StatisticsController, MapStatisticsRequest and ReleaseCache serve four GET endpoints. PublicMapData performs lightweight aggregate sums/ratios for administrative summaries, never spatial buffer generation or geocoding.

Actual data review/import and Supabase setup remain deferred as listed in `docs/PEKERJAAN-LOKASI-DITUNDA.txt`. All integration examples are synthetic. No Archives changes or actual publication took place. Next: verify the isolated CI run, then WF-085.
