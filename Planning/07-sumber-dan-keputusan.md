# Sumber rujukan dan catatan keputusan

## Sumber lokal utama

| ID | Sumber dan lokasi | Kontribusi dan batas |
|---|---|---|
| L01 | `Archives/Proposal.docx`, Latar Belakang, Tujuan, Batasan Masalah, Software, Desain Tabel | Dasar scope. Menyebut MySQL, bukan Supabase; perubahan database berasal dari permintaan pengguna |
| L02 | `Archives/Puskesmas_2024.pdf`, keputusan HK.01.07/MENKES/1690/2024 | Identitas sumber fasilitas Semester I 2024; angka CSV tetap perlu rekonsiliasi ke halaman daftar Jatim |
| L03 | `Archives/puskesmas_jatim_alamat.csv`, baris 2–974 | Master 973 fasilitas, kategori dan alamat |
| L04 | `Archives/puskesmas_jatim_koordinat.csv`, baris 2–974 | Kandidat koordinat dan status geocoding |
| L05 | `Archives/jumlah_puskesmas_per_kecamatan.csv` | Detail, subtotal kabupaten dan total provinsi; audit menyingkirkan agregat dari penjumlahan detail |
| L06 | `Archives/Data_Gabungan_Kecamatan_Jawa_Timur.xlsx`, sheet `Catatan` dan `Gabungan` | 667 detail, Sempol tanpa indikator, alias dan catatan campuran sumber |
| L07 | `Archives/langsung buka csv disini/Data_Penduduk_Per_Kecamatan_Jawa_Timur_2024 .xlsx`, sheet `Catatan` dan wilayah | Tahun observasi menurut catatan, OCR dan provenance yang perlu dilengkapi |
| L08 | `Archives/langsung buka csv disini/Data_Luas_Wilayah_Per_Kecamatan_Jawa_Timur_2024.xlsx`, sheet `Catatan` dan wilayah | Tahun luas alternatif dan konversi unit |
| L09 | `Archives/per kecamatan/*.pdf` | 38 buku BPS kabupaten/kota; pemeriksaan tiap tabel/halaman masih pekerjaan implementasi |
| L10 | `Archives/GIS.ipynb`, cell 4 dan cell 6 (indeks 0-based) | Dua pola geocoding; fallback centroid dan kebutuhan cache/review |

Hasil kuantitatif paket ini berasal dari script lokal, bukan dari asumsi nama file. [Manifest sumber dengan SHA-256](bahan/inventaris_sumber.csv) dan [catatan workbook yang diekstrak](bahan/catatan_workbook.json) memudahkan pemeriksaan ulang.

## Rujukan web resmi

Diakses untuk perencanaan pada 22 Oktober 2026. Tautan mendukung keputusan teknis dan pencarian bahan; keberadaan layanan publik tidak berarti dataset telah diunduh atau hak redistribusinya sudah ditetapkan.

| ID | Sumber primer | Bagian yang dipakai |
|---|---|---|
| S01 | [Permenkes 19/2024, JDIH Kemenkes](https://jdih.kemkes.go.id/storage/documents/pdfs/2024permenkes019.pdf) | Pasal 10 pada halaman PDF 8: rasio, kecamatan dan aksesibilitas; interpretasi metode dijelaskan di dokumen arsitektur |
| S02 | [MFD Jawa Timur 2023, BPS](https://jatim.bps.go.id/id/publication/2024/07/26/d64a7ab574bdbb877d3f5665/village-master-file-of-jawa-timur-province-2023.html) | Kandidat master kode/nama administrasi sesuai baseline |
| S03 | [MFD Jawa Timur 2024, BPS](https://jatim.bps.go.id/id/publication/2025/07/25/e43fa2236e8c5703965ae076/village-master-file-of-jawa-timur-province-2024.html) | Pembanding edisi wilayah; perlu crosswalk jika dipilih |
| S04 | [Jumlah kecamatan tahun 2023, BPS Jawa Timur](https://jatim.bps.go.id/id/statistics-table/3/S3pkSVdHdG1iVU50TXlzdlNYY3pZVzFVV1haVlFUMDkjMw%3D%3D/jumlah-kecamatan-menurut-kabupaten-kota-di-provinsi-jawa-timur--2023.html?year=2023) | Pemeriksaan baseline administrasi; isi dan tahun tabel harus dicatat saat unduh |
| S05 | [Batas kecamatan BIG](https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KECAMATAN_AR/MapServer) | Metadata layanan saat diperiksa: edisi Juni 2026, CRS 4326; kebutuhan harmonisasi historis |
| S06 | [Supabase dengan Laravel](https://supabase.com/docs/guides/getting-started/quickstarts/laravel) | Integrasi PostgreSQL, schema aplikasi, koneksi dan autentikasi Laravel |
| S07 | [Supabase PostGIS](https://supabase.com/docs/guides/database/extensions/postgis) | Ekstensi spasial, tipe dan kueri geografi |
| S08 | [Koneksi PostgreSQL Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres) | Pemilihan direct/session pooler sesuai environment |
| S09 | [Pengamanan Data API](https://supabase.com/docs/guides/api/securing-your-api) | Grants, RLS, schema terekspos dan opsi menonaktifkan Data API |
| S10 | [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) | Hak role, bypass, view dan uji allow/deny |
| S11 | [Backup Supabase](https://supabase.com/docs/guides/platform/backups) | Backup/restore serta ketergantungan paket |
| S12 | [Deployment Laravel 13](https://laravel.com/framework/docs/13.x/deployment) | PHP minimal 8.3, ekstensi, document root dan konfigurasi deployment |
| S13 | [Leaflet reference](https://leafletjs.com/reference.html) | API peta dan GeoJSON; dokumentasi 1.9.4 saat diperiksa |
| S14 | [Folium MarkerCluster](https://python-visualization.github.io/folium/latest/user_guide/plugins/marker_cluster.html) | Marker cluster untuk artefak HTML; pilih versi paket stabil saat implementasi |
| S15 | [GeoPandas to_crs](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.to_crs.html) | Transformasi CRS, berbeda dari sekadar memberi label CRS |
| S16 | [PostGIS ST_Buffer](https://postgis.net/docs/ST_Buffer.html) | Satuan geography dalam meter, geometri mengikuti CRS dan parameter kurva |
| S17 | [Kebijakan Nominatim](https://operations.osmfoundation.org/policies/nominatim/) | Batas layanan publik, cache, batch, identitas dan larangan autocomplete |
| S18 | [Kebijakan tile OSM](https://operations.osmfoundation.org/policies/tiles/) | Atribusi, caching, penggunaan server tile dan larangan bulk/offline prefetch |

Tidak ada harga layanan yang dikutip karena paket anggaran belum dipilih. Tidak ada klaim bahwa koordinat hasil Nominatim adalah data resmi Kemenkes. Tanggal sumber historis dan tanggal akses dokumentasi teknis dipisahkan.

## Keputusan yang telah digunakan dalam rencana

| ID | Keputusan | Dasar |
|---|---|---|
| ADR-01 | Supabase PostgreSQL/PostGIS menggantikan MySQL | Permintaan pengguna; dicatat sebagai perubahan terhadap proposal |
| ADR-02 | Laravel tetap backend; Leaflet peta dinamis; Colab/Folium tetap keluaran penelitian | Menjaga kebutuhan proposal sekaligus fitur aplikasi |
| ADR-03 | Semua akses database publik melalui Laravel; akun memakai Laravel | Menyederhanakan auth dan mencegah dua sistem izin yang tidak sinkron |
| ADR-04 | Snapshot fasilitas 2024-S1; tahun penduduk/luas per observasi | Kondisi aktual arsip dan kebutuhan provenance |
| ADR-05 | Koordinat perkiraan/centroid tidak dipakai untuk buffer fasilitas | Menghindari kepastian lokasi yang tidak didukung bukti |
| ADR-06 | Rilis immutable dan analisis mempunyai versi/parameter | Reproduksibilitas, audit dan rollback |
| ADR-07 | Routing dan waktu tempuh P2 | Proposal membatasi analisis radius; data jaringan belum tersedia |
| ADR-08 | Output perencanaan berbentuk Markdown, dataset CSV, JSON audit dan SQL staging | Mudah dibaca, diperiksa dan dipakai dalam workspace pengembangan |

## Keputusan terbuka sebelum implementasi yang bergantung padanya

| ID | Hal yang perlu ditetapkan | Default rencana | Dampak bila berbeda |
|---|---|---|---|
| OPEN-01 | Persyaratan dosen tentang perubahan MySQL | Catat Supabase sebagai revisi teknis sesuai instruksi pengguna | Bila MySQL juga wajib demonstrasi, tambah scope sinkronisasi/migrasi tersendiri |
| OPEN-02 | Edisi kode/polygon dan izin penggunaan | Utamakan edisi 2023/2024 yang cocok baseline | Boundary 2026 memerlukan harmonisasi dan batas interpretasi |
| OPEN-03 | Tahun penduduk/luas yang bisa dibuktikan | Penduduk 2023, luas selaras bila tersedia | Data campuran hanya dipakai dengan metadata/label dan tanpa klaim satu tahun |
| OPEN-04 | Provider geocoding, sumber koordinat dan bukti yang diterima | Koordinat resmi dan review POI; provider batch yang diizinkan | Biaya, throughput, lisensi hasil dan ketepatan lokasi |
| OPEN-05 | Cakupan analisis penuh atau parsial saat deadline | Penuh memerlukan seluruh 973 lokasi valid | Parsial wajib menyebut missing dan membatasi kesimpulan coverage |
| OPEN-06 | Tanggal penyerahan, kapasitas tim, hosting dan budget | 8 minggu, 3 orang, 12–15 jam/orang/minggu sebagai estimasi | Jadwal P1 dan layanan harus disesuaikan |
| OPEN-07 | Apakah UI admin/ekspor wajib di penilaian | P1; kontrol impor/publish backend tetap P0 | Tambah prioritas dan pengujian sebelum rilis bila diwajibkan |

Hal terbuka di atas tidak menghalangi penyelesaian paket perencanaan. Saat implementasi, keputusan dicatat bersama penanggung jawab dan tanggal sebelum pekerjaan yang bergantung padanya dijalankan.
