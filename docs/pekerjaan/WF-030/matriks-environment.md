# Environment dan provisioning

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Ini pilihan desain; belum instalasi, provisioning, atau pembelian layanan.

| Environment | Runtime / data | Isolasi dan acceptance |
|---|---|---|
| Dev Windows Laragon | PHP 8.4 target, Laravel 13; Node 24 target; Python 3.12 venv; PostgreSQL/PostGIS lokal atau dev terpisah | .env lokal, fixture; tidak menggunakan produksi; verifikasi PDO pgsql/SSL dan query spasial |
| CI Linux | PHP 8.4, Node 24, Python 3.12; service PostgreSQL 17/PostGIS 3.5 sebagai target awal | DB fresh per job/roles non-owner; pin image digest saat provisioning; tidak memakai SQLite sebagai pengganti spasial |
| Staging | Build/revision/dependency sama produksi; dataset kandidat, storage staging | Project/database, account dan bucket terpisah; allowlisted akses UAT/load test |
| Produksi | Hosting PHP HTTPS/queue/cron, Supabase PG/PostGIS | Versi PG/PostGIS disamakan dengan CI setelah layanan dipilih; release immutable, backup dan operator nyata |
| Colab | Python runtime tersedia + environment compatible dengan lock Python3.12 | Jika runtime berbeda, bootstrap interpreter/venv teruji atau gagal jelas; tidak mengklaim Colab selalu 3.12 |

Pemeriksaan fase 1 menemukan PHP8.4.22 tanpa pdo_pgsql, Python3.10.6, Composer2.4.1 dengan peringatan deprecation; hasil itu bukan verifikasi hari ini. Sebelum WF-054/055 aktifkan driver yang cocok, update Composer kompatibel dan siapkan Python3.12 terisolasi. Tidak mengubah instalasi global dalam fase desain.

Laravel13 mensyaratkan PHP≥8.3 dan ekstensi dasar menurut [deployment resmi](https://laravel.com/framework/docs/13.x/deployment); driver PostgreSQL diperlukan tambahan untuk koneksi yang dipilih. Supabase [koneksi resmi](https://supabase.com/docs/guides/database/connecting-to-postgres) mendukung direct atau session pooler; desain memakai session mode bila IPv4-only, direct bila tersedia. Jangan mengubah ke transaction pooling tanpa review prepared statement/session state. TLS wajib, verify-full dengan CA/provider hostname tervalidasi saat setup; jangan menonaktifkan verifikasi untuk mengatasi error.

Provisioning: pilih layanan/region/versi → buat dev/test/staging/production terpisah → aktifkan extension dengan schema tetap `extensions` → role non-owner dan secret terpisah → migration → seed fixture → smoke SQL/PHP/Python/browser. CI DB sementara dibuat sebelum WF-056; WF-072 memverifikasi provisioning final. Jika Supabase tidak mendukung versi target, pilih versi yang didukung lalu pin CI dan bukti kompatibilitas bersama, bukan menyamakan asumsi dengan fakta.

Nama konfigurasi: APP_ENV, APP_URL, APP_KEY, APP_DEBUG, DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD, DB_SSLMODE, DB_SSLROOTCERT, WORKER_DB_*, PUBLISHER_DB_*, PRIVATE_STORAGE_ROOT, PUBLIC_ARTIFACT_GATEWAY, SOURCE_CACHE_DIR, SESSION_LIFETIME, OPERATOR_TOKEN_FILE. Nilai rahasia tidak disertakan. Publisher variables hanya pada proses CLI terkontrol, bukan web worker.
