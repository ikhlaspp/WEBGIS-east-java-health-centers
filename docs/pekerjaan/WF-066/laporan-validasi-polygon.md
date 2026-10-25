# Laporan validasi polygon

Tanggal: 2026-10-25. Versi: validate-boundaries-1.0. Pelaksana/review teknis mandiri: Codex; bukan penerimaan independen atau persetujuan publikasi.

## Input dan hasil

Input dipatok melalui hash akuisisi WF-061 dan crosswalk WF-063. Sumber geometri HDX/BPS/OCHA edisi 2020-04-01, master BPS 2023; seluruh analisis tetap berlabel mixed_period_exploration. Hash, versi GEOS/PROJ, lisensi, metrik per kecamatan dan hash keluaran tersedia dalam manifest-geometri.json.

- 666 kecamatan pada 38 kabupaten/kota; himpunan kode tepat sama dengan master.
- Tidak ada geometri invalid/kosong, kode duplikat, polygon identik lintas kode, parent salah, kode hilang atau berlebih.
- CRS84 longitude/latitude, Polygon/MultiPolygon, ring tertutup dan koordinat terbatas diperiksa tanpa perbaikan diam-diam.
- Semua 1191 komponen dipertahankan. Objek perairan ID3522888 tetap terpisah dari master.
- Pabean Cantian 3578240 tetap muncul walau tidak memiliki assignment fasilitas pada snapshot ini. Ini bukan klaim ketiadaan fasilitas sebenarnya.
- Tidak diperlukan repair; log repairs kosong. Geometri analisis sama persis dengan koordinat sumber.

## Geometri display

File analysis.geojson dan display.geojson disimpan terpisah dalam data/processed/boundaries. Display menggunakan proyeksi AEQD lokal per feature dan Douglas-Peucker preserve_topology, toleransi awal 50 meter dengan enam tingkat pengurangan. Kandidat harus valid, memiliki tipe/jumlah komponen/jumlah lubang yang sama, mempertahankan titik interior tiap komponen, serta perubahan luas geodesik tiap komponen dan keseluruhan maksimal 0,5%. Kandidat tanpa pengurangan vertex atau yang gagal guard dikembalikan ke sumber.

Vertex turun dari 886297 menjadi 161014 (sekitar 81,8%); 21 feature memakai sumber penuh. Perubahan luas maksimum 0,489864%. Luas diukur pada ellipsoid WGS84 dengan orientasi ring khusus pengukuran; tidak menggantikan luas statistik. Penyederhanaan per feature tidak menjamin shared-edge coverage antarwilayah; display tidak boleh dipakai untuk overlay atau metrik analisis.

## Review dan verifikasi

Overlay biru sumber/oranye display diperiksa pada enam panel: Jawa Timur, Madura, Bawean, Kangean/Sapeken, Masalembu, pesisir selatan. Outline berimpit pada skala review dan kelompok pulau tetap terlihat; pemeriksaan numerik mencakup semua komponen. Bukti gambar lokal dan hash: visual-review.json. Review ini tidak membuktikan ketepatan lapangan atau edisi batas 2023.

Perintah aktual (exit 0):

```text
.venv/Scripts/python.exe -m pytest tests/python -q
185 passed in 15.23s
.venv/Scripts/python.exe scripts/etl/validate_boundaries.py --acquisition-evidence docs/pekerjaan/WF-061/region-reconciliation.json --crosswalk-evidence docs/pekerjaan/WF-063/output-verification.json --report docs/pekerjaan/WF-066/manifest-geometri.json
```

21 tes khusus mencakup input invalid/tidak tertutup/koordinat terbalik, identitas dan parent salah, perubahan edisi, pelestarian pulau/lubang, batas toleransi, geometri analisis tidak berubah, determinisme dan wilayah tanpa assignment. Suite penuh 185 lulus tanpa warning. Dua eksekusi dataset menghasilkan metrik sama; hasil terakhir menggunakan API transform aktif Shapely 2.2.

Referensi API: https://shapely.readthedocs.io/en/stable/reference/shapely.transform.html dan https://shapely.readthedocs.io/en/stable/reference/shapely.simplify.html.

Temuan total luas Lamongan dan Surabaya dari WF-065 tetap terbuka pada gerbang kualitas. publication_allowed tetap false; validitas geometri tidak menghapus temuan sumber statistik.
