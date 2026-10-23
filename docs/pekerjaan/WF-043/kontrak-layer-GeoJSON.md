# Kontrak layer GeoJSON

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

Endpoint feature collection: `type=FeatureCollection`, features[], meta{release_id,analysis_run_id,boundary_set_id,metric,unit,source_periods,legend,coordinate_coverage,warnings,geometry_detail}. Feature id=official_code (atau facility_code untuk points), bukan nama. Properties: code,parent_code,name,value nullable,unit,completeness,reason,without_facility,source_ids,source_periods,release_id,analysis_run_id. Semua values JSON finite; null bukan NaN/Infinity.

Polygon join exactly1 feature/code untuk boundary set scoped; no duplicate join akibat dua observasi sumber. Missing indicator tetap feature dengan value null/reason, bukan menghilangkan polygon. F0 dengan knownP → ratio null dan without_facility=true; unknownP plus F0 menampilkan no-data dan flag pada detail. Missing facility point tidak masuk GeoJSON point features tetapi total/missing di meta dan fasilitas tetap tabel.

`geometry_detail=display|full` allowlist; default display. Full geometry analisis tidak diubah; display simplified topology-preserving pada toleransi metrik10m kab/kecamatan awal, lalu quality area≤0.5% dan valid/nonempty/component survival. Bila gagal, pakai full feature; jangan membuang pulau kecil. Shared border gaps/overlap diperiksa lintas feature; bila simplifikasi independen merusak coverage, gunakan shared-boundary simplification atau full. JSON example file `contoh-layer.json` memakai MultiPolygon sintetis valid, nilai valid/zero/null dan dua pulau.

Tile/geometry rendering tidak membuat request analisis baru. Tooltip di-escape text, label periode dan quality serta tautan detail yang dibuat dari kode encoded. Geometry CRS standardized4326, tidak menambah custom CRS member untuk menyembunyikan koordinat metrik. Antarmuka L.geoJSON melakukan konversi sesuai format, tidak memanggil LatLng array dengan urutan lonlat mentah.
