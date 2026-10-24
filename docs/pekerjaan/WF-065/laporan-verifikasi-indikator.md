# Verifikasi penduduk dan luas statistik

25 Oktober 2026. Pelaksana/reviewer teknis: Codex, melalui pemeriksaan sumber, perbandingan terprogram, dan pengujian. Ini bukan persetujuan manusia independen atau penerimaan rilis publik.

Sebanyak **1.332 observasi utama** (666 penduduk + 666 luas, 38 kabupaten/kota) ditelusuri ke **76 tabel sumber terpilih**. Semua mempunyai identitas wilayah hasil WF-063, hash sumber, locator halaman/tabel/baris, tahun observasi, unit, dan keputusan konversi. Seluruh 110 nilai penduduk dari lima PDF hasil pindai diperiksa secara visual; tabel luas alternatif dan halaman pendukung unit juga diperiksa. Tabel dengan lapisan teks dibandingkan per baris dengan sumber, bukan disetujui hanya karena totalnya cocok.

Implementasi: `scripts/etl/validate_indicators.py`, dengan modul bersama `python/gis_pipeline/etl/validate_indicators.py`. Input WF-062/WF-063 diverifikasi hash, jumlah, dan batch; dokumen sumber, gambar pemeriksaan, serta bukti teks diverifikasi hash. Crosswalk yang ambigu, stale, duplikat, atau berbeda induk ditolak. Arsip asli tidak diubah: hash seluruh **49 file Archives** tetap sama dengan manifest WF-061.

## Keputusan yang mengubah data

**47 nilai** berbeda secara numerik dari workbook. Seluruh nilai lama tetap disimpan sebagai kandidat asal; keluaran baru tidak menimpa workbook.

| Kelompok | Jumlah | Keputusan |
|---|---:|---|
| Luas Lumajang | 2 | Candipuro 143,09 km2 dan Pasirian 128,39 km2 sesuai tabel asli; pasangan workbook tertukar. |
| Luas Lamongan | 2 | Pilih tabel 2022 yang menyatakan km2 secara eksplisit: Karangbinangun 52,28 dan Solokuro 101,02. Ini pemilihan sumber/periode, bukan klaim erratum penerbit untuk 2023. |
| Penduduk Sidoarjo | 11 | Perbaiki pasangan nama/nilai sejak Tulangan; misalnya Tulangan 101.177 dan Sidoarjo 197.756. Total daerah yang sama sebelumnya menyembunyikan kesalahan penempatan baris. |
| Penduduk Mojokerto | 18 | Gunakan kolom 2023 pada tabel 3.1.1, halaman fisik 114. Angka workbook cocok dengan tabel sensus 2020, halaman 118, tetapi dilabeli 2023. |
| Penduduk Trenggalek | 14 | Gunakan nilai 2023 per kecamatan pada tabel 3.1.3, halaman fisik 109; jangan membawa nilai/urutan kolom lama ke label 2023. |

Blitar dapat diverifikasi dari tabel **3.1.5 hasil registrasi**, halaman fisik 109. Tabel 3.1.3 hasil proyeksi pada halaman 105 memang tidak menyediakan rincian kecamatan; kekosongan tabel tersebut tidak membuktikan seluruh publikasi tidak mempunyai data. Kediri menggunakan tabel registrasi 3.1.10, halaman 218, kolom 2023. Kota Kediri menggunakan tabel 3.1.4, halaman 104, kolom total 2023 sehingga presisi jiwa tetap dipertahankan.

**110 label tahun luas** dikoreksi berdasarkan judul tabel yang benar-benar dipilih. Distribusi akhir:

| Tahun luas | Kecamatan | Wilayah di luar kelompok 2023 |
|---|---:|---|
| 2019 | 33 | Malang |
| 2020 | 5 | Kota Probolinggo |
| 2021 | 19 | Tulungagung |
| 2022 | 31 | Lamongan dan Kota Pasuruan |
| 2023 | 507 | Wilayah lainnya, termasuk Kota Madiun |
| 2024 | 71 | Lumajang, Kediri, dan Probolinggo |

Penduduk seluruh 666 kecamatan berobservasi 2023, tetapi definisi sumber tetap beragam (registrasi/proyeksi). Tahun yang sama bukan bukti bahwa semua nilai berasal dari satu sensus atau definisi identik. Mode historis selaras dan penerimaan kualitas rilis belum diberikan. Kebijakan periode campuran WF-019 tetap berlaku.

## Unit dan sumber alternatif

Header `ribu` pada beberapa tabel bertentangan dengan angka jiwa penuh. Keputusan tidak dibuat berdasarkan besarnya angka saja. Tabel umur/jenis kelamin atau narasi resmi yang menyatakan jiwa menjadi pembanding, dengan halaman/hash tersimpan. Contoh Jember: 1.298.852 laki-laki + 1.301.811 perempuan = 2.600.663 jiwa; Kota Madiun: 99.319 + 103.225 = 202.544 jiwa. Sidoarjo menggunakan pemisah ribuan koma dan total 1.996.825 jiwa yang juga muncul pada tabel umur/jenis kelamin. Interpretasi teknis ini dicatat terbuka, bukan diklaim sebagai erratum resmi.

Untuk tabel yang benar-benar memakai ribu jiwa, faktor 1.000 diterapkan sekali dengan locale yang eksplisit. Konversi hektar ke km2 memakai faktor 0,01 dan diuji, tetapi tabel Lamongan 2023 yang unitnya bertentangan tidak diam-diam dikonversi ulang dari workbook. Dipilih tabel alternatif 2022 dengan header km2 yang jelas. Luas statistik tidak diganti dengan luas geometri.

Lima unduhan pendukung dibekukan dalam `supplemental-receipts.json`: profil resmi Malang (tabel 2019), publikasi BPS Kota Probolinggo 2021 (tabel observasi 2020), Statistik Daerah Tulungagung 2022 (lampiran observasi 2021), laporan PPH pemerintah Lamongan 2023 (tabel observasi 2022), dan Statistik Daerah Tulungagung 2024 (bukti unit penduduk 2023). File mentah tetap privat di `data/raw`; URL dan hash tersedia dalam receipt. Metadata publikasi tidak disamakan dengan tahun observasi.

## Rekonsiliasi dan batas penerimaan

Hasil 76 total sumber: **55 tepat**, **19 berada dalam rentang kemungkinan pembulatan sesuai presisi sumber**, dan **2 selisih belum terjelaskan**. Rentang pembulatan bukan bukti penyebab selisih; semua selisih tetap dicatat. Tidak ada nilai yang dinaikkan/diturunkan agar jumlah cocok.

| Sumber dengan selisih di luar rentang | Jumlah rincian km2 | Total tercetak km2 | Selisih |
|---|---:|---:|---:|
| Lamongan, tabel alternatif 2022 | 1.812,20 | 1.812,80 | -0,60 |
| Kota Surabaya, tabel 2023 | 335,54 | 335,93 | -0,39 |

Kedua tabel diperiksa kembali; angka per kecamatan dan total tercetak dipertahankan. Isu diteruskan ke pemeriksaan kualitas sebelum publikasi, bukan disamarkan sebagai lulus. Bangkalan penduduk, misalnya, mempunyai jumlah rincian 1.047.320 versus total tercetak 1.047.310; selisih 10 jiwa berada dalam presisi tabel ribu jiwa dua desimal.

Ijen/Sempol pada workbook gabungan historis tetap **ditahan sebagai dua baris alias duplikat**. Penduduk dan luas Sempol yang kosong tetap null; tidak diisi nol, tidak dijumlahkan dengan Ijen, dan tidak dipakai menambal observasi utama. Nilai utama Ijen berasal dari tabel asli yang terpisah dan crosswalk yang sudah diperiksa.

`all_sources_reviewed=true` dan `risk_review_complete=true` berarti pekerjaan pemeriksaan sumber ini selesai. **`data_quality_accepted=false` dan `publication_allowed=false`** tetap berlaku. Gerbang kualitas/publikasi berikutnya harus memproses perbedaan total, periode campuran, dan definisi sumber tersebut.

## Bukti dan pengujian

- `reviewed-source-tables.json`: keputusan per baris, sumber, metadata, locator, hash gambar/teks, dan checklist risiko.
- `keputusan-nilai-indikator.json`: 47 koreksi nilai, perubahan periode, rekonsiliasi total, serta penahanan alias historis.
- `output-verification.json`: hash artefak privat `data/processed/indicator-decisions.json`, ringkasan periode, dan pemeriksaan keutuhan arsip.
- `tests/python/test_validate_indicators.py`: **22 lulus**, termasuk baris tertukar dengan total tetap sama, konversi unit, null, area nol/negatif, crosswalk ambigu, bukti berubah, dan Sempol.
- Suite Python lengkap: **164 lulus**; compileall berhasil. Semua pemeriksaan tersebut exit 0. Perintah produksi dengan sumber aktual juga exit 0.

Perintah reproduksi dari root tercantum di `handoff.md`. Artefak mentah, staging, gambar, dan keluaran data tidak dimasukkan Git. Bukti ini tidak menggantikan pengujian spasial WF-066 atau gerbang rilis.
