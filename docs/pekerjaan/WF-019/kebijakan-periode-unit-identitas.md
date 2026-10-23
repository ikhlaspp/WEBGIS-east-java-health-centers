> Current decision: [WF-G2 accepted](../WF-028/penerimaan-WF-G2.md). The accepted supplement supersedes earlier pending gate/scope statements. Data completeness and source checks remain mandatory before dependent implementation; partial demos are labelled; optional UI/public CSV/ranking tests are out of scope, not passed. Existing P0 checks remain required.

# Periode, unit dan identitas sumber

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Kebijakan kandidat untuk SRS.

## Periode

Fasilitas dibekukan 2024-S1 sesuai KMK 1690/2024. Penduduk ditargetkan observasi 2023; luas statistik diutamakan 2023. Nama file 2024 tidak membuktikan observasi 2024. Bedakan `observation_period`, `published_at`, `retrieved_at`, `effective_from/to` dan `release_id`; tanggal akses hari ini tidak mengubah tahun historis.

Master kode target MFD BPS 2023. Polygon wajib memiliki boundary_set/version/edition/CRS dan izin yang dapat ditelusuri. Sumber BIG yang ditemukan adalah 2026: belum dipilih untuk produksi. Pilihan yang masih memerlukan keputusan adalah memperoleh polygon historis yang cocok atau menerima harmonisasi eksplisit 2026 dengan crosswalk dan batas klaim. Jangan menggunakan geometri terbaru secara diam-diam. Jumlah 666 kecamatan diverifikasi terhadap edisi, tidak dipaksakan.

## Unit dan kunci

| Atribut | Representasi normal | Raw dan validasi |
|---|---|---|
| Kode fasilitas | String persis; identitas bersama release_id | Tidak diparse numerik/dipangkas nol depan; kode tidak dijadikan kode kecamatan |
| Kode wilayah | String + code_system + edition + parent_code | Join melalui crosswalk yang direview, bukan nama saja |
| Penduduk | Jiwa, bilangan nonnegatif | Simpan raw/unit asli; ribu jiwa ×1000 hanya jika metadata membuktikan; missing null |
| Luas statistik | km² positif atau null | Hektar/100; pertahankan unit dan faktor, source locator, presisi |
| Koordinat | WGS84 EPSG:4326; lon [-180,180], lat [-90,90] | Pair lengkap, raw/provider/precision/status; rentang global bukan bukti lokasi Jatim |
| Radius | Meter, allowlist 1000/3000/5000 | Jangan memakai derajat; parameter analisis versioned |
| Luas geometri | m² untuk komputasi; km² = m²/1.000.000 untuk display | Metode geodesik/proyeksi dan boundary_set wajib; bukan A statistik BPS |

Normalisasi pemisah ribuan/desimal berdasarkan sumber; string ambigu masuk quarantine. Simpan nilai penuh untuk kalkulasi dan format Indonesia hanya pada tampilan. `raw_value`, `normalized_value`, `unit`, `factor`, `source_id`, `table`, `page/row`, `observation_period` wajib untuk fakta terisi. Metadata sumber memuat penerbit, judul, URL, hash file, hak pakai dan tanggal akses.

## Campuran sumber

Mode historis selaras hanya aktif jika tahun/definisi/edisi yang dipersyaratkan terbukti. Mode eksplorasi campuran diperbolehkan sebagai kandidat dengan label per nilai dan banner ringkasan; jangan menulis “rasio 2024” tanpa menjelaskan fasilitas 2024-S1 dan penduduk 2023. Luas 2019/2021/2025 tetap berlabel sesuai observasi. Perbandingan lintas wilayah dengan periode berbeda menampilkan peringatan.

Indikator terkait dinonaktifkan bila unit/tahun/provenance tidak diketahui, mapping ambiguous, A≤0, atau input penting null. Rilis dapat menampilkan data valid lainnya dengan alasan no-data; tidak boleh menampilkan angka hasil imputasi seolah sumber asli. Crosswalk menyimpan alias, kode asal/tujuan, sistem/edisi, bukti perubahan, reviewer, status dan cardinality; many-to-one dilarang menggandakan P/A. Kasus Sempol–Ijen belum diputuskan.
