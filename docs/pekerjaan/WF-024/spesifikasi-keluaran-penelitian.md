# Keluaran penelitian dan batas kesimpulan

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

| Keluaran wajib | Isi dan format | Bukti penerimaan |
|---|---|---|
| Notebook | ipynb, urutan manifest→validasi→indikator→spasial→visualisasi→export; dependency terkunci | Run all pada runtime Colab bersih tanpa langkah tersembunyi, fixture lalu snapshot |
| HTML Folium | Peta, cluster, legenda/metode, release/run dan label partial | Dibuka dua browser; jumlah/kelas/unit sama dengan aplikasi; tidak mengandung credential |
| Tabel indikator | CSV/format tabular artefak penelitian, kode sebagai teks, nilai/unit/period/source/status | Nilai penuh sesuai hasil run, no-data terbedakan, formula-safe untuk spreadsheet |
| Layer/peta | GeoJSON dan gambar peta terpilih dengan legenda, skala/radius dan attribution | Kode/polygon/run konsisten; geometri display dan analisis dibedakan |
| Screenshot | Halaman fitur dan kondisi no-data/error yang relevan | Tanggal, versi, viewport dan skenario dicatat; bukan pengganti log uji |
| Laporan akhir | Sumber, metode, kurasi, hasil, uji, batas kesimpulan dan pembahasan | Semua angka ditelusuri ke tabel/run yang sama; tanpa hasil rekaan |
| Manifest | JSON identitas kode/rilis/run, input/output SHA256, parameter, dependency, boundary edition dan metode | Artefak tidak bercampur lintas versi; checksum diverifikasi |

Ekspor tabel penelitian P0 ini berbeda dari tombol CSV publik FR-14 yang P1. File Folium dapat bergantung tile/CDN; jangan menjanjikan offline penuh tanpa dependency lokal dan hak basemap yang sesuai. Colab membaca snapshot tersanitasi, bukan kredensial produksi.

Metadata pada setiap keluaran (atau sidecar yang tertaut): release_id, analysis_run_id, code_revision, generated_at, observation_periods, source_ids/locator, boundary_set_id, T, radius_m, coordinate coverage, exclusion reasons, method_version, input/output hashes. Field nondeterministik seperti waktu pembuatan dipisahkan dari content hash.

Bandingkan aplikasi dan penelitian dengan manifest yang sama: pin release/run; cocokkan daftar kode dan count, nilai indikator sebelum format, legenda/breakpoints, radius dan eligibility. Perbedaan geometri hanya diterima dalam toleransi metode yang dibekukan; output lama tidak ditimpa.

Batas klaim wajib: data historis bukan direktori layanan terkini; periode campuran tidak dianggap satu tahun; missing/partial dapat bias geografis; radius bukan perjalanan atau layanan penduduk; rasio/defisit bukan rekomendasi pembangunan otomatis; marker cluster bukan statistik klaster. Routing, prediksi, optimasi fasilitas dan evaluasi mutu tetap P2. Tidak ada kewajiban menambah Moran/DBSCAN agar laporan dianggap lengkap.
