# Struktur kode dan kontrak modul

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Path berikut target pembangunan, belum file aplikasi tersedia.

| Lokasi | Tanggung jawab / kontrak | Owner peran |
|---|---|---|
| app/Http/Controllers/Api, Requests, Resources | Parse allowlist, panggil service, bentuk respons; tanpa rumus bisnis di controller | BE |
| app/Services/ReleaseContext.php | Pilih rilis/run published sekali; validasi pasangan dan visibility sebelum cache | BE |
| app/Services/ReleaseLifecycleService.php, ReleaseAuditService.php | Enam checkpoint review/analyze/validate/publish/rollback/audit; transaksi khusus publisher | BE |
| app/Services/StatisticsService.php | Baca hasil run/aggregate; denominator administratif, bukan filter marker | BE/DG |
| app/Policies, Middleware, Console/Commands | Auth/policy/session dan CLI token terikat actor/ability | BE |
| database/migrations | Schema/tabel/FK/grants/RLS/functions satu sumber migrasi | BE |
| scripts/etl, scripts/analysis | Entry points kecil ke paket `gis_pipeline`, bukan salinan algoritma | DG |
| python/gis_pipeline | adapters, normalize, quality, coordinates, indicators, spatial, manifests, exports | DG |
| resources/views, resources/js/map | Blade dan modul state/requests/layers/legend, escape popup | FE |
| notebooks | Orkestrasi input/run/export menggunakan paket Python terpin | DG |
| tests/data/wf-NNN | Fixture sintetis milik item, schema manifest dan expected | QA |
| tests/Feature, tests/Unit, tests/Browser, tests/python, tests/sql | PHPUnit, Playwright, pytest dan assertions role/spasial | QA/BE/DG |
| data/raw, data/staging, data/processed | Penyimpanan lokal/private terpisah Git; raw hash immutable | DG/OP |
| docs/pekerjaan, docs/runbooks | Desain, keputusan, bukti sanitasi; Planning lokal ignored | Semua |

Satu modul indikator Python menghasilkan hasil kanonik run; SQL reference independen untuk pemeriksaan dan view agregasi harus mengikuti method_version. Laravel tidak mengimplementasi formula alternatif di template. Boundary/input hashes dan JSON contract menjadi batas antarmodul; worker mengeluarkan manifest yang divalidasi sebelum import backend. Penyimpanan status job dan audit memakai ID yang konsisten.

Pemetaan seluruh 52 item implementasi tersedia di `pemetaan-implementasi.json` dan `pemetaan-implementasi.md`: file, test, runner, fixture, working directory. Target katalog dipertahankan; entry point Python diarahkan ke shared package. File target boleh belum ada pada desain, tetapi jalur/runner harus final sebelum pelaksanaan item. Data review manual memakai checkpoint per ≤25 kode dan tidak membutuhkan test palsu untuk menyatakan lokasi verified.
