# Pemetaan implementasi dan verifikasi

Versi1 · 23 Oktober2026 · Penyusun Codex. Target file belum dibangun. Semua command dari root repo dengan runtime/locks WF-030; P1 hanya bila dipilih. Entry scripts Python memanggil shared package, bukan duplikasi algoritma.

| Item | Target | Runner / verifikasi | Fixture |
|---|---|---|---|
| WF-053 | `.gitignore`; `README.md` | repo: `git diff --check` | `tests/data/wf-053/` |
| WF-054 | `composer.json`; `package.json`; `routes/web.php`; `.env.example` | php: `php artisan test tests/Feature/HealthTest.php` | `tests/data/wf-054/` |
| WF-055 | `requirements.lock`; `notebooks/gis_puskesmas.ipynb`; `pyproject.toml`; `python/gis_pipeline/__init__.py` | python: `python -m pytest tests/python/test_environment.py -q` | `tests/data/wf-055/` |
| WF-056 | `.github/workflows/checks.yml`; `phpunit.xml`; `pytest.ini`; `playwright.config.js` | ci: `python -m pytest tests/python -q`; `php artisan test`; `npm run build` | `tests/data/wf-056/` |
| WF-057 | `scripts/etl/facilities.py`; `python/gis_pipeline/etl/facilities.py` | python: `python -m pytest tests/python/test_facilities_parser.py -q` | `tests/data/wf-057/` |
| WF-058 | `scripts/etl/indicators.py`; `python/gis_pipeline/etl/indicators.py` | python: `python -m pytest tests/python/test_indicators_parser.py -q` | `tests/data/wf-058/` |
| WF-059 | `scripts/etl/boundaries.py`; `python/gis_pipeline/etl/boundaries.py` | python: `python -m pytest tests/python/test_boundaries_source.py -q` | `tests/data/wf-059/` |
| WF-060 | `scripts/etl/http_client.py`; `scripts/etl/batch.py`; `python/gis_pipeline/etl/http_client.py`; `python/gis_pipeline/etl/batch.py` | python: `python -m pytest tests/python/test_scraping_resilience.py -q` | `tests/data/wf-060/` |
| WF-061 | `scripts/etl/acquire.py`; `data/raw/manifest.json`; `python/gis_pipeline/etl/acquire.py` | data: Seluruh sumber wajib tersedia atau memiliki keputusan pengganti yang diterima; unduhan parsial tidak diteruskan sebagai input lengkap. | `tests/data/wf-061/` |
| WF-062 | `scripts/etl/normalize.py`; `python/gis_pipeline/etl/normalize.py` | python: `python -m pytest tests/python/test_normalize.py -q` | `tests/data/wf-062/` |
| WF-063 | `scripts/etl/crosswalk.py`; `data/processed/crosswalk.json`; `python/gis_pipeline/etl/crosswalk.py` | python: `python -m pytest tests/python/test_crosswalk.py -q` | `tests/data/wf-063/` |
| WF-064 | `scripts/etl/reconcile_facilities.py`; `python/gis_pipeline/etl/reconcile_facilities.py` | python: `python -m pytest tests/python/test_reconcile_facilities.py -q` | `tests/data/wf-064/` |
| WF-065 | `scripts/etl/validate_indicators.py`; `python/gis_pipeline/etl/validate_indicators.py` | python: `python -m pytest tests/python/test_validate_indicators.py -q` | `tests/data/wf-065/` |
| WF-066 | `scripts/etl/validate_boundaries.py`; `python/gis_pipeline/etl/validate_boundaries.py` | python: `python -m pytest tests/python/test_validate_boundaries.py -q` | `tests/data/wf-066/` |
| WF-067 | `scripts/etl/geocode.py`; `data/staging/location_queue.json`; `python/gis_pipeline/etl/geocode.py` | python: `python -m pytest tests/python/test_geocode_queue.py -q` | `tests/data/wf-067/` |
| WF-068 | `data/staging/location_reviews.json` | data: Seluruh 565 kandidat mempunyai hasil review atau penghalang eksplisit; jumlah verified hanya menghitung bukti facility yang diterima. | `tests/data/wf-068/` |
| WF-069 | `data/staging/location_searches.json` | data: 408 kode memiliki catatan penelusuran; pencarian selesai tidak disamakan dengan 408 lokasi berhasil diverifikasi. | `tests/data/wf-069/` |
| WF-070 | `data/staging/location_anomalies.json` | data: Setiap anomali mempunyai keputusan berbukti; data tidak dideduplicate hanya berdasarkan koordinat. | `tests/data/wf-070/` |
| WF-071 | `scripts/etl/validate_eligibility.py`; `python/gis_pipeline/etl/validate_eligibility.py` | python: `python -m pytest tests/python/test_eligibility.py -q` | `tests/data/wf-071/` |
| WF-072 | `config/database.php`; `.env.example` | php: `php artisan test tests/Feature/DatabaseConnectionTest.php` | `tests/data/wf-072/` |
| WF-073 | `database/migrations/` | php: `php artisan test tests/Feature/DatabaseConstraintsTest.php` | `tests/data/wf-073/` |
| WF-074 | `database/migrations/`; `tests/sql/role_access.sql` | php: `php artisan test tests/Feature/DatabaseAccessTest.php` | `tests/data/wf-074/` |
| WF-075 | `app/Console/Commands/ImportDataset.php`; `app/Services/DatasetImportService.php` | php: `php artisan test tests/Feature/DatasetImportTest.php` | `tests/data/wf-075/` |
| WF-076 | `data/processed/`; `app/Console/Commands/ImportDataset.php` | data: Kandidat DB sesuai manifest kurasi dan semua referensi berada pada edisi wilayah/rilis yang tepat. | `tests/data/wf-076/` |
| WF-077 | `scripts/analysis/indicators.py`; `python/gis_pipeline/analysis/indicators.py` | python: `python -m pytest tests/python/test_indicators.py -q` | `tests/data/wf-077/` |
| WF-078 | `scripts/analysis/aggregates.py`; `python/gis_pipeline/analysis/aggregates.py` | python: `python -m pytest tests/python/test_aggregates.py -q` | `tests/data/wf-078/` |
| WF-079 | `scripts/analysis/buffers.py`; `python/gis_pipeline/analysis/buffers.py` | python: `python -m pytest tests/python/test_buffers.py -q` | `tests/data/wf-079/` |
| WF-080 | `scripts/analysis/coverage.py`; `python/gis_pipeline/analysis/coverage.py` | python: `python -m pytest tests/python/test_coverage.py -q` | `tests/data/wf-080/` |
| WF-081 | `scripts/analysis/export_layers.py`; `python/gis_pipeline/analysis/export_layers.py` | python: `python -m pytest tests/python/test_analysis_manifest.py -q` | `tests/data/wf-081/` |
| WF-082 | `routes/api.php`; `app/Http/Controllers/Api/ReleaseController.php`; `app/Http/Controllers/Api/RegionController.php`; `app/Http/Controllers/Api/SourceController.php`; `app/Services/ReleaseContext.php` | php: `php artisan test tests/Feature/ReferenceApiTest.php` | `tests/data/wf-082/` |
| WF-083 | `app/Http/Controllers/Api/FacilityController.php`; `app/Http/Requests/FacilityFilterRequest.php` | php: `php artisan test tests/Feature/FacilityApiTest.php` | `tests/data/wf-083/` |
| WF-084 | `app/Http/Controllers/Api/StatisticsController.php`; `app/Http/Controllers/Api/MapController.php`; `app/Services/ReleaseCache.php`; `app/Services/StatisticsService.php` | php: `php artisan test tests/Feature/MapStatisticsApiTest.php` | `tests/data/wf-084/` |
| WF-085 | `routes/web.php`; `app/Http/Controllers/Auth/`; `app/Policies/`; `config/session.php` | php: `php artisan test tests/Feature/AdminAuthenticationTest.php` | `tests/data/wf-085/` |
| WF-086 | `app/Console/Commands/`; `app/Services/ReleaseLifecycleService.php`; `app/Services/ReleaseAuditService.php` | php: `php artisan test tests/Feature/ReleaseLifecycleTest.php` | `tests/data/wf-086/` |
| WF-087 | `resources/views/layouts/app.blade.php`; `resources/views/home.blade.php`; `resources/css/app.css` | browser: `npx --no-install playwright test tests/Browser/dashboard.spec.js`; `npm run build` | `tests/data/wf-087/` |
| WF-088 | `resources/js/map/markers.js`; `resources/views/map.blade.php` | browser: `npx --no-install playwright test tests/Browser/markers.spec.js`; `npm run build` | `tests/data/wf-088/` |
| WF-089 | `resources/js/map/filters.js` | browser: `npx --no-install playwright test tests/Browser/filters.spec.js`; `npm run build` | `tests/data/wf-089/` |
| WF-090 | `resources/js/map/layers.js`; `resources/js/map/legend.js` | browser: `npx --no-install playwright test tests/Browser/layers.spec.js`; `npm run build` | `tests/data/wf-090/` |
| WF-091 | `resources/views/facilities/`; `resources/views/districts/` | browser: `npx --no-install playwright test tests/Browser/details.spec.js`; `npm run build` | `tests/data/wf-091/` |
| WF-092 | `resources/views/methodology.blade.php`; `resources/js/map/state.js` | browser: `npx --no-install playwright test tests/Browser/ui_states.spec.js`; `npm run build` | `tests/data/wf-092/` |
| WF-093 | `notebooks/gis_puskesmas.ipynb`; `scripts/analysis/snapshot.py`; `python/gis_pipeline/analysis/snapshot.py` | python: `python -m pytest tests/python/test_snapshot.py -q` | `tests/data/wf-093/` |
| WF-094 | `notebooks/gis_puskesmas.ipynb`; `scripts/analysis/` | python: `python -m pytest tests/python/test_notebook_parity.py -q` | `tests/data/wf-094/` |
| WF-095 | `scripts/analysis/folium_export.py`; `python/gis_pipeline/analysis/folium_export.py` | python: `python -m pytest tests/python/test_folium_export.py -q` | `tests/data/wf-095/` |
| WF-096 | `notebooks/gis_puskesmas.ipynb`; `docs/panduan-Run-all.md` | notebook: Tidak ada langkah tersembunyi atau rahasia dalam notebook/HTML; konten deterministik dapat dibandingkan tanpa terpengaruh timestamp. | `tests/data/wf-096/` |
| WF-097 | `resources/views/admin/batches/`; `app/Http/Controllers/Admin/BatchController.php` | browser: `npx --no-install playwright test tests/Browser/admin_batches.spec.js`; `npm run build` | `tests/data/wf-097/` |
| WF-098 | `resources/views/admin/reviews/`; `app/Http/Controllers/Admin/ReviewController.php` | browser: `npx --no-install playwright test tests/Browser/admin_reviews.spec.js`; `npm run build` | `tests/data/wf-098/` |
| WF-099 | `app/Http/Controllers/Api/FacilityExportController.php`; `app/Services/FacilityCsvExport.php` | php: `php artisan test tests/Feature/FacilityExportTest.php` | `tests/data/wf-099/` |
| WF-100 | `app/Services/DistrictRankingService.php`; `resources/views/districts/ranking.blade.php` | php: `php artisan test tests/Feature/DistrictRankingTest.php` | `tests/data/wf-100/` |
| WF-101 | `tests/Browser/release_flow.spec.js` | browser: `npx --no-install playwright test tests/Browser/release_flow.spec.js`; `npm run build` | `tests/data/wf-101/` |
| WF-102 | `tests/Feature/`; `tests/python/` | suite: `python -m pytest tests/python -q`; `php artisan test` | `tests/data/wf-102/` |
| WF-103 | `tests/Browser/smoke.spec.js` | browser: `npx --no-install playwright test tests/Browser/smoke.spec.js`; `npm run build` | `tests/data/wf-103/` |
| WF-104 | `docs/pekerjaan/WF-104/manifest-kandidat-uji.json` | gate: Kandidat dapat direproduksi dan semua prasyarat uji sistem tersedia sebelum fase 5 dibuka. | `tests/data/wf-104/` |

WF-068–070: batch≤25, queue hash/stable codes, pending+blocked+completed=initial; keputusan lokasi memerlukan bukti manusia. WF-086: checkpoint review→analyze→validate→publish→rollback→audit/cache/race, setiap substep punya negative test sebelum lanjut. CI PostgreSQL/PostGIS test harus tersedia sebelum WF-056, tidak menunggu WF-072.
