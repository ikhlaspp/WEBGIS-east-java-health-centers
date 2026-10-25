# Bahan pendukung perencanaan

Semua berkas berasal dari pembacaan lokal `Archives` atau rancangan untuk implementasi. Berkas sumber tidak diubah. Dataset di sini merupakan **staging**, belum data produksi atau hasil analisis terverifikasi. Tidak ada data yang telah diunggah ke Supabase.

| Berkas | Isi | Status dan cara penggunaan |
|---|---|---|
| [audit_archives.py](audit_archives.py) | Script audit dan ekspor dengan pustaka standar Python | Jalankan dari root: `python Planning/bahan/audit_archives.py`; menulis ulang keluaran audit yang dihasilkan script |
| [hasil_audit.json](hasil_audit.json) | Jumlah data, kualitas koordinat, rekap dan struktur workbook | Bukti audit lokal; bukan hasil uji aplikasi |
| [verifikasi_paket.json](verifikasi_paket.json) | Pemeriksaan hash sumber, isi staging, header CSV/SQL dan tautan lokal | Pemeriksaan lokal lulus; SQL dan aplikasi belum dieksekusi |
| [inventaris_sumber.csv](inventaris_sumber.csv) | 49 path, ukuran byte dan SHA-256 | Deteksi perubahan input dan penelusuran sumber |
| [catatan_workbook.json](catatan_workbook.json) | Catatan sumber/tahun/alias/OCR dari workbook | Klaim dalam catatan tetap perlu diverifikasi ke sumber primer |
| [staging_puskesmas_2024_s1.csv](staging_puskesmas_2024_s1.csv) | 973 fasilitas dan kandidat koordinat | Semua `eligible_for_buffer=false`; source_row mengacu nomor baris CSV koordinat termasuk header |
| [staging_kecamatan_gabungan.csv](staging_kecamatan_gabungan.csv) | 667 baris detail dari sheet Gabungan | source_row adalah baris Excel; nilai kosong dipertahankan; kode/tahun belum dilengkapi |
| [jumlah_puskesmas_tanpa_total.csv](jumlah_puskesmas_tanpa_total.csv) | 665 baris detail, jumlah 973 | Hanya menghapus baris TOTAL; nama belum dikoreksi; tidak mewakili seluruh master kecamatan |
| [antrean_review_koordinat.csv](antrean_review_koordinat.csv) | 418 baris: 408 missing dan 10 fasilitas dengan titik kembar | Prioritas masalah; 565 kandidat terisi tetap seluruhnya perlu verifikasi |
| [rekonsiliasi_nama_kecamatan.csv](rekonsiliasi_nama_kecamatan.csv) | 97 baris perbandingan nama persis | Dua sisi alias dapat muncul; jangan menyamakan jumlah ini dengan jumlah salah-data |
| [supabase_staging.sql](supabase_staging.sql) | DDL 3 tabel staging mentah | Draft belum dieksekusi; hanya untuk Supabase test/schema baru |
| [pemeriksaan_staging.sql](pemeriksaan_staging.sql) | Query pemeriksaan pascaimpor | Expected ada pada komentar; jangan menganggap SQL sudah lulus PostgreSQL |
| [template_sumber.csv](template_sumber.csv) | Header katalog sumber | Isi metadata sumber asli, tanpa menebak tahun atau tanggal unduh |
| [template_crosswalk.csv](template_crosswalk.csv) | Header mapping wilayah | Isi kode/sistem/edisi, bukti dan reviewer; jangan memakai kode rekaan |
| [template_review_koordinat.csv](template_review_koordinat.csv) | Header hasil verifikasi lokasi | Tautkan kode fasilitas, bukti, ketelitian dan keputusan reviewer |

CSV memakai UTF-8 dengan BOM pada ekspor audit, koma sebagai delimiter, titik untuk desimal, dan field kosong untuk null. Simpan kode sebagai teks ketika membukanya di Excel agar tidak berubah menjadi notasi ilmiah. Template hanya berisi header dan belum berisi keputusan/review palsu.

## Cara menggunakan staging pada tahap implementasi

1. Baca [rancangan Supabase](../04-supabase-dan-kamus-data.md); tentukan environment test.
2. Tinjau `supabase_staging.sql`. Script membuat schema `planning_staging` baru; jika sudah ada, hentikan dan periksa, jangan menghapus data lama. Tidak ada `DROP`, `TRUNCATE` atau kebijakan tulis publik.
3. Setelah DDL dijalankan oleh pengelola, impor tiga CSV sesuai pasangan tabel berikut melalui Table Editor yang mendukung schema tersebut atau `COPY` dari client terotorisasi.
4. Jalankan query pemeriksaan sebagai pemilik/importer yang berwenang, simpan hasil aktual, lalu lanjut kurasi. RLS tanpa policy sengaja menolak role biasa.

| CSV | Tabel |
|---|---|
| staging_puskesmas_2024_s1.csv | planning_staging.puskesmas_2024_s1 |
| staging_kecamatan_gabungan.csv | planning_staging.kecamatan_gabungan |
| jumlah_puskesmas_tanpa_total.csv | planning_staging.jumlah_puskesmas_kecamatan |

Jangan mengisi credential di CSV atau notebook yang dibagikan. Skrip audit tidak menghubungi internet/database dan tidak memutuskan alias resmi, menilai kelayakan layanan, atau melakukan geocoding.
