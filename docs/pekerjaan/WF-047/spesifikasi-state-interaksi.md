# State dan interaksi UI

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

| State | Pemicu | Tampilan / transisi |
|---|---|---|
| bootstrapping | Buka aplikasi tanpa context | Fetch releases/active; belum tampil angka0; pilih release/run sekali |
| loading | Submit filter/metric/initial data | aria-live, spinner, keep previous data hanya dengan label loading/context lama; controls bebas cancel |
| success | Semua response current sequence valid | Atomik update markers/table/meta/legend untuk context sama |
| empty | Current request sukses dengan filter_total0 | Pesan filter kosong+reset; bukan dataset unavailable |
| error | Timeout/non2xx/invalid payload | Error code generik+retry; tidak overwrite valid data sebagai0 |
| no_release |503 NO_PUBLISHED_RELEASE | Belum ada dataset; tidak fallback draft |
| withdrawn |404 untuk pinned release | Bersihkan data lama, tawarkan pilih active; tidak silently campur |
| tile_error | Basemap request gagal | Banner; overlays/table usable jika data ada; retry tile terpisah |

State object {releaseId,runId,regionSelection,facilityFilters,metric,radius,geometryDetail,requestSequence,status}. Setiap perubahan filter menaikkan sequence; AbortController membatalkan request sebelumnya dan handler tetap memeriksa sequence+context sebelum commit UI. Promise abort bukan error pengguna. Responses yang berbeda release/run ditolak sebagai contract mismatch dan tidak dirender. Debounce search300ms; Enter memicu langsung. Contoh race slow A lalu fast B: hanya B boleh commit walaupun abort A tidak efektif.

Ganti kabupaten mereset district dan child options; parent options request juga sequence-guarded. Facility filter memengaruhi point/table saja; stats request region-only. Perubahan metric menahan legend lama berlabel loading sampai layer dan legend baru siap bersama. Bbox hanya marker viewport; statistik administrative tetap scope terpilih. Empty point layer dengan missing_count>0 bukan empty facility table.

Pinned context disimpan pada URL query atau sessionStorage scoped app, lalu divalidasi server; tidak menyimpan token admin. Poll/reload active catalog hanya memberi banner rilis baru. Klik Muat rilis baru membatalkan semua pending requests, reset context/cache client dan reload seluruh data; tidak mengganti setengah layer. Retry automatic GET maksimal1 setelah1s untuk transient503/network;429 mengikuti Retry-After; error validation tidak retry. Mutation tidak pernah retry browser tanpa idempotency/confirmation.

Keyboard: label associated form, native controls bila mungkin, focus visible; dialog focus trap/Escape/restore trigger; popup close reachable; skip to table. aria-live polite status, alert hanya gagal penting; tidak mengumumkan setiap tile. Focus tetap pada selector saat data berubah; no scroll-jump tiap search. Legend memiliki teks/units dan no-data pattern; semua pointer actions punya keyboard/tap equivalent.
