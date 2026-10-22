# Analisis radius geometris

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Radius kandidat tetap 1000, 3000, 5000 meter. Tidak ada hasil buffer produksi dihitung dalam pekerjaan kebutuhan.

## Eligibility dan input

Hanya koordinat review_status=verified, precision_level=facility, berpasangan valid dan memiliki sumber, bukti, reviewer/tanggal yang boleh digunakan. Street/village/district/regency centroid tidak eligible. Input berisi release_id, boundary_set_id, input hash, eligible/excluded dengan alasan, radius_m dan metode. Seluruh titik kandidat belum otomatis verified.

## Operasi dan ukuran

Buffer per titik menggunakan metode meter yang benar. WGS84 EPSG:4326 disimpan untuk pertukaran, bukan CRS untuk buffer angka meter sebagai derajat. [PostGIS ST_Buffer](https://postgis.net/docs/ST_Buffer.html) mendefinisikan radius geography dalam meter; desain WF-042 harus menguji metode yang dipilih terhadap referensi independen, termasuk proyeksi lokal dan kepulauan. `quad_segs=32` adalah kandidat, belum benchmark.

Untuk wilayah W dan radius r: ambil seluruh fasilitas eligible Jatim yang buffernya dapat beririsan dengan W, bentuk union buffer, lalu intersection dengan polygon W. Luas coverage = area(intersection)/area(W)×100%, memakai metode area konsisten. Wajib 0≤coverage≤100 dalam toleransi numerik yang ditetapkan sebelum uji. Denominator menggunakan geometri penuh, bukan luas statistik BPS atau geometri simplified display. Overlap tidak dijumlah dua kali.

Fasilitas kabupaten tetangga dalam Jatim dapat berkontribusi. `registered_in_region` tidak sama dengan `contributors_from_dataset`; laporkan keduanya. Fasilitas luar provinsi tidak ada pada snapshot sehingga efek tepi adalah keterbatasan. Pulau dan MultiPolygon dipertahankan; buffer dapat melintasi laut secara geometris dan tidak membuktikan akses transportasi. Tanpa land mask yang sah, gunakan istilah luas polygon, bukan luas daratan.

## Output dan kegagalan

Output per wilayah/radius/run: geometry hasil, covered_area_m2, denominator_area_m2, percentage, registered_count, eligible_count, excluded_count/reasons, contributing_count, boundary edition, metode/parameter, source periods, status penuh/parsial dan hash. Laporkan eligibility pada cakupan yang jelas; kontribusi tetangga tidak menambah denominator fasilitas administratif.

Polygon invalid/empty/tanpa edisi → analisis terkait blocked. Eligible kosong padahal ada master fasilitas yang belum verified → hasil unavailable/null, bukan 0% layanan. Rilis partial merupakan asumsi kerja menunggu keputusan pemilik; seluruh output menampilkan x/y lokasi dan bias missing per wilayah. Full memerlukan 973 eligible dan cakupan boundary disetujui. Tidak ada penggantian titik supaya memenuhi target.

## Penerimaan

Uji radius meter pada titik daratan/pulau, union dua buffer overlap, batas wilayah, fasilitas tetangga, polygon invalid, zero eligible, dan cross-implementation. Kandidat toleransi luas/radius 1% harus dibuktikan metode/kurva dan dibekukan WF-042/049 sebelum uji; tidak boleh dilonggarkan sesudah melihat kegagalan. Coverage bukan persentase penduduk terlayani, waktu tempuh, kapasitas, wilayah kerja resmi atau kepatuhan kebijakan.
