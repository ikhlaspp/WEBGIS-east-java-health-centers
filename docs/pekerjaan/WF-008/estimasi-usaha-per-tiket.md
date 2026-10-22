# Estimasi usaha per tiket

Versi 1 — 23 Oktober 2026. Estimasi engineering awal, belum disepakati tim dan bukan realisasi. Satuan jam orang. Waktu mesin/AI tidak otomatis sama dengan jam orang. Angka bergantung pada langkah, kompleksitas integrasi dan volume data; kalibrasi ulang setelah pilot kurasi dan implementasi pertama.

Pelaksanaan berbeda per tiket. Review = 25% pelaksanaan (minimum 0,5 jam), perbaikan normal = 15%; cadangan risiko = 20% dari ketiganya dan ditampilkan terpisah. Angka persentase adalah asumsi perencanaan, bukan hasil pengukuran. Cadangan menutup ketidakpastian sumber/OCR/crosswalk/integrasi (R01–R14 pada WF-009), bukan izin mengurangi kualitas. Incident support adalah alokasi awal; lama masa dukungan belum disepakati.

WF-068: 565 kandidat × 5 menit = 47,08 jam pelaksanaan; sensitivitas 3–8 menit = 28,25–75,33 jam. WF-069: 408 lokasi × 12 menit = 81,60 jam; sensitivitas 8–20 menit = 54,40–136 jam. Kedua asumsi harus diuji pada batch maksimum 25 objek. WF-070 menyediakan 16 jam untuk anomali tersisa, tidak menggandakan review rutin; jika kasus melampaui alokasi, estimasi diperbarui. Kecepatan geocoder tidak membuktikan lokasi benar.

Waktu tunggu sumber, konfirmasi, provisioning, review dan dukungan dicatat terpisah pada jadwal. Biaya layanan ada di WF-007 dan tidak dijumlahkan dengan jam orang. Semua P0 termasuk backend validasi file dan command lifecycle; empat tiket P1 ditampilkan terpisah.

| Tiket | P | Pekerjaan | Pelaksanaan | Review | Perbaikan | Dasar | Cadangan |
|---|---|---|---:|---:|---:|---:|---:|
| WF-001 | P0 | Menelaah proposal, planning awal, dan revisi pengguna | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-002 | P0 | Mengidentifikasi stakeholder dan penerima hasil | 2.00 | 0.50 | 0.30 | 2.80 | 0.56 |
| WF-003 | P0 | Menentukan sasaran dan ukuran keberhasilan proyek | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-004 | P0 | Menyusun dan meninjau project charter | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-005 | P0 | Memeriksa kelengkapan WBS bersama tim | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-006 | P0 | Menetapkan penanggung jawab dan reviewer paket kerja | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-007 | P0 | Menyusun kebutuhan biaya, alat, akun, dan lingkungan | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-008 | P0 | Menaksir usaha, dependensi, dan durasi dari paket kerja | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-009 | P0 | Membuat daftar risiko dan rencana penanganannya | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-010 | P0 | Menetapkan tata cara perubahan scope dan keputusan | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-011 | P0 | Menetapkan standar bukti selesai dan penyimpanan artefak | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-012 | P0 | Menetapkan pelaporan rutin dan menerima WF-G1 | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-013 | P0 | Menggali skenario penggunaan admin dan guest | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-014 | P0 | Menetapkan kebutuhan fungsional dan prioritas rilis | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-015 | P0 | Menetapkan batas akses aplikasi | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-016 | P0 | Menentukan isi setiap halaman dan alur navigasi | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-017 | P0 | Menginventarisasi arsip dan kesenjangan dataset | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-018 | P0 | Memeriksa kelayakan sumber untuk scraping/pengunduhan | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-019 | P0 | Menetapkan periode, satuan, dan identitas sumber | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-020 | P0 | Menentukan aturan kelengkapan dan penanganan data bermasalah | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-021 | P0 | Menentukan indikator tabular dan cara agregasinya | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-022 | P0 | Menentukan kebutuhan peta tematik dan legenda | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-023 | P0 | Menentukan kebutuhan analisis radius | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-024 | P0 | Menetapkan keluaran penelitian dan batas kesimpulan | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-025 | P0 | Menetapkan target performa dan kegunaan | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-026 | P0 | Menetapkan target keamanan, backup, dan reproduksibilitas | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-027 | P0 | Menyusun strategi UAT serta matriks kebutuhan–uji | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-028 | P0 | Menyelesaikan SRS dan menerima WF-G2 | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-029 | P0 | Merancang hubungan Laravel, Leaflet, Supabase, dan Colab | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-030 | P0 | Merancang lingkungan development, test/staging, dan produksi | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-031 | P0 | Merancang struktur kode dan alur integrasi | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-032 | P0 | Merancang proses batch dan penanganan kegagalan | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-033 | P0 | Membuat ERD dan kamus data final | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-034 | P0 | Merancang constraint, indeks, dan migrasi | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-035 | P0 | Merancang otorisasi admin dan akun teknis database | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-036 | P0 | Merancang versi rilis, publikasi, dan pemulihan | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-037 | P0 | Merancang adapter pengambilan tiap sumber | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-038 | P0 | Merancang normalisasi dan crosswalk wilayah | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-039 | P0 | Merancang pencarian dan review koordinat | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-040 | P0 | Merancang staging dan laporan kualitas | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-041 | P0 | Menulis spesifikasi rumus dan contoh hasil acuan | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-042 | P0 | Merancang operasi spasial dan toleransi | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-043 | P0 | Merancang GeoJSON dan kelas choropleth | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-044 | P0 | Merancang notebook dan manifest hasil | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-045 | P0 | Menentukan kontrak endpoint dan respons | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-046 | P0 | Membuat wireframe halaman publik | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-047 | P0 | Merancang interaksi dan keadaan antarmuka | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-048 | P0 | Merancang login admin dan fitur P1 terpilih | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-049 | P0 | Menyiapkan spesifikasi fixture dan expected result | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-050 | P0 | Menyusun prosedur uji integrasi dan nonfungsional | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-051 | P0 | Menyusun prosedur UAT dan kriteria gerbang rilis | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-052 | P0 | Meninjau konsistensi desain dan menerima WF-G3 | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-053 | P0 | Membuat repositori dan struktur proyek | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-054 | P0 | Menyiapkan Laravel dan build frontend | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-055 | P0 | Menyiapkan Python, Colab, dan alat pengujian | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-056 | P0 | Menyiapkan pipeline pemeriksaan otomatis | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-057 | P0 | Mengimplementasikan pengunduh dan parser data fasilitas | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-058 | P0 | Mengimplementasikan pengambilan data penduduk dan luas | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-059 | P0 | Mengimplementasikan pengambilan kode dan polygon wilayah | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-060 | P0 | Menambahkan cache, retry, dan pemeriksaan kelengkapan scraping | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-061 | P0 | Menjalankan pengambilan sumber dan membekukan input mentah | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-062 | P0 | Mengekstrak dan menormalisasi tabel sumber | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-063 | P0 | Menyelesaikan crosswalk kode serta alias wilayah | 20.00 | 5.00 | 3.00 | 28.00 | 5.60 |
| WF-064 | P0 | Memisahkan subtotal dan merekonsiliasi master fasilitas | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-065 | P0 | Memverifikasi angka penduduk, luas, tahun, dan unit | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-066 | P0 | Memvalidasi polygon dan kelengkapan master wilayah | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-067 | P0 | Menyiapkan antrean geocoding dan pencatatan bukti | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-068 | P0 | Mereview 565 pasangan koordinat yang sudah tersedia | 47.08 | 11.77 | 7.06 | 65.91 | 13.18 |
| WF-069 | P0 | Menelusuri 408 fasilitas tanpa koordinat | 81.60 | 20.40 | 12.24 | 114.24 | 22.85 |
| WF-070 | P0 | Menyelesaikan anomali koordinat dan konflik wilayah | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-071 | P0 | Membekukan laporan kelayakan data spasial | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-072 | P0 | Menyiapkan database development dan test dengan PostGIS | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-073 | P0 | Membuat migration tabel, constraint, dan indeks | 14.00 | 3.50 | 2.10 | 19.60 | 3.92 |
| WF-074 | P0 | Mengimplementasikan grants dan pembatasan akses data | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-075 | P0 | Membuat impor staging dan promosi data tervalidasi | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-076 | P0 | Memuat kandidat dataset hasil kurasi | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-077 | P0 | Membuat perhitungan indikator kecamatan | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-078 | P0 | Membuat agregasi kabupaten dan provinsi | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-079 | P0 | Membuat buffer radius titik yang terverifikasi | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-080 | P0 | Membuat union, clip, dan luas cakupan wilayah | 14.00 | 3.50 | 2.10 | 19.60 | 3.92 |
| WF-081 | P0 | Menyimpan hasil run dan layer tematik | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-082 | P0 | Membuat API rilis, wilayah, dan katalog sumber | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-083 | P0 | Membuat API fasilitas, pencarian, filter, dan detail | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-084 | P0 | Membuat API statistik, GeoJSON, dan buffer | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-085 | P0 | Membuat login/logout admin dan otorisasi operasi internal | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-086 | P0 | Membuat command review, analisis, publish, rollback, dan audit | 24.00 | 6.00 | 3.60 | 33.60 | 6.72 |
| WF-087 | P0 | Membuat layout, navigasi, dan dashboard | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-088 | P0 | Membuat peta dasar, marker, cluster, dan popup | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-089 | P0 | Membuat pencarian dan filter bertingkat | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-090 | P0 | Membuat layer choropleth, buffer, dan legenda | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-091 | P0 | Membuat tabel dan halaman detail fasilitas/kecamatan | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-092 | P0 | Membuat halaman metodologi dan penanganan state UI | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-093 | P0 | Menghubungkan notebook ke snapshot rilis yang aman | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-094 | P0 | Mengintegrasikan modul analisis ke notebook | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-095 | P0 | Membuat visualisasi Folium dan ekspor HTML/tabel | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-096 | P0 | Menambahkan manifest dan panduan Run all | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-097 | P1 | Membuat dashboard admin untuk menjalankan dan memantau batch | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-098 | P1 | Membuat layar review data dan publikasi rilis | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-099 | P1 | Membuat ekspor CSV hasil filter | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-100 | P1 | Membuat daftar prioritas kecamatan | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-101 | P0 | Menghubungkan pipeline, database, API, UI, dan artefak | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-102 | P0 | Melengkapi unit/component test modul yang berubah | 20.00 | 5.00 | 3.00 | 28.00 | 5.60 |
| WF-103 | P0 | Menjalankan smoke test dan memperbaiki kegagalan integrasi | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-104 | P0 | Membekukan kandidat uji dan menerima WF-G4 | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-105 | P0 | Menguji kegagalan sumber dan perubahan struktur scraping | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-106 | P0 | Menguji integritas identitas, jumlah, dan kategori | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-107 | P0 | Menguji mapping, tahun, unit, dan nilai berisiko | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-108 | P0 | Menguji pengulangan ETL dan konsistensi provenance | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-109 | P0 | Menguji formula, pembulatan, null, nol, dan agregasi | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-110 | P0 | Menguji kelayakan koordinat dan join peta | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-111 | P0 | Menguji radius, overlap, clip, geometri, dan pulau | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-112 | P0 | Membandingkan hasil spasial lintas implementasi | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-113 | P0 | Menguji migration, constraint, dan impor | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-114 | P0 | Menguji konsistensi rilis, rollback, dan kegagalan layanan | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-115 | P0 | Menguji session, otorisasi, injeksi, dan keamanan popup | 10.00 | 2.50 | 1.50 | 14.00 | 2.80 |
| WF-116 | P0 | Menguji paparan rahasia dan izin database aktual | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-117 | P0 | Menguji navigasi, peta, pencarian, dan filter | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-118 | P0 | Menguji choropleth, statistik, detail, dan metode | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-119 | P0 | Menguji responsivitas, aksesibilitas, dan request bersaing | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-120 | P0 | Menguji fitur P1 terpilih dan validasi file backend P0 | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-121 | P0 | Mengukur waktu muat, respons API, dan beban staging | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-122 | P0 | Menguji backup dan restore database serta artefak | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-123 | P0 | Menjalankan Colab dari runtime bersih dan mengulang run | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-124 | P0 | Membandingkan HTML Folium dengan aplikasi | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-125 | P0 | Menyiapkan peserta, kandidat rilis, dan instrumen UAT | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-126 | P0 | Melaksanakan UAT dan merangkum temuan | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-127 | P0 | Memperbaiki defect dan menjalankan retest/regresi | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-128 | P0 | Menyelesaikan laporan uji dan menerima WF-G5 | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-129 | P0 | Menyiapkan hosting, domain bila diperlukan, dan HTTPS | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-130 | P0 | Menyiapkan Supabase produksi dan penyimpanan artefak | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-131 | P0 | Menyiapkan runbook deployment dan titik pemulihan | 5.00 | 1.25 | 0.75 | 7.00 | 1.40 |
| WF-132 | P0 | Memasang versi aplikasi yang telah diterima | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-133 | P0 | Menjalankan migration dan memuat dataset final | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-134 | P0 | Memasang konfigurasi rahasia dan akun admin awal | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-135 | P0 | Memasang hasil analisis dan menerbitkan rilis aktif | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-136 | P0 | Mengaktifkan worker, monitoring, dan backup | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-137 | P0 | Menjalankan smoke test produksi | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-138 | P0 | Memeriksa akses publik dan konfigurasi operasi | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-139 | P0 | Menangani kegagalan penerapan atau memvalidasi kesiapan rollback | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-140 | P0 | Mencatat hasil deployment dan menerima WF-G6 | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-141 | P0 | Memfinalisasi panduan guest dan admin | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-142 | P0 | Memfinalisasi panduan instalasi dan operasi | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-143 | P0 | Memfinalisasi dokumentasi desain as-built | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-144 | P0 | Memfinalisasi panduan data dan reproduksi analisis | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-145 | P0 | Menulis hasil analisis beserta keterbatasannya | 16.00 | 4.00 | 2.40 | 22.40 | 4.48 |
| WF-146 | P0 | Menyusun bagian implementasi dan pengujian laporan | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-147 | P0 | Menyiapkan materi presentasi dan skenario demonstrasi | 8.00 | 2.00 | 1.20 | 11.20 | 2.24 |
| WF-148 | P0 | Mengemas kode, data yang boleh dibagikan, dan bukti proyek | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-149 | P0 | Melaksanakan demonstrasi dan orientasi penggunaan | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-150 | P0 | Menyerahkan akses dan kepemilikan operasional | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-151 | P0 | Memeriksa kelengkapan paket dan isu yang diterima | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-152 | P0 | Menyepakati dukungan awal dan menerima WF-G7 | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |
| WF-153 | P0 | Memantau kesehatan layanan dan backup selama dukungan | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-154 | P0 | Menerima dan mengklasifikasikan insiden | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-155 | P0 | Memperbaiki bug atau koreksi data yang diterima | 12.00 | 3.00 | 1.80 | 16.80 | 3.36 |
| WF-156 | P0 | Memverifikasi perbaikan serta memperbarui catatan rilis | 6.00 | 1.50 | 0.90 | 8.40 | 1.68 |
| WF-157 | P0 | Membandingkan realisasi dengan baseline proyek | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-158 | P0 | Menyusun lessons learned dan backlog lanjutan | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-159 | P0 | Mengarsipkan artefak dan menyelesaikan transisi akses | 4.00 | 1.00 | 0.60 | 5.60 | 1.12 |
| WF-160 | P0 | Menyelesaikan kewajiban dukungan dan menerima WF-G8 | 3.00 | 0.75 | 0.45 | 4.20 | 0.84 |

## Rekonsiliasi

| Scope | Pelaksanaan | Review | Perbaikan | Dasar | Cadangan | Total |
|---|---:|---:|---:|---:|---:|---:|
| P0 | 1236.68 | 309.17 | 185.50 | 1731.35 | 346.27 | 2077.62 |
| P0+P1 | 1280.68 | 320.17 | 192.10 | 1792.95 | 358.59 | 2151.54 |

P0 berisi 156 tiket. Empat P1 hanya boleh deferred melalui keputusan scope; tambahkan administrasi keputusan 0,25 jam per tiket (1 jam) pada skenario P0, di luar total tabel. Data terstruktur: `estimasi.json`; rumus pembentukan: `../susun-bukti-inisiasi.py`.
