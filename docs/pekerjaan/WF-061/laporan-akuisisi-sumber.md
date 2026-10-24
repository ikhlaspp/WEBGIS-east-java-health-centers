# Akuisisi dan pembekuan sumber

Tanggal pemeriksaan: 2026-10-24. Status: selesai untuk ketersediaan input; bukan penerimaan kualitas data atau izin publikasi aplikasi.

## Input yang dibekukan

`source-plan.json` menetapkan 49 berkas Archives sesuai hash baseline WF-017 dan 42 berkas unduhan resmi: PDF fasilitas Kemenkes, PDF master BPS, anggota ZIP batas HDX, katalog lisensinya, dan 38 tabel penghubung kode BPS. Hasil aktual 91 entri, 757.876.806 byte; tidak ada sumber wajib hilang, berubah, berlebih, duplikat, atau gagal verifikasi. Notebook dan proposal dipertahankan sebagai konteks; notebook tidak dijalankan.

`data/raw/manifest.json` adalah manifest operasional lokal. `manifest-input-mentah.json` mencatat hash manifest tersebut, setiap berkas, konfigurasi keputusan sumber, periode dan laporan rekonsiliasi. Data mentah tetap diabaikan Git; hanya kode, metadata dan bukti pemeriksaan yang dikirim. Semua 38 PDF BPS dapat dibuka dan memiliki total 17.208 halaman. Ini pemeriksaan container dan jumlah halaman, bukan klaim seluruh tabel telah diekstrak atau angka OCR telah disahkan.

Unduhan terpilih yang telah selesai digunakan kembali dengan verifikasi hash/ukuran. Adapter dijalankan ulang pada snapshot yang sama, sehingga tidak mengganti edisi historis dengan isi URL terbaru. Batas HDX menggunakan anggota ZIP `idn_admin3.geojson` yang lengkap dan terverifikasi CRC/hash; tidak ada klaim ZIP nasional utuh telah diunduh. Kandidat BIG 2026 dan percobaan ZIP parsial tidak masuk manifest.

## Hasil aktual

- Fasilitas: kedua PDF dipindai masing-masing 239 halaman; masing-masing 973 fasilitas / 38 kabupaten-kota, tanpa duplikat, quarantine atau diagnostic. Perbedaan field antar-PDF: 0. Seluruh kode cocok dengan CSV historis.
- Master: 666 kecamatan / 38 induk; 16 konflik internal sumber tetap tercatat dengan resolusi berbukti dari tabel kode resmi, 0 konflik belum terselesaikan. Penghubung kode: 38 tabel / 666 pasangan unik.
- Batas: 666 kecamatan / 38 induk, 603 Polygon dan 63 MultiPolygon; satu objek Perairan dipisahkan. Geometri bertanggal 2020-04-01, master 2023, fasilitas 2024-S1. Mode eksplorasi lintas periode wajib diberi label; validasi geometri ketat tahun 2023 tidak diklaim.
- Penduduk dan luas: masing-masing 666 baris detail + 38 total, tanpa diagnostic parser; seluruh nilai tetap `staging_unverified`. Tahun penduduk yang diklaim catatan workbook: 2023. Tahun luas: 585 baris 2023, 33 baris 2019, 24 baris 2021, 24 baris 2025.
- Workbook gabungan berisi 667 baris detail. Lima nama penduduk berbeda dalam pemisahan kata; tidak dilakukan fuzzy join. Entri Bondowoso/Sempol merupakan tambahan pada gabungan, perlu kurasi terhadap Ijen agar tidak menghitung ganda. Tidak ada selisih penduduk pada pasangan nama tepat. Ada 39 selisih luas, tampak berkaitan dengan pembulatan; nilai asli dan selisih dipertahankan dalam `reconciliation.json`, tidak dikoreksi otomatis.

## Pemeriksaan dan tindak lanjut

Suite Python: 94 passed; compileall berhasil. Delapan kasus akuisisi mencakup hasil normal/reuse dan penolakan berkas berubah, hilang, tambahan, unduhan rusak, identitas duplikat, path keluar direktori, serta penulisan ke Archives. Setelah pengetatan target manifest JSON, delapan kasus tersebut diulang: passed. Kedua perintah adapter aktual berakhir exit 0.

Snapshot tidak boleh diedit; perubahan sumber memerlukan snapshot baru dan review rencana. Ketentuan ini bersifat prosedural, bukan ACL sistem operasi. Kegagalan invocation baru tidak mengubah manifest sukses sebelumnya menjadi bukti sukses run baru.

Tidak ada penghalang ketersediaan untuk WF-062. Kualitas angka derivative, pembacaan PDF scan, perbedaan total Bangkalan yang sudah dicatat WF-058, validitas geometri dan koordinat yang belum lengkap tetap harus ditangani pada ekstraksi/kurasi/validasi sebelum rilis. Pernyataan catatan workbook tentang CSV sumber tahun lain bukan bukti bahwa CSV asli tersebut tersedia di Archives. Tidak ada persetujuan dosen, reviewer independen atau UAT yang diklaim. Pemeriksaan teknis dilakukan oleh agen.
