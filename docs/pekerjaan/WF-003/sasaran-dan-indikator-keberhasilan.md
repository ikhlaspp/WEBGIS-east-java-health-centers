# Sasaran dan ukuran keberhasilan

Versi 1, 23 Oktober 2026. Target di bawah merumuskan mandat proposal dan WBS. Angka performa/UAT adalah usulan yang dibekukan pada WF-G2; kolom bukti menyatakan cara mengukur, bukan hasil yang sudah dicapai.

| ID | Sasaran dan ukuran | Cara membuktikan | Keluaran dan penerima |
|---|---|---|---|
| OBJ-01 | Master historis mempertahankan 973 kode unik di 38 kabupaten/kota, termasuk missing | Rekonsiliasi himpunan kode, kategori 616+357 dan 658+294+16+5; koreksi bersumber dicatat | Dataset, D01–D04/D10; DG dan penerima data |
| OBJ-02 | Semua kandidat/pencarian memiliki hasil review atau penghalang eksplisit; titik buffer 100% memenuhi verified facility+bukti | Rekonsiliasi antrean 565/408, bukti lokasi, anomali dan excluded count | Laporan lokasi, G01–G04; DG |
| OBJ-03 | Indikator per wilayah benar, tahun/unit/sumber terlihat | Fixture null/nol, ceil, agregat rasio 40.000; banding SQL/Python; A08-PARAM wajib | Tabel, API, A01–A08-PARAM; DG/QA |
| OBJ-04 | Peta titik, choropleth dan buffer konsisten dengan rilis/run | Uji join, radius meter, union/clip, pulau, metadata yang sama | WebGIS/HTML, G05–G11/W01–W10; QA/pengguna |
| OBJ-05 | Guest membaca published; hanya admin menjalankan operasi internal | Uji non-owner, akses draft/tulis ditolak, session dan audit | Login/command/izin, I05–I08/S01–S07; BE/QA |
| OBJ-06 | Analisis dapat dijalankan ulang dari input berhash | Dua runtime Colab bersih, lockfile/parameter, tabel identik dan geometri ekuivalen dalam toleransi | Notebook/manifest/HTML, R01–R03; reviewer penelitian |
| OBJ-07 | Antarmuka dapat dipakai pada 360/768/1366 px dan keyboard; target awal peta ≤5s, p95 warm API ≤800ms | Profil browser/jaringan/cache tetap, metrik aktual dan empty/error | Uji UI/performa; QA/penerima kebutuhan |
| OBJ-08 | Target awal ≥80% tugas UAT mandiri, tanpa salah tafsir kritis terbuka | Peserta nyata, tugas mandiri/dibantu/gagal terpisah; target jumlah awal 5 peserta | Catatan UAT; penerima UAT |
| OBJ-09 | DB dan artefak pulih pada environment terpisah; target RPO 24h/RTO 4h | Restore nyata, hash/jumlah/FK/peta/login dan waktu terukur | Runbook + S06; OP/pemilik layanan |
| OBJ-10 | Paket akademik dan operasi lengkap, akses penerima teruji | Manifest kode/data yang boleh dibagi, laporan, panduan, demo, serah akses | WF-G7/G8; penerima yang ditetapkan |

Fasilitas administratif, pasangan koordinat, lokasi verified dan lokasi eligible selalu dihitung terpisah. Cakupan penuh mensyaratkan seluruh lokasi yang diperlukan terbukti; cakupan parsial hanya boleh sesuai keputusan SRS dan harus berlabel. Tidak ada target yang membenarkan centroid palsu, null menjadi nol, atau buffer dianggap waktu tempuh. Empat P1 menambah sasaran hanya setelah dipilih; P0 tidak diturunkan karena P1 ditunda.
