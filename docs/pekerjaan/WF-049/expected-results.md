# Expected results dan penolakan

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

| Case | Expected |
|---|---|
| Duplicate release/facility code | Unique violation; jumlah master tidak bertambah |
| Same district name different regency | Dua district tetap terpisah; mapping tanpa parent rejected |
| Foreign boundary district | Composite FK violation, bukan diterima lalu salah polygon |
| Selected review milik code/release lain | FK/constraint failure |
| Verified tanpa evidence/precision/reviewer | Rejected, bukan eligible |
| Location tidak sama candidate selected review | Deferred constraint failure saat commit |
| Null P vs zero P | Need/deficit null versus0; without_facility tetap berdasarkan F |
| Invalid negative/A0/T0 | Validation error; tidak clamp/abs |
| F-RATIO aggregate30000/1+90000/2 | Ratio40000 exact; bukan37500 |
| Facilities tanpa koordinat | Tetap pada table/master dan denominator F; tidak point marker |
| Zero eligible tapi master ada | Coverage unavailable/null, bukan0% |
| Overlap buffer | Union tidak double-count; clip≤region area |
| Point boundary/pulau | Boundary diagnostic includes covers; pulau tidak hilang; eligibility tetap evidence |
| Worker publish/direct status/audit deletion | Permission denied; pointer unchanged |
| Runtime read draft/source privat | No rows/404; tidak bocor lewat cache atau artifact path |
| CLI token palsu/expired/ability salah | Denied; no successful audit event/transition |
| Dua publish expected version sama | Tepat satu successful transition+audit/outbox, satu409 stale |
| Crash sebelum commit | Status/pointer/audit sukses semuanya rollback |
| Crash sesudah commit sebelum cache | DB tetap committed; outbox retry, fresh visibility/context tetap benar |
| Partial download/HTTP200login | Incomplete/content mismatch; no promotion |
| Duplicate input idempotency | Existing job/result returned; no duplicate rows |
| Rapid filter A slow B fast | Hanya B dirender; release/run consistent |
| Withdrawn cached release |404/gateway denied walau cache bytes masih ada |
| Restore DB tanpa artifact | Drill fail, bukan RTO sukses |
| Colab changed hash/dependency | Run stops; no latest fallback |

Spatial tolerances mengikuti WF-042; data IDs/counts exact. Formula vectors termasuk expected density/ratio/need/deficit/flags disediakan JSON. Semua case ini not_run pada aplikasi. Phase design hanya memvalidasi konsistensi fixture/kontrak dan arithmetic independen; SQL constraint/security/browser tests menunggu implementasi nyata.
