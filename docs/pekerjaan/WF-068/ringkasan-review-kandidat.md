# Screening dan progres review 565 kandidat

Tanggal 2026-10-25. Status: in_progress; review fasilitas belum selesai. Pelaksana: Codex. Tidak ada penerimaan independen atau promosi lokasi.

## Bukti yang sudah diperiksa

Seluruh 565 kandidat CSV direkonsiliasi tepat ke kode, nama, alamat, query dan koordinat pada baris normalisasi sumber yang dipatok SHA256. Geometri analisis penuh WF-066 digunakan; geometri display tidak dipakai. Pembagian 44 batch per kabupaten/kota, maksimum 25 kode, tersimpan dalam review-565-kandidat.json. Data rinci lokal: data/staging/location_reviews.json; hash keluaran ada pada laporan.

- 543 titik tercakup polygon kecamatan yang ditugaskan; 22 di luar.
- Tiga tidak tercakup polygon manapun dalam himpunan terpilih.
- Delapan dalam jarak 50 meter dari batas kecamatan yang ditugaskan, termasuk titik di kedua sisi batas.
- Lima kelompok berbagi koordinat; tidak digabung sebagai satu fasilitas.
- Seluruh 565 mempunyai label historis Ditemukan, tetapi tidak satu query historis pun menyertakan alamat jalan lengkap.
- Nol lokasi verified. Kedekatan, nama sama, dan containment administrasi tidak cukup untuk menerima lokasi fasilitas.

Jarak batas dihitung dalam proyeksi AEQD lokal berpusat pada titik. Ia digunakan untuk flag review, bukan memindahkan titik atau menilai akurasi edisi batas 2024. Batas sumber tahun 2020 tetap dicatat. Kasus jauh antara lain Margomulyo (sekitar 48 km dari batas kecamatan yang ditugaskan), Sumbersari Jember (36 km), Wonosari Malang (25 km), Arjasa Jember (10 km), Wates Kediri (7 km). Seluruhnya memerlukan bukti lokasi, bukan koreksi otomatis.

## Penelusuran sumber tambahan

Dataset pemerintah Trenggalek https://satudata.trenggalekkab.go.id/json/507 menghasilkan HTTP403. PDF Kemenkes https://sehatnegeriku.kemkes.go.id/wp-content/uploads/2018/06/BUKU-INFORMASI-MUDIK-TAHUN-2018-FINAL.pdf gagal DNS baik sandbox maupun elevated; browser fetch502. Kegagalan tidak diubah menjadi no_match.

Katalog CKAN HDX Indonesia Healthsites berhasil diambil melalui https://data.humdata.org/api/3/action/package_show?id=indonesia-healthsites. Dataset ODbL, sumber OSM/Healthsites, pembaruan 2026-09-29, berisi 17862 feature nasional. Katalog dan GeoJSON dibekukan dengan receipt SHA256. Respons redirect resmi menuju s3.us-east-1.amazonaws.com diizinkan untuk unduhan; URL bertanda tangan tidak disimpan sebagai identitas sumber.

Discovery memeriksa 3327 geometri valid dalam extent luas Jawa Timur termasuk pulau, lalu mencari kandidat di jendela 0,05 derajat. Jendela ini bukan toleransi matching. 193 dari 565 mempunyai nama ter-normalisasi sama di sekitar titik; 96 tidak mempunyai healthsite dalam jendela. Hanya tiga kandidat awal tercakup geometri bernama cocok: Tambak (way/1295378350), Kendalkerep (way/629408229), Trajeng (way/1536417875). Ini daftar prioritas, bukan accepted. Ringkasan/hash: healthsites-discovery-summary.json; detail privat: data/staging/location-evidence-discovery.json.

Tambak: OSM memuat Jalan Bhakti No.44, Gresik; master Jl. Bakti Kepulauan Bawean, Kecamatan Tambak. Object version1 bertanggal 2024-06-23. Perlu pemeriksaan bukti alamat dan bangunan sebelum keputusan.

Kendalkerep: profil resmi https://puskkendalkerep.malangkota.go.id/profil/ menyebut Jalan Sulfat100, Bunulrejo, Blimbing, sesuai master. Object OSM version3 bertanggal 2025-08-05; source footprint dan riwayat perlu ditinjau untuk batas observasi temporal.

Trajeng: https://pasuruankota.go.id/puskesmas/ menyebut Jl. Maluku1, Panggungrejo, sedangkan https://dinkes.pasuruankota.go.id/puskesmas/ menyebut jalan sama tetapi Kecamatan Gadingrejo. Master Panggungrejo. Konflik antarhalaman resmi dicatat; object OSM baru bertanggal 2026-07-08 tidak membuktikan lokasi 2024. Jangan auto-accept.

## Verifikasi dan pekerjaan tersisa

Perintah aktual exit0:

```text
.venv/Scripts/python.exe scripts/etl/geocode.py audit-existing --queue-report docs/pekerjaan/WF-067/antrean-review-lokasi.json --normalization-report docs/pekerjaan/WF-062/manifest-normalisasi.json --boundary-manifest docs/pekerjaan/WF-066/manifest-geometri.json --report docs/pekerjaan/WF-068/review-565-kandidat.json
.venv/Scripts/python.exe -m pytest tests/python -q
221 passed in 15.14s
.venv/Scripts/python.exe -m compileall -q python scripts/etl
```

Ulang audit menghasilkan artefak identik. Enam tes khusus membuktikan boundary covers termasuk titik tepat di batas, shared-point tidak didedup, sumber/identitas berubah ditolak dan tidak ada auto-accept. Seluruh 565 screened masih pending review bukti fasilitas; partition completed0+pending565+blocked0 tepat565. Status screening selesai berbeda dari review lokasi selesai.

Berikutnya: tinjau bukti per fasilitas pada 44 batch, simpan reviewer/tanggal/alasan dan hasil, selesaikan konflik. Jangan menutup WF-068 atau lanjut antrean serial hanya berdasarkan screening otomatis. Perubahan saat ini disimpan lokal sampai satu commit item dapat memuat hasil review yang lengkap.
