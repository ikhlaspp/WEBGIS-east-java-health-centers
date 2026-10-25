# Kebutuhan dan ruang lingkup

## Dasar perencanaan

Proposal membahas persebaran dan keterjangkauan puskesmas berdasarkan penduduk di Jawa Timur. Dokumen sumber memuat BAB 1, tujuan, batasan masalah, daftar perangkat lunak, dan contoh tabel lima kabupaten. Belum terdapat rancangan pengujian terperinci, autentikasi, skema Supabase, jadwal, atau kontrak API. Kebutuhan tambahan di bawah merupakan rancangan implementasi, bukan kutipan kewajiban proposal.

Gunakan tiga penanda asal: **P** berarti eksplisit dalam proposal, **U** berarti permintaan pengguna, dan **R** berarti rekomendasi agar sistem dapat digunakan dan diuji. Prioritas **P0** harus selesai sebelum rilis; **P1** menyusul setelah inti berjalan; **P2** adalah pengembangan lanjutan.

## Matriks kebutuhan dan penerimaan

| ID | Asal dan lokasi sumber | Kebutuhan | Prioritas | Bukti penerimaan dan pengujian |
|---|---|---|---|---|
| FR-01 | P, Tujuan 1 dan Batasan 1–2 | Basis data 973 puskesmas, 38 kabupaten/kota, snapshot 2024-S1 | P0 | Kode unik, jumlah cocok sumber, fasilitas tanpa titik tetap ada; D01–D03 |
| FR-02 | P, Latar Belakang dan Batasan Analisis | Geocoding alamat dengan tingkat ketelitian dan pemeriksaan | P0 | Tiap fasilitas berstatus missing/unverified/verified/rejected; titik analisis harus verified; G01–G04 |
| FR-03 | P, Tujuan 3 | Peta interaktif titik dan marker cluster | P0 | Zoom, pan, popup, cluster, layer, legenda; W01–W04 |
| FR-04 | P, Batasan Analisis | Choropleth per kabupaten/kota | P0 | Join berbasis kode, statistik berasal dari rilis sama, warna null tersendiri; G05, W05 |
| FR-05 | P, Tujuan 2 dan Desain Tabel | Analisis penduduk, luas, dan puskesmas per kecamatan | P0 | Kepadatan, rasio dan kebutuhan indikatif dihitung dengan metadata tahun; A01–A08 |
| FR-06 | P, Batasan Analisis | Buffer radius pelayanan | P0 | Radius dalam meter, hanya titik terverifikasi, overlap tidak dihitung ganda; G06–G10 |
| FR-07 | P, Tujuan 3 dan Lingkungan Pengujian | Python, GeoPandas, Folium, Google Colab, ekspor HTML | P0 | Run all dari runtime bersih menghasilkan laporan dan HTML tanpa rahasia; R01–R03 |
| FR-08 | P, Software | Laravel, Python, JavaScript | P0 | Aplikasi Laravel, pipeline Python dan peta JS berfungsi; I01, W01 |
| FR-09 | U, permintaan Supabase | PostgreSQL/PostGIS pada Supabase menggantikan MySQL | P0 | Migration, staging, constraints dan backup diuji pada PostgreSQL; I01–I06 |
| FR-10 | R | Pencarian nama/kode/alamat; filter kabupaten, kecamatan, layanan, karakter wilayah | P0 | Hasil peta, tabel, statistik konsisten; W02–W04 |
| FR-11 | R | Dashboard jumlah fasilitas, kualitas koordinat, penduduk dan rasio | P0 | Pembilang/penyebut jelas, agregasi berbobot, periode tampil; A06, W06 |
| FR-12 | R, mendukung tujuan aksesibilitas kecamatan | Choropleth kecamatan dan detail indikator | P0 | Kelengkapan wilayah dan indikator dapat diperiksa; G05, W05 |
| FR-13 | R | Sumber, metode, keterbatasan, versi dataset dapat dilihat | P0 | Setiap indikator memiliki sumber dan tahun; D07, W07 |
| FR-14 | R | Ekspor tabel CSV sesuai filter | P1 | Jumlah dan periode sama dengan tampilan, formula injection dinetralkan; W08, S05 |
| FR-15 | R | Admin terbatas untuk unggah, review, publikasi rilis, audit | P1 | Login, otorisasi dan rollback berfungsi; S01–S04, I04 |
| FR-16 | R | Daftar prioritas kecamatan berdasarkan defisit indikatif | P1 | Formula dan urutan transparan, nilai null tidak diperingkat; A04–A08 |
| FR-17 | U, permintaan testing | Pengujian data, spasial, aplikasi, keamanan, UAT dan reproduksibilitas | P0 | Laporan eksekusi, hasil aktual, defect dan bukti tersedia; semua suite |

**Catatan FR-15:** proses review dan publikasi dataset tetap wajib pada P0. Sebelum ada halaman admin, pengelola menjalankannya lewat perintah backend terkontrol. Antarmuka admin dapat menyusul tanpa mengurangi pengamanan data.

## Pemakai dan hak akses

| Peran | Aktivitas yang diizinkan | Batas akses |
|---|---|---|
| Pengunjung/penilai | Melihat peta, filter, tabel, statistik, metode dan artefak terbit | Hanya dataset yang dipublikasikan; tanpa akun |
| Pengelola data | Mengunggah ke staging, memperbaiki mapping, mereview koordinat, menjalankan analisis | Tidak boleh mengubah rilis terbit secara langsung |
| Admin/penerbit | Mengelola akun internal dan menerbitkan/mengembalikan versi rilis | Semua tindakan dicatat; hanya akun yang diundang |

Tim tiga orang dapat berbagi peran, tetapi review data penting sebaiknya diperiksa anggota yang berbeda dari penginputnya. Tidak ada pengumpulan data pasien, rekam medis, atau akun masyarakat dalam lingkup ini.

## Rancangan halaman dan alur

| Halaman | Komponen utama | Keadaan yang harus ditangani |
|---|---|---|
| Beranda/dashboard | Deskripsi penelitian, periode sumber, jumlah fasilitas, koordinat tervalidasi, tautan peta | Data sedang dimuat, dataset belum terbit, sumber tidak lengkap |
| Peta | Peta dominan, panel filter, pencarian, layer titik/batas/choropleth/buffer, legenda, daftar hasil | Hasil kosong, tile gagal, titik belum diverifikasi, permintaan gagal |
| Detail kecamatan | Nama dan kode, penduduk/tahun, luas/tahun, fasilitas terdaftar/terpetakan, rasio, daftar fasilitas | Jumlah nol, indikator null, periode berbeda, polygon belum ada |
| Detail puskesmas | Kode, alamat, wilayah, pelayanan, karakteristik, asal dan ketelitian koordinat | Titik belum ada: tampilkan alamat serta status, jangan letakkan di pusat wilayah |
| Data dan metodologi | Tabel paginasi, katalog sumber, versi, definisi rumus dan keterbatasan | Data belum valid dan perbedaan edisi sumber dijelaskan |
| Admin tahap P1 | Impor, daftar masalah, perbandingan kandidat lokasi, konfirmasi review, publish | Preview sebelum commit, error per baris, progres tugas, rollback |

Alur pengunjung: buka peta → pilih kabupaten → pilih kecamatan → lihat rasio dan fasilitas → aktifkan radius → baca batas interpretasinya → unduh tabel bila tersedia. Alur pengelola: unggah sumber → lihat laporan validasi → selesaikan masalah → hasilkan analisis → tinjau ringkasan rilis → publikasikan.

Peta default menunjukkan jumlah fasilitas yang benar-benar dipetakan. Ringkasan juga menampilkan jumlah terdaftar dan jumlah tanpa koordinat. Filter kualitas koordinat tidak boleh mengurangi jumlah fasilitas administratif untuk perhitungan rasio tanpa penjelasan khusus.

## Kebutuhan nonfungsional

Target di bawah adalah usulan engineering yang akan diukur pada staging, bukan angka dari proposal.

| ID | Sasaran | Cara menerima |
|---|---|---|
| NFR-01 | Benar dan terlacak | 100% kode fasilitas unik, FK valid, sumber/tahun wajib, tidak ada total ganda |
| NFR-02 | Responsif | Lebar 360, 768, 1366 px; panel filter dan popup dapat dipakai tanpa terpotong |
| NFR-03 | Performa | p95 API baca ≤800 ms warm; tampilan peta operasional ≤5 detik pada profil uji yang ditetapkan |
| NFR-04 | Aksesibilitas | Form berlabel, navigasi keyboard, fokus terlihat, data dapat dibaca lewat tabel, warna disertai legenda teks |
| NFR-05 | Keamanan | Rahasia hanya di server, akses tulis tertutup, input tervalidasi, audit perubahan tersedia |
| NFR-06 | Reproduksibilitas | Versi dependensi terkunci, hash input, parameter dan keluaran setiap run tersimpan |
| NFR-07 | Pemulihan | Target RPO 24 jam, RTO 4 jam untuk proyek; buktikan restore pada environment terpisah |
| NFR-08 | Kejelasan ilmiah | Radius dijelaskan sebagai jarak geometris; tahun berbeda dan keterbatasan koordinat selalu tampil |

## Batas penelitian dan pengembangan lanjutan

P0 menganalisis fasilitas terdaftar dan jarak geometris. Rute jalan, isochrone waktu tempuh, perjalanan antarpulau, penempatan lokasi puskesmas baru yang optimal, prediksi kebutuhan masa depan, serta pemeringkatan mutu layanan berada di P2. Diperlukan data jaringan, transportasi, hambatan dan/atau kapasitas tenaga kesehatan untuk klaim tersebut.

Marker clustering adalah pengelompokan visual saat zoom, bukan analisis statistik klaster spasial. DBSCAN, Moran's I atau Getis-Ord tidak menjadi syarat proposal. Bila ditambahkan, perlu hipotesis, parameter, unit analisis dan pengujian tersendiri.

Rujukan Pasal 10 Permenkes 19/2024 menyebut rasio 1:30.000 sekaligus aksesibilitas berbasis waktu tempuh. Rancangan menghitung indikator kebutuhan berbasis rasio dan membatasi kesimpulan buffer pada jarak geometris. Hasilnya merupakan bahan penelitian, bukan penetapan otomatis kepatuhan atau keputusan pembangunan. [Naskah resmi Pasal 10 halaman 8](https://jdih.kemkes.go.id/storage/documents/pdfs/2024permenkes019.pdf).
