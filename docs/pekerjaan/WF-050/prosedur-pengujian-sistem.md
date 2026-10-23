# Prosedur pengujian sistem

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Prosedur untuk tester selain penulis modul; semua aplikasi test masih not_run. `prosedur-per-test.json` dan `cakupan-test.md` memetakan seluruh ID planning awal serta tambahan scraping/CLI/lifecycle ke setup, tindakan, expected dan bukti.

## Persiapan dan eksekusi

1. Checkout code_revision kandidat, install lockfiles, catat runtime/native versions. Provision PostgreSQL/PostGIS test kosong dan storage test; jalankan migration sebagai migrator, lalu putus koneksi migrator. Pastikan host/database bukan produksi dan label TEST/synthetic pada fixture.
2. Jalankan seed fixtures yang ditentukan per suite. Buat token/akun sintetis melalui provisioning test, bukan login milik produksi; catat IDs tanpa token plaintext. Mock sumber HTTP/tile/geocoder pada server lokal dengan delay/failure yang bisa dikontrol.
3. Jalankan test spesifik dari mapping WF-031 dengan working_directory root; capture exit code, stdout sanitized, assertions, SQL role actual, input/output hash dan elapsed. Contract runner harus tersedia sebelum claim test pass; missing runner=blocked.
4. Bandingkan actual terhadap expected versioned, bukan screenshot kosong. Fail → defect dengan langkah reproduksi, severity, code/data revision dan owner. Perbaikan→retest failed case serta regresi modul terkait; hasil awal tidak dihapus.
5. Catat matrix seluruh ID P0, P1 terpilih, out-of-scope dengan keputusan. Unknown/not_run/blocked tidak pass. Simpan report di docs/pekerjaan/WF-NNN, raw log besar private bila perlu.

## Prosedur spesifik lintas modul

Data: import F-DATA/F-CROSS twice; query IDs/counts/FK/provenance sebelum/sesudah; compare raw hash dan rejected row partition. Formula: jalankan same JSON vectors pada Python dan SQL reference; exact counts, ratio≤1e-9. Spatial: geodesic reference+invariants WF-042, native versions dan shapes disimpan. Jangan mengganti PostgreSQL dengan SQLite.

Permissions: gunakan koneksi login role runtime/worker/publisher nyata (bukan SET ROLE dari owner sebagai satu-satunya bukti). SELECT published/draft, DML tiap state, execute functions token cases, audit delete, Data API negative. Record current_user/session_user dan grants tanpa password. FK/immutability juga dites dengan direct SQL agar policy Laravel bukan satu-satunya proteksi.

Concurrency: dua koneksi publisher, barrier setelah read expected pointer version, execute publish berbeda kandidat; collect both transaction outcomes. Assert1success/1stale, pointer/run/report pair benar, satu successful audit/outbox, tidak ada child mutations. Inject failure sebelum audit dan sebelum commit; all rollback. Inject outbox failure sesudah commit; retry not duplicate and public context consistent.

Browser: deterministic fixture server; desktop/tablet/mobile widths360/768/1366; missing search, null vs zero, filter parent, point duplicate, legend breaks, tile/API fail and slow-A/fast-B; screenshot+assert data, not screenshot only. Test keyboard actual focus/Escape/return and popup HTML escaped. Sesi timeout/admin403/draft404/CSRF419 tested on isolated accounts.

Performance profile follows WF-025: desktop4core/8GB,10Mbps down/2up,100ms; map30cold browser navigations p95≤5s;20VU ramp1min steady5min with≥100samples per facilities/statistics/points/regions, mix30/25/25/20%,think1s. p95 each warm API≤800ms,error<1%. Record warm-up/cache separately and P02-COLD results. Tile/geocoder public never load-tested; provider real smoke single ordinary usage only. Record payload/vertices/simplification/version/device; mobile emulator not substitute actual device usability.

Recovery: restore DB+artifact checkpoint to empty isolated environment, verify hashes/count/FK/roles/pointer, smoke app/notebook; measure RPO≤24h/RTO≤4h including verification. Missing artifact deliberate case must fail. Repro: Colab clean runtime, locked module, fixture then sanitized release, rerun same inputs; table content exact and geometry within WF-042 tolerance, generated_at excluded from canonical content hash. HTML compared two browsers and API pinned release.

## Result record

test_id,requirement_ids,fixture_ids,revision,release_id,run_id,environment,db_role,steps,expected,actual,status,evidence_paths,started_at,finished_at,executor,defect_id,retest_of. Status not_run/passed/failed/blocked/not_in_scope_for_release. Secret sanitization before publish; never include auth headers/token/dump in Git. Gate criteria at WF-051; no target loosening after seeing outcomes without approved baseline change.
