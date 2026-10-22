# Rencana pengujian WebGIS

## Status dan sasaran

Dokumen ini adalah **rencana uji, bukan laporan kelulusan aplikasi**. Yang sudah dijalankan saat perencanaan adalah audit CSV/workbook, pemeriksaan silang jumlah workbook, dan pemeriksaan konsistensi bahan keluaran. Laravel, Supabase/PostGIS, Colab end-to-end, browser aplikasi, performa, keamanan dan UAT belum diuji karena belum diimplementasikan.

Tujuan pengujian adalah memastikan data benar, metode spasial dapat dipertanggungjawabkan, fitur sesuai proposal, akses data aman, dan hasil dapat dibuat ulang. Bukti setiap eksekusi minimal memuat test_id, versi kode, release_id, environment, input, langkah, hasil diharapkan, hasil aktual, status, pelaksana, tanggal dan tautan screenshot/log/query.

## Environment dan alat

| Lapisan | Environment dan alat | Aturan isolasi |
|---|---|---|
| Unit Python | Python terkunci dan pytest | Fixture sintetis kecil; geocoder dimock |
| Database/spasial | PostgreSQL + PostGIS dengan versi kompatibel Supabase | Database test terpisah; SQLite tidak membuktikan fungsi spasial/RLS |
| Backend | Laravel test runner PHPUnit/Pest | Akun, release dan file test; tidak memakai credential production |
| Browser | Playwright; pemeriksaan manual Chrome/Edge dan browser seluler | Data test atau salinan staging; viewport 360/768/1366 |
| Performa | k6 atau alat setara, browser network/trace | Hanya hosting staging yang dikelola tim; tile/geocoder publik dimock pada load test |
| Reproduksibilitas | Runtime Colab baru | Input berhash, versi paket dan urutan Run all dicatat |
| UAT | Staging kandidat rilis | Peserta menjalankan skenario dan mencatat kesulitan tanpa dibimbing tiap langkah |

Setiap PR menjalankan unit dan backend tests. Perubahan ETL, rumus, geometri atau mapping juga menjalankan data/spatial tests. Browser smoke test dijalankan untuk perubahan UI/API. Suite penuh, restore dan UAT dilakukan pada kandidat rilis. Tidak perlu mengulang seluruh load test untuk perubahan teks yang tidak memengaruhi perilaku.

## Fixture yang harus dibuat pada implementasi

| Fixture | Isi dan nilai yang diharapkan |
|---|---|
| F-DATA | Kabupaten A/B dengan nama kecamatan sama; kode fasilitas duplikat; baris TOTAL; penduduk null/0/negatif; angka desimal dan ribuan |
| F-RATIO | P=30.000,F=1 → kebutuhan 1/defisit 0; P=30.001,F=1 → kebutuhan 2/defisit 1; P=60.000,F=2 → rasio 30.000/defisit 0 |
| F-ZERO | P=10.000,F=0 → rasio null, status tanpa_puskesmas, kebutuhan 1, defisit 1; P=null → kebutuhan/defisit null; P=0,F=0 → kebutuhan 0, rasio null, flag tanpa_puskesmas |
| F-AGG | Wilayah A P=30.000,F=1 dan B P=90.000,F=2 → rasio gabungan 40.000, bukan rata-rata 37.500 |
| F-GEO | Dua titik fasilitas dengan buffer bertumpuk; titik di luar polygon, tepat di batas, centroid desa dan fasilitas di pulau; satu polygon invalid |
| F-ACCESS | Guest, pengelola, admin, runtime DB, worker DB; satu rilis draft dan satu published |
| F-IMPORT | Berkas valid; salah header; angka nonnumerik; kode ganda; impor ulang hash sama; baris dengan HTML/script dan formula CSV |

Fixture sintetis disimpan di `tests/data` dan tidak pernah digabungkan dengan data publik. Ambang toleransi geometri dicatat bersama versi pustaka; ekspektasi dihitung dengan metode referensi independen.

## Uji dataset

| ID | Langkah/input | Hasil yang diharapkan | Prioritas |
|---|---|---|---|
| D01 | Impor master 2024-S1 dan hitung kode | 973 baris, 973 kode unik; nol kode kosong | P0 |
| D02 | Group master per kab/kota dan kategori | 38 kab/kota; layanan 616 + 357; karakter 658 + 294 + 16 + 5; semua total 973 | P0 |
| D03 | Bandingkan kode master dan koordinat; hitung status | Himpunan kode sama; baseline 565 berpasangan/408 kosong; missing tetap ada dalam master | P0 |
| D04 | Impor CSV rekap yang mengandung TOTAL | 665 detail/39 agregat; sum detail 973, all-rows 2.919 ditandai tidak valid untuk analisis | P0 |
| D05 | Join dua kecamatan senama di kab berbeda, alias Sempol–Ijen | Join memakai kode+parent+edisi; alias tidak disetujui otomatis; tidak menggandakan P/F | P0 |
| D06 | Bandingkan master wilayah dengan seluruh polygon dan fakta | Set kode sama; unmatched/duplicate nol setelah kurasi; baseline 666 diverifikasi, bukan dipaksakan | P0 |
| D07 | Periksa tahun, unit, sumber dan locator per nilai | Nilai terisi memiliki metadata; sumber 2019/2021/2025 tidak dilabeli 2023 tanpa bukti | P0 |
| D08 | Periksa 5 wilayah OCR, 8 luas alternatif, TOTAL per kab | Verifikasi semua nilai berisiko terhadap sumber; selisih dicatat, bukan dikoreksi hanya agar total cocok | P0 |
| D09 | Null, nol, negatif, angka format lokal, hektar | Null tetap null; negatif ditolak; unit/locale benar; konversi mempunyai bukti | P0 |
| D10 | Bandingkan CSV dengan XLSX salinan berdasarkan kode | Seluruh atribut yang dipilih sama atau konflik diputuskan dan diaudit | P0 |
| D11 | Jalankan ETL dua kali dengan input/versi sama | Output konten identik, tak ada duplikat; timestamp tidak dimasukkan ke hash konten deterministik | P0 |

## Uji formula dan agregasi

| ID | Langkah/input | Hasil yang diharapkan | Prioritas |
|---|---|---|---|
| A01 | F-RATIO pada batas 30.000/30.001/60.000 | Pembulatan kebutuhan memakai ceil; tidak ada off-by-one | P0 |
| A02 | F-ZERO | Null/0/F=0 diperlakukan seperti tabel fixture; tidak ada Infinity/NaN atau pembagian nol | P0 |
| A03 | P=10.000,A=2; A=0/null | Kepadatan 5.000 jiwa/km²; nilai tidak sah diblokir atau null beralasan | P0 |
| A04 | P=60.000,F=3; lalu P=90.001,F=1 | Defisit0; lalu kebutuhan 4/defisit 3; tidak ada defisit negatif | P0 |
| A05 | Kurangi jumlah titik terpetakan tanpa mengubah master | Rasio administratif tidak berubah; kelengkapan koordinat berubah | P0 |
| A06 | F-AGG dan kecamatan dengan P hilang | Rasio40.000 untuk data lengkap; agregat tidak mengaku lengkap ketika ada P hilang | P0 |
| A07 | Bandingkan indikator pada SQL dan Python untuk fixture dan sampel arsip | Bilangan hitung sama persis; rasio beda ≤1e-9 sebelum format | P0 |
| A08 | Ubah T dan ulang run; bandingkan ranking | Run baru menyimpan parameter; nilai null tidak masuk ranking seolah-olah0; tie-break deterministik | P1 |

Untuk publikasi rasio, pemeriksaan A08 tentang pencatatan parameter tetap wajib P0; antarmuka ranking/parameter interaktif dapat P1. Jangan memilih toleransi yang menutupi perbedaan unit atau tahun.

## Uji geospasial

| ID | Langkah/input | Hasil yang diharapkan | Prioritas |
|---|---|---|---|
| G01 | Tukar lat/lon pada fixture dan cek titik terhadap polygon | Data invalid tidak diterbitkan; koordinat benar tampil di lokasi referensi | P0 |
| G02 | Masukkan village/district centroid dengan status Ditemukan | Tidak masuk buffer fasilitas; UI menyebut ketelitian perkiraan | P0 |
| G03 | Periksa lima grup koordinat identik dan seluruh 565 kandidat | Tidak auto-deduplicate; seluruh keputusan lokasi punya bukti, reviewer dan tanggal | P0 |
| G04 | Titik di batas, di luar kab, di kepulauan | Titik boundary ditangani konsisten; konflik direview; pulau sah tidak gugur karena bbox sempit | P0 |
| G05 | Join polygon dan indikator, termasuk null/0 | Satu feature per kode; missing berbeda warna dari0; kab dan kecamatan cocok sumber | P0 |
| G06 | Buffer titik valid radius 1000/3000/5000 meter | Jarak vertex batas terhadap pusat sesuai radius, usulan toleransi maksimum1% dan metode tercatat | P0 |
| G07 | Dua buffer overlap; bandingkan union vs penjumlahan | Luas union≤jumlah luas; bagian overlap dihitung satu kali | P0 |
| G08 | Clip pada polygon dan ukur coverage | 0≤covered_area≤region_area; coverage0–100; perbedaan float kecil ditangani eksplisit | P0 |
| G09 | Polygon invalid/empty, CRS salah, MultiPolygon pulau | Validasi gagal dengan pesan; perbaikan geometri dicatat; tidak hilang bagian pulau | P0 |
| G10 | Fasilitas dekat batas kabupaten dan wilayah luar Jatim | Fasilitas tetangga dalam dataset ikut bila memenuhi radius; keterbatasan luar provinsi dijelaskan | P0 |
| G11 | Bandingkan PostGIS dengan referensi GeoPandas/pyproj | Radius/luas konsisten dalam toleransi usulan 1%; perbedaan proyeksi dan kurva dibahas | P0 |

Luas yang dihitung dua implementasi tidak harus sama digit terakhir. Tetapkan toleransi dari metode dan presisi, bukan mengubah toleransi agar uji kelihatan lulus. Uji G03 meliputi pemeriksaan manusia terhadap kandidat, sementara pengujian otomatis hanya memverifikasi kelengkapan bukti/status dan anomali spasial.

## Uji backend dan Supabase

| ID | Langkah/input | Hasil yang diharapkan | Prioritas |
|---|---|---|---|
| I01 | Migration dari DB test kosong; koneksi SSL; PostGIS | Semua objek ada, spatial query berhasil, secret tidak masuk log | P0 |
| I02 | Insert kode duplikat, FK tak ada, angka negatif, status verified tanpa bukti | Ditolak constraint/validator; tidak ada partial publish | P0 |
| I03 | Hubungkan distrik dari boundary_set berbeda ke rilis | Ditolak meskipun district_id valid secara individual | P0 |
| I04 | Impor valid, impor ulang, impor gagal di tengah | Idempotent; transaksi/validasi menjaga konsistensi; error report tersimpan | P0 |
| I05 | Jalankan SELECT/INSERT/UPDATE/DELETE sebagai setiap role | Runtime hanya dataset published; worker tidak mengubah published; publik tidak membaca staging | P0 |
| I06 | Publish release, baca beberapa endpoint, rollback pointer | Semua respons satu release_id; cache berubah; rilis lama dapat diakses sesuai kebijakan | P0 |
| I07 | Parameter SQL injection, sort tidak dikenal, bbox/radius invalid | Ditolak atau diparameterisasi; tidak mengubah schema/data; response 422/400 sesuai kontrak | P0 |
| I08 | Database timeout dan worker gagal | API 503 bersih; retry terkendali; tidak menerbitkan hasil setengah jadi | P0 |

## Uji antarmuka dan black box

| ID | Langkah pengguna | Hasil yang diharapkan | Prioritas |
|---|---|---|---|
| W01 | Buka beranda lalu peta, zoom, pan, ubah layer | Peta dan kontrol berfungsi; judul/periode/sumber terlihat | P0 |
| W02 | Pilih kabupaten lalu kecamatan dan cari kode/nama | Pilihan anak sesuai parent; marker dan tabel cocok filter; reset bekerja | P0 |
| W03 | Filter rawat inap dan karakter wilayah | Hasil sesuai atribut; indikator administratif diberi cakupan yang jelas | P0 |
| W04 | Klik cluster, fasilitas bertitik sama, fasilitas tanpa titik | Cluster dapat dibuka; semua identitas terakses; tanpa titik tampil di tabel tanpa marker palsu | P0 |
| W05 | Ganti metric choropleth, hover dan buka detail | Angka, unit, kelas warna dan no-data konsisten | P0 |
| W06 | Pilih wilayah dengan F=0 atau indikator kosong | Status tanpa fasilitas/belum lengkap tampil; grafik dan kartu tidak crash | P0 |
| W07 | Buka metode dan sumber, putus tile/API | Metadata rilis terbaca; fallback tabel/pesan gagal jelas, bukan layar kosong | P0 |
| W08 | Ekspor setelah filter, buka CSV | Jumlah, kode, tahun dan atribut sama dengan hasil yang diizinkan | P1 |
| W09 | Pakai keyboard dan viewport 360/768/1366 | Fokus terlihat; label form; panel dan popup dapat ditutup/digulir; tidak ada kontrol tertutup | P0 |
| W10 | Muat data lambat lalu ubah filter cepat | Request lama tidak menimpa hasil filter baru; state loading/error/empty konsisten | P0 |

## Keamanan dan operasi

| ID | Skenario | Hasil yang diharapkan | Prioritas |
|---|---|---|---|
| S01 | Guest membuka route admin; user biasa mencoba publish atau ID rilis draft | 401/403/404 sesuai kontrak; tidak ada kebocoran IDOR | P0 |
| S02 | Input HTML/script pada nama, alamat, popup | Ditampilkan sebagai teks aman; tidak ada eksekusi script | P0 |
| S03 | Request ubah data tanpa CSRF/session valid; percobaan login berulang | Ditolak; rate limit; session secure/httpOnly/sameSite dan expiry sesuai konfigurasi | P0 |
| S04 | Periksa JS bundle, HTML Folium, log, .env publik, akses Data API | Tidak ada password/secret; schema privat tidak terbaca; error tidak membuka konfigurasi | P0 |
| S05 | Unggah file besar/salah ekstensi/kolom; ekspor string berawalan =,+,-,@ | Unggahan divalidasi dan dibatasi; CSV untuk pembaca spreadsheet tidak mengeksekusi formula | P1 |
| S06 | Restore backup DB dan berkas ke staging kosong | Jumlah, hash, FK, artefak, login dan peta pulih; ukur RPO 24h/RTO 4h | P0 |
| S07 | Uji public grants/RLS sebagai anon, authenticated, runtime non-owner | Izin tepat; pengujian tidak dijalankan hanya dengan postgres/service role | P0 |

S05 bagian validasi file wajib sebelum fitur impor command/API dibuka; antarmuka unggah P1 tidak menunda validasi backend P0. Uji serangan dibatasi pada aplikasi dan environment yang dikelola tim.

## Performa dan reproduksibilitas

| ID | Profil eksekusi | Target penerimaan |
|---|---|---|
| P01 | 973 fasilitas dan seluruh polygon target; desktop 4-core/8GB sebagai profil awal, jaringan 10 Mbps/latensi 100 ms, cache dingin | Peta operasional≤5s; catat perangkat/browser aktual dan ukuran payload |
| P02 | 20 pengguna virtual, ramp-up 1 menit, steady 5 menit; GET peta/tabel/statistik pada staging | p95 API warm≤800ms; error<1%; tidak ada connection exhaustion; record cold path terpisah |
| P03 | Zoom/pan/filter mobile; polygon full vs simplified | Tidak ada freeze berkepanjangan; simplifikasi menjaga batas yang diperlukan; tidak mengukur “lulus” hanya dari FPS mesin pengembang |
| R01 | Colab runtime bersih, Run all dengan fixture lalu data rilis | Tanpa langkah tersembunyi; hash input dan versi paket tersimpan; kegagalan sumber memberi pesan jelas |
| R02 | Jalankan ulang release/parameter yang sama | Tabel hasil identik; geometri ekuivalen dalam toleransi; hash output memperhitungkan field non-deterministik yang dikeluarkan |
| R03 | Buka HTML ekspor di dua browser dan bandingkan API aplikasi | Jumlah, kategori, tahun dan legenda sama; akses tile/CDN dan kebutuhan internet dijelaskan |

P01/P02 target internal dapat direvisi dengan catatan keputusan bila hosting nyata memiliki batas berbeda. Perubahan target harus disepakati sebelum hasil uji dinyatakan lulus. Jangan mengarahkan load test ke Nominatim/OSM publik.

## UAT yang direncanakan

Libatkan minimal 5 peserta sebagai target awal: pengguna umum/mahasiswa dan calon penilai; jika tersedia, seorang pengguna yang memahami SIG/data kesehatan. Komposisi dan jumlah aktual dicatat. Partisipasi pihak dinas tidak diasumsikan tersedia.

| Tugas | Keberhasilan |
|---|---|
| Temukan satu puskesmas dan baca alamat serta pelayanan | Fasilitas yang dipilih sesuai kode/nama, informasi dapat dibaca |
| Bandingkan dua kecamatan | Peserta dapat menyebut penduduk, fasilitas, rasio dan tahun sumber |
| Tampilkan radius 3 km | Peserta memahami itu jarak geometris dan bukan waktu tempuh |
| Cari wilayah yang datanya belum lengkap | Peserta mengenali no-data, bukan menyimpulkan nol fasilitas/penduduk |
| Jelaskan sumber dan versi peta | Peserta dapat menemukan periode fasilitas dan indikator |

Catat keberhasilan mandiri, waktu, kesalahan, bantuan, dan komentar per tugas. Target usulan: ≥80% total tugas selesai mandiri; semua peserta dapat menemukan sumber setelah orientasi singkat; tidak ada salah pengertian kritis yang belum diperbaiki. Tambahkan kuesioner kemudahan skala1–5 bila dibutuhkan, tetapi jangan mengklaimnya sebagai SUS atau instrumen tervalidasi tanpa menggunakan instrumen yang benar.

## Gerbang rilis dan pelaporan defect

**Gerbang data:** identitas, total dan mapping konsisten; tahun/unit/sumber lengkap; titik analisis verified; polygon valid; seluruh pengecualian dicatat. Analisis parsial harus ditandai dan tidak memenuhi klaim coverage provinsi lengkap.

**Gerbang aplikasi:** semua uji P0 yang relevan lulus; nol defect kritis/tinggi; target performa terukur; izin akses, restore, Colab dan HTML telah diuji. P1 yang belum dibangun diberi status `not_in_scope_for_release`, bukan `passed`. Untuk penyerahan lengkap yang mencakup P1, semua P1 tersebut juga harus lulus.

**Gerbang akademik:** seluruh kebutuhan P/U pada matriks FR memiliki artefak dan bukti; metode/rumus/keterbatasan ditinjau; UAT selesai; screenshot/peta/laporan menampilkan versi sumber yang sama.

Severity: kritis = kebocoran kredensial, akses tulis publik, korupsi data atau kesimpulan utama salah; tinggi = rumus/join/buffer salah atau fitur inti gagal; sedang = fungsi pendukung terganggu; rendah = masalah tampilan minor. Setiap defect memuat langkah reproduksi, dampak, owner, perbaikan dan retest. Nilai “tidak dapat diuji” tetap terbuka, tidak diubah menjadi lulus.

Template catatan hasil per test:

```text
test_id:
tanggal_dan_pelaksana:
code_revision / release_id / analysis_run_id:
environment_dan_role:
input_dan_langkah:
expected:
actual:
status: not_run | passed | failed | blocked | not_in_scope_for_release
evidence_path:
defect_id_dan_retest:
```
