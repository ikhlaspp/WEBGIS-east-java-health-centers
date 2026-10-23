# Review, commit dan CI

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

Preferensi pengguna: satu commit per item, judul deskriptif tanpa ID tiket; pengiriman ke origin/main dengan identitas Git pengguna. Planning tidak di-stage. Instruksi lanjut mengotorisasi progress checkpoint meskipun review eksternal belum tersedia; commit bukan accepted otomatis. Tidak menambah Co-authored-by AI. Pada tahap kolaborasi besar, branch singkat dapat dipakai tetapi tidak mengubah target tanpa kebutuhan.

Sebelum commit: periksa scope diff, secret dan dump, jalankan pemeriksaan relevan, catat expected/actual. Stage hanya folder/file item. Push fast-forward dan verifikasi SHA remote/ancestor. Jika rejected karena remote maju, fetch/integrasikan dan retest yang relevan; jangan force-push progres biasa.

CI dari root repo: PHP `composer install --no-interaction`, `composer check-platform-reqs`, `php artisan test`; JS `npm ci`, `npm run build`, `npx playwright test` sesuai suite; Python install lock lalu `python -m pytest tests/python`; SQL assertions via psql test role/DB. Token CI tidak dapat mengakses produksi. Sintaks pipeline final mengikuti runner yang tersedia pada WF-056, bukan klaim pipeline sudah berjalan.

Perubahan rumus/ETL/geometry menjalankan fixture, replay deterministik dan SQL/Python reference. API/UI menjalankan contract/browser smoke. Grants/lifecycle menjalankan allow/deny non-owner, race dua koneksi dan rollback audit. Teks saja cukup tautan/struktur tanpa full load test. Semua P0 suite, performance/restore/repro/UAT dijalankan saat release candidate; P1 deferred ditandai out-of-scope, bukan passed.

CI PostgreSQL/PostGIS ephemeral tersedia sebelum WF-056; koneksi migrator membuat schema, lalu pengujian menggunakan runtime/worker/publisher yang berbeda. Laporan menyebut engine version, revision, input hashes, status dan log sanitized. Reviewer manusia dan acceptance dicatat nyata; hasil mandiri Codex tetap diberi nama demikian.
