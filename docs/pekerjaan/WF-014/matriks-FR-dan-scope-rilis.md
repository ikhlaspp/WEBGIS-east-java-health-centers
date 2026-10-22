# Kebutuhan fungsional dan scope rilis

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. P=proposal, U=arahan pengguna, R=rekomendasi engineering. Kandidat SRS; perilaku di bawah adalah expected, bukan hasil pengujian aplikasi.

| ID | Asal | Perilaku yang dapat diuji / keluaran | Prioritas | Skenario | Pembangunan | Pengujian |
|---|---|---|---|---|---|---|
| FR-01 | P tujuan 1, batasan 1–2 | 973 kode unik dan 38 kab/kota snapshot 2024-S1; fasilitas missing tetap di master | P0 | UC-01/05/08 | WF-057/064/073/076 | WF-106; D01–D04,D10 |
| FR-02 | P latar/batasan | Tiap lokasi memiliki precision/status/bukti; buffer hanya verified facility | P0 | UC-03/09 | WF-067–071 | WF-110; G01–G04 |
| FR-03 | P tujuan 3 | Peta zoom/pan/cluster; setiap kode dapat dibuka; missing lewat tabel | P0 | UC-01/05 | WF-088/089 | WF-117; W01–W04 |
| FR-04 | P batasan | Choropleth kabupaten berjoin kode, unit/kelas/no-data eksplisit | P0 | UC-02 | WF-081/090 | WF-110/118; G05,W05 |
| FR-05 | P tujuan 2/tabel | P,A,F,T; rasio/kepadatan/defisit sesuai katalog indikator dan periode | P0 | UC-02/10 | WF-077/078 | WF-109; A01–A08-PARAM |
| FR-06 | P batasan | Radius 1/3/5 km, union dan clip; coverage berpenyebut luas geometri | P0 | UC-03/10 | WF-079/080 | WF-111/112; G06–G11 |
| FR-07 | P tujuan 3/lingkungan | Colab Run all menghasilkan tabel dan HTML Folium beridentitas rilis/run | P0 | UC-04/10 | WF-093–096 | WF-123/124; R01–R03 |
| FR-08 | P software | Laravel melayani aplikasi/API, Python ETL/analisis, JavaScript interaksi peta | P0 | Semua | WF-054/055/101 | WF-103/113/117; I01,W01 |
| FR-09 | U Supabase | PostgreSQL/PostGIS, migration/constraint/grants/restore; bukan SQLite untuk bukti spasial | P0 | UC-08–12 | WF-072–075 | WF-113/114/116/122; I01–I06,S06,S07 |
| FR-10 | R | Cari nama/kode/alamat; filter parent/kategori konsisten antara daftar dan marker | P0 | UC-01/05 | WF-083/089 | WF-117/119; W02–W04,W10 |
| FR-11 | R | Dashboard memisahkan F administratif, mapped, verified, missing dan populasi lengkap | P0 | UC-02/05 | WF-078/087 | WF-109/118; A05,A06,W06 |
| FR-12 | R | Detail dan choropleth kecamatan memakai boundary_set dan indikator rilis sama | P0 | UC-02 | WF-081/090/091 | WF-110/118; G05,W05 |
| FR-13 | R | Sumber, locator, periode, metode, keterbatasan, release/run terlihat | P0 | UC-04 | WF-082/092/096 | WF-107/118/124; D07,W07,R03 |
| FR-14 | R | CSV sesuai seluruh hasil filter (bukan hanya halaman); kode teks dan formula aman | P1 | UC-05 tambahan | WF-099 | WF-120; W08,S05-EXPORT |
| FR-15 | R, diperjelas WBS/revisi | Login admin, otorisasi dan command review/analyze/publish/rollback/audit wajib; dashboard/review UI opsional | P0 backend, P1 UI | UC-07–12 | WF-085/086; WF-097/098 opsional | WF-114–116/120; I04–I06,S01–S05-IMPORT,S07 |
| FR-16 | R | Ranking defisit desc, rasio desc, kode asc; null tidak diberi skor 0 | P1 | UC-02 tambahan | WF-100 | WF-120; A08-RANK |
| FR-17 | U testing | Semua suite relevan mempunyai expected/actual, defect, retest dan bukti penerimaan | P0 | Semua | WF-056/102 | WF-105–128 |

## Empat opsi P1

| Item | Asumsi kerja | Alasan dan konsekuensi |
|---|---|---|
| WF-097 dashboard batch admin | Ditunda dari kandidat rilis inti | Command tetap memberi status/job/log; UI bukan prasyarat kontrol operasional |
| WF-098 layar review/publish | Ditunda dari kandidat rilis inti | Review tercatat dan publish/rollback tetap P0 lewat command terotorisasi |
| WF-099 ekspor CSV publik | Ditunda dari kandidat rilis inti | Tabel paginasi tetap P0; ekspor artefak penelitian FR-07/024 tetap wajib |
| WF-100 ranking kecamatan | Ditunda dari kandidat rilis inti | Angka defisit/detail tetap tersedia; A08-PARAM tetap wajib |

Ini default P0-first yang diajukan untuk review, bukan klaim pengguna telah menyetujui deferred. Keputusan akhir dan sumber jawaban dirangkum dalam [register scope](../WF-028/keputusan-scope-P1.md). Ketika scope dipilih, perubahan berlaku pada desain, pembangunan dan suite terkait bersama-sama.

P2 di luar rilis: routing/waktu tempuh, isochrone, rekam medis, akun publik, optimasi lokasi, prediksi, penilaian mutu, statistik klaster lanjutan. Tidak ada skor prioritas berbobot baru tanpa tujuan dan CR. Penerimaan: semua 17 FR terlacak; FR-15 dipecah sehingga P1 tidak dapat menunda pengamanan backend.
