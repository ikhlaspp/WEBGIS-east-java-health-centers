# Rencana pengembangan WebGIS Puskesmas Jawa Timur

Disusun 22 Oktober 2026 berdasarkan `Archives/Proposal.docx` dan audit berkas di `Archives`. Dokumen ini menjadi panduan implementasi untuk tim proyek, termasuk persiapan data, Supabase, analisis spasial, pengujian, dan penyerahan hasil. Status seluruh pekerjaan aplikasi masih **direncanakan**. Audit lokal dan ekspor bahan staging telah dilakukan; belum ada aplikasi, database Supabase, atau deployment yang dibuat.

Rekomendasi utama: gunakan **Laravel dan Leaflet untuk aplikasi, Python/GeoPandas/Folium di Google Colab untuk pengolahan dan ekspor HTML, serta Supabase PostgreSQL dengan PostGIS untuk database**. Supabase menggantikan MySQL yang disebut dalam proposal, mengikuti permintaan pengguna. Analisis menggunakan snapshot historis puskesmas Semester I 2024; tahun penduduk, luas, dan batas wilayah disimpan terpisah.

## Urutan membaca

| Dokumen | Isi dan kegunaan |
|---|---|
| [01 Kebutuhan dan ruang lingkup](01-kebutuhan-dan-ruang-lingkup.md) | Pemetaan kebutuhan proposal, fitur, peran, layar, kriteria penerimaan |
| [02 Dataset dan hasil audit](02-dataset-dan-audit.md) | Kondisi data aktual, kekurangan, kebutuhan sumber, ETL dan validasi |
| [03 Arsitektur dan analisis](03-arsitektur-dan-analisis.md) | Stack, alur sistem, kontrak API, rumus, metode spasial |
| [04 Supabase dan kamus data](04-supabase-dan-kamus-data.md) | Model relasional, kolom, akses, impor, keamanan, operasi |
| [05 Rencana pengujian](05-rencana-pengujian.md) | Kasus uji, fixture, UAT, performa, keamanan, gerbang rilis |
| [06 Tahapan dan kebutuhan pendukung](06-tahapan-dan-kebutuhan.md) | Backlog, estimasi, pembagian kerja, risiko, bahan yang perlu dicari |
| [07 Sumber dan keputusan](07-sumber-dan-keputusan.md) | Rujukan resmi dan catatan asumsi yang perlu ditetapkan |
| [Bahan pendukung](bahan/README.md) | Dataset staging, antrean review, audit yang bisa diulang, SQL staging |
| [Variasi waterfall — WBS tiga level](Waterfall/01-WBS-waterfall.md) | Alternatif urutan waterfall dengan tugas rinci, PIC, bukti selesai, dan gerbang penerimaan; mengikuti revisi admin/guest serta scraping |
| [Tiket waterfall — urutan 160 tugas](Waterfall/Tiket/README.md) | Satu tiket per tugas WBS, langkah kerja terperinci, input/dependensi, keluaran, kriteria penerimaan, dan tautan tiket berikutnya |

## Temuan yang memengaruhi pekerjaan

1. Master berisi **973 kode puskesmas unik di 38 kabupaten/kota**, sesuai jumlah dalam proposal.
2. **565 puskesmas memiliki pasangan koordinat dan 408 belum memiliki koordinat**. Status `Ditemukan` belum membuktikan titik berada tepat pada fasilitas. Ada 5 pasangan koordinat identik yang dipakai oleh 10 fasilitas.
3. Workbook gabungan berisi **667 baris kecamatan**, termasuk Sempol dengan penduduk dan luas kosong. Daftar wilayah harus dicocokkan dengan master resmi; Sempol–Ijen menjadi kasus prioritas.
4. CSV jumlah puskesmas berisi **39 baris agregat**. Menjumlah seluruh baris menghasilkan 2.919, sedangkan jumlah 665 baris detail adalah 973.
5. Nama berkas penduduk/luas menyebut 2024, tetapi catatan workbook menyatakan penduduk 2023 dan luas dari beberapa tahun, termasuk 2019, 2021, 2023, dan 2025. Label tahun harus diperbaiki pada metadata aplikasi.
6. Polygon administrasi dan kode kecamatan resmi belum tersedia dalam arsip. Choropleth dan pemeriksaan titik dalam wilayah bergantung pada bahan ini.

Rincian serta batas audit ada di [laporan dataset](02-dataset-dan-audit.md). Dataset hasil ekspor adalah **bahan staging**, belum layak dianggap dataset analisis tervalidasi.

## Sasaran hasil akhir

- WebGIS berbahasa Indonesia dengan peta, pencarian, filter, statistik, detail kecamatan/fasilitas, dan sumber data.
- Database historis yang menjaga 973 fasilitas, termasuk fasilitas tanpa koordinat.
- Notebook Colab yang dapat dijalankan ulang serta ekspor HTML Folium yang konsisten dengan versi data aplikasi.
- Choropleth kabupaten/kota dan kecamatan; analisis radius menggunakan titik fasilitas yang telah diverifikasi.
- Laporan pengujian, bukti UAT, dokumentasi metode, petunjuk instalasi, dan pemulihan data.

Estimasi awal **8 minggu untuk 3 anggota tim**, dengan alokasi 12–15 jam per orang per minggu. Pembersihan sumber dan pemeriksaan lokasi merupakan penentu jadwal. Angka ini adalah estimasi perencanaan, bukan tenggat dari proposal.
