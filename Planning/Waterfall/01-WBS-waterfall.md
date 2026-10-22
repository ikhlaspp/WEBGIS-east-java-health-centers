# WBS waterfall — WebGIS Puskesmas Jawa Timur

Versi: **usulan v1** · Tanggal: **22 Oktober 2026** · Status: **rencana, belum menjadi baseline yang disetujui**.

## Dasar dan batas WBS

WBS ini menguraikan seluruh pekerjaan untuk menghasilkan WebGIS analisis persebaran puskesmas Jawa Timur dengan Laravel, Leaflet, Supabase PostgreSQL/PostGIS, serta Python/Google Colab dan HTML Folium. Dokumen merupakan variasi waterfall, bukan penggantian jadwal delapan minggu pada planning sebelumnya.

Sumber cakupan: [kebutuhan](../01-kebutuhan-dan-ruang-lingkup.md), [audit dataset](../02-dataset-dan-audit.md), [arsitektur/metode](../03-arsitektur-dan-analisis.md), [database](../04-supabase-dan-kamus-data.md), [rencana uji](../05-rencana-pengujian.md), [tahapan awal](../06-tahapan-dan-kebutuhan.md), [catatan keputusan](../07-sumber-dan-keputusan.md), dan [revisi peran](../revisi.txt). Angka kondisi data di bawah berasal dari audit tersebut, bukan audit baru atau hasil scraping baru.

Ketentuan variasi ini:

- **Peran aplikasi:** admin dan user/guest. User/guest melihat hasil tanpa wajib akun. Admin menjalankan pengambilan data, review, analisis, dan publikasi. Tidak ada akun khusus pemegang/pengelola data. Peran kerja tim dan akun teknis database bukan tambahan peran pengguna aplikasi.
- **Pengumpulan data:** scraping/pengunduhan sumber terpilih, diikuti ekstraksi tabel dan validasi. Arsip lokal digunakan sebagai pembanding dan input historis yang dapat dilacak. Pengambilan data baru tidak boleh diam-diam mengganti snapshot historis fasilitas 2024-S1.
- **Baseline data awal:** 973 fasilitas di 38 kabupaten/kota; 565 kandidat koordinat dan 408 belum berkoordinat; lima kelompok koordinat identik; workbook gabungan memiliki 667 baris detail yang perlu rekonsiliasi. Jumlah kecamatan final mengikuti master resmi yang dipilih, bukan dipaksa sama dengan jumlah baris workbook.
- **P0:** keluaran inti yang wajib diterima. Login/session admin minimal dimasukkan dalam variasi ini untuk mendukung revisi peran. Operasi impor, review, analisis, publish, dan rollback wajib tersedia lewat perintah backend terotorisasi; antarmuka admin lengkap tetap P1. Ini memperjelas pemisahan FR-15 pada planning awal.
- **P1:** antarmuka admin lengkap, ekspor CSV publik, dan daftar prioritas kecamatan. Pekerjaannya tetap diuraikan agar tidak terlupakan, tetapi masuk rilis hanya jika dipilih saat pembekuan scope. P1 yang ditunda harus tercatat, bukan dianggap selesai.
- **Di luar scope/P2:** rekam medis/pasien, registrasi masyarakat, rute jalan dan waktu tempuh, optimasi lokasi fasilitas baru, prediksi kebutuhan, serta analisis statistik klaster lanjutan.
- Target performa, pemulihan, parameter analisis, dan UAT di planning awal adalah **usulan penerimaan proyek** yang ditetapkan pada fase kebutuhan; WBS tidak menyatakan bahwa target sudah tercapai.

## Cara membaca tiga level

WBS ini berisi **8 fase level 1, 38 kelompok pekerjaan level 2, dan 160 tugas rinci level 3**. Jumlah tersebut mencakup tugas P1 bersyarat; tugas itu tidak otomatis masuk komitmen rilis P0.

| Level | Bentuk kode | Isi | Contoh |
|---|---|---|---|
| 1 | `4` | Fase utama waterfall | Implementasi dan penyiapan data |
| 2 | `4.3` | Kelompok pekerjaan dengan satu keluaran utama | Data wilayah dan indikator |
| 3 | `4.3.2` | Tugas rinci/work package yang ditugaskan dan diverifikasi | Menyelesaikan crosswalk kode serta alias wilayah |

Nama proyek menjadi judul induk di luar penomoran; tidak dihitung sebagai level tambahan. Semua baris tabel berkode tiga bagian adalah level 3. Kolom bukti selesai berisi syarat penerimaan tugas, bukan level 4. Tidak ada tugas level 3 yang dianggap selesai hanya karena kode atau dokumennya sudah dibuat: hasil harus direview dan buktinya ditautkan.

PIC adalah peran pelaksana utama: **PM** = koordinator proyek; **AN** = analis kebutuhan; **DG** = data/GIS; **BE** = backend/database; **FE** = frontend; **QA** = pengujian; **OP** = deployment/operasi. Satu orang dapat memegang beberapa peran. Untuk tim tiga orang, pembagian awal dapat berupa A = DG/AN, B = BE/OP, C = FE/QA, dengan PM dirangkap salah satu anggota. PIC belum merupakan penetapan nama. Review pekerjaan penting dilakukan anggota lain bila memungkinkan; penerima hasil adalah pemilik proyek/dosen/pihak penilai yang benar-benar ditunjuk.

## Ringkasan fase dan aturan waterfall

| Level 1 | Fase | Keluaran utama | Prasyarat mulai | Gerbang keluar |
|---|---|---|---|---|
| 1 | Inisiasi dan perencanaan proyek | Charter, WBS baseline, mekanisme kendali | Proposal dan planning tersedia | WF-G1: mandat dan rencana disetujui |
| 2 | Analisis kebutuhan | SRS, spesifikasi data/metode, kriteria penerimaan | WF-G1 | WF-G2: kebutuhan dibekukan |
| 3 | Perancangan sistem | Desain data, aplikasi, pipeline, UI, dan pengujian | WF-G2 | WF-G3: desain dibekukan |
| 4 | Implementasi dan penyiapan data | Kandidat rilis aplikasi, dataset, notebook, dan HTML | WF-G3 | WF-G4: siap uji sistem |
| 5 | Pengujian dan penerimaan | Laporan uji, hasil UAT, kandidat rilis diterima | WF-G4 | WF-G5: layak deployment |
| 6 | Deployment dan verifikasi produksi | Aplikasi terpasang, data publik, operasi aktif | WF-G5 | WF-G6: produksi terverifikasi |
| 7 | Dokumentasi akhir dan serah terima | Paket as-built, laporan penelitian, berita acara | WF-G6 | WF-G7: hasil diserahterimakan |
| 8 | Pemeliharaan awal dan penutupan | Catatan dukungan, transisi operasi, penutupan | WF-G7 | WF-G8: kewajiban proyek selesai |

Fase berikutnya dimulai setelah gerbang fase sebelumnya diterima. Pekerjaan independen di dalam fase yang sama boleh berjalan bersamaan. Unit test dilakukan bersama implementasi, sedangkan pengujian sistem/UAT memiliki fase sendiri. Dokumen draf dikumpulkan sejak pekerjaan terkait berlangsung; fase 7 memfinalisasi versi as-built, bukan menulis semuanya dari nol.

Kegagalan gerbang menghasilkan daftar perbaikan dan pengujian ulang. Jika perbaikan mengubah kebutuhan/desain yang sudah dibekukan, PM membuat catatan perubahan, menilai dampaknya, meminta keputusan pihak penerima, lalu memperbarui baseline sebelum melanjutkan. Tidak meneruskan pekerjaan dengan dependensi yang belum dipenuhi.

## 1 — Inisiasi dan perencanaan proyek

### 1.1 — Mandat dan tujuan proyek

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 1.1.1 | Menelaah proposal, planning awal, dan revisi pengguna | AN | Ringkasan tujuan, batas penelitian, serta daftar konflik antar dokumen tersedia. |
| 1.1.2 | Mengidentifikasi stakeholder dan penerima hasil | PM | Daftar stakeholder, kebutuhan keterlibatan, serta pihak yang berhak menerima tiap gerbang ditetapkan. |
| 1.1.3 | Menentukan sasaran dan ukuran keberhasilan proyek | PM | Sasaran aplikasi, dataset, hasil analisis, dan keluaran akademik terukur dicatat. |
| 1.1.4 | Menyusun dan meninjau project charter | PM | Charter memuat tujuan, scope awal, asumsi, batasan, serta penanggung jawab; hasil review terdokumentasi. |

### 1.2 — Rencana pelaksanaan dan sumber daya

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 1.2.1 | Memeriksa kelengkapan WBS bersama tim | PM | Seluruh keluaran proyek memiliki paket kerja; tidak ada pekerjaan ganda tanpa pembagian keluaran. |
| 1.2.2 | Menetapkan penanggung jawab dan reviewer paket kerja | PM | Matriks nama–peran, kapasitas, dan reviewer dibuat; peran aplikasi tetap admin dan guest. |
| 1.2.3 | Menaksir usaha, dependensi, dan durasi dari paket kerja | PM | Estimasi bottom-up, asumsi produktivitas verifikasi lokasi, cadangan, dan jalur kritis disusun untuk jadwal berikutnya. |
| 1.2.4 | Menyusun kebutuhan biaya, alat, akun, dan lingkungan | OP | Daftar hosting, database, sumber data, geocoding, penyimpanan, serta pemilik akun dan anggaran disiapkan. |

### 1.3 — Kendali proyek dan kualitas

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 1.3.1 | Membuat daftar risiko dan rencana penanganannya | PM | Risiko sumber berubah, data hilang, lokasi sulit, polygon historis, dan kapasitas tim memiliki owner serta respons. |
| 1.3.2 | Menetapkan tata cara perubahan scope dan keputusan | PM | Format change request, pencatatan keputusan, penilaian dampak, dan alur persetujuan baseline tersedia. |
| 1.3.3 | Menetapkan standar bukti selesai dan penyimpanan artefak | QA | Aturan nama berkas, versi, reviewer, pencatatan defect, serta lokasi bukti kerja disepakati. |
| 1.3.4 | Menetapkan pelaporan rutin dan menerima WF-G1 | PM | Jadwal laporan status/risiko dan format notulen aktif; charter serta rencana awal memiliki catatan penerimaan. |

## 2 — Analisis kebutuhan

### 2.1 — Kebutuhan pengguna dan batas sistem

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 2.1.1 | Menggali skenario penggunaan admin dan guest | AN | Skenario melihat hasil, mencari fasilitas, membandingkan wilayah, serta pengelolaan rilis admin terdokumentasi. |
| 2.1.2 | Menetapkan kebutuhan fungsional dan prioritas rilis | AN | FR-01–FR-17 dipetakan ke P0/P1; keputusan fitur opsional tercatat satu per satu. |
| 2.1.3 | Menetapkan batas akses aplikasi | BE | Guest hanya membaca hasil terbit; admin mengelola proses internal; tidak ada registrasi publik atau role pengelola data. |
| 2.1.4 | Menentukan isi setiap halaman dan alur navigasi | FE | Kebutuhan beranda, peta, tabel, detail, sumber/metode, dan login admin ditulis dengan keadaan kosong/gagal. |

### 2.2 — Kebutuhan sumber dan pengumpulan data

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 2.2.1 | Menginventarisasi arsip dan kesenjangan dataset | DG | Audit awal dipetakan ke kebutuhan fasilitas, koordinat, penduduk, luas, kode wilayah, dan polygon. |
| 2.2.2 | Memeriksa kelayakan sumber untuk scraping/pengunduhan | DG | Daftar sumber, format, akses, ketentuan penggunaan, contoh halaman/file, dan alternatif sumber tercatat; belum menjalankan batch produksi. |
| 2.2.3 | Menetapkan periode, satuan, dan identitas sumber | DG | Snapshot fasilitas, tahun observasi/publikasi, sistem kode, edisi polygon, dan aturan data campuran ditetapkan. |
| 2.2.4 | Menentukan aturan kelengkapan dan penanganan data bermasalah | DG | Null/nol, agregat, duplikat, alias, OCR, koordinat hilang, dan analisis parsial memiliki kriteria penerimaan. |

### 2.3 — Kebutuhan analisis dan interpretasi

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 2.3.1 | Menentukan indikator tabular dan cara agregasinya | DG | Kepadatan, rasio, kebutuhan/defisit indikatif, jumlah fasilitas, dan perlakuan pembagi nol didefinisikan. |
| 2.3.2 | Menentukan kebutuhan peta tematik dan legenda | DG | Metrik kabupaten/kecamatan, kelas warna, unit, no-data, dan filter kualitas koordinat ditetapkan. |
| 2.3.3 | Menentukan kebutuhan analisis radius | DG | Radius usulan 1/3/5 km, input lokasi terverifikasi, overlap, batas wilayah, dan arti cakupan geometris dicatat. |
| 2.3.4 | Menetapkan keluaran penelitian dan batas kesimpulan | AN | Notebook, HTML, tabel/peta laporan, sumber dan tahun wajib; tidak menyamakan radius dengan waktu tempuh atau penduduk terlayani. |

### 2.4 — Kebutuhan nonfungsional dan penerimaan

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 2.4.1 | Menetapkan target performa dan kegunaan | QA | Profil perangkat/jaringan, p95 API, waktu peta siap, viewport, keyboard, dan format label disepakati. |
| 2.4.2 | Menetapkan target keamanan, backup, dan reproduksibilitas | BE | Hak akses, lokasi rahasia, audit, retensi, RPO/RTO, versi dependensi, dan manifest run menjadi kriteria tertulis. |
| 2.4.3 | Menyusun strategi UAT serta matriks kebutuhan–uji | QA | Skenario, calon peserta, target keberhasilan, dan jejak FR/NFR ke test ID tersedia. |
| 2.4.4 | Menyelesaikan SRS dan menerima WF-G2 | PM | Keputusan sumber, P1, cakupan analisis, dan target uji tidak lagi ambigu; SRS mendapat penerimaan baseline. |

## 3 — Perancangan sistem

### 3.1 — Arsitektur dan lingkungan

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 3.1.1 | Merancang hubungan Laravel, Leaflet, Supabase, dan Colab | BE | Diagram komponen, alur data, dan batas browser/server/notebook tersedia. |
| 3.1.2 | Merancang lingkungan development, test/staging, dan produksi | OP | Kebutuhan runtime, koneksi, isolasi akun/data, serta strategi dependency lock ditulis. |
| 3.1.3 | Merancang struktur kode dan alur integrasi | BE | Struktur repositori, modul, aturan review, CI, konfigurasi, serta penyimpanan artefak disepakati. |
| 3.1.4 | Merancang proses batch dan penanganan kegagalan | BE | Alur job, retry terbatas, idempotensi, timeout, log, dan pemulihan batch parsial terdokumentasi. |

### 3.2 — Basis data dan keamanan

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 3.2.1 | Membuat ERD dan kamus data final | BE | Entitas sumber, wilayah, fasilitas, indikator, review, rilis, analisis, artefak, dan audit memiliki kolom/relasi jelas. |
| 3.2.2 | Merancang constraint, indeks, dan migrasi | BE | Kunci unik, FK lintas edisi, status koordinat, geometri, nilai null, serta urutan migration dirinci. |
| 3.2.3 | Merancang otorisasi admin dan akun teknis database | BE | Session/policy admin, role runtime/worker/publisher, grants/RLS, dan penutupan akses publik staging dirancang. |
| 3.2.4 | Merancang versi rilis, publikasi, dan pemulihan | BE | Transisi status, larangan mengubah rilis terbit, pergantian pointer, backup berkas/DB, serta rollback didefinisikan. |

### 3.3 — Scraping, ETL, dan verifikasi data

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 3.3.1 | Merancang adapter pengambilan tiap sumber | DG | URL/parameter, paginasi/daftar file, parser HTML/PDF/CSV, metadata unduh, cache, dan deteksi struktur berubah dirinci. |
| 3.3.2 | Merancang normalisasi dan crosswalk wilayah | DG | Aturan angka/unit, pemisahan subtotal, alias dalam parent/edisi, serta penanganan Sempol–Ijen ditulis. |
| 3.3.3 | Merancang pencarian dan review koordinat | DG | Prioritas sumber, query, precision/status, bukti lokasi, antrean missing/duplikat, dan syarat verified didefinisikan. |
| 3.3.4 | Merancang staging dan laporan kualitas | DG | Kontrak file, hash, nomor baris asal, quarantine baris gagal, manifest, serta aturan lolos dataset tersedia. |

### 3.4 — Metode analisis dan keluaran penelitian

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 3.4.1 | Menulis spesifikasi rumus dan contoh hasil acuan | DG | Rumus dan contoh independen mencakup null, nol, pembulatan, agregasi berbobot, dan defisit antarwilayah. |
| 3.4.2 | Merancang operasi spasial dan toleransi | DG | CRS, lon/lat, buffer meter, union, clip, luas, pulau/perbatasan, serta toleransi pembanding ditetapkan. |
| 3.4.3 | Merancang GeoJSON dan kelas choropleth | DG | Geometri analisis/tampilan dipisahkan; join berbasis kode dan legenda setiap metrik ditentukan. |
| 3.4.4 | Merancang notebook dan manifest hasil | DG | Tahapan Run all, input rilis, parameter, output HTML/tabel/peta, serta kesetaraan dengan aplikasi dirinci. |

### 3.5 — API dan antarmuka

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 3.5.1 | Menentukan kontrak endpoint dan respons | BE | Endpoint rilis, wilayah, fasilitas, statistik, layer, buffer, sumber, serta validasi/error memiliki spesifikasi. |
| 3.5.2 | Membuat wireframe halaman publik | FE | Beranda, peta/filter, detail, tabel, dan metode memiliki rancangan desktop/mobile yang direview. |
| 3.5.3 | Merancang interaksi dan keadaan antarmuka | FE | Loading, empty, gagal, reset filter, pergantian rilis, request terlambat, fokus keyboard, dan popup dirinci. |
| 3.5.4 | Merancang login admin dan fitur P1 terpilih | FE | Login/logout selalu dirancang; rancangan dashboard admin/ekspor/ranking hanya disertakan sesuai keputusan scope. |

### 3.6 — Desain pengujian dan review desain

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 3.6.1 | Menyiapkan spesifikasi fixture dan expected result | QA | Kasus data, formula, spasial, akses, impor, serta kegagalan scraping mempunyai ekspektasi yang dapat diperiksa. |
| 3.6.2 | Menyusun prosedur uji integrasi dan nonfungsional | QA | Langkah uji API/UI, keamanan, beban, restore, dan Colab mencantumkan environment, input, serta bukti. |
| 3.6.3 | Menyusun prosedur UAT dan kriteria gerbang rilis | QA | Skrip tugas pengguna, pencatatan bantuan, severity defect, retest, dan penerimaan rilis siap digunakan. |
| 3.6.4 | Meninjau konsistensi desain dan menerima WF-G3 | PM | Desain ditelusuri ke SRS; konflik skema/API/metode diselesaikan; baseline desain diterima. |

## 4 — Implementasi dan penyiapan data

### 4.1 — Fondasi pengembangan

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.1.1 | Membuat repositori dan struktur proyek | BE | Struktur kode, aturan ignore, README pengembangan, dan jejak revisi tersedia tanpa rahasia atau dump produksi. |
| 4.1.2 | Menyiapkan Laravel dan build frontend | BE | Aplikasi dasar berjalan lokal; konfigurasi contoh, dependency lock, dan proses build tersedia. |
| 4.1.3 | Menyiapkan Python, Colab, dan alat pengujian | DG | Environment terkunci, notebook awal, serta test runner dapat dijalankan dengan fixture sintetis. |
| 4.1.4 | Menyiapkan pipeline pemeriksaan otomatis | QA | Lint/build/unit test berjalan pada perubahan kode; hasil kegagalan dapat ditelusuri. |

### 4.2 — Pengambilan sumber melalui scraping

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.2.1 | Mengimplementasikan pengunduh dan parser data fasilitas | DG | Data identitas/alamat/pelayanan diekstrak dari sumber periode terpilih; URL, halaman/baris, dan respons mentah tersimpan. |
| 4.2.2 | Mengimplementasikan pengambilan data penduduk dan luas | DG | Adapter tabel/file BPS mempertahankan tahun, unit, dan locator; OCR digunakan hanya pada sumber yang memerlukannya. |
| 4.2.3 | Mengimplementasikan pengambilan kode dan polygon wilayah | DG | Master/polygon sesuai edisi pilihan tersimpan dengan sistem kode, CRS, metadata, dan cakupan wilayah. |
| 4.2.4 | Menambahkan cache, retry, dan pemeriksaan kelengkapan scraping | DG | Timeout, rate limit sesuai sumber, paginasi terputus, kolom berubah, dan hasil kosong tidak menghasilkan batch sukses palsu. |
| 4.2.5 | Menjalankan pengambilan sumber dan membekukan input mentah | DG | Manifest unduh, hash, jumlah objek, periode, dan laporan kegagalan tersedia; input lengkap dibandingkan dengan arsip historis. |

### 4.3 — Data wilayah dan indikator

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.3.1 | Mengekstrak dan menormalisasi tabel sumber | DG | Kode tetap teks; spasi/angka dinormalisasi pada kolom olahan; nilai mentah dan locator tetap tersimpan. |
| 4.3.2 | Menyelesaikan crosswalk kode serta alias wilayah | DG | Pemetaan berdasarkan kode, parent, dan edisi; antrean alias serta kasus Sempol–Ijen memiliki keputusan berbukti. |
| 4.3.3 | Memisahkan subtotal dan merekonsiliasi master fasilitas | DG | Detail tidak tercampur agregat; 973 identitas historis serta kategori/totalnya cocok atau koreksinya dijelaskan. |
| 4.3.4 | Memverifikasi angka penduduk, luas, tahun, dan unit | DG | Nilai berisiko OCR/sumber alternatif diperiksa; hektar/km² serta null/nol benar; selisih total dicatat. |
| 4.3.5 | Memvalidasi polygon dan kelengkapan master wilayah | DG | Geometri valid, pulau terjaga, kode join unik, dan wilayah tanpa fasilitas tetap muncul; perbaikan memiliki log. |

### 4.4 — Koordinat fasilitas dan mutu lokasi

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.4.1 | Menyiapkan antrean geocoding dan pencatatan bukti | DG | Query alamat, kandidat, provider, waktu, precision, status, dan reviewer dapat disimpan per kode fasilitas. |
| 4.4.2 | Mereview 565 pasangan koordinat yang sudah tersedia | DG | Setiap kandidat mempunyai keputusan serta bukti; label ditemukan tidak otomatis menjadi verified. |
| 4.4.3 | Menelusuri 408 fasilitas tanpa koordinat | DG | Setiap fasilitas memiliki hasil pencarian; yang belum dapat dibuktikan tetap missing/unverified dengan alasan. |
| 4.4.4 | Menyelesaikan anomali koordinat dan konflik wilayah | DG | Lima kelompok titik identik, lokasi di batas/luar polygon, centroid, serta pulau ditinjau tanpa menghapus fasilitas secara otomatis. |
| 4.4.5 | Membekukan laporan kelayakan data spasial | DG | Daftar titik layak buffer, titik dikeluarkan, cakupan numerik, dan batas analisis tersedia; cakupan sesuai SRS. |

**Pelaksanaan tugas berulang:** 4.4.2–4.4.4 menggunakan checklist per kode fasilitas dan dapat dibagi per kabupaten. Checklist adalah rincian eksekusi dalam paket level 3, bukan penambahan level WBS. Menelusuri seluruh fasilitas tidak berarti semua lokasi pasti ditemukan. Jika SRS mensyaratkan cakupan penuh, lokasi yang belum terverifikasi tetap menghalangi gerbang; cakupan parsial hanya diterima melalui keputusan scope yang terdokumentasi.

### 4.5 — Supabase dan pipeline impor

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.5.1 | Menyiapkan database development dan test dengan PostGIS | BE | Koneksi server, SSL, konfigurasi rahasia, dan kueri spasial dasar berfungsi pada environment terpisah. |
| 4.5.2 | Membuat migration tabel, constraint, dan indeks | BE | Skema app/gis/staging beserta relasi, validasi geometri, dan indeks dapat dibangun dari database kosong. |
| 4.5.3 | Mengimplementasikan grants dan pembatasan akses data | BE | Runtime, worker, dan publisher hanya memiliki hak yang dirancang; staging/draft tidak terbaca publik. |
| 4.5.4 | Membuat impor staging dan promosi data tervalidasi | BE | Impor mengikuti urutan FK; baris gagal dilaporkan; menjalankan ulang batch tidak menggandakan data. |
| 4.5.5 | Memuat kandidat dataset hasil kurasi | BE | Jumlah, FK, tahun, sumber, kode wilayah, dan status lokasi sesuai laporan mutu; kandidat memiliki release_id. |

### 4.6 — Perhitungan indikator dan analisis spasial

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.6.1 | Membuat perhitungan indikator kecamatan | DG | Kepadatan, rasio, kebutuhan/defisit, flag tanpa fasilitas, dan null/nol sesuai contoh acuan. |
| 4.6.2 | Membuat agregasi kabupaten dan provinsi | DG | Rasio berasal dari total pembilang/penyebut; defisit agregat sesuai definisi; kelengkapan data ditampilkan. |
| 4.6.3 | Membuat buffer radius titik yang terverifikasi | DG | Radius dalam meter, parameter run tersimpan, dan kandidat tidak layak tidak masuk analisis. |
| 4.6.4 | Membuat union, clip, dan luas cakupan wilayah | DG | Overlap dihitung sekali; fasilitas tetangga dalam dataset diperhitungkan; hasil 0–100% memiliki penyebut luas geometri. |
| 4.6.5 | Menyimpan hasil run dan layer tematik | DG | Hasil tabel/GeoJSON terhubung ke rilis, parameter dan versi metode; unit test formula/spasial lulus. |

### 4.7 — Backend publik dan kendali admin

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.7.1 | Membuat API rilis, wilayah, dan katalog sumber | BE | Hanya metadata publik terbaca; parent wilayah, edisi, dan periode sumber sesuai kontrak. |
| 4.7.2 | Membuat API fasilitas, pencarian, filter, dan detail | BE | Daftar terpaginasi; filter tervalidasi; fasilitas tanpa titik tetap terakses; response/error sesuai desain. |
| 4.7.3 | Membuat API statistik, GeoJSON, dan buffer | BE | Semua endpoint memakai rilis/run konsisten; query dan cache tidak mencampur hasil antarversi. |
| 4.7.4 | Membuat login/logout admin dan otorisasi operasi internal | BE | Session admin dan policy berjalan; guest tidak dapat menulis, memanggil proses internal, atau melihat draft. |
| 4.7.5 | Membuat command review, analisis, publish, rollback, dan audit | BE | Admin dapat menjalankan siklus rilis via jalur terotorisasi; publikasi atomik, rilis terbit immutable, dan audit tersedia. |

### 4.8 — Antarmuka publik dan peta

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.8.1 | Membuat layout, navigasi, dan dashboard | FE | Tampilan Indonesia responsif; jumlah terdaftar, terpetakan, terverifikasi, serta periode dibedakan. |
| 4.8.2 | Membuat peta dasar, marker, cluster, dan popup | FE | Zoom/pan, kontrol layer, atribusi, titik bertumpuk, dan popup aman berfungsi; tidak membuat marker palsu untuk missing. |
| 4.8.3 | Membuat pencarian dan filter bertingkat | FE | Kabupaten–kecamatan, pelayanan, karakteristik, kualitas titik, reset, serta hasil kosong sesuai kontrak. |
| 4.8.4 | Membuat layer choropleth, buffer, dan legenda | FE | Warna/unit/no-data jelas; radius dan cakupan input tampil; metrik administratif tidak keliru berubah oleh filter marker. |
| 4.8.5 | Membuat tabel dan halaman detail fasilitas/kecamatan | FE | Tabel dapat dipaginasi; identitas, indikator, tahun, sumber, serta status tanpa koordinat dapat dibaca. |
| 4.8.6 | Membuat halaman metodologi dan penanganan state UI | FE | Sumber/versi tersedia; loading/error/empty, tile gagal, respons lama, serta navigasi keyboard ditangani. |

### 4.9 — Notebook dan HTML Folium

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.9.1 | Menghubungkan notebook ke snapshot rilis yang aman | DG | Input, hash, release_id, parameter, serta urutan validasi tersedia tanpa kredensial produksi. |
| 4.9.2 | Mengintegrasikan modul analisis ke notebook | DG | Notebook memakai definisi metode yang sama dengan 4.6; tidak membuat rumus alternatif tanpa kendali versi. |
| 4.9.3 | Membuat visualisasi Folium dan ekspor HTML/tabel | DG | Marker, layer, legenda, sumber, periode, serta batas interpretasi sesuai dataset/run yang dipilih. |
| 4.9.4 | Menambahkan manifest dan panduan Run all | DG | Artefak memiliki hash/versi; kebutuhan internet dan langkah menjalankan dari runtime bersih terdokumentasi. |

### 4.10 — Fitur tambahan P1 sesuai scope terpilih

Seluruh tugas pada kelompok ini **P1**. Jika tidak dipilih pada WF-G2, statusnya `deferred` dengan catatan keputusan. Kontrol backend P0 pada 4.7.5 tetap wajib.

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.10.1 | Membuat dashboard admin untuk menjalankan dan memantau batch | FE | Admin dapat memulai pekerjaan yang diizinkan serta melihat status/error; hanya admin dapat mengaksesnya. |
| 4.10.2 | Membuat layar review data dan publikasi rilis | FE | Masalah mapping/lokasi dapat ditinjau; preview, alasan keputusan, publish/rollback, dan audit tersambung ke backend. |
| 4.10.3 | Membuat ekspor CSV hasil filter | BE | Kode, jumlah, periode, dan filter sesuai tampilan; nilai berpotensi formula spreadsheet dinetralkan. |
| 4.10.4 | Membuat daftar prioritas kecamatan | FE | Urutan berdasarkan definisi defisit/rasio; tie-break stabil; data tidak lengkap tidak diperingkat sebagai nol. |

### 4.11 — Integrasi kandidat rilis

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 4.11.1 | Menghubungkan pipeline, database, API, UI, dan artefak | BE | Satu kandidat rilis dapat ditelusuri dari sumber ke tabel, peta, statistik, dan HTML. |
| 4.11.2 | Melengkapi unit/component test modul yang berubah | QA | Parser, formula, geometri, validasi, otorisasi, dan layanan rilis memiliki hasil uji acuan yang lulus. |
| 4.11.3 | Menjalankan smoke test dan memperbaiki kegagalan integrasi | QA | Alur utama berjalan di staging; kegagalan komponen sudah diperbaiki atau tercatat sebagai penghalang gerbang. |
| 4.11.4 | Membekukan kandidat uji dan menerima WF-G4 | PM | Revisi kode, release_id, analysis_run_id, laporan mutu, dan daftar scope tersedia; kandidat layak masuk uji sistem. |

**Dependensi penting di dalam fase 4:** 4.2 menghasilkan input untuk 4.3/4.4; review koordinat terhadap wilayah memerlukan polygon 4.3.5. Setup dan migration 4.5.1–4.5.4 dapat berjalan bersama pengolahan data, tetapi 4.5.5 menunggu hasil kurasi 4.3/4.4. Analisis final 4.6 menunggu data yang lolos; frontend/API dapat dikembangkan memakai fixture sesuai kontrak. Notebook 4.9 memakai hasil/modul 4.6. Integrasi 4.11 menunggu semua paket P0 dan P1 terpilih. Fixture tidak dipublikasikan sebagai hasil penelitian.

## 5 — Pengujian dan penerimaan

### 5.1 — Pengujian scraping dan dataset

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 5.1.1 | Menguji kegagalan sumber dan perubahan struktur scraping | QA | Respons timeout, rate limit, halaman kosong, schema berubah, dan paginasi tidak lengkap menghasilkan laporan yang benar; uji memakai fixture/mocking. |
| 5.1.2 | Menguji integritas identitas, jumlah, dan kategori | QA | D01–D04/D10 lulus; 973 kode historis tidak hilang/ganda, subtotal tidak terhitung sebagai detail. |
| 5.1.3 | Menguji mapping, tahun, unit, dan nilai berisiko | QA | D05–D09 lulus; bukti OCR/sumber alternatif, kelengkapan polygon, serta null/nol tersedia. |
| 5.1.4 | Menguji pengulangan ETL dan konsistensi provenance | QA | D11 dan pemeriksaan manifest lulus; input yang sama tidak menggandakan data atau mengubah nilai tanpa sebab. |

### 5.2 — Pengujian formula dan spasial

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 5.2.1 | Menguji formula, pembulatan, null, nol, dan agregasi | QA | A01–A07 lulus dengan hasil acuan independen; kesetaraan Python/SQL tercatat. |
| 5.2.2 | Menguji kelayakan koordinat dan join peta | QA | G01–G05 lulus; urutan koordinat, duplikat, bukti verified, no-data, dan perbatasan diperiksa. |
| 5.2.3 | Menguji radius, overlap, clip, geometri, dan pulau | QA | G06–G10 lulus; satuan meter benar, overlap tidak ganda, cakupan terbatas, dan pulau tidak hilang. |
| 5.2.4 | Membandingkan hasil spasial lintas implementasi | DG | G11 lulus terhadap referensi independen dengan toleransi yang ditetapkan sebelum uji, bukan disesuaikan setelah gagal. |

### 5.3 — Pengujian backend dan keamanan

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 5.3.1 | Menguji migration, constraint, dan impor | QA | I01–I04 lulus pada PostgreSQL/PostGIS; data lintas edisi, duplikat, dan partial import ditolak dengan benar. |
| 5.3.2 | Menguji konsistensi rilis, rollback, dan kegagalan layanan | QA | I05–I08 lulus; akses dibatasi, cache/endpoint konsisten, timeout tidak menghasilkan publikasi setengah jadi. |
| 5.3.3 | Menguji session, otorisasi, injeksi, dan keamanan popup | QA | S01–S03 lulus untuk admin/guest; role pengelola pada rencana lama dihapus dari fixture; akses command internal turut diuji. |
| 5.3.4 | Menguji paparan rahasia dan izin database aktual | QA | S04/S07 lulus dengan runtime non-owner; HTML/bundle/log tidak membocorkan rahasia; staging/draft tidak terbaca publik. |

### 5.4 — Pengujian antarmuka dan fitur terpilih

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 5.4.1 | Menguji navigasi, peta, pencarian, dan filter | QA | W01–W04 lulus; tabel/marker sesuai filter; fasilitas tanpa titik tetap ditemukan. |
| 5.4.2 | Menguji choropleth, statistik, detail, dan metode | QA | W05–W07 lulus; tahun, rilis, unit, sumber, dan no-data konsisten di seluruh layar. |
| 5.4.3 | Menguji responsivitas, aksesibilitas, dan request bersaing | QA | W09–W10 lulus pada viewport dan browser yang ditetapkan; filter lama tidak menimpa hasil terbaru. |
| 5.4.4 | Menguji fitur P1 terpilih dan validasi file backend P0 | QA | W08/A08/S05 relevan lulus; antarmuka admin terpilih diuji end-to-end. Validasi input backend tetap diuji meskipun UI P1 ditunda. |

### 5.5 — Performa, pemulihan, dan reproduksibilitas

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 5.5.1 | Mengukur waktu muat, respons API, dan beban staging | QA | P01–P03 memiliki profil pengukuran dan hasil terhadap target; layanan tile/geocoder publik tidak dijadikan target load test. |
| 5.5.2 | Menguji backup dan restore database serta artefak | OP | S06 lulus di lingkungan terpisah; jumlah/hash, relasi, login, peta, RPO dan RTO tercatat. |
| 5.5.3 | Menjalankan Colab dari runtime bersih dan mengulang run | QA | R01–R02 lulus; input/versi/parameter jelas dan hasil ekuivalen sesuai toleransi. |
| 5.5.4 | Membandingkan HTML Folium dengan aplikasi | QA | R03 lulus di browser yang ditetapkan; jumlah, kategori, legenda, tahun, rilis, dan ketergantungan internet sesuai. |

### 5.6 — UAT dan penerimaan kandidat rilis

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 5.6.1 | Menyiapkan peserta, kandidat rilis, dan instrumen UAT | QA | Peserta aktual, skrip, lembar hasil, dan release_id dicatat; komposisi mengikuti baseline kebutuhan. |
| 5.6.2 | Melaksanakan UAT dan merangkum temuan | QA | Keberhasilan mandiri, bantuan, waktu, serta salah tafsir radius/sumber direkam untuk setiap tugas. |
| 5.6.3 | Memperbaiki defect dan menjalankan retest/regresi | QA | Defect memiliki pelaksana perbaikan BE/FE/DG, bukti retest, dan dampak regresi; tidak ada kritis/tinggi terbuka. |
| 5.6.4 | Menyelesaikan laporan uji dan menerima WF-G5 | PM | Semua P0 dan P1 terpilih lulus, UAT memenuhi baseline, batas data diterima; kandidat kode/data untuk deployment ditetapkan. |

## 6 — Deployment dan verifikasi produksi

### 6.1 — Persiapan lingkungan produksi

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 6.1.1 | Menyiapkan hosting, domain bila diperlukan, dan HTTPS | OP | Runtime kompatibel, document root, sertifikat, konfigurasi jaringan, dan akun pemilik tersedia. |
| 6.1.2 | Menyiapkan Supabase produksi dan penyimpanan artefak | BE | PostGIS, koneksi, kapasitas, izin, serta storage terpisah dari data uji dan siap menerima migration. |
| 6.1.3 | Memasang konfigurasi rahasia dan akun admin awal | OP | Rahasia berada di server, debug publik mati, admin tersedia, dan akses teknis dibatasi sesuai desain. |
| 6.1.4 | Menyiapkan runbook deployment dan titik pemulihan | OP | Urutan rilis, penanggung jawab, kriteria rollback, backup awal, serta jendela penerapan tercatat. |

### 6.2 — Penerapan aplikasi dan dataset

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 6.2.1 | Memasang versi aplikasi yang telah diterima | OP | Kode/build/lockfile sama dengan kandidat WF-G5; revision tag tercatat. |
| 6.2.2 | Menjalankan migration dan memuat dataset final | BE | Struktur/grants terpasang; jumlah, FK, hash, dan release_id cocok dengan kandidat yang diterima. |
| 6.2.3 | Memasang hasil analisis dan menerbitkan rilis aktif | BE | Artefak/run sesuai dataset; pointer rilis berganti atomik; cache dan metadata publik benar. |
| 6.2.4 | Mengaktifkan worker, monitoring, dan backup | OP | Job, health check, log, peringatan operasional, serta jadwal backup DB/berkas berjalan sesuai kebutuhan. |

### 6.3 — Verifikasi pascadeployment

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 6.3.1 | Menjalankan smoke test produksi | QA | HTTPS, login/logout, peta, filter, detail, sumber, dan HTML dapat dibuka menggunakan rilis yang benar. |
| 6.3.2 | Memeriksa akses publik dan konfigurasi operasi | QA | Guest tidak melihat draft/rahasia; admin berfungsi; monitoring dan backup pertama memiliki bukti. |
| 6.3.3 | Menangani kegagalan penerapan atau memvalidasi kesiapan rollback | OP | Jika gagal, versi terakhir yang valid dipulihkan dan diuji; jika berhasil, hasil rehearsal staging serta titik pemulihan diverifikasi tanpa gangguan produksi yang tidak perlu. |
| 6.3.4 | Mencatat hasil deployment dan menerima WF-G6 | PM | URL, versi aplikasi/data, bukti smoke test, isu tersisa, dan pemilik operasi dicatat; produksi diterima. |

## 7 — Dokumentasi akhir dan serah terima

### 7.1 — Dokumentasi pengguna dan teknis

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 7.1.1 | Memfinalisasi panduan guest dan admin | FE | Panduan memakai layar aktual dan menjelaskan pencarian, filter, interpretasi hasil, serta proses admin yang benar-benar tersedia. |
| 7.1.2 | Memfinalisasi panduan instalasi dan operasi | OP | Langkah build, konfigurasi, migration, job, deployment, backup, restore, dan troubleshooting sesuai hasil implementasi. |
| 7.1.3 | Memfinalisasi dokumentasi desain as-built | BE | Diagram, ERD, kamus data, kontrak API, hak akses, dan perubahan dari desain awal sesuai aplikasi final. |
| 7.1.4 | Memfinalisasi panduan data dan reproduksi analisis | DG | Sumber, scraping, kurasi, metode, parameter, manifest, serta langkah Run all/ekspor dapat diikuti ulang. |

### 7.2 — Laporan penelitian dan paket hasil

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 7.2.1 | Menulis hasil analisis beserta keterbatasannya | DG | Tabel/peta, tahun sumber, cakupan lokasi, dan kesimpulan sesuai dataset final; tidak melampaui bukti yang tersedia. |
| 7.2.2 | Menyusun bagian implementasi dan pengujian laporan | QA | Metode waterfall, hasil uji aktual, defect/retest, UAT, serta keputusan scope didukung bukti. |
| 7.2.3 | Menyiapkan materi presentasi dan skenario demonstrasi | PM | Demo memperlihatkan fitur inti, admin, sumber, radius, no-data, serta notebook/HTML pada versi yang sama. |
| 7.2.4 | Mengemas kode, data yang boleh dibagikan, dan bukti proyek | OP | Manifest paket mencakup kode, migration, lockfile, notebook, HTML, dokumentasi, hasil uji, dan backup; rahasia diserahkan lewat jalur terpisah. |

### 7.3 — Penyerahan kepada penerima

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 7.3.1 | Melaksanakan demonstrasi dan orientasi penggunaan | PM | Peserta mencoba alur guest/admin yang relevan; pertanyaan serta tindak lanjut tercatat. |
| 7.3.2 | Menyerahkan akses dan kepemilikan operasional | OP | Penerima dapat mengakses repositori, hosting, database, dan backup sesuai wewenangnya; serah akses dibuktikan tanpa menulis rahasia di laporan. |
| 7.3.3 | Memeriksa kelengkapan paket dan isu yang diterima | QA | Checklist keluaran lengkap; semua tautan/artefak dapat dibuka; known issues dan P1 yang ditunda dinyatakan jelas. |
| 7.3.4 | Menyepakati dukungan awal dan menerima WF-G7 | PM | Berita acara mencatat hasil diterima, tanggal mulai/akhir dukungan, batas layanan, owner insiden, dan kewajiban tersisa. |

## 8 — Pemeliharaan awal dan penutupan

Fase ini terbatas pada masa dukungan yang ditetapkan saat serah terima. Operasi berkelanjutan setelahnya menjadi tanggung jawab penerima; pengembangan fitur baru memerlukan scope tersendiri.

### 8.1 — Dukungan dan perbaikan awal

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 8.1.1 | Memantau kesehatan layanan dan backup selama dukungan | OP | Log pemeriksaan, error aplikasi/job, kapasitas, dan keberhasilan backup diperiksa sesuai frekuensi yang disepakati. |
| 8.1.2 | Menerima dan mengklasifikasikan insiden | QA | Setiap laporan memiliki langkah reproduksi, severity, dampak, owner, dan keputusan bug/perubahan scope. |
| 8.1.3 | Memperbaiki bug atau koreksi data yang diterima | BE | Perbaikan dilaksanakan pemilik modul BE/FE/DG; koreksi data menjadi rilis baru dan tidak mengubah sejarah terbit. |
| 8.1.4 | Memverifikasi perbaikan serta memperbarui catatan rilis | QA | Uji regresi relevan lulus, deployment perbaikan terverifikasi, serta panduan/known issues diperbarui. |

### 8.2 — Evaluasi dan penutupan proyek

| Kode | Tugas level 3 | PIC | Keluaran / bukti selesai |
|---|---|---|---|
| 8.2.1 | Membandingkan realisasi dengan baseline proyek | PM | Usaha, durasi, biaya, scope, dan kualitas dibandingkan dengan baseline yang benar-benar disetujui. |
| 8.2.2 | Menyusun lessons learned dan backlog lanjutan | PM | Penyebab deviasi, keputusan yang membantu, serta P1/P2 lanjutan dicatat tanpa menjadikannya kewajiban rilis awal. |
| 8.2.3 | Mengarsipkan artefak dan menyelesaikan transisi akses | OP | Paket final, backup, versi, dan bukti penerimaan tersimpan; akses sementara dicabut setelah akses penerima terbukti berfungsi. |
| 8.2.4 | Menyelesaikan kewajiban dukungan dan menerima WF-G8 | PM | Masa dukungan berakhir, isu wajib terselesaikan atau dialihkan secara tertulis, dan penutupan proyek diterima. |

## Ketertelusuran kebutuhan ke paket kerja

Matriks ini memastikan ruang lingkup lama tercakup dalam variasi waterfall. Rujukan kode kelompok level 2 mencakup tugas-tugas level 3 di bawahnya. Semua fitur juga melewati integrasi 4.11, penerimaan 5.6, deployment 6, dan dokumentasi 7.

| Kebutuhan dari planning awal | Paket pembangunan utama | Paket verifikasi utama |
|---|---|---|
| FR-01 — Basis data fasilitas historis | 4.2, 4.3, 4.5 | 5.1, 5.3.1 |
| FR-02 — Geocoding dan review lokasi | 4.4 | 5.2.2 |
| FR-03 — Peta interaktif dan cluster | 4.8.2 | 5.4.1 |
| FR-04 — Choropleth kabupaten/kota | 4.6.2, 4.6.5, 4.8.4 | 5.2.2, 5.4.2 |
| FR-05 — Indikator kecamatan | 4.3.4, 4.6.1, 4.8.5 | 5.1.3, 5.2.1 |
| FR-06 — Buffer radius | 4.6.3–4.6.5, 4.8.4 | 5.2.3, 5.2.4 |
| FR-07 — Colab, GeoPandas, Folium, HTML | 4.6, 4.9 | 5.5.3, 5.5.4 |
| FR-08 — Laravel, Python, JavaScript | 4.1, 4.6–4.9 | 4.11, 5.3, 5.4, 5.5.3 |
| FR-09 — Supabase PostgreSQL/PostGIS | 4.5 | 5.3, 5.5.2 |
| FR-10 — Pencarian dan filter | 4.7.2, 4.8.3 | 5.4.1, 5.4.3 |
| FR-11 — Dashboard dan kualitas data | 4.4.5, 4.7.3, 4.8.1 | 5.2.1, 5.4.2 |
| FR-12 — Choropleth/detail kecamatan | 4.6.5, 4.8.4, 4.8.5 | 5.2.2, 5.4.2 |
| FR-13 — Sumber, metode, dan versi | 4.2.5, 4.7.1, 4.8.6, 4.9.4 | 5.1.4, 5.4.2, 5.5.4 |
| FR-14 — Ekspor CSV P1 | 4.10.3 jika dipilih | 5.4.4 |
| FR-15 — Admin dan pengelolaan rilis | 4.7.4–4.7.5 P0; 4.10.1–4.10.2 P1 | 5.3.2–5.3.4, 5.4.4 |
| FR-16 — Prioritas kecamatan P1 | 4.10.4 jika dipilih | 5.4.4 |
| FR-17 — Pengujian dan penerimaan | 3.6, 4.11, seluruh fase 5 | 5.6.4, 6.3, 7.3.3 |
| NFR-01 — Integritas dan jejak sumber | 4.2–4.5 | 5.1, 5.3.1 |
| NFR-02 — Responsivitas | 3.5.2, 4.8 | 5.4.3 |
| NFR-03 — Performa | 3.1.4, 3.2.2, 4.7.3, 4.8 | 5.5.1 |
| NFR-04 — Aksesibilitas | 3.5.3, 4.8.5–4.8.6 | 5.4.3 |
| NFR-05 — Keamanan | 3.2.3, 4.5.3, 4.7.4–4.7.5 | 5.3, 6.3.2 |
| NFR-06 — Reproduksibilitas | 4.1, 4.2.5, 4.6.5, 4.9 | 5.1.4, 5.5.3 |
| NFR-07 — Pemulihan | 3.2.4, 6.1.4, 6.2.4 | 5.5.2, 6.3.3 |
| NFR-08 — Kejelasan ilmiah | 2.3, 4.4.5, 4.8.6, 7.2.1 | 5.4.2, 5.6.2 |
| Revisi — Admin dan guest, tanpa pengelola data | 2.1.3, 3.2.3, 4.7.4 | 5.3.3–5.3.4 |
| Revisi — Pengumpulan data melalui scraping | 2.2.2, 3.3.1, 4.2 | 5.1.1, 5.1.4 |

## Kriteria penerimaan gerbang

| Gerbang | Bukti minimum sebelum berpindah fase |
|---|---|
| WF-G1 | Charter, daftar stakeholder, WBS, peran, estimasi/jadwal awal, kebutuhan sumber daya, dan mekanisme perubahan diterima. |
| WF-G2 | SRS dan matriks FR/NFR dibekukan; peran admin/guest, sumber/periode, metode, P1 terpilih, target uji, dan cakupan penuh/parsial diputuskan. |
| WF-G3 | Desain arsitektur, DB, pipeline scraping/ETL, API, UI, metode, fixture, serta prosedur uji konsisten dan diterima. |
| WF-G4 | Kandidat aplikasi/data/analisis terintegrasi; unit test serta smoke test lulus; kualitas data sesuai SRS; tidak ada penghalang uji sistem. |
| WF-G5 | Seluruh uji P0 serta P1 terpilih lulus; UAT dan restore memenuhi baseline; nol defect kritis/tinggi; versi kandidat diterima. |
| WF-G6 | Produksi berjalan dengan rilis yang diterima; smoke test, akses, monitoring, backup, dan kesiapan rollback terbukti. |
| WF-G7 | Dokumen as-built, laporan, notebook/HTML, kode, bukti uji, serta akses diterima; batas dan periode dukungan tertulis. |
| WF-G8 | Dukungan awal selesai; isu wajib ditutup/dialihkan secara tertulis; arsip dan transisi operasi lengkap; penutupan diterima. |

Pada setiap gerbang, PM menyusun paket bukti; reviewer teknis memeriksa substansi; pihak penerima yang ditetapkan pada 1.1.2 mencatat keputusan. Status gerbang hanya `pending`, `accepted`, atau `rework`. Persetujuan tidak boleh dicatat hanya karena tanggal jadwal sudah lewat.

## Cara menggunakan WBS untuk kendali pekerjaan

Setiap kode level 3 menjadi satu tiket/lembar kendali. Untuk paket berulang seperti review 565 koordinat, tambahkan checklist per fasilitas atau batch kabupaten, sambil mempertahankan satu owner dan keluaran penerimaan paket. Progress paket dihitung dari item yang telah direview, bukan sekadar jumlah yang pernah diproses. Porsi usaha setiap paket diestimasi kemudian; jumlah baris WBS tidak menjadi bobot progress keseluruhan.

Gunakan format berikut saat pekerjaan mulai ditugaskan:

```text
Kode WBS / nama tugas:
PIC bernama / reviewer:
Prioritas dan rilis sasaran:
Input / paket pendahulu:
Keluaran yang diserahkan:
Kriteria selesai: [salin dan pertegas dari kolom bukti selesai]
Estimasi usaha / tanggal mulai / target selesai:
Checklist objek jika tugas berulang:
Status: not_started | in_progress | blocked | in_review | done | deferred
Tautan artefak / bukti uji:
Catatan risiko, defect, atau change request:
Hasil review / tanggal penerimaan:
```

Aturan status:

- `done` hanya setelah keluaran lengkap, dependensi terpenuhi, pemeriksaan relevan lulus, dan reviewer menerima bukti.
- `blocked` mencatat penghalang, owner penyelesaian, dan tindak lanjut; tidak dihitung selesai.
- `deferred` hanya untuk pekerjaan yang resmi tidak masuk rilis, misalnya P1; perubahan P0 memerlukan revisi baseline.
- Audit dan bahan staging yang sudah tersedia menjadi input pekerjaan. Keberadaannya tidak membuat tugas implementasi atau pengujian aplikasi otomatis berstatus selesai.

Dokumen ini menyelesaikan dekomposisi WBS terlebih dahulu. Estimasi jam, tanggal mulai/selesai, anggaran, dan penugasan nama akan diisi melalui paket 1.2 setelah kapasitas dan target penyerahan ditetapkan. Jadwal delapan minggu pada planning awal tidak otomatis berlaku untuk urutan waterfall ini.
