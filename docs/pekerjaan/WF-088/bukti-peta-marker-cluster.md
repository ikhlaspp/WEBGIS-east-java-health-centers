# Bukti peta, marker, cluster dan popup

27 Oktober 2026. Implementasi lokal terverifikasi; bukan bukti penerimaan data lapangan atau deployment produksi.

## Implementasi

- Leaflet 1.9.4 dan Leaflet.markercluster 1.5.3 dikunci dalam package-lock. Modul peta dimuat dinamis pada halaman peta/detail.
- `/peta` menyediakan zoom/pan bawaan Leaflet, kontrol layer, skala, atribusi dan tombol kembali ke seluruh titik. Tile memakai HTTPS OpenStreetMap, caching browser normal, tanpa prefetch atau bulk download.
- GeoJSON `[longitude, latitude]` diubah sekali ke LatLng `[latitude, longitude]`. Geometri salah, kode duplikat dan hitungan tidak konsisten ditolak sebelum marker ditampilkan. Missing tidak diberi titik pengganti.
- Cluster memperluas titik bertumpuk. Pilihan dari tabel membuka popup pada koordinat asli, terpisah dari posisi visual sementara saat spiderfy. Ini memperbaiki konflik animasi ketika berpindah dari cluster yang sudah terbuka ke fasilitas lain di titik sama.
- Popup memakai node DOM/textContent untuk nama, status dan layanan. Layanan diambil dari API detail pada rilis/run yang sama. Link detail memakai kode numerik dan membawa identitas rilis.
- Daftar memakai API fasilitas, 50 per halaman; termasuk fasilitas tanpa koordinat. Kegagalan tile tidak menghapus marker atau tabel. Kegagalan API memiliki retry tanpa berpindah rilis.
- Pada environment testing, Vite menggunakan hot-file terpisah yang tidak ada sehingga pengujian memakai build produksi dan tidak bergantung server dev pengguna.

## Expected / actual

| Kasus | Hasil aktual |
|---|---|
| Dua fasilitas satu koordinat dan fasilitas pulau | Cluster 2 terbuka; kedua identitas dan layanan dapat diakses; pulau tetap terlihat dalam fit bounds |
| Popup nama mengandung HTML berbahaya | Ditampilkan literal; tidak ada elemen img atau script yang berjalan |
| Missing | Tetap ada pada tabel; tidak ada tombol titik atau marker pengganti |
| Tile gagal | Banner tersedia, tabel/paging/layer tetap dapat digunakan |
| API gagal, retry, navigasi | Rilis tetap dipatok; tautan Ringkasan dan detail mempertahankan rilis/run |
| Rilis belum tersedia / koordinat terbalik | Pesan jelas dan tidak ada marker |
| Tabel dari rilis berbeda | Respons ditolak; baris tidak ditampilkan |
| Desktop 1280px / mobile 360px | Screenshot diperiksa; kontrol, atribusi, heading terbaca; tabel mobile menggulir horizontal di dalam kontainer |

`npm.cmd run test:e2e`: **15 passed (21.6s), exit 0**, termasuk 10 regresi dashboard/health dan 5 tes map. `npm.cmd run build`, `npm.cmd run lint`, Pint dan `git diff --check` lulus. `php artisan test --compact tests/Feature/ExampleTest.php`: 1 passed, 1 assertion. Warning build fontaine opsional sudah ada sebelumnya.

Screenshot: `test-results/markers-map-clusters-coloc-b1ffc-ides-safe-popups-and-detail/map-desktop.png` dan `test-results/markers-tile-failure-prese-8351d--controls-and-mobile-layout/map-mobile.png`. CI mengunggah test-results dan report selama tujuh hari. Tile pada pengujian diganti gambar fixture atau sengaja digagalkan; gambar kosong pada screenshot bukan bukti tile provider nyata gagal. Tidak dilakukan load test atau klaim smoke provider nyata.

Fixture hanya empat identitas sintetis (tiga titik, satu missing). Kasus paging memakai total sintetis 51 untuk memeriksa kontrol halaman. Tidak ada perubahan database asli.

Referensi implementasi: [Leaflet API 1.9.4](https://leafletjs.com/reference.html), [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster), [kebijakan tile OSM](https://operations.osmfoundation.org/policies/tiles/). Kebijakan provider diverifikasi saat implementasi; kesiapan deployment tetap perlu memastikan referer browser dan penggunaan sesuai kebijakan.

Pengiriman: `1756002d92a147d8cd4f0d9d1249e0ccd356920d` sudah ada pada remote `work/continued-implementation` (SHA cocok melalui ls-remote). [CI 40454524048](https://github.com/ikhlaspp/WEBGIS-east-java-health-centers/actions/runs/40454524048) lulus pada kedua job application dan python, termasuk database terisolasi serta browser Linux.
