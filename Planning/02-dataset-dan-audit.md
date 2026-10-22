# Dataset dan hasil audit

## Inventaris dan metode audit

Audit membaca 49 berkas: 1 DOCX, 39 PDF, 3 CSV, 5 XLSX dan 1 notebook. Pemeriksaan terstruktur dilakukan pada seluruh CSV dan seluruh workbook melalui nilai tersimpan OOXML. Jumlah baris dan total workbook gabungan juga diperiksa secara independen menggunakan openpyxl. Proposal dibaca melalui teks paragraf dan tabel. PDF Kemenkes dan contoh PDF BPS diperiksa melalui ekstraksi teks; belum dilakukan validasi visual seluruh halaman pada 39 PDF.

Audit ini **belum memverifikasi lokasi di lapangan, keakuratan setiap angka BPS, hasil OCR, kelengkapan polygon, atau keaslian tiap titik geocoding**. Hasil `0 verified_for_analysis` berarti tidak ada bukti review yang disertakan dalam bahan saat ini, bukan bukti semua koordinat salah. Bukti mesin ada di [hasil_audit.json](bahan/hasil_audit.json); inventaris dan SHA-256 di [inventaris_sumber.csv](bahan/inventaris_sumber.csv).

| Bahan lokal | Isi teramati | Penggunaan dan status |
|---|---|---|
| `puskesmas_jatim_alamat.csv` | 973 baris, 973 kode unik, 38 kab/kota, 665 pasangan nama kab/kecamatan | Master fasilitas mentah; siap masuk staging |
| `puskesmas_jatim_koordinat.csv` | 973 baris; himpunan kode sama dengan master | Kandidat lokasi; wajib review sebelum buffer |
| `jumlah_puskesmas_per_kecamatan.csv` | 704 baris: 665 detail dan 39 agregat | Rekonsiliasi jumlah, bukan tabel analisis yang langsung dijumlah |
| `Data_Gabungan_Kecamatan_Jawa_Timur.xlsx`, sheet `Gabungan` | 667 detail, 39 agregat; total fasilitas 973 | Bahan indikator; belum konsisten dengan master wilayah |
| `Data_Penduduk_Per_Kecamatan_Jawa_Timur_2024 .xlsx` | Catatan + tabel per kab/kota; catatan menyebut data 2023 | Penduduk per kecamatan; sumber asli dan tahun harus direview |
| `Data_Luas_Wilayah_Per_Kecamatan_Jawa_Timur_2024.xlsx` | Catatan + tabel per kab/kota; beberapa tahun sumber | Luas statistik; simpan tahun per observasi |
| Dua XLSX alamat/koordinat | Salinan bahan tabular untuk dibuka di Excel | Periksa kesetaraan dengan CSV saat menetapkan sumber utama |
| `Puskesmas_2024.pdf` | Kepmenkes HK.01.07/MENKES/1690/2024 | Sumber primer snapshot fasilitas Semester I 2024 |
| `per kecamatan/*.pdf` | 38 publikasi BPS kabupaten/kota | Rujukan per tabel dan halaman, meskipun nama folder menyebut kecamatan |
| `GIS.ipynb` | Unduh CSV dan dua pendekatan geocoding Nominatim | Belum memuat pipeline analisis, Supabase, pengujian atau ekspor peta lengkap |

## Temuan kuantitatif

| Pemeriksaan | Hasil | Tindakan |
|---|---|---|
| Jenis layanan | 616 Rawat Inap, 357 Non Rawat Inap | Jadikan baseline rekonsiliasi snapshot |
| Karakteristik | 658 Perdesaan, 294 Perkotaan, 16 Terpencil, 5 Sangat Terpencil | Batasi nilai kategori dan pertahankan ejaan sumber |
| Pasangan koordinat terisi | 565/973 atau 58,07% | Review kandidat; jangan disamakan dengan 58,07% lokasi akurat |
| Koordinat belum ada | 408/973 | Prioritas pencarian dari sumber resmi atau geocoder terpilih |
| Pasangan koordinat unik | 560 | 5 kelompok duplikat, 10 fasilitas perlu diperiksa |
| Jumlah CSV jika semua baris dijumlah | 2.919 | Buang 38 subtotal kab/kota dan 1 grand total dari fakta detail |
| Jumlah sesudah agregat dikeluarkan | 973 | Cocok persis dengan pengelompokan master menurut nama mentah |
| Workbook gabungan | 667 detail dengan 667 pasangan nama berbeda | Cocokkan ke master wilayah resmi dan kode lintas sumber |
| Penduduk/luas kosong | Bondowoso–Sempol | Jangan isi nol atau menebak penduduk |
| Jumlah fasilitas nol pada gabungan | Bondowoso–Ijen; Kota Surabaya–Pabean Cantian | Verifikasi mapping dan data sumber; jangan langsung menyimpulkan tidak terlayani |
| Antrean rekonsiliasi nama | 97 baris perbandingan | Banyak berupa dua sisi alias; bukan berarti 97 kecamatan salah |

Lima kelompok titik identik: KALIWATES–JEMBER KIDUL, URANGAGUNG–URANGAGUNG 2, NGAWI–PARON, PESANTREN I–PESANTREN II, SUKOREJO–KEPANJENKIDUL. Koordinat identik adalah tanda review, bukan dasar otomatis menghapus fasilitas. Kode fasilitas tetap menjadi identitas utama.

## Masalah tahun sumber

Workbook penduduk menyatakan tahun observasi 2023, meskipun nama file berakhiran 2024. Catatan juga menyebut CSV sensus dan OCR; karena asal indikator per baris belum terlacak ke URL/tabel asli, tahun dan definisinya harus diperiksa kembali. Lima wilayah OCR ialah Bojonegoro, Jember, Lamongan, Lumajang dan Kota Madiun. Penjumlahan yang sesuai total tidak membuktikan setiap angka kecamatan benar.

| Luas wilayah menurut catatan workbook | Tahun yang dinyatakan | Tindakan |
|---|---|---|
| Mayoritas wilayah | 2023, publikasi 2024 | Rekam tabel/halaman dan tahun observasi |
| Malang | 2019 | Cari edisi yang sesuai baseline; bila dipertahankan, tampilkan tahun 2019 |
| Tulungagung dan Kota Probolinggo | 2021 | Perlakuan sama; total historis tidak dipaksa sama dengan total 2023 |
| Bojonegoro, Jember, Lamongan | 2023 dari CSV lain | Lengkapi URL dan metadata; periksa konversi hektar Lamongan |
| Lumajang dan Kota Madiun | 2025 | Hindari memasukkan tanpa label ke analisis historis 2023/2024 |

Strategi utama adalah mencari sumber yang sejalan dengan 2023 untuk penduduk/luas dan 2024-S1 untuk fasilitas. Bila belum tersedia, mode eksplorasi boleh memakai sumber campuran dengan penanda yang jelas. Analisis historis yang mengklaim satu tahun harus ditahan sampai tahun diselaraskan. Tahun publikasi, tahun observasi, tanggal unduh dan periode fasilitas adalah kolom yang berbeda.

## Dataset tambahan yang wajib disiapkan

| ID | Dataset/bahan | Kolom atau format minimal | Sumber dan penerimaan |
|---|---|---|---|
| DS-01 | Master kode kabupaten/kecamatan | sistem_kode, kode, nama, parent, berlaku_mulai/akhir | MFD BPS edisi yang sesuai; 38 kab/kota, baseline 666 kecamatan untuk 2023 |
| DS-02 | Crosswalk kode BPS–Kemendagri–polygon | kode asal/tujuan, sistem/edisi, dasar, status review | Sumber resmi dan penilaian manual; tidak menebak kode dari nama/kode fasilitas |
| DS-03 | Polygon kabupaten dan kecamatan | GeoPackage/GeoJSON, kode sumber, nama, MultiPolygon, CRS, edisi | BIG/instansi resmi; lisensi, tahun dan kelengkapan pulau direview |
| DS-04 | Lokasi fasilitas terverifikasi | kode fasilitas, lon/lat, sumber, tanggal, metode, precision, reviewer | Registri/dinas/koordinat resmi atau verifikasi POI yang dapat dilacak |
| DS-05 | Bukti angka indikator | jumlah, unit, tahun observasi, tabel, halaman, URL | BPS; prioritaskan 5 wilayah OCR dan 8 wilayah luas alternatif |
| DS-06 | Katalog sumber dan hak penggunaan | penerbit, judul, periode, URL, file, hash, lisensi | Rekam untuk semua input dan artefak hasil |
| DS-07 | Fixture pengujian | titik/polygon kecil dan nilai rasio yang diketahui | Sintetis dan diberi label; tidak dicampur dengan data penelitian |

[MFD Jawa Timur 2023](https://jatim.bps.go.id/id/publication/2024/07/26/d64a7ab574bdbb877d3f5665/village-master-file-of-jawa-timur-province-2023.html) merupakan kandidat sumber kode dan nama. [Layanan batas kecamatan BIG](https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KECAMATAN_AR/MapServer) yang diperiksa menyebut edisi Juni 2026, sehingga tidak boleh dianggap otomatis cocok untuk snapshot 2023/2024. URL tersebut adalah titik pencarian bahan; polygon belum diunduh atau dilisensikan untuk proyek ini.

## Alur ETL yang direncanakan

1. **Bekukan input.** Simpan berkas asli, SHA-256, metadata dan versi. `Archives` tetap menjadi sumber baca. Pilih CSV sebagai master awal fasilitas, setelah dicocokkan dengan PDF dan salinan XLSX.
2. **Masukkan staging.** Semua nilai mentah dipertahankan, nomor baris sumber dicatat. Kolom identitas berupa teks. Normalisasi spasi/kapital dilakukan pada kolom pencocokan, bukan menimpa nama sumber.
3. **Pisahkan agregat.** Keluarkan baris TOTAL dari fakta; simpan untuk rekonsiliasi. Jangan menjumlah subtotal dan detail bersama.
4. **Bangun master wilayah.** Gunakan kode resmi dan parent kabupaten. Review semua alias dalam konteks kabupaten/edisi; nama sama di dua kabupaten tidak boleh digabung.
5. **Selesaikan kasus Sempol–Ijen.** Periksa kode/nama historis dan alamat fasilitas. Jika terbukti alias unit yang sama, petakan fasilitas ke satu kecamatan resmi, tanpa menjumlah penduduk dua kali. Bukti harus tersimpan; audit ini belum menerapkan penggabungan.
6. **Normalisasi indikator.** Parse angka sesuai sumber, periksa jiwa versus ribu jiwa, km² versus hektar, dan nol versus kosong. Catat tahun per nilai. Rekonsiliasi total dengan toleransi pembulatan yang diturunkan dari presisi sumber; selisih harus dijelaskan.
7. **Review lokasi.** Verifikasi 565 kandidat dan cari 408 yang kosong. Simpan raw response, query, provider, tanggal, tipe objek, ketelitian, alasan keputusan dan reviewer. Semua 565 tetap perlu review, bukan hanya 10 duplikat.
8. **Validasi spasial.** CRS, geometri valid, pulau lengkap, titik di wilayah yang diharapkan, konflik kode dan kandidat centroid. Titik di perbatasan memakai pemeriksaan yang memasukkan boundary dan review jarak toleransi, bukan pemindahan otomatis.
9. **Bangun analisis.** Hitung jumlah fasilitas dari snapshot master; buffer hanya dari verified facility points. Simpan parameter, versi input dan hasil.
10. **Promosikan rilis.** Validasi FK, jumlah, tahun, sumber, artefak dan laporan uji. Publikasi satu release_id secara atomik; cache ikut berubah. Rilis terbit tidak diedit di tempat.

## Kebijakan geocoding

Notebook awal mencari nama fasilitas/kecamatan tanpa alamat lengkap. Versi berikutnya memakai fallback desa, kecamatan dan kabupaten. Fallback tersebut hanya perkiraan posisi wilayah dan tidak boleh dipakai sebagai lokasi bangunan atau titik buffer fasilitas.

Gunakan `precision_level = facility | street | village | district | regency | unknown`; `review_status = missing | unverified | verified | rejected`. Hanya `verified` dengan `precision_level=facility` dan bukti review boleh masuk analisis radius. Kandidat lain dapat ditampilkan sebagai lapisan perkiraan dengan simbol berbeda, dimatikan secara default.

Pemilihan provider geocoding menjadi keputusan eksplisit pada fase data. Prioritaskan koordinat resmi; opsi batch adalah provider yang mengizinkan pekerjaan ini atau Nominatim yang dikelola sendiri. **Nominatim publik tidak menjadi layanan geocoding otomatis bawaan aplikasi.** Jika tim secara sadar memilihnya untuk batch kecil sekali jalan, ikuti [kebijakan resmi Nominatim](https://operations.osmfoundation.org/policies/nominatim/): maksimum 1 permintaan/detik untuk seluruh aplikasi, satu thread/satu mesin, identitas User-Agent, atribusi, cache dan tidak mengulang query. Bulk besar tidak dianjurkan; pekerjaan rutin atau lebih dari satu hari dibatasi 4 permintaan/menit. Tidak ada autocomplete dan tidak ada jaminan ketersediaan. Notebook lama perlu diubah sebelum dijalankan ulang.

## Definisi dataset siap analisis

- 973 fasilitas historis dipertahankan dan seluruhnya terpetakan ke kode wilayah yang disepakati; jumlah kategori cocok baseline atau selisih punya bukti koreksi.
- Master wilayah dan polygon cocok satu-ke-satu sesuai edisi. Target baseline 666 bukan alasan menghapus baris hanya agar jumlahnya sesuai.
- Setiap penduduk/luas punya tahun, unit dan sumber; nilai kosong tidak menjadi nol.
- Setiap koordinat yang digunakan dalam buffer memiliki bukti verifikasi lokasi fasilitas.
- Analisis penuh seluruh fasilitas membutuhkan 973 lokasi terverifikasi. Bila belum tercapai, hanya rilis analisis parsial dengan cakupan numerik dan batas kesimpulan yang jelas; tidak boleh mengklaim coverage provinsi yang lengkap.
- Semua masalah kritis identitas, tahun, jumlah dan geometri selesai atau indikator terkait dinonaktifkan. Masalah yang tersisa ditampilkan dalam metadata kualitas rilis.
