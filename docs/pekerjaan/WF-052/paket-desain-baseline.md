# Paket desain kandidat

Versi kandidat1.0 · 23 Oktober 2026 · Penyusun: Codex. Mandat: pengguna meminta seluruh folder03. Terdapat24item WF-029–052; satu progress commit per item mengikuti preferensi sesi. Planning lokal tetap ignored. Belum ada keputusan stakeholder WF-G3 accepted.

| Domain | Desain normatif |
|---|---|
| Komponen/data flow | [Arsitektur](../WF-029/diagram-arsitektur.md), [alur](../WF-029/alur-data.md) |
| Environment/dependency | [Environment](../WF-030/matriks-environment.md), [locks](../WF-030/kebijakan-dependensi.md) |
| Modul/CI/handoff52items | [Struktur](../WF-031/desain-struktur-repositori.md), [CI](../WF-031/alur-review-CI.md), [mapping](../WF-031/pemetaan-implementasi.md) |
| Batch/error | [State](../WF-032/desain-job-batch.md), [retry](../WF-032/matriks-error-retry.md) |
| Data model | [ERD](../WF-033/ERD-final.md), [kamus](../WF-033/kamus-data-final.md) |
| Integritas/migration | [Constraints](../WF-034/spesifikasi-constraint-indeks.md), [urutan](../WF-034/urutan-migration.md) |
| Security/lifecycle/recovery | [Grants](../WF-035/desain-otorisasi-dan-grants.md), [lifecycle](../WF-036/desain-lifecycle-rilis.md), [restore](../WF-036/desain-backup-rollback.md) |
| Akuisisi/kurasi | [Adapter](../WF-037/spesifikasi-adapter-sumber.md), [crosswalk](../WF-038/spesifikasi-normalisasi-crosswalk.md), [review](../WF-039/prosedur-geocoding-review.md), [bukti](../WF-039/skema-bukti-lokasi.md) |
| Staging/quality | [Kontrak](../WF-040/kontrak-staging.md), [report](../WF-040/spesifikasi-laporan-kualitas.md) |
| Metode | [Formula](../WF-041/spesifikasi-formula.md), [acuan](../WF-041/contoh-acuan-formula.md), [spasial](../WF-042/spesifikasi-operasi-spasial.md) |
| Layer/penelitian | [GeoJSON](../WF-043/kontrak-layer-GeoJSON.md), [warna](../WF-043/spesifikasi-kelas-warna.md), [notebook](../WF-044/desain-notebook-dan-manifest.md) |
| API | [Kontrak](../WF-045/kontrak-API.md), [contoh](../WF-045/contoh-respons-API.json) |
| UI | [Publik](../WF-046/wireframe-publik.md), [review](../WF-046/catatan-review-wireframe.md), [state](../WF-047/spesifikasi-state-interaksi.md), [admin](../WF-048/wireframe-admin-dan-P1.md) |
| Uji | [Fixture](../WF-049/spesifikasi-fixture.md), [expected](../WF-049/expected-results.md), [prosedur](../WF-050/prosedur-pengujian-sistem.md), [UAT](../WF-051/skrip-UAT.md), [gate](../WF-051/checklist-gerbang-rilis.md) |

## Walkthrough integrasi dan keputusan teknis

Sumber bytes/hash→row envelope→crosswalk/source metadata→composite FK release/district/set→accepted selected review→run immutable params→report/hash→publisher lock+audit/outbox→APIcontext→UI pinned release→Colab sanitized same revision. Setiap boundary memiliki ID/schema/error path. `traceability-desain.json` menghubungkan17FR/8NFR ke item desain dan test IDs.

Konflik yang diselesaikan di desain: (1) role pengelola lama dihapus; (2) actor CLI tidak berasal flag bebas, memakai hashed capability token; (3) parameter T tidak memodifikasi run/rilis terbit; (4) active pointer memuat pasangan run/release; (5) audit dan outbox berada satu transaksi, visibility sebelum cache untuk withdrawn; (6) F administrative berbeda filter marker; (7) dictionary menambah composite FK dan review ownership; (8) API public memakai kode, bukan UUID `_id` ambigu; (9) CI PostGIS tersedia sebelum WF-056; (10) notebook memakai shared Python package dan independent spatial implementation teruji, bukan formula copy.

Semua adalah elaborasi teknis kandidat SRS, bukan persetujuan mengubah scope P0/P1. Target runtime dipilih untuk implementasi tetapi versi aktual Supabase/hosting perlu dicocokkan saat provisioning. P1 belum dipilih sehingga desain UI opsional tetap ditahan; tidak menandai fitur deferred resmi tanpa keputusan. Source edition/izin/budget dan reviewer eksternal tetap terbuka pada [gerbang](penerimaan-WF-G3.md).

Pemeriksaan desain lokal: files/links/JSON,52handoff targets,FR/NFR,test ID coverage,fixture arithmetic,APIcontext dan hash paket; laporan `verifikasi-desain.json`. Tidak ada migration, geospatial runtime, browser aplikasi, production publish atau UAT yang dijalankan. Input SRS dan paket desain dibekukan hash UTF8-LF dalam manifest agar perubahan review terlihat. Acceptance eksternal diperlukan untuk menyebut baseline accepted; progress Git tetap dikirim sesuai instruksi pengguna.
