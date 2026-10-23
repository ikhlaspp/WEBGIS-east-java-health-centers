# Cakupan test per ID

Versi1 · 23 Oktober2026 · Seluruh actual not_run; prosedur dan expected bukan bukti test pass. Setup dan environment per ID di prosedur-per-test.json; framework runner dari mapping WF-031.

| ID | Prioritas | Fixture / environment | Tindakan | Expected |
|---|---|---|---|---|
| D01 | P0 | F-DATA/F-CROSS / python+PostGIS | Impor master 2024-S1 dan hitung kode | 973 baris, 973 kode unik; nol kode kosong |
| D02 | P0 | F-DATA/F-CROSS / python+PostGIS | Group master per kab/kota dan kategori | 38 kab/kota; layanan 616 + 357; karakter 658 + 294 + 16 + 5; semua total 973 |
| D03 | P0 | F-DATA/F-CROSS / python+PostGIS | Bandingkan kode master dan koordinat; hitung status | Himpunan kode sama; baseline 565 berpasangan/408 kosong; missing tetap ada dalam master |
| D04 | P0 | F-DATA/F-CROSS / python+PostGIS | Impor CSV rekap yang mengandung TOTAL | 665 detail/39 agregat; sum detail 973, all-rows 2.919 ditandai tidak valid untuk analisis |
| D05 | P0 | F-DATA/F-CROSS / python+PostGIS | Join dua kecamatan senama di kab berbeda, alias Sempol–Ijen | Join memakai kode+parent+edisi; alias tidak disetujui otomatis; tidak menggandakan P/F |
| D06 | P0 | F-DATA/F-CROSS / python+PostGIS | Bandingkan master wilayah dengan seluruh polygon dan fakta | Set kode sama; unmatched/duplicate nol setelah kurasi; baseline 666 diverifikasi, bukan dipaksakan |
| D07 | P0 | F-DATA/F-CROSS / python+PostGIS | Periksa tahun, unit, sumber dan locator per nilai | Nilai terisi memiliki metadata; sumber 2019/2021/2025 tidak dilabeli 2023 tanpa bukti |
| D08 | P0 | F-DATA/F-CROSS / python+PostGIS | Periksa 5 wilayah OCR, 8 luas alternatif, TOTAL per kab | Verifikasi semua nilai berisiko terhadap sumber; selisih dicatat, bukan dikoreksi hanya agar total cocok |
| D09 | P0 | F-DATA/F-CROSS / python+PostGIS | Null, nol, negatif, angka format lokal, hektar | Null tetap null; negatif ditolak; unit/locale benar; konversi mempunyai bukti |
| D10 | P0 | F-DATA/F-CROSS / python+PostGIS | Bandingkan CSV dengan XLSX salinan berdasarkan kode | Seluruh atribut yang dipilih sama atau konflik diputuskan dan diaudit |
| D11 | P0 | F-DATA/F-CROSS / python+PostGIS | Jalankan ETL dua kali dengan input/versi sama | Output konten identik, tak ada duplikat; timestamp tidak dimasukkan ke hash konten deterministik |
| A01 | P0 | F-RATIO / python+SQL | F-RATIO pada batas 30.000/30.001/60.000 | Pembulatan kebutuhan memakai ceil; tidak ada off-by-one |
| A02 | P0 | F-RATIO / python+SQL | F-ZERO | Null/0/F=0 diperlakukan seperti tabel fixture; tidak ada Infinity/NaN atau pembagian nol |
| A03 | P0 | F-RATIO / python+SQL | P=10.000,A=2; A=0/null | Kepadatan 5.000 jiwa/km²; nilai tidak sah diblokir atau null beralasan |
| A04 | P0 | F-RATIO / python+SQL | P=60.000,F=3; lalu P=90.001,F=1 | Defisit0; lalu kebutuhan 4/defisit 3; tidak ada defisit negatif |
| A05 | P0 | F-RATIO / python+SQL | Kurangi jumlah titik terpetakan tanpa mengubah master | Rasio administratif tidak berubah; kelengkapan koordinat berubah |
| A06 | P0 | F-RATIO / python+SQL | F-AGG dan kecamatan dengan P hilang | Rasio40.000 untuk data lengkap; agregat tidak mengaku lengkap ketika ada P hilang |
| A07 | P0 | F-RATIO / python+SQL | Bandingkan indikator pada SQL dan Python untuk fixture dan sampel arsip | Bilangan hitung sama persis; rasio beda ≤1e-9 sebelum format |
| A08-PARAM | P0 | F-RATIO / python+SQL | Ubah T dan ulang run, termasuk saat ranking ditunda | Run baru menyimpan T/metode/hash input; run lama tidak berubah; API dan notebook memakai parameter run yang sama |
| A08-RANK | P1 | F-RATIO / python+SQL | Bandingkan ranking bila fitur dipilih | Nilai null tidak masuk ranking seolah-olah 0; tie-break deterministik |
| G01 | P0 | F-GEO / PostGIS+pyproj | Tukar lat/lon pada fixture dan cek titik terhadap polygon | Data invalid tidak diterbitkan; koordinat benar tampil di lokasi referensi |
| G02 | P0 | F-GEO / PostGIS+pyproj | Masukkan village/district centroid dengan status Ditemukan | Tidak masuk buffer fasilitas; UI menyebut ketelitian perkiraan |
| G03 | P0 | F-GEO / PostGIS+pyproj | Periksa lima grup koordinat identik dan seluruh 565 kandidat | Tidak auto-deduplicate; seluruh keputusan lokasi punya bukti, reviewer dan tanggal |
| G04 | P0 | F-GEO / PostGIS+pyproj | Titik di batas, di luar kab, di kepulauan | Titik boundary ditangani konsisten; konflik direview; pulau sah tidak gugur karena bbox sempit |
| G05 | P0 | F-GEO / PostGIS+pyproj | Join polygon dan indikator, termasuk null/0 | Satu feature per kode; missing berbeda warna dari0; kab dan kecamatan cocok sumber |
| G06 | P0 | F-GEO / PostGIS+pyproj | Buffer titik valid radius 1000/3000/5000 meter | Jarak vertex batas terhadap pusat sesuai radius, usulan toleransi maksimum1% dan metode tercatat |
| G07 | P0 | F-GEO / PostGIS+pyproj | Dua buffer overlap; bandingkan union vs penjumlahan | Luas union≤jumlah luas; bagian overlap dihitung satu kali |
| G08 | P0 | F-GEO / PostGIS+pyproj | Clip pada polygon dan ukur coverage | 0≤covered_area≤region_area; coverage0–100; perbedaan float kecil ditangani eksplisit |
| G09 | P0 | F-GEO / PostGIS+pyproj | Polygon invalid/empty, CRS salah, MultiPolygon pulau | Validasi gagal dengan pesan; perbaikan geometri dicatat; tidak hilang bagian pulau |
| G10 | P0 | F-GEO / PostGIS+pyproj | Fasilitas dekat batas kabupaten dan wilayah luar Jatim | Fasilitas tetangga dalam dataset ikut bila memenuhi radius; keterbatasan luar provinsi dijelaskan |
| G11 | P0 | F-GEO / PostGIS+pyproj | Bandingkan PostGIS dengan referensi GeoPandas/pyproj | Radius/luas konsisten dalam toleransi usulan 1%; perbedaan proyeksi dan kurva dibahas |
| I01 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Migration dari DB test kosong; koneksi SSL; PostGIS | Semua objek ada, spatial query berhasil, secret tidak masuk log |
| I02 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Insert kode duplikat, FK tak ada, angka negatif, status verified tanpa bukti | Ditolak constraint/validator; tidak ada partial publish |
| I03 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Hubungkan distrik dari boundary_set berbeda ke rilis | Ditolak meskipun district_id valid secara individual |
| I04 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Impor valid, impor ulang, impor gagal di tengah | Idempotent; transaksi/validasi menjaga konsistensi; error report tersimpan |
| I05 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Jalankan SELECT/INSERT/UPDATE/DELETE sebagai setiap role | Runtime hanya dataset published; worker tidak mengubah published; publik tidak membaca staging |
| I06 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Publish release, baca beberapa endpoint, rollback pointer | Semua respons satu release_id; cache berubah; rilis lama dapat diakses sesuai kebijakan |
| I07 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Parameter SQL injection, sort tidak dikenal, bbox/radius invalid | Ditolak atau diparameterisasi; tidak mengubah schema/data; response 422/400 sesuai kontrak |
| I08 | P0 | F-ACCESS/F-RACE / PHP+PostGIS | Database timeout dan worker gagal | API 503 bersih; retry terkendali; tidak menerbitkan hasil setengah jadi |
| W01 | P0 | F-DATA/F-ACCESS / Playwright | Buka beranda lalu peta, zoom, pan, ubah layer | Peta dan kontrol berfungsi; judul/periode/sumber terlihat |
| W02 | P0 | F-DATA/F-ACCESS / Playwright | Pilih kabupaten lalu kecamatan dan cari kode/nama | Pilihan anak sesuai parent; marker dan tabel cocok filter; reset bekerja |
| W03 | P0 | F-DATA/F-ACCESS / Playwright | Filter rawat inap dan karakter wilayah | Hasil sesuai atribut; indikator administratif diberi cakupan yang jelas |
| W04 | P0 | F-DATA/F-ACCESS / Playwright | Klik cluster, fasilitas bertitik sama, fasilitas tanpa titik | Cluster dapat dibuka; semua identitas terakses; tanpa titik tampil di tabel tanpa marker palsu |
| W05 | P0 | F-DATA/F-ACCESS / Playwright | Ganti metric choropleth, hover dan buka detail | Angka, unit, kelas warna dan no-data konsisten |
| W06 | P0 | F-DATA/F-ACCESS / Playwright | Pilih wilayah dengan F=0 atau indikator kosong | Status tanpa fasilitas/belum lengkap tampil; grafik dan kartu tidak crash |
| W07 | P0 | F-DATA/F-ACCESS / Playwright | Buka metode dan sumber, putus tile/API | Metadata rilis terbaca; fallback tabel/pesan gagal jelas, bukan layar kosong |
| W08 | P1 | F-DATA/F-ACCESS / Playwright | Ekspor setelah filter, buka CSV | Jumlah, kode, tahun dan atribut sama dengan hasil yang diizinkan |
| W09 | P0 | F-DATA/F-ACCESS / Playwright | Pakai keyboard dan viewport 360/768/1366 | Fokus terlihat; label form; panel dan popup dapat ditutup/digulir; tidak ada kontrol tertutup |
| W10 | P0 | F-DATA/F-ACCESS / Playwright | Muat data lambat lalu ubah filter cepat | Request lama tidak menimpa hasil filter baru; state loading/error/empty konsisten |
| S01 | P0 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Guest/disabled admin/invalid CLI token accesses protected operations and public draft URL | 401/403 or public404; actor cannot be forged; no draft data leak |
| S02 | P0 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Input HTML/script pada nama, alamat, popup | Ditampilkan sebagai teks aman; tidak ada eksekusi script |
| S03 | P0 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Request ubah data tanpa CSRF/session valid; percobaan login berulang | Ditolak; rate limit; session secure/httpOnly/sameSite dan expiry sesuai konfigurasi |
| S04 | P0 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Periksa JS bundle, HTML Folium, log, .env publik, akses Data API | Tidak ada password/secret; schema privat tidak terbaca; error tidak membuka konfigurasi |
| S05-IMPORT | P0 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Importer file21MiB/salah header/jenis dan HTML input | Backend rejects invalid file; safe storage, escaped strings; no publish |
| S05-EXPORT | P1 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Export text beginning =,+,-,@ from selected public filter | Formula-neutralized CSV, exact filtered rows, metadata preserved |
| S06 | P0 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Restore backup DB dan berkas ke staging kosong | Jumlah, hash, FK, artefak, login dan peta pulih; ukur RPO 24h/RTO 4h |
| S07 | P0 | F-ACCESS/F-CLI/F-IMPORT / PHP+SQL+browser | Uji public grants/RLS sebagai anon, authenticated, runtime non-owner | Izin tepat; pengujian tidak dijalankan hanya dengan postgres/service role |
| P01 | P0 | 973 dataset and full boundary candidate / staging+k6/browser | 973 fasilitas dan seluruh polygon target; desktop 4-core/8GB sebagai profil awal, jaringan 10 Mbps/latensi 100 ms, cache dingin | Peta operasional≤5s; catat perangkat/browser aktual dan ukuran payload |
| P02 | P0 | 973 dataset and full boundary candidate / staging+k6/browser | 20 pengguna virtual, ramp-up 1 menit, steady 5 menit; GET peta/tabel/statistik pada staging | p95 API warm≤800ms; error<1%; tidak ada connection exhaustion; record cold path terpisah |
| P03 | P0 | 973 dataset and full boundary candidate / staging+k6/browser | Zoom/pan/filter mobile; polygon full vs simplified | Tidak ada freeze berkepanjangan; simplifikasi menjaga batas yang diperlukan; tidak mengukur “lulus” hanya dari FPS mesin pengembang |
| R01 | P0 | F-REPRO / Colab+Python/browser | Colab runtime bersih, Run all dengan fixture lalu data rilis | Tanpa langkah tersembunyi; hash input dan versi paket tersimpan; kegagalan sumber memberi pesan jelas |
| R02 | P0 | F-REPRO / Colab+Python/browser | Jalankan ulang release/parameter yang sama | Tabel hasil identik; geometri ekuivalen dalam toleransi; hash output memperhitungkan field non-deterministik yang dikeluarkan |
| R03 | P0 | F-REPRO / Colab+Python/browser | Buka HTML ekspor di dua browser dan bandingkan API aplikasi | Jumlah, kategori, tahun dan legenda sama; akses tile/CDN dan kebutuhan internet dijelaskan |
| SRC-01 | P0 | F-FAIL / mock HTTP + PostGIS/PHP as applicable | Serve429+Retry-After then200 | Respect delay, bounded attempts, no extra concurrency |
| SRC-02 | P0 | F-FAIL / mock HTTP + PostGIS/PHP as applicable | Serve200loginHTML instead of PDF | Reject content/magic mismatch |
| SRC-03 | P0 | F-FAIL / mock HTTP + PostGIS/PHP as applicable | Omit one expected page/feature ID | Incomplete source blocks promotion |
| SRC-04 | P0 | F-FAIL / mock HTTP + PostGIS/PHP as applicable | Change mandatory header/unit | Schema change detected, raw preserved |
| SRC-05 | P0 | F-FAIL / mock HTTP + PostGIS/PHP as applicable | Timeout on all3attempts | Job failed, no release promotion |
| SRC-06 | P0 | F-IMPORT / mock HTTP + PostGIS/PHP as applicable | Replay same input/hash/version/target twice | Existing batch/no duplicate effects |
| CLI-01 | P0 | F-CLI / mock HTTP + PostGIS/PHP as applicable | Forge actor/expired/revoked/wrong ability token | Deny; audited actor derived only from valid token |
| LIFE-01 | P0 | F-RACE / mock HTTP + PostGIS/PHP as applicable | Concurrent publish same expected pointer version | One winner, one409; atomic pointer/run/audit |
| LIFE-02 | P0 | F-RACE / mock HTTP + PostGIS/PHP as applicable | Inject failure before commit and after commit before outbox | Precommit all rollback; postcommit outbox retry, no mixed release |
| LIFE-03 | P0 | F-ACCESS / mock HTTP + PostGIS/PHP as applicable | Withdraw release after cache populated | Public API/gateway404 even if server cache retained |
| LIFE-04 | P0 | F-ACCESS / mock HTTP + PostGIS/PHP as applicable | Mutate published child/shared source/review or run | Denied; immutable history |
| LIFE-05 | P0 | F-ACCESS / mock HTTP + PostGIS/PHP as applicable | Edit draft concurrently with validate | Lock serialization; report/input_revision must match |
| P02-COLD | P0 | Performance profile / staging browser/performance profile | Measure cold API path separately before warm-up | Record uncached timings; do not present as warm target pass |
| U01 | P0 | F-DATA/UI / staging browser/performance profile | Inspect360/768/1366 layouts including panel/table | All controls usable, no page overflow hiding actions |
| U02 | P0 | F-DATA/UI / staging browser/performance profile | Navigate controls/dialog by keyboard and Escape | Labels and visible focus; dialog closes and restores focus |
| U03 | P0 | F-DATA/UI / staging browser/performance profile | Use no-data legend/table without map or color | Information equivalent; no-data distinguished from zero |
| UAT-01 | P0 | UAT staging / human participants on staging | Participant finds specified facilities including missing point | Correct identity/address/service independently |
| UAT-02 | P0 | UAT staging / human participants on staging | Participant compares two districts | Correct population/F/ratio and periods |
| UAT-03 | P0 | UAT staging / human participants on staging | Participant enables3km and interprets result | Recognizes geometric distance and partial scope, not travel or population coverage |
| UAT-04 | P0 | UAT staging / human participants on staging | Participant identifies unknown data and zero | Explains distinct meanings correctly |
| UAT-05 | P0 | UAT staging / human participants on staging | Participant finds sources and versions | Identifies observation periods/release/run |
