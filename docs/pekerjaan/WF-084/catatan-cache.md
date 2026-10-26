# Release-aware cache

Payload keys hash an explicit schema version, release UUID, succeeded run UUID, boundary UUID, endpoint and sorted validated query parameters. Keys include metric, geometry detail, radius, bbox and all accepted filters. TTL is 300 seconds. Omitted versus explicit default parameters may create equivalent separate entries; they cannot mix different results.

Every request resolves published visibility and matching run before accessing the cache. Region/parent validation also precedes cache access. Fresh response metadata is assembled after retrieval; request IDs and visibility are never cached. Withdrawn data therefore returns 404 even when its old payload remains cached. Cache-Control remains no-cache/must-revalidate at the HTTP boundary.

Point counts are computed before bbox, then bbox selects only visible points. No page limit is applied. Administrative endpoints reject service/coordinate filters. District thematic values read stored metrics; regency metrics and statistics use totals, not averages of district ratios. Deficit sums district deficits. Missing population/area remains null with a partial label.

Stored display boundary geometry is used when available; otherwise full geometry is explicitly labeled. Coverage currently returns stored full geometry for either requested detail, explicitly labeled as fallback. No runtime simplify, buffer, polygon union, Colab call or geocoding is performed. Shared persistent cache provisioning for multiple deployment instances remains deployment work.
