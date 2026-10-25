"""Kontrak handoff per tiket; hanya merender rencana, tidak menjalankan tugas."""

SECTION = '## Handoff dan checkpoint eksekusi'
INDEX_NOTE = '''## Persiapan eksekusi agen

Baca [panduan eksekusi](../panduan-eksekusi.md) dan [register prasyarat](../prasyarat-eksekusi.md) sebelum mulai. Setiap tiket memiliki handoff; 52 tiket fase implementasi juga memiliki target file, fixture/check, serta perintah verifikasi usulan. Path tersebut belum merupakan file aplikasi yang sudah dibuat. Isi handoff aktual berdasarkan desain diterima sebelum mengubah kode.

Kerjakan satu tiket aktif dengan checkpoint tersimpan. WF-068/069/070 menggunakan batch lokasi; WF-086 menggunakan enam checkpoint lifecycle. Checkpoint tidak menambah tiket WBS dan tidak membuka antrean berikutnya sebelum syarat penutupan tiket induk terpenuhi. Pencatatan parameter A08-PARAM dan validasi impor S05 tetap P0 walaupun seluruh P1 ditunda.

'''

# Target usulan yang disahkan/disesuaikan melalui WF-031/WF-G3; bukan berkas aktual.
# ID | file/modul | fixture atau pemeriksaan | runner
_TARGETS = '''053|.gitignore;README.md|git diff --check|repo
054|composer.json;package.json;routes/web.php;.env.example|tests/Feature/HealthTest.php|php
055|requirements.lock;notebooks/gis_puskesmas.ipynb|tests/python/test_environment.py|python
056|.github/workflows/checks.yml;phpunit.xml;pytest.ini;playwright.config.js|Pipeline lint, PHPUnit/Pest, pytest, build; satu kegagalan assertion terkontrol harus menggagalkan job|ci
057|scripts/etl/facilities.py|tests/python/test_facilities_parser.py|python
058|scripts/etl/indicators.py|tests/python/test_indicators_parser.py|python
059|scripts/etl/boundaries.py|tests/python/test_boundaries_source.py|python
060|scripts/etl/http_client.py;scripts/etl/batch.py|tests/python/test_scraping_resilience.py|python
061|scripts/etl/acquire.py;data/raw/manifest.json|Manifest seluruh halaman/file, hash dan periode sesuai target sumber|data
062|scripts/etl/normalize.py|tests/python/test_normalize.py|python
063|scripts/etl/crosswalk.py;data/processed/crosswalk.json|tests/python/test_crosswalk.py|python
064|scripts/etl/reconcile_facilities.py|tests/python/test_reconcile_facilities.py|python
065|scripts/etl/validate_indicators.py|tests/python/test_validate_indicators.py|python
066|scripts/etl/validate_boundaries.py|tests/python/test_validate_boundaries.py|python
067|scripts/etl/geocode.py;data/staging/location_queue.json|tests/python/test_geocode_queue.py|python
068|data/staging/location_reviews.json|565 kode awal direkonsiliasi dengan keputusan dan bukti per fasilitas|data
069|data/staging/location_searches.json|408 kode awal direkonsiliasi dengan hasil pencarian termasuk missing|data
070|data/staging/location_anomalies.json|Seluruh anomali, lima kelompok identik, boundary dan pulau memiliki keputusan berbukti|data
071|scripts/etl/validate_eligibility.py|tests/python/test_eligibility.py|python
072|config/database.php;.env.example|tests/Feature/DatabaseConnectionTest.php|php
073|database/migrations/|tests/Feature/DatabaseConstraintsTest.php|php
074|database/migrations/;tests/sql/role_access.sql|tests/Feature/DatabaseAccessTest.php|php
075|app/Console/Commands/ImportDataset.php;app/Services/DatasetImportService.php|tests/Feature/DatasetImportTest.php|php
076|data/processed/;app/Console/Commands/ImportDataset.php|Rekonsiliasi file kurasi dan DB kandidat: kode, jumlah, FK, tahun, hash dan eligibility|data
077|scripts/analysis/indicators.py|tests/python/test_indicators.py|python
078|scripts/analysis/aggregates.py|tests/python/test_aggregates.py|python
079|scripts/analysis/buffers.py|tests/python/test_buffers.py|python
080|scripts/analysis/coverage.py|tests/python/test_coverage.py|python
081|scripts/analysis/export_layers.py|tests/python/test_analysis_manifest.py|python
082|routes/api.php;app/Http/Controllers/Api/ReleaseController.php;app/Http/Controllers/Api/RegionController.php;app/Http/Controllers/Api/SourceController.php|tests/Feature/ReferenceApiTest.php|php
083|app/Http/Controllers/Api/FacilityController.php;app/Http/Requests/FacilityFilterRequest.php|tests/Feature/FacilityApiTest.php|php
084|app/Http/Controllers/Api/StatisticsController.php;app/Http/Controllers/Api/MapController.php;app/Services/ReleaseCache.php|tests/Feature/MapStatisticsApiTest.php|php
085|routes/web.php;app/Http/Controllers/Auth/;app/Policies/;config/session.php|tests/Feature/AdminAuthenticationTest.php|php
086|app/Console/Commands/;app/Services/ReleaseLifecycleService.php;app/Services/ReleaseAuditService.php|tests/Feature/ReleaseLifecycleTest.php|php
087|resources/views/layouts/app.blade.php;resources/views/home.blade.php;resources/css/app.css|tests/Browser/dashboard.spec.js|browser
088|resources/js/map/markers.js;resources/views/map.blade.php|tests/Browser/markers.spec.js|browser
089|resources/js/map/filters.js|tests/Browser/filters.spec.js|browser
090|resources/js/map/layers.js;resources/js/map/legend.js|tests/Browser/layers.spec.js|browser
091|resources/views/facilities/;resources/views/districts/|tests/Browser/details.spec.js|browser
092|resources/views/methodology.blade.php;resources/js/map/state.js|tests/Browser/ui_states.spec.js|browser
093|notebooks/gis_puskesmas.ipynb;scripts/analysis/snapshot.py|tests/python/test_snapshot.py|python
094|notebooks/gis_puskesmas.ipynb;scripts/analysis/|tests/python/test_notebook_parity.py|python
095|scripts/analysis/folium_export.py|tests/python/test_folium_export.py|python
096|notebooks/gis_puskesmas.ipynb;docs/panduan-Run-all.md|Run all pada Colab bersih; log versi, input/output hash dan pemeriksaan manifest|notebook
097|resources/views/admin/batches/;app/Http/Controllers/Admin/BatchController.php|tests/Browser/admin_batches.spec.js|browser
098|resources/views/admin/reviews/;app/Http/Controllers/Admin/ReviewController.php|tests/Browser/admin_reviews.spec.js|browser
099|app/Http/Controllers/Api/FacilityExportController.php;app/Services/FacilityCsvExport.php|tests/Feature/FacilityExportTest.php|php
100|app/Services/DistrictRankingService.php;resources/views/districts/ranking.blade.php|tests/Feature/DistrictRankingTest.php|php
101|tests/Browser/release_flow.spec.js|tests/Browser/release_flow.spec.js|browser
102|tests/Feature/;tests/python/|Suite modul berubah dan expected result independen sesuai matriks kebutuhan-uji|suite
103|tests/Browser/smoke.spec.js|tests/Browser/smoke.spec.js|browser
104|docs/pekerjaan/WF-104/manifest-kandidat-uji.json|Cocokkan revision, lockfile, hash data/artefak, rilis/run dan bukti uji dengan keputusan WF-G4|gate'''

TARGETS = {}
for row in _TARGETS.splitlines():
    number, paths, check, runner = row.split('|')
    TARGETS['WF-' + number] = (paths.split(';'), check, runner)

LIFECYCLE_CHECKPOINTS = [
    'C1 Review: simpan actor, bukti, alasan dan versi kandidat; tolak guest, bukti milik fasilitas lain, dan perubahan published.',
    'C2 Analisis: jalankan input berhash dengan run_id dan parameter; uji retry/idempotensi serta gagal tanpa run succeeded palsu.',
    'C3 Validasi: periksa kualitas, eligibility, FK, hash artefak dan kecocokan release/run; setiap kegagalan menahan publish.',
    'C4 Publish: transaksi dan lock/pemeriksaan versi mencegah dua publish bersaing; uji dua koneksi bersamaan dan gagal di tengah transaksi. Pointer, status serta audit harus commit bersama atau rollback bersama; cache hanya diperbarui setelah commit.',
    'C5 Rollback: pilih rilis lama valid tanpa mengubah sejarah; uji balapan publish/rollback dan konsistensi cache serta pembacaan release_id.',
    'C6 Audit/integrasi: identitas operator CLI ditentukan lewat jalur desain (bukan session HTTP yang diasumsikan ada); uji seluruh allow/deny sebagai non-owner serta alur lengkap tanpa UI P1. Audit tidak memuat rahasia.',
]


def handoff_metadata(ticket_id, dependency_inputs):
    result = {'plan_version': 1, 'actual_path': f'docs/pekerjaan/{ticket_id}/handoff.md',
              'progress_path': f'docs/pekerjaan/{ticket_id}/checkpoint.json',
              'dependency_inputs': dependency_inputs}
    if ticket_id not in TARGETS:
        return result
    paths, check, runner = TARGETS[ticket_id]
    commands = {
        'php': [f'php artisan test {check}'],
        'python': [f'python -m pytest {check} -q'],
        'browser': [f'npx --no-install playwright test {check}', 'npm run build'],
        'repo': ['git diff --check'],
        'ci': ['python -m pytest tests/python -q', 'php artisan test', 'npm run build'],
        'suite': ['python -m pytest tests/python -q', 'php artisan test'],
    }.get(runner, [])
    result.update({'proposed_targets': paths, 'verification_target': check,
                   'proposed_commands': commands, 'runner': runner,
                   'fixture_directory': f'tests/data/{ticket_id.lower()}/'})
    return result


def render_handoff(ticket_id, dependency_inputs):
    meta = handoff_metadata(ticket_id, dependency_inputs)
    lines = [SECTION, '',
             'Ikuti [panduan eksekusi](../../panduan-eksekusi.md) dan [register prasyarat](../../prasyarat-eksekusi.md). '
             f"Simpan handoff aktual pada `{meta['actual_path']}` dan progres pada `{meta['progress_path']}` saat tiket dimulai. "
             'Keduanya masih target; bukan bukti pekerjaan sudah berjalan.', '',
             'Catat input/versi yang benar-benar tersedia, keputusan prasyarat yang berlaku, batas perubahan, '
             'pemeriksaan expected/actual, penghalang, dan langkah berikutnya. Gunakan persetujuan pengguna yang sudah tercatat; '
             'jangan meminta ulang keputusan yang sama. Bukti penerimaan eksternal tetap harus berasal dari pihak sebenarnya.', '']
    if ticket_id in TARGETS:
        lines += ['**Kontrak implementasi usulan:** sahkan melalui WF-031/WF-G3 dan resolusikan ke file aktual sebelum mengubah kode. '
                  'Jangan membuat modul paralel jika fungsi yang sama sudah tersedia; catat pemetaan path yang berubah.', '',
                  '- Target file/modul: ' + ', '.join(f'`{p}`' for p in meta['proposed_targets']) + '.',
                  '- Fixture sintetis bila diperlukan: `' + meta['fixture_directory'] + '`; gunakan kasus normal/negatif pada langkah tiket dan expected result dari WF-049. Jangan salin rumus implementasi sebagai oracle.',
                  '- Pemeriksaan spesifik: ' + meta['verification_target'] + '.',
                  '- Syarat selesai: kode/data aktual pada target yang disepakati tersedia bersama bukti verifikasi; laporan saja tidak menggantikan implementasi.']
        if meta['proposed_commands']:
            lines += ['- Perintah usulan dari root repo, setelah toolchain dan test di atas tersedia: ' +
                      '; '.join(f'`{c}`' for c in meta['proposed_commands']) +
                      '. Catat perintah final dan exit code; test tidak ditemukan/0 test bukan lulus. PHP memakai DB test PostgreSQL/PostGIS untuk kasus DB/spasial.']
        else:
            lines += ['- Catat command/query atau langkah manual final beserta environment dan input pada handoff; pemeriksaan di atas harus menghasilkan bukti aktual, bukan hanya file checklist.']
        if dependency_inputs:
            lines += ['', '**Lokasi input pendahulu yang direncanakan (root repo):**']
            lines += ['- `' + p + '`.' for p in dependency_inputs]
            lines += ['Jika lokasi aktual berbeda, ambil tautan dari log tiket sumber; cek versi dan penerimaan, bukan sekadar keberadaan nama file.']
    if ticket_id in {'WF-068', 'WF-069', 'WF-070'}:
        lines += ['', '**Checkpoint batch lokasi:** satu kabupaten per antrean, maksimal 25 fasilitas per checkpoint '
                  '(boleh lebih kecil untuk kasus sulit). Bekukan daftar kode dan hash input. '
                  'Setelah tiap batch simpan kode selesai, pending, blocked, lokasi hasil, dan batch berikutnya. '
                  'Mulai ulang hanya kode pending setelah mencocokkan hash; hasil lama tidak dihapus. '
                  'Perubahan sumber/keputusan menandai kode terdampak untuk review ulang. '
                  'Jumlah kode unik selesai + pending + blocked harus sama dengan antrean awal tanpa irisan. '
                  'Status checkpoint berbeda dari status lokasi: review selesai dapat menghasilkan missing/unverified. '
                  'Seluruh batch tetap bagian tiket induk; penghalang wajib tetap menahan penutupan.']
    if ticket_id == 'WF-086':
        lines += ['', '**Checkpoint lifecycle, dikerjakan berurutan dalam tiket yang sama:**', '']
        lines += ['- ' + item for item in LIFECYCLE_CHECKPOINTS]
        lines += ['', 'Simpan hasil uji dan revision per checkpoint; keenam checkpoint beserta integrasi harus selesai sebelum tiket diajukan untuk review.']
    if ticket_id == 'WF-120':
        lines += ['', '**Wajib meskipun semua P1 deferred:** A08-PARAM menguji perubahan T pada run baru, '
                  'parameter/metode/hash input tersimpan, run lama tidak berubah, dan API/notebook membaca parameter run yang sama. '
                  'A08-RANK hanya berlaku bila ranking dipilih. S05 validasi impor backend tetap wajib. '
                  'Laporkan ketiganya terpisah agar keputusan P1 tidak menyembunyikan kegagalan P0.']
    if ticket_id == 'WF-031':
        lines += ['', '**Handoff desain:** tinjau target file/test usulan 52 tiket WF-053–WF-104 pada katalog. '
                  'Tetapkan modul yang berbagi fungsi, runner, working directory, dan lokasi fixture; '
                  'simpan pemetaan final dalam desain-struktur-repositori.md, lalu periksa kembali pada WF-G3.']
    if ticket_id == 'WF-052':
        lines += ['', '**Penerimaan handoff:** cocokkan pemetaan WF-031 dengan kontrak schema/API, '
                  'fixture WF-049, prosedur WF-050, dan seluruh 52 handoff implementasi. '
                  'Tetapkan metode spasial/toleransi, identitas operator CLI, transaksi/locking publikasi, '
                  'serta test allow/deny sebelum desain diterima.']
    return '\n'.join(lines).rstrip() + '\n'
