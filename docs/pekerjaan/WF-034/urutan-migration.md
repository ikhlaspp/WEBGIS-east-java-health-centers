# Urutan migration

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

1. Preflight DB test kosong, versi engine dan privileges extension; bootstrap role deployment (tanpa credential di migration). Buat schema app/gis/staging/extensions, PostGIS pada schema yang dipilih. Jika provider sudah menginstal di lokasi lain, hentikan dan sinkronkan konfigurasi qualified type/function; jangan install kedua kali membabi buta.
2. app.users/sessions/operator_tokens/jobs/failed_jobs; sumber dan boundary_sets; regencies lalu districts dan aliases.
3. dataset_releases tanpa FK quality/default; release_sources, fakta, facilities tanpa selected_review FK; reviews; tambahkan FK komposit siklik deferred.
4. analysis_runs, indicator_results, coverage_results, artifacts, batches/staging.rows dan quality_reports; tambahkan FK report/default ke releases.
5. active_release singleton kosong, audit/outbox; indexes/checks/triggers input_revision, selected review dan immutability.
6. Security functions dengan schema-qualified names, role owner tanpa LOGIN dan privileges minimum; revoke default PUBLIC execute, grant execute terpilih; RLS/grants/column permissions; freeze rules shared sources/boundaries.
7. Verify fresh migrate, negative inserts, runtime/worker/publisher deny tests, rollback pointer dan transaction failure. Seed fixture hanya environment test; jangan seed fasilitas sintetis sebagai produksi.

Satu migration history Laravel. SQL PostgreSQL khusus disimpan dalam migration versioned; tidak ada rangkaian Supabase schema kedua yang mengelola tabel sama. Migration role tersedia hanya deploy; runtime bukan owner.

Perubahan schema terbit memakai expand→backfill terverifikasi→switch reader→contract setelah backup dan kompatibilitas rilis lama. Down migration destruktif tidak menjadi mekanisme rollback produksi; gunakan redeploy compatible atau restore drill dengan persetujuan operasi yang berlaku. Unique/index besar dapat memakai CREATE INDEX CONCURRENTLY dalam migration nontransactional terpisah; saat dataset kecil, pilih transaksi biasa untuk kesederhanaan. Catat actual SQL/versions/test logs pada WF-073/074, bukan mengklaim desain ini sudah membuktikan enforcement.
