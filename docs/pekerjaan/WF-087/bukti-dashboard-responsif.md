# Bukti dashboard responsif

Tanggal: 27 Oktober 2026. Pelaksana implementasi dan pemeriksaan: agen pengembangan atas instruksi pengguna. Ini bukti pengujian perangkat lunak, bukan penerimaan data lapangan atau review eksternal.

## Implementasi

Halaman `/` memakai `resources/views/home.blade.php` dan layout publik `resources/views/layouts/app.blade.php`. `resources/js/dashboard.js` mengambil rilis aktif dari metadata katalog, kemudian mengunci statistik, wilayah dan sumber pada pasangan release_id/analysis_run_id yang sama. Pasangan tersebut disimpan pada URL; retry tidak berpindah otomatis ke rilis baru. Respons dengan identitas berbeda ditolak sebelum menampilkan ringkasan.

Empat kartu membedakan fasilitas terdaftar, memiliki koordinat, lokasi terverifikasi, dan tanpa koordinat. Kelayakan analisis radius dijelaskan terpisah. Periode fasilitas, penduduk dan luas wilayah ditampilkan sesuai API. Nilai belum tersedia memakai tanda pisah atau keterangan, sedangkan angka nol sah tetap ditampilkan sebagai nol.

Navigasi saat ini menuju bagian Ringkasan, Wilayah, Sumber & metode serta login admin yang sudah tersedia. Halaman peta dan tabel akan dihubungkan saat implementasi tiket berikutnya; tidak ada tautan ke halaman yang belum tersedia. Bahasa dokumen Indonesia, skip link, fokus keyboard, status aria-live, aria-busy dan reduced-motion tersedia.

## Pemeriksaan aktual

| Pemeriksaan | Hasil |
|---|---|
| `npm.cmd run test:e2e` | 10 passed, 12.8s, exit 0 |
| Lebar 360 / 768 / 1366 px | Tidak ada overflow horizontal; kartu satu / dua / empat kolom; navigasi dapat dipakai |
| Review gambar ketiga ukuran | Teks, angka, periode, sumber dan logo terbaca; tidak ada elemen terpotong |
| Belum ada rilis publik | Angka tidak diganti nol; pesan kosong tampil |
| API gagal dan retry | Loading tidak menampilkan nol; retry mempertahankan rilis |
| Respons beda rilis | Ringkasan parsial tidak ditampilkan |
| URL rilis eksplisit / UUID tidak valid | Katalog dilewati untuk rilis eksplisit; identitas tidak valid ditolak |
| Sumber berisi HTML / URL javascript | HTML tampil sebagai teks; URL tidak aman tidak dibuat menjadi tautan |
| `npm.cmd run lint` / `npm.cmd run build` | Lulus; build menyampaikan warning fontaine opsional yang sudah ada |
| `php vendor/bin/pint --dirty --format agent` | Lulus |
| `php artisan test --compact tests/Feature/ExampleTest.php` | 1 passed, 1 assertion |

Test aktual: `tests/browser/dashboard.spec.js`, menyesuaikan direktori Playwright yang sudah ada dari target rencana `tests/Browser`. Screenshot dibuat ulang pada `test-results/**/dashboard-360.png`, `dashboard-768.png`, dan `dashboard-1366.png`. Workflow menyimpan `test-results/` dan `playwright-report/` dalam artifact `application-results` selama tujuh hari.

Seluruh respons API browser memakai fixture sintetis, termasuk angka 973/565/240/408 dan kelayakan 230. Angka tersebut tidak menyatakan koordinat Archives sudah diterima. Server pengujian diarahkan ke loopback, bukan Supabase. Tidak ada migrasi, impor, publikasi atau perubahan data online dalam pekerjaan ini.

Pengujian awal lulus assertion tetapi cleanup server Windows tertahan. Server sementara dihentikan sesuai identitas proses; pengujian ulang dengan izin kontrol proses selesai normal dalam 12.8 detik.
