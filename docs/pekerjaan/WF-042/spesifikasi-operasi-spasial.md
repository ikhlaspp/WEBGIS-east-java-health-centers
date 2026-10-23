# Operasi spasial dan toleransi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Metode kandidat dibekukan untuk fixture sebelum implementasi, bukan klaim hasil spasial telah diuji.

Storage/GeoJSON EPSG4326 `[longitude,latitude]`; Leaflet LatLng API `[latitude,longitude]`, L.geoJSON membaca standard GeoJSON tanpa membalik dua kali. Geometry analisis full precision; display simplified terpisah. Transform CRS dengan reprojection, bukan set_srid untuk mengubah koordinat yang masih CRS lain.

Buffer kanonik PostGIS per eligible point `ST_Buffer(location::geography,radius_m,'quad_segs=32')::geometry`; radius1000/3000/5000meter. [ST_Buffer](https://postgis.net/docs/ST_Buffer.html) memakai meter untuk geography dan proyeksi internal; buffer per point kecil menghindari satu UTM sembarang untuk seluruh Jatim/kepulauan. Reference Python independen menggunakan local AEQD centered per point via pyproj, Shapely buffer quad_segs32 (resolusi sesuai versi API) lalu transform4326. Notebook memakai metode Python yang diuji ekuivalen, method_version membedakan implementation tag.

Candidate selection ST_DWithin(point::geography,region::geography,radius_m+2meter) agar error numeric tidak mengeluarkan boundary contributor; setelah buffer tetap exact intersection. Ambil semua eligible Jatim, bukan hanya district F. Union buffers→intersection full polygon→extract polygon components→MultiPolygon. Empty intersection sah menghasilkan empty geometry pada artefak/DB geom null + area0; berbeda dari invalid input atau no eligible unavailable. Coverage denominator ST_Area(region::geography,true); numerator ST_Area(intersection::geography,true). [ST_Area](https://postgis.net/docs/ST_Area.html) geography memberi area spheroid meter persegi. Python reference memakai pyproj.Geod polygon area (orient holes benar) dan union/clip output equivalence.

MultiPolygon islands dipertahankan; no centroid fallback. Invalid/empty boundary input rejected; repair hanya explicit versioned operation dengan before/after validity/area/component diff dan review. Point exactly boundary ST_Covers sebagai diagnostic; official administrative mapping dan evidence tetap penentu, tidak memindah point. Fasilitas luar provinsi tidak tersedia: edge limitation selalu di metadata. Land/water tidak ditafsirkan travel path.

| Uji | Toleransi sebelum melihat hasil |
|---|---|
| Radius geodesik sampled vertices/bearing | Error absolut≤max(2m,0.01×radius); uji128vertices serta midpoint arah utama |
| Luas SQL vs independent Python | Abs difference≤max(1m²,0.01×reference area) untuk area nonempty; zero expected≤1m² numerical residue dengan penjelasan |
| Percentage | [0,100], internal deviation≤1e-8 sebelum clamp numeric kecil; out-of-range besar fail |
| Overlap invariant | Area union≤sum individual +1m²; clip≤denominator+1m²; monotonic r1≤r3≤r5 dengan1m² slack |
| Set/kode/eligibility | Exact, toleransi0 |
| Display simplification | Max area change0.5%, valid topology per feature dan code set exact; tidak dipakai analisis |

Area near-zero memakai abs floor untuk stabilitas; toleransi1% bukan izin memperbaiki method setelah hasil fail tanpa CR. Benchmark daratan/Madura/pulau jauh/boundary/overlap pada WF-049/111/112. Catat PROJ/GEOS/PostGIS versions, CRS definitions dan code revision. Tidak ada library spasial dijalankan pada pekerjaan desain ini.
