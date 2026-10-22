"""Membangun tiket awal dari WBS dan rincian yang ditulis khusus per tugas.

Jalankan dari workspace: python Planning/Waterfall/bahan-tiket/susun_tiket.py
Generator menolak menimpa folder Tiket yang sudah ada agar catatan kerja tidak hilang.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import os
import re
from github_ticket_rules import POLICY, render_push_closure, closing_metadata

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
DETAILS = {}

def ticket(code, deps, artifacts, steps, verify):
    assert code not in DETAILS, code
    DETAILS[code] = {
        'dependencies': deps.split(),
        'artifacts': artifacts.split(' ; '),
        'steps': steps.split(' || '),
        'verification': verify,
    }

# Fase 1: keputusan proyek dan kendali pelaksanaan.
ticket('1.1.1', '', 'ringkasan-sumber.md ; daftar-konflik.md',
       'Baca proposal, tujuh dokumen planning, revisi.txt, dan WBS; catat versi serta lokasi bagian yang dipakai. || Pisahkan kebutuhan proposal, permintaan pengguna, dan rekomendasi implementasi dalam tabel asal kebutuhan. || Tandai konflik MySQL–Supabase, peran pengelola–admin/guest, serta sumber arsip–scraping; usulkan penyelesaian mengikuti revisi pengguna. || Daftar keputusan yang belum tersedia seperti tahun polygon, cakupan analisis, anggaran, dan tenggat tanpa mengarang jawabannya.',
       'Reviewer menelusuri setiap simpulan ke dokumen asal; admin/guest, Supabase, scraping, serta snapshot historis tidak saling bertentangan.')
ticket('1.1.2', '1.1.1', 'register-stakeholder.md ; matriks-penerima-gerbang.md',
       'Identifikasi pemilik proyek, anggota tim, dosen/penilai yang benar-benar terlibat, calon pengguna, dan pengelola hosting. || Catat nama atau posisi yang belum terisi, kepentingan, keluaran yang diterima, dan jalur koordinasi masing-masing. || Tentukan siapa meninjau teknis dan siapa berwenang menerima WF-G1 sampai WF-G8. || Konfirmasikan penugasan yang tersedia; catat posisi belum terisi sebagai keputusan terbuka sebelum gerbang terkait.',
       'Setiap gerbang memiliki pihak penerima yang dapat dihubungi; instansi/dinas tidak dianggap sudah ikut hanya karena datanya digunakan.')
ticket('1.1.3', '1.1.1 1.1.2', 'sasaran-dan-indikator-keberhasilan.md',
       'Turunkan tujuan penelitian menjadi sasaran dataset, aplikasi publik, analisis, notebook, dan laporan. || Tentukan indikator keberhasilan, cara mengukur, bukti yang diperlukan, serta penerima untuk tiap sasaran. || Pisahkan jumlah fasilitas administratif dari jumlah lokasi terpetakan dan lokasi layak analisis. || Tandai target usulan yang masih memerlukan baseline SRS dan kaitkan dengan FR/NFR planning awal.',
       'Tidak ada sasaran tanpa cara pembuktian; sasaran tidak menjanjikan cakupan penuh bila verifikasi lokasi belum diputuskan.')
ticket('1.1.4', '1.1.1 1.1.2 1.1.3', 'project-charter.md ; catatan-review-charter.md',
       'Rangkum latar belakang, tujuan, manfaat, keluaran, stakeholder, dan batas proyek. || Tuliskan asumsi tim, akses sumber, peran admin/guest, teknologi, serta pekerjaan P2 di luar scope. || Cantumkan milestone fase dan daftar keputusan terbuka beserta owner; jangan menetapkan tanggal fiktif. || Minta review pihak yang ditetapkan dan rekam koreksi serta status charter sebagai bahan WF-G1.',
       'Charter dapat dibaca mandiri dan konsisten dengan revisi pengguna; penerimaan hanya dicatat jika benar-benar diberikan.')
ticket('1.2.1', '1.1.4', 'audit-cakupan-wbs.md ; matriks-keluaran-wbs.md',
       'Petakan setiap keluaran charter ke kode tugas level 3 pada WBS. || Periksa data, scraping, keamanan, notebook, uji, deployment, serah terima, dan dukungan tercakup. || Tandai pekerjaan ganda dan jelaskan batas keluaran antartiket yang berdekatan. || Rekam koreksi WBS melalui catatan perubahan dan pertahankan pemetaan ID tiket bila judul berubah.',
       'Seluruh 160 kode memiliki satu tiket; keluaran wajib tidak memiliki celah atau dua owner yang saling menganggap pihak lain mengerjakan.')
ticket('1.2.2', '1.1.2 1.2.1', 'penugasan-pic-reviewer.md ; kapasitas-tim.md',
       'Daftar anggota aktual dan jam tersedia per minggu, termasuk kegiatan di luar proyek. || Petakan peran PM/AN/DG/BE/FE/QA/OP ke nama dan beri satu PIC utama untuk setiap tiket. || Tentukan reviewer selain pembuat untuk data/metode/keamanan dan penerima khusus untuk gerbang. || Tinjau benturan kapasitas dan tetapkan pengganti bila PIC tidak tersedia.',
       'Tidak ada tiket wajib tanpa PIC dan reviewer; peran kerja tim tidak menjadi tambahan role aplikasi.')
ticket('1.2.3', '1.2.1 1.2.2 1.2.4', 'estimasi-usaha-per-tiket.md ; jadwal-baseline.md ; catatan-jalur-kritis.md',
       'Estimasi jam orang setiap tiket berdasarkan langkah dan volume objek, terutama 565 kandidat serta 408 lokasi kosong. || Pisahkan usaha pelaksana, review, perbaikan, waktu tunggu sumber, dan biaya layanan dari durasi kalender. || Terapkan dependensi serta kapasitas aktual; hitung urutan paling awal, bottleneck, dan jalur kritis. || Susun skenario P0 dan P0+P1, cadangan risiko, serta tanggal hanya setelah target penyerahan diketahui.',
       'Total usaha dapat direkonsiliasi ke seluruh tiket yang dipilih; jadwal tidak otomatis menyalin delapan minggu atau membagi 160 tugas secara rata.')
ticket('1.2.4', '1.1.4 1.2.2', 'register-kebutuhan-sumber-daya.md ; estimasi-biaya.md',
       'Daftar kebutuhan PHP/Node/Python, hosting, Supabase, penyimpanan, geocoder, tile, dan alat uji. || Catat alat/akun yang sudah tersedia, pemilik, batas kapasitas, dan kebutuhan pemisahan test/produksi. || Verifikasi biaya dan ketentuan pada saat perencanaan dilaksanakan; simpan tanggal serta sumber penawaran. || Susun pilihan minimal dan cadangan, termasuk kebutuhan akses yang belum diberikan; jangan melakukan pembelian dalam tiket perencanaan.',
       'Setiap item memiliki tujuan, owner, asumsi biaya, dan status ketersediaan; kredensial tidak dicantumkan dalam dokumen.')
ticket('1.3.1', '1.2.1 1.2.3 1.2.4', 'register-risiko.md',
       'Identifikasi risiko perubahan halaman sumber, lisensi, tahun campuran, lokasi kosong, polygon historis, dan keterbatasan kapasitas. || Nilai kemungkinan dan dampak memakai skala yang sama serta catat pemicu yang bisa diamati. || Tetapkan tindakan pencegahan, rencana cadangan, owner, dan titik eskalasi. || Hubungkan risiko ke tiket terdampak serta cadangan usaha/jadwal yang dapat dijelaskan.',
       'Risiko koordinat dan sumber memiliki respons yang menjaga kebenaran data, bukan mengisi centroid atau mengubah tahun agar jadwal tampak selesai.')
ticket('1.3.2', '1.1.2 1.2.1 1.3.1', 'prosedur-perubahan.md ; template-change-request.md ; register-keputusan.md',
       'Definisikan perubahan kebutuhan, desain, data, target uji, dan fitur P1 yang membutuhkan pembaruan baseline. || Buat formulir alasan, alternatif, dampak tiket/biaya/jadwal, serta pihak yang memutuskan. || Tetapkan aturan versi dokumen dan hubungan keputusan dengan tiket yang dibuka kembali. || Simulasikan satu perubahan cakupan analisis penuh menjadi parsial untuk memastikan keputusan dan konsekuensinya tercatat.',
       'Contoh perubahan dapat ditelusuri dari permintaan sampai pembaruan baseline; tidak ada persetujuan otomatis karena keterlambatan.')
ticket('1.3.3', '1.2.1 1.2.2 1.3.2', 'standar-definition-of-done.md ; standar-bukti-dan-defect.md',
       'Tetapkan pola direktori bukti per tiket, nama file, versi, tanggal, serta identitas pelaksana/reviewer. || Definisikan status not_started, in_progress, blocked, in_review, done, dan deferred. || Buat format expected/actual, severity, langkah reproduksi, perbaikan, dan retest untuk defect. || Tetapkan larangan menyimpan rahasia di bukti serta aturan arsip input asli, hash, dan keputusan review.',
       'Satu contoh tiket dokumentasi dan satu contoh tiket uji dapat ditutup menggunakan standar yang sama tanpa mengarang bukti.')
ticket('1.3.4', '1.1.4 1.2.1 1.2.2 1.2.3 1.2.4 1.3.1 1.3.2 1.3.3', 'rencana-komunikasi.md ; penerimaan-WF-G1.md',
       'Tetapkan frekuensi laporan status, pembaruan risiko, rapat review, dan tempat menyimpan notulen. || Kumpulkan charter, WBS, penugasan, estimasi/jadwal, sumber daya, serta prosedur kendali versi yang telah direview. || Tinjau isu terbuka bersama penerima WF-G1 dan tetapkan owner/tenggat untuk hal yang belum selesai. || Catat keputusan accepted atau rework dengan bukti; hanya accepted membuka fase kebutuhan.',
       'Checklist WF-G1 seluruhnya terpenuhi dan identitas penerima serta tanggal keputusan nyata tersedia.')

# Fase 2: spesifikasi kebutuhan, bukan pembangunan fitur.
ticket('2.1.1', '1.3.4', 'skenario-penggunaan.md',
       'Susun alur guest menemukan fasilitas, membandingkan kecamatan, melihat radius, dan membaca sumber. || Susun alur admin mengambil sumber, memeriksa masalah data, menjalankan analisis, serta menerbitkan hasil. || Untuk setiap alur, catat pemicu, input, hasil, kondisi gagal, serta informasi yang harus terlihat. || Tinjau alur dengan pemilik kebutuhan dan catat pertanyaan yang belum diputuskan.',
       'Skenario mencakup fasilitas tanpa koordinat dan data belum lengkap serta tidak mengharuskan akun guest.')
ticket('2.1.2', '2.1.1 1.2.1', 'matriks-FR-dan-scope-rilis.md',
       'Salin FR-01 sampai FR-17 dengan asal kebutuhan dan rumuskan perilaku yang dapat diuji. || Kaitkan setiap FR dengan skenario, keluaran, dan tiket pembangunan/pengujian. || Putuskan masing-masing P1: dashboard admin, review UI, ekspor CSV, dan ranking, termasuk alasan ditunda. || Catat login admin dan command pengelolaan sebagai inti; tandai P2 di luar rilis.',
       'Tujuh belas FR tercakup dan keputusan empat tiket P1 eksplisit sebelum WF-G2.')
ticket('2.1.3', '2.1.1 2.1.2', 'matriks-hak-akses-aplikasi.md',
       'Daftar halaman, endpoint baca, command internal, operasi review, publish, dan rollback. || Isi hak guest dan admin untuk setiap operasi; guest hanya melihat rilis publik. || Tentukan login/logout admin, penanganan sesi berakhir, serta respons penolakan akses. || Bedakan role aplikasi dari runtime/worker/publisher database dan hapus kebutuhan role pengelola data.',
       'Setiap operasi tulis hanya dapat dilakukan admin melalui jalur terotorisasi; tidak ada registrasi publik yang tidak diminta.')
ticket('2.1.4', '2.1.1 2.1.2 2.1.3', 'inventaris-halaman-dan-konten.md',
       'Daftar beranda, peta, tabel, detail fasilitas/kecamatan, sumber/metode, dan login admin. || Tentukan kolom, label, satuan, periode, dan tombol minimum tiap halaman. || Definisikan hubungan navigasi serta apa yang ditampilkan ketika data kosong, layanan gagal, atau titik belum ada. || Pisahkan elemen P1 agar rancangan inti tetap dapat diterima tanpa fitur tambahan.',
       'Seluruh skenario 2.1.1 memiliki jalur halaman yang jelas dan tidak bergantung pada marker untuk mengakses fasilitas tanpa titik.')
ticket('2.2.1', '1.1.1 2.1.2', 'matriks-ketersediaan-dataset.md',
       'Baca inventaris sumber dan audit lokal tanpa mengubah berkas Archives. || Petakan berkas ke identitas fasilitas, koordinat, penduduk, luas, kode wilayah, dan polygon. || Catat angka baseline, keterbatasan audit, serta kebutuhan sumber tambahan. || Prioritaskan kekurangan yang menghalangi indikator atau peta dan tetapkan calon penanggung jawab pengadaan.',
       'Matriks membedakan data mentah, staging, dan data tervalidasi; 565 kandidat tidak disebut lokasi terverifikasi.')
ticket('2.2.2', '2.2.1', 'katalog-sumber-scraping.md ; catatan-kelayakan-sumber.md',
       'Periksa halaman/sumber primer kandidat untuk fasilitas, penduduk, luas, master kode, dan batas wilayah. || Catat format HTML/PDF/CSV/API, cakupan periode, kebutuhan akses, lisensi, dan ketentuan pengambilan. || Simpan contoh kecil yang cukup untuk menentukan parser serta apakah OCR atau paginasi diperlukan. || Tetapkan sumber utama/cadangan dan tandai sumber yang tidak dapat digunakan beserta konsekuensinya.',
       'Setiap dataset wajib memiliki jalur akuisisi yang dapat dijelaskan; pemeriksaan sampel bukan klaim batch penuh sudah berhasil.')
ticket('2.2.3', '2.2.1 2.2.2', 'kebijakan-periode-unit-identitas.md',
       'Tetapkan snapshot fasilitas 2024-S1 dan bedakan tahun observasi, publikasi, serta tanggal pengambilan. || Pilih edisi kode/polygon dan tentukan kebutuhan crosswalk jika periode sumber berbeda. || Definisikan unit penduduk, luas, koordinat, kode teks, serta aturan mempertahankan nilai mentah. || Tulis keputusan penggunaan sumber campuran, label yang wajib tampil, dan syarat indikator dinonaktifkan.',
       'Nama file tidak menjadi bukti tahun observasi dan edisi batas wilayah tidak dianggap otomatis sesuai snapshot fasilitas.')
ticket('2.2.4', '2.2.3', 'aturan-kualitas-dataset.md',
       'Tetapkan kriteria kode unik, jumlah, kelengkapan sumber/unit/tahun, serta join wilayah. || Definisikan perlakuan nilai null/nol, subtotal, alias, OCR, titik identik, dan lokasi tanpa bukti. || Tentukan apakah analisis harus penuh atau boleh parsial, beserta ukuran cakupan dan penandanya. || Tentukan kondisi blokir publikasi, daftar pengecualian yang bisa diterima, dan pihak yang memutuskan.',
       'Tidak ada aturan yang menyamakan data hilang dengan nol atau menganggap verifikasi parsial sebagai cakupan penuh.')
ticket('2.3.1', '2.2.3 2.2.4', 'katalog-indikator.md',
       'Daftar P penduduk, A luas statistik, F fasilitas administratif, dan T parameter rasio. || Tentukan kepadatan, penduduk per fasilitas, kebutuhan/defisit indikatif, serta flag tanpa fasilitas. || Tetapkan aturan null, pembagi nol, pembulatan, jumlah defisit, dan rasio agregat berbasis total. || Nyatakan metadata tahun, sumber, parameter, dan batas interpretasi yang menyertai setiap indikator.',
       'F berasal dari master administratif, bukan banyaknya marker; rasio kabupaten bukan rata-rata sederhana rasio kecamatan.')
ticket('2.3.2', '2.1.4 2.3.1', 'kebutuhan-layer-dan-legenda.md',
       'Tentukan layer titik, batas wilayah, choropleth kabupaten/kecamatan, dan buffer. || Pilih metrik, unit, kelas warna, legenda, dan perlakuan no-data/zero untuk tiap layer. || Tetapkan efek filter fasilitas terhadap marker serta efek pilihan wilayah terhadap indikator administratif. || Tentukan informasi tooltip/detail dan label kualitas lokasi yang diperlukan pengguna.',
       'Setiap warna memiliki arti tertulis; data hilang berbeda dengan nol dan perubahan skala tidak tersembunyi.')
ticket('2.3.3', '2.2.4 2.3.1', 'kebutuhan-analisis-radius.md',
       'Tetapkan radius usulan 1000, 3000, dan 5000 meter serta syarat lokasi verified pada bangunan fasilitas. || Definisikan union overlap, clipping wilayah, dan penyebut luas geometri. || Tentukan perlakuan fasilitas dekat batas, kepulauan, dan fasilitas luar provinsi yang tidak ada dalam dataset. || Nyatakan keluaran cakupan area serta informasi jumlah input/dikeluarkan yang wajib menyertainya.',
       'Radius tidak disebut waktu tempuh dan cakupan area tidak diubah menjadi persentase penduduk terlayani.')
ticket('2.3.4', '2.3.1 2.3.2 2.3.3', 'spesifikasi-keluaran-penelitian.md',
       'Daftar notebook, HTML Folium, tabel indikator, peta, screenshot, dan laporan akhir. || Tentukan metadata versi kode/rilis/run, periode, sumber, dan parameter pada setiap keluaran. || Tuliskan batas klaim yang disebabkan sumber campuran, lokasi parsial, serta radius geometris. || Tentukan cara membandingkan hasil aplikasi dengan artefak penelitian agar memakai rilis yang sama.',
       'Keluaran penelitian memiliki hubungan yang jelas ke data dan metode; laporan tidak memerlukan analisis P2.')
ticket('2.4.1', '2.1.4 2.3.2', 'baseline-performa-dan-kegunaan.md',
       'Tinjau usulan p95 API 800 ms, peta siap 5 detik, serta viewport 360/768/1366 dari planning. || Tetapkan perangkat, browser, jaringan, ukuran data, pola cache, dan jumlah pengguna untuk pengukuran. || Definisikan label form, fokus keyboard, tabel alternatif, keterbacaan legenda, serta penanganan panel mobile. || Catat target final dan alasan perubahan sebelum uji dilakukan.',
       'Setiap target mempunyai profil uji; angka usulan tidak dinyatakan sebagai hasil pengukuran.')
ticket('2.4.2', '2.1.3 2.2.4 1.2.4', 'baseline-keamanan-pemulihan-reproduksi.md',
       'Tentukan penyimpanan rahasia, hak tulis, kebutuhan audit, dan proteksi session admin. || Tetapkan data/berkas yang dibackup, retensi, owner, serta target awal RPO 24 jam dan RTO 4 jam untuk diputuskan. || Tentukan penguncian dependensi, hash input, parameter run, dan penyimpanan output yang dibutuhkan untuk reproduksi. || Sesuaikan target dengan layanan/anggaran yang tersedia dan dokumentasikan setiap keputusan.',
       'Backup DB dan artefak sama-sama tercakup; target pemulihan bisa diuji pada environment terpisah.')
ticket('2.4.3', '2.1.2 2.3.4 2.4.1 2.4.2', 'matriks-kebutuhan-pengujian.md ; strategi-UAT.md',
       'Petakan FR/NFR ke suite data, formula, spasial, backend, UI, keamanan, performa, dan reproduksi. || Susun tugas UAT untuk pencarian, perbandingan kecamatan, radius, no-data, serta sumber/versi. || Tentukan target peserta dan ukuran keberhasilan mandiri; tinjau usulan minimal lima peserta dan 80 persen tugas mandiri. || Catat cara merekam bantuan, kesalahan, waktu, serta salah tafsir kritis yang wajib diperbaiki.',
       'Seluruh FR/NFR mempunyai test atau bukti penerimaan; jumlah peserta usulan tidak dianggap peserta sudah tersedia.')
ticket('2.4.4', '2.1.1 2.1.2 2.1.3 2.1.4 2.2.1 2.2.2 2.2.3 2.2.4 2.3.1 2.3.2 2.3.3 2.3.4 2.4.1 2.4.2 2.4.3', 'SRS-baseline.md ; penerimaan-WF-G2.md ; keputusan-scope-P1.md',
       'Gabungkan kebutuhan fungsional, data, analisis, hak akses, nonfungsional, dan penerimaan ke SRS berversi. || Selesaikan keputusan yang memblokir desain, terutama sumber/periode, cakupan penuh/parsial, dan empat fitur P1. || Lakukan review konsistensi bersama penerima; tautkan matriks kebutuhan serta keputusan perubahan. || Catat accepted/rework dan identitas penerima WF-G2; fase desain hanya dibuka setelah accepted.',
       'Tidak ada kebutuhan wajib dengan kriteria penerimaan ambigu; semua P1 berstatus dipilih atau ditunda dengan alasan.')

# Fase 3: desain terperinci dan prosedur verifikasi.
ticket('3.1.1', '2.4.4', 'diagram-arsitektur.md ; alur-data.md',
       'Petakan sumber ke pengunduh, staging, kurasi, Supabase, Laravel, Leaflet, dan notebook. || Tentukan komponen yang berjalan di browser, server, worker, serta Colab. || Gambarkan alur publikasi dataset dan pembacaan rilis publik dengan release_id/analysis_run_id. || Tinjau batas data dan tanggung jawab agar browser/Colab tidak memerlukan rahasia produksi.',
       'Setiap keluaran SRS memiliki jalur komponen; tidak ada query browser langsung ke schema privat.')
ticket('3.1.2', '3.1.1 1.2.4', 'matriks-environment.md ; kebijakan-dependensi.md',
       'Daftar kebutuhan runtime aplikasi, PostgreSQL/PostGIS, Python, browser, dan build tool untuk tiap environment. || Tentukan isolasi development, test/staging, produksi, akun, database, dan penyimpanan. || Pilih mekanisme lockfile serta smoke test kompatibilitas Windows, Colab, dan hosting. || Tulis contoh nama variabel konfigurasi tanpa nilai rahasia dan cara provisioning yang akan digunakan.',
       'Uji spasial direncanakan di PostgreSQL/PostGIS, bukan hanya SQLite; data uji tidak memakai kredensial produksi.')
ticket('3.1.3', '3.1.1 3.1.2', 'desain-struktur-repositori.md ; alur-review-CI.md',
       'Bagi modul controller/service/policy, ETL, analisis, peta, notebook, dan tests. || Tetapkan direktori sumber, processed, manifest, dokumentasi, dan artefak besar di luar Git bila diperlukan. || Susun aturan commit/review, branch, pemeriksaan CI, serta strategi konfigurasi. || Tentukan kontrak integrasi antarmodul dan pemilik perubahan agar rumus tidak bercabang tanpa versi.',
       'Setiap modul mempunyai lokasi dan tanggung jawab; rahasia, cache, dan dump tidak masuk daftar berkas yang dikomit.')
ticket('3.1.4', '3.1.1 2.2.4', 'desain-job-batch.md ; matriks-error-retry.md',
       'Gambarkan status pending/running/succeeded/failed beserta transisi batch pengambilan, impor, dan analisis. || Tentukan idempotency key dari sumber/hash/versi pipeline serta checkpoint yang dapat dilanjutkan. || Tetapkan timeout, retry terbatas, penanganan rate limit, dan deteksi batch parsial. || Tentukan pesan publik, detail log internal, serta tindakan operator saat pengulangan tetap gagal.',
       'Batch gagal tidak boleh mempromosikan rilis; pengulangan tidak menambah fasilitas atau analisis duplikat secara tak terkendali.')
ticket('3.2.1', '3.1.1 2.2.3 2.3.1', 'ERD-final.md ; kamus-data-final.md',
       'Rinci tabel sumber, boundary set, kabupaten/kecamatan, alias, rilis, fasilitas, indikator, dan geocode review. || Rinci analysis run, coverage, artifacts, import batches, audit, akun, dan session. || Tetapkan tipe, nullable, identitas teks, primary/foreign key, serta metadata sumber/tahun tiap fakta. || Cocokkan kebutuhan atribut API dan laporan dengan skema tanpa menyimpan rasio lepas dari versi metodenya.',
       'Setiap fakta penelitian dapat ditelusuri ke sumber dan rilis; seluruh hubungan ERD mempunyai definisi kolom.')
ticket('3.2.2', '3.2.1', 'spesifikasi-constraint-indeks.md ; urutan-migration.md',
       'Tentukan unique key per rilis, FK wilayah/edisi, nilai nonnegatif, dan syarat verified dengan bukti lokasi. || Tetapkan validasi Point/MultiPolygon, SRID, geometri kosong, serta indeks spasial dan filter. || Urutkan pembuatan schema/extension/tabel/FK/index/grants agar dapat dijalankan dari database kosong. || Definisikan kasus insert/update yang harus ditolak serta strategi perubahan migration tanpa kehilangan data.',
       'Desain mencegah distrik boundary set lain masuk rilis dan status verified tanpa bukti yang dimiliki fasilitas terkait.')
ticket('3.2.3', '3.2.1 2.1.3 2.4.2', 'desain-otorisasi-dan-grants.md',
       'Petakan login/session/policy Laravel untuk admin dan akses baca guest. || Tentukan hak database runtime, worker, publisher, dan migration owner tanpa mengubahnya menjadi role UI. || Rancang grants/RLS, schema yang diekspos, dan jalur publikasi khusus yang tidak bisa dilewati worker. || Tulis matriks allow/deny tiap operasi serta cara mengujinya memakai koneksi non-owner.',
       'Runtime harian tidak memakai owner/BYPASSRLS; policy tidak mengasumsikan auth.uid Supabase jika identitas memakai session Laravel.')
ticket('3.2.4', '3.2.1 3.2.3 2.4.2', 'desain-lifecycle-rilis.md ; desain-backup-rollback.md',
       'Definisikan draft, validated, published, withdrawn dan validator tiap transisi. || Rancang immutability tabel rilis beserta anaknya serta pointer aktif yang berganti atomik. || Tentukan hubungan release_id, analysis_run_id, artefak, dan cache ketika publish/rollback. || Rancang backup DB/berkas, restore terpisah, retensi, dan titik pemulihan sebelum migration berisiko.',
       'Rollback memilih versi valid sebelumnya tanpa menghapus sejarah; koreksi data membentuk rilis baru.')
ticket('3.3.1', '3.1.4 2.2.2 2.2.3', 'spesifikasi-adapter-sumber.md',
       'Untuk setiap sumber, tentukan URL/parameter, periode, paginasi/daftar file, serta format parser. || Definisikan kolom wajib, penanda total, locator halaman/baris, dan cara mendeteksi schema berubah. || Tentukan aturan cache, jeda permintaan, identitas klien, retry, serta metadata unduh sesuai sumber yang dipilih. || Siapkan contoh input/output parser dan perilaku saat sumber gagal atau sebagian halaman hilang.',
       'Tidak ada adapter yang menganggap respons HTTP sukses selalu berarti dataset lengkap; sumber historis tetap terkunci periodenya.')
ticket('3.3.2', '3.3.1 2.2.4 3.2.1', 'spesifikasi-normalisasi-crosswalk.md',
       'Definisikan normalisasi spasi, angka lokal, ribuan/desimal, hektar/km², serta null versus nol. || Pisahkan field mentah dari field olahan dan tentukan identitas teks agar leading zero aman. || Rancang pencocokan wilayah dengan kode/parent/edisi dan tabel alias yang memerlukan bukti. || Susun alur keputusan Sempol–Ijen, nama kembar antar kabupaten, dan pencegahan penjumlahan penduduk dua kali.',
       'Aturan tidak menebak kode wilayah dari nama atau potongan kode fasilitas dan tidak menghapus baris hanya demi jumlah target.')
ticket('3.3.3', '3.3.1 2.2.4 3.2.1', 'prosedur-geocoding-review.md ; skema-bukti-lokasi.md',
       'Tentukan prioritas sumber koordinat resmi dan kandidat geocoder yang diizinkan untuk pekerjaan batch. || Definisikan query alamat lengkap, penyimpanan kandidat/raw response, objek provider, serta precision facility/street/village/district. || Buat aturan accepted/rejected/missing/unverified beserta bukti, alasan, reviewer, dan tanggal. || Tentukan review lima kelompok titik identik, centroid, perbatasan, serta fasilitas kepulauan.',
       'Hanya lokasi facility yang terbukti dan verified layak buffer; fallback wilayah tidak otomatis dipromosikan menjadi lokasi bangunan.')
ticket('3.3.4', '3.3.1 3.3.2 3.3.3 3.2.2', 'kontrak-staging.md ; spesifikasi-laporan-kualitas.md',
       'Definisikan header, tipe mentah, encoding, hash sumber, nomor baris, dan batch ID setiap input. || Tentukan penyimpanan baris diterima/ditolak serta alasan quarantine yang dapat diperbaiki. || Rancang rekonsiliasi total, unmapped code, tahun kosong, geometri invalid, dan kelayakan titik. || Susun syarat promosi staging dan isi manifest agar penerbit dapat menilai kualitas kandidat.',
       'Baris gagal tidak hilang diam-diam; kualitas dilaporkan per kategori dan kandidat gagal tidak mendapat status validated.')
ticket('3.4.1', '2.3.1 3.2.1', 'spesifikasi-formula.md ; contoh-acuan-formula.md',
       'Tuliskan formula lengkap, domain input, unit, dan cara agregasi dari katalog indikator. || Hitung contoh independen P=30000/30001, F=0, P=null, A=0, dan defisit nonnegatif. || Hitung contoh agregat 30000/1 dan 90000/2 yang menghasilkan rasio gabungan 40000. || Tetapkan presisi internal, pembulatan tampilan, toleransi perbandingan Python/SQL, serta parameter T per run.',
       'Expected result diturunkan dari definisi metode, bukan disalin dari fungsi implementasi yang kelak diuji.')
ticket('3.4.2', '2.3.3 3.3.3', 'spesifikasi-operasi-spasial.md',
       'Tentukan penyimpanan WGS84 dan urutan GeoJSON lon/lat versus Leaflet lat/lon. || Pilih metode buffer meter serta luas geodesik/proyeksi yang sesuai extent Jawa Timur dan pulau. || Rinci union, clip, fasilitas tetangga, serta geometri invalid/boundary dan parameter ketelitian kurva. || Tetapkan metode pembanding dan toleransi jarak/luas sebelum pengujian; bedakan luas polygon dari luas statistik.',
       'Tidak ada buffer dalam derajat yang ditafsirkan meter; overlap dan denominator cakupan memiliki definisi yang dapat diperiksa.')
ticket('3.4.3', '2.3.2 3.4.1 3.4.2', 'kontrak-layer-GeoJSON.md ; spesifikasi-kelas-warna.md',
       'Tentukan properti kode, metrik, unit, periode, sumber, dan status kelengkapan tiap feature. || Rancang join satu feature per kode dan geometri tampilan yang disederhanakan tanpa mengganti geometri analisis. || Tetapkan batas kelas, label no-data/tanpa fasilitas, dan kestabilan legenda setelah filter. || Siapkan contoh feature untuk nilai valid, nol, null, serta multipolygon pulau.',
       'Contoh JSON valid tanpa Infinity/NaN dan skema properti cukup untuk tooltip serta halaman detail.')
ticket('3.4.4', '3.4.1 3.4.2 3.4.3 2.3.4', 'desain-notebook-dan-manifest.md',
       'Bagi notebook menjadi input, validasi, mapping, indikator, buffer, visualisasi, dan ekspor. || Tentukan snapshot sanitized yang diunduh tanpa kredensial produksi dan versi modul yang digunakan. || Definisikan manifest input/output, parameter, code revision, hash, serta field nondeterministik yang dikecualikan saat membandingkan hasil. || Tentukan pesan gagal, kebutuhan koneksi internet, dan langkah Run all dari runtime kosong.',
       'Notebook dapat direproduksi tanpa langkah tersembunyi atau rumus yang berbeda dari aplikasi.')
ticket('3.5.1', '3.2.1 3.2.3 3.4.3', 'kontrak-API.md ; contoh-respons-API.json',
       'Rinci endpoint releases, regions, facilities/detail, map points/regions, statistics, buffers, dan sources. || Definisikan filter, pagination, batas q/per_page/bbox/radius, allowlist sort/metric, dan penetapan release_id. || Tulis respons sukses/error, metadata periode/coverage, serta perilaku draft/tidak ditemukan/timeout. || Cocokkan API dengan hak akses serta kebutuhan frontend dan fitur P1 terpilih.',
       'Kontrak menjaga satu rilis untuk satu sesi tampilan; fasilitas tanpa titik tetap masuk endpoint tabel.')
ticket('3.5.2', '2.1.4 3.5.1', 'wireframe-publik.md ; catatan-review-wireframe.md',
       'Buat wireframe beranda, peta dengan panel filter, tabel, dua detail, serta metode/sumber. || Buat variasi desktop dan layar kecil; tentukan ukuran/pola buka-tutup panel dan popup. || Tampilkan posisi tahun, sumber, kualitas koordinat, legenda, loading, empty, dan error. || Telusuri skenario guest di wireframe bersama reviewer dan catat perubahan yang diterima.',
       'Tidak ada skenario yang hanya dapat diselesaikan pada desktop atau membutuhkan marker untuk fasilitas missing.')
ticket('3.5.3', '3.5.1 3.5.2', 'spesifikasi-state-interaksi.md',
       'Gambarkan transisi loading/success/empty/error dan reset filter kabupaten–kecamatan. || Tentukan pembatalan/abaikan request lama agar hasil filter terbaru tidak tertimpa. || Tetapkan penyimpanan release_id sesi, perubahan rilis, retry, fallback tabel, serta pesan ketika tile gagal. || Rinci fokus keyboard, label form, akses kontrol layer, serta penutupan popup/panel.',
       'Setiap state memiliki pemicu dan tampilan; request lambat serta sesi rilis berubah mempunyai perilaku pasti.')
ticket('3.5.4', '2.1.2 2.1.3 3.5.2 3.2.4', 'wireframe-admin-dan-P1.md',
       'Rancang login/logout admin, sesi habis, kegagalan login, dan pesan akses ditolak. || Baca keputusan P1; rancang hanya dashboard batch/review/ekspor/ranking yang dipilih. || Untuk tindakan publish/rollback, tampilkan preview versi, kualitas, dan alasan keputusan. || Jelaskan padanan command P0 ketika UI P1 ditunda agar operator tetap memiliki alur kerja.',
       'Login admin inti tidak ikut ditunda bersama UI P1 dan tidak ada role pengelola baru.')
ticket('3.6.1', '3.3.4 3.4.1 3.4.2 3.2.3', 'spesifikasi-fixture.md ; expected-results.md',
       'Rinci fixture kode ganda, nama kecamatan sama, subtotal, null/nol/negatif, unit, dan angka lokal. || Rinci fixture formula batas ceil, agregat berbobot, titik overlap, centroid, batas wilayah, dan pulau. || Rinci admin/guest serta akun DB teknis, rilis draft/published, file invalid, dan respons scraping gagal. || Tentukan expected result independen dan label sintetis agar fixture tidak masuk penelitian.',
       'Kasus negatif mempunyai hasil penolakan yang jelas; peran pengelola pada fixture planning lama diganti sesuai revisi.')
ticket('3.6.2', '3.6.1 3.5.1 2.4.1 2.4.2', 'prosedur-pengujian-sistem.md',
       'Turunkan suite data/formula/spasial/API/UI/keamanan menjadi langkah input, expected, environment, dan bukti. || Tentukan akun non-owner untuk izin DB, mock sumber eksternal, serta data test terisolasi. || Rinci profil load test, pencatatan latency/payload, restore DB+artefak, dan Colab bersih. || Petakan seluruh test ID planning awal dan tambahkan pengujian scraping yang belum mempunyai ID.',
       'Prosedur dapat dijalankan tester selain penulis modul; load test tidak diarahkan ke tile/geocoder publik.')
ticket('3.6.3', '2.4.3 3.5.2 3.6.2', 'skrip-UAT.md ; checklist-gerbang-rilis.md',
       'Tuliskan instruksi tugas UAT tanpa membocorkan langkah solusi kepada peserta. || Siapkan formulir waktu, mandiri/dibantu/gagal, kesalahan, komentar, dan persetujuan partisipasi yang relevan. || Tetapkan aturan severity, retest/regresi, bukti hasil, serta target UAT sesuai SRS. || Susun checklist penerimaan data, aplikasi, akademik, P1, dan penanganan isu tertunda.',
       'Definisi lulus tidak dapat diubah sesudah melihat hasil uji tanpa perubahan baseline tercatat.')
ticket('3.6.4', '3.1.1 3.1.2 3.1.3 3.1.4 3.2.1 3.2.2 3.2.3 3.2.4 3.3.1 3.3.2 3.3.3 3.3.4 3.4.1 3.4.2 3.4.3 3.4.4 3.5.1 3.5.2 3.5.3 3.5.4 3.6.1 3.6.2 3.6.3', 'paket-desain-baseline.md ; penerimaan-WF-G3.md',
       'Kumpulkan semua desain beserta versi dan tautan sumber SRS. || Lakukan walkthrough sumber–staging–DB–API–UI–notebook dan periksa kecocokan tipe, metode, izin, serta error. || Selesaikan konflik desain atau kembalikan perubahan kebutuhan melalui change request. || Minta keputusan penerima WF-G3 dan bekukan paket accepted sebelum pembangunan produksi dimulai.',
       'Semua kebutuhan P0 dan P1 terpilih punya desain serta prosedur verifikasi; konflik yang memblokir implementasi sudah selesai.')

# Fase 4: langkah pembangunan dan pengolahan data konkret.
ticket('4.1.1', '3.6.4 3.1.3', 'catatan-inisialisasi-repo.md ; struktur-proyek.txt',
       'Periksa kondisi workspace dan perubahan yang sudah ada; pertahankan Archives dan Planning. || Inisialisasi repositori bila belum tersedia dan buat struktur modul sesuai desain yang diterima. || Pasang ignore untuk .env, dependensi terpasang, cache, dump, serta output besar; sediakan file contoh tanpa secret. || Tulis README alur kerja dan catat baseline revision; hubungkan remote hanya bila akun/tujuannya sudah ditetapkan.',
       'Daftar berkas terlacak tidak memuat rahasia atau salinan sumber yang tidak perlu; dokumen lama tetap tersedia.')
ticket('4.1.2', '4.1.1 3.1.2', 'log-setup-Laravel.md ; log-build-frontend.txt',
       'Periksa runtime PHP, Composer, Node, dan ekstensi PostgreSQL terhadap versi yang telah dipilih. || Buat aplikasi Laravel di workspace tanpa menimpa arsip/perencanaan dan pasang dependensi frontend. || Siapkan .env.example, konfigurasi lokal, route health dasar, serta proses Vite/Blade. || Jalankan aplikasi dan build production assets lokal; catat perintah, versi, serta hasilnya pada bukti.',
       'Halaman dasar merespons tanpa error dan build selesai dari dependensi terkunci; .env aktual tidak dikomit.')
ticket('4.1.3', '4.1.1 3.1.2 3.6.1', 'log-setup-Python-Colab.md ; hasil-fixture-awal.txt',
       'Buat environment Python terisolasi dan lock versi pustaka data/spasial/Folium serta test runner. || Buat kerangka notebook dengan sel instalasi/import, konfigurasi input, dan validasi awal. || Sediakan fixture sintetis kecil, termasuk satu Point dan satu MultiPolygon, pada direktori tests/data. || Jalankan import library, operasi spasial sederhana, dan satu uji fixture di lokal serta Colab.',
       'Versi dan prosedur setup dapat diulang; fixture memiliki label sintetis dan terpisah dari data penelitian.')
ticket('4.1.4', '4.1.2 4.1.3 3.1.3', 'konfigurasi-CI.md ; log-pemeriksaan-awal.txt',
       'Konfigurasikan lint, pemeriksaan Python, backend test, dan build frontend sesuai toolchain. || Sediakan database test PostgreSQL/PostGIS untuk job yang memerlukan spasial serta kredensial test terpisah. || Tentukan trigger perubahan kode dan penyimpanan ringkasan hasil tanpa rahasia. || Jalankan pipeline dengan fixture yang lulus lalu contoh kegagalan terkontrol untuk memastikan job benar-benar menghentikan proses.',
       'Pipeline lokal/CI yang tersedia mencatat exit code dan gagal saat assertion gagal; remote yang belum tersedia tidak diklaim sudah aktif.')
ticket('4.2.1', '4.1.3 3.3.1', 'log-parser-fasilitas.md ; sampel-output-fasilitas.json',
       'Implementasikan adapter unduh fasilitas periode yang disepakati dalam scripts/etl. || Parse kode, nama, alamat, kabupaten/kecamatan, layanan, dan karakter wilayah sambil mempertahankan nilai mentah. || Rekam URL, tanggal, hash, locator halaman/baris, dan file respons sumber untuk setiap batch. || Uji parser pada fixture normal, header hilang, kode kosong, dan baris total; laporkan baris yang gagal tanpa menghapusnya.',
       'Output parser sesuai kontrak staging dan dapat ditelusuri ke sumber; dataset baru tidak diam-diam mengganti snapshot 2024-S1.')
ticket('4.2.2', '4.1.3 3.3.1 4.2.1', 'log-parser-indikator.md ; sampel-output-indikator.json',
       'Implementasikan adapter tabel/file penduduk dan luas untuk setiap format sumber yang dipilih. || Ekstrak nilai, unit, tahun observasi/publikasi, wilayah, halaman/tabel, dan catatan sumber. || Gunakan OCR hanya jika teks/tabel tidak dapat diambil langsung; simpan hasil OCR serta halaman asal untuk review. || Uji angka lokal, satuan ribu jiwa/hektar, sel kosong, dan perubahan header dengan fixture.',
       'Nilai mentah, hasil parse, serta provenance tetap tersedia; tahun tidak diambil hanya dari nama file.')
ticket('4.2.3', '4.1.3 3.3.1 2.2.3', 'manifest-unduh-wilayah.json ; log-parser-wilayah.md',
       'Ambil master kode dan polygon sesuai edisi/sistem kode yang diterima pada SRS. || Tangani pagination atau daftar file sampai seluruh objek target terambil dan simpan metadata layanan. || Rekam CRS, cakupan kabupaten/kecamatan/pulau, lisensi, sumber, waktu, dan hash file. || Uji pembacaan kode sebagai teks serta MultiPolygon tanpa mengganti geometri asli.',
       'Jumlah objek dan cakupan dapat direkonsiliasi ke sumber; polygon edisi berbeda ditandai untuk harmonisasi.')
ticket('4.2.4', '4.2.1 4.2.2 4.2.3 3.1.4', 'hasil-uji-ketahanan-scraping.md',
       'Tambahkan cache respons berdasarkan identitas sumber/parameter dan checksum agar unduhan valid dapat digunakan ulang. || Terapkan retry terbatas, jeda/rate limit, timeout, dan checkpoint sesuai desain serta ketentuan sumber. || Validasi schema wajib, jumlah halaman, tanda akhir pagination, dan hasil kosong sebelum batch dianggap lengkap. || Mock timeout, 429, perubahan header, halaman duplikat, serta kegagalan tengah batch dan periksa laporan error.',
       'Tidak ada loop retry tanpa batas atau batch parsial berstatus sukses; cache tidak mencampur periode sumber.')
ticket('4.2.5', '4.2.4', 'manifest-input-mentah.json ; laporan-akuisisi-sumber.md',
       'Jalankan adapter pada sumber terpilih dengan konfigurasi rate dan periode yang telah diterima. || Rekonsiliasi seluruh file/halaman terhadap manifest target serta catat sumber yang gagal. || Bandingkan master fasilitas dan indikator dengan arsip historis, lalu catat perbedaan untuk kurasi. || Simpan snapshot input mentah berhash sebagai read-only secara prosedural dan laporkan kelengkapan sebelum ETL.',
       'Seluruh sumber wajib tersedia atau memiliki keputusan pengganti yang diterima; unduhan parsial tidak diteruskan sebagai input lengkap.')
ticket('4.3.1', '4.2.5 3.3.2 3.3.4', 'manifest-normalisasi.json ; laporan-parse-dan-reject.md',
       'Baca snapshot mentah yang dibekukan dan validasi header/encoding/hash sebelum transformasi. || Normalisasi spasi, angka lokal, tipe kode teks, dan unit sesuai aturan tanpa menimpa field raw. || Simpan source row, batch, nilai sebelum/sesudah, serta alasan setiap konversi yang bermakna. || Pisahkan baris gagal ke quarantine dan hasil normalisasi ke staging; hitung jumlah input/diterima/ditolak.',
       'Input sama menghasilkan konten normalisasi sama; jumlah baris dapat direkonsiliasi dan null tetap berbeda dari nol.')
ticket('4.3.2', '4.3.1 4.2.3 3.3.2', 'crosswalk-terreview.json ; keputusan-alias-wilayah.md',
       'Bangun master kabupaten/kecamatan dari kode resmi dan parent sesuai edisi. || Cocokkan nama mentah dalam konteks kabupaten dan sumber; gunakan antrean rekonsiliasi sebagai input, bukan bukti mapping benar. || Telusuri kasus Sempol–Ijen serta alias lain ke sumber historis dan simpan keputusan reviewer. || Terapkan hanya mapping approved; laporkan unmatched, konflik many-to-one, dan risiko penggandaan indikator.',
       'Semua fasilitas kandidat publik memiliki satu wilayah resmi; nama sama lintas kabupaten tidak tergabung dan perubahan nama mempunyai bukti.')
ticket('4.3.3', '4.3.1 4.3.2', 'rekonsiliasi-master-fasilitas.md ; daftar-perbedaan-master.json',
       'Pisahkan detail, subtotal kabupaten, dan total provinsi dengan aturan yang dapat diulang. || Cocokkan kode/atribut master CSV, salinan workbook, sumber fasilitas, serta tabel koordinat. || Rekonsiliasi 973 fasilitas historis, 38 kabupaten/kota, kategori layanan dan karakteristik terhadap audit awal. || Catat koreksi bersumber; pertahankan fasilitas tanpa titik dan wilayah tanpa fasilitas dalam master wilayah.',
       '39 baris agregat tidak ikut penjumlahan detail pada sumber baseline; setiap selisih dari 973 mempunyai keputusan, bukan dihapus diam-diam.')
ticket('4.3.4', '4.3.1 4.3.2 2.2.3', 'laporan-verifikasi-indikator.md ; keputusan-nilai-indikator.json',
       'Susun checklist nilai berisiko dari lima wilayah OCR dan sumber luas alternatif dalam audit. || Bandingkan nilai per kecamatan dengan halaman/tabel asli dan simpan locator serta hasil reviewer. || Periksa tahun observasi, satuan jiwa/ribu jiwa dan hektar/km²; simpan konversi dan sumber yang diterima. || Rekonsiliasi total dengan presisi sumber, pertahankan null, dan jelaskan selisih tanpa memaksa angka agar cocok.',
       'Setiap nilai terisi mempunyai tahun/unit/sumber; Sempol atau indikator lain yang belum terbukti tidak diisi nol.')
ticket('4.3.5', '4.2.3 4.3.2 3.4.2', 'laporan-validasi-polygon.md ; manifest-geometri.json',
       'Periksa CRS, tipe, geometri kosong/invalid, duplikat kode, dan parent seluruh polygon. || Cocokkan himpunan kode polygon dengan master wilayah dan catat yang hilang/berlebih. || Tinjau pulau dan batas wilayah secara visual; setiap perbaikan geometri disimpan bersama versi sebelum/sesudah. || Buat geometri display yang disederhanakan terpisah dan periksa tidak hilang feature/pulau yang diperlukan.',
       'Tidak ada unmatched/duplicate yang tidak diselesaikan untuk cakupan SRS; luas statistik tidak dipakai menggantikan geometri.')
ticket('4.4.1', '4.3.3 4.3.5 3.3.3', 'antrean-review-lokasi.json ; log-setup-geocoder.md',
       'Buat antrean per kode fasilitas berisi kandidat lama, alamat, wilayah, dan status awal. || Implementasikan query/cache geocoder sesuai provider terpilih; simpan query, respons, objek, waktu, dan precision. || Siapkan formulir bukti, alasan accepted/rejected, reviewer, tanggal, serta penanda kandidat centroid. || Gunakan file review lokal terstruktur sesuai desain; impor ke geocode_reviews dilakukan kemudian pada 4.5.5.',
       '565 kandidat dan 408 missing terwakili tanpa dianggap verified; pekerjaan review tidak bergantung pada DB yang belum dibangun.')
ticket('4.4.2', '4.4.1', 'review-565-kandidat.json ; ringkasan-review-kandidat.md',
       'Bagi antrean 565 kandidat menurut kabupaten dan tetapkan reviewer untuk setiap batch. || Untuk setiap kode, cocokkan nama/alamat/posisi dengan bukti lokasi fasilitas yang dapat dilacak. || Catat status, precision, sumber, alasan, reviewer, dan tanggal; kandidat yang belum terbukti tetap unverified. || Rekonsiliasi jumlah seluruh keputusan terhadap daftar awal dan kirim konflik/titik identik ke 4.4.4.',
       'Seluruh 565 kandidat mempunyai hasil review atau penghalang eksplisit; jumlah verified hanya menghitung bukti facility yang diterima.')
ticket('4.4.3', '4.4.1 4.4.2', 'penelusuran-408-missing.json ; ringkasan-lokasi-missing.md',
       'Gunakan daftar awal 408 kode missing; cari koordinat resmi lebih dulu lalu sumber kandidat terpilih. || Jalankan query alamat lengkap secara terkendali dan catat hasil kosong maupun kandidat yang ditemukan. || Review bukti facility sebelum menerima koordinat; jangan memakai pusat desa/kecamatan sebagai pengganti bangunan. || Catat seluruh keputusan dan kasus yang belum terselesaikan untuk penentuan cakupan analisis.',
       '408 kode memiliki catatan penelusuran; pencarian selesai tidak disamakan dengan 408 lokasi berhasil diverifikasi.')
ticket('4.4.4', '4.4.2 4.4.3 4.3.5', 'keputusan-anomali-lokasi.md ; review-lokasi-final.json',
       'Periksa lima pasangan titik identik baseline dan seluruh anomali tambahan yang ditemukan. || Tinjau titik di luar wilayah, tepat pada boundary, kepulauan, dan indikasi centroid memakai bukti alamat/lokasi. || Tentukan koordinat terpilih dan alasan, atau pertahankan status belum layak; jangan otomatis memindahkan titik ke polygon. || Cocokkan pilihan review ke kode fasilitas dan pastikan fasilitas berbeda tetap dipertahankan meski titiknya sama.',
       'Setiap anomali mempunyai keputusan berbukti; data tidak dideduplicate hanya berdasarkan koordinat.')
ticket('4.4.5', '4.4.4 4.3.4 4.3.5 2.2.4', 'laporan-kualitas-data-final.md ; manifest-titik-layak-buffer.json',
       'Hitung jumlah registered, paired, verified, missing, unverified, rejected, dan eligible per wilayah. || Validasi syarat verified+precision facility+bukti/reviewer untuk setiap titik analisis. || Bandingkan cakupan yang tersedia dengan SRS serta daftar indikator yang harus dibatasi/dinonaktifkan. || Bekukan kandidat data dan daftar pengecualian; bila cakupan tidak memenuhi SRS, blokir promosi sampai perbaikan atau perubahan scope diterima.',
       'Jumlah input dan dikeluarkan dapat direkonsiliasi ke 973 fasilitas; analisis parsial dilabeli dan diterima secara eksplisit bila digunakan.')
ticket('4.5.1', '4.1.2 3.2.1 3.1.2', 'log-provisioning-DB-dev-test.md',
       'Siapkan Supabase/PostgreSQL development dan test yang terisolasi sesuai akun/anggaran yang disediakan. || Aktifkan PostGIS, catat schema extension serta versi database, dan konfigurasi koneksi server ber-SSL. || Simpan credential di environment, pilih pool/koneksi sesuai desain, dan uji koneksi PDO. || Jalankan kueri versi serta konstruksi titik sederhana di kedua environment dan simpan log tanpa password.',
       'DB test bukan produksi; koneksi spasial bekerja dengan konfigurasi yang terdokumentasi.')
ticket('4.5.2', '4.5.1 3.2.2', 'log-migration-kosong.md ; hasil-constraint-dasar.md',
       'Implementasikan migration schema/tabel/FK/index sesuai kamus data final dengan satu sistem migration. || Tambahkan constraint rilis, boundary set, identitas, nilai, status titik, serta relasi review yang benar. || Buat indeks GiST dan indeks pencarian/filter yang dirancang; seed hanya kategori/fixture yang sesuai environment. || Bangun DB test kosong, jalankan migration, dan coba insert valid serta contoh pelanggaran constraint.',
       'Skema dapat direkonstruksi tanpa langkah SQL tersembunyi; duplikat, FK salah, dan verified tanpa bukti ditolak.')
ticket('4.5.3', '4.5.2 3.2.3 3.2.4', 'matriks-grants-aktual.md ; log-uji-role-DB.md',
       'Buat akun teknis runtime/worker/publisher dan grants minimum sesuai desain. || Terapkan RLS/jalur baca publik serta batasi schema Data API yang tidak diperlukan. || Lindungi rilis published beserta anaknya dari perubahan runtime/worker dan batasi transisi publish. || Uji allow/deny dengan setiap role non-owner termasuk anon/authenticated bila jalurnya tersedia.',
       'Staging/draft tidak terbaca publik dan runtime bukan owner; uji tidak hanya menggunakan service/owner yang melewati policy.')
ticket('4.5.4', '4.5.3 3.3.4', 'log-uji-impor-idempotent.md ; contoh-laporan-error-impor.json',
       'Buat command/job impor yang memeriksa jenis file, ukuran, header, hash, dan kontrak staging. || Implementasikan urutan sumber–wilayah–alias–draft–indikator–fasilitas–review dengan transaksi yang sesuai. || Simpan accepted/rejected count, error per baris, dan batch status; jangan lanjut jika referensi gagal. || Uji impor valid, ulang batch sama, file invalid, dan kegagalan tengah proses tanpa mengubah rilis terbit.',
       'Impor ulang tidak menggandakan fasilitas dan kegagalan tidak meninggalkan kandidat seolah siap publish.')
ticket('4.5.5', '4.5.4 4.4.5 4.3.3 4.3.4 4.3.5', 'manifest-kandidat-dataset.json ; rekonsiliasi-pasca-impor.md',
       'Tetapkan release_id draft untuk snapshot kurasi yang sudah dibekukan. || Jalankan impor sumber, boundary, crosswalk, indikator, fasilitas, dan review sesuai urutan FK. || Bandingkan jumlah/kode/kategori/hash, tahun/sumber, serta eligible point antara berkas kurasi dan DB. || Simpan laporan kualitas dan jangan mempublikasikan kandidat sebelum analisis serta gerbang uji selesai.',
       'Kandidat DB sesuai manifest kurasi dan semua referensi berada pada edisi wilayah/rilis yang tepat.')
ticket('4.6.1', '4.5.5 3.4.1', 'hasil-unit-indikator.md ; contoh-output-indikator.json',
       'Implementasikan perhitungan P/A, P/F, rasio fasilitas, ceil kebutuhan, defisit, dan flag tanpa fasilitas. || Pisahkan data sumber dari nilai turunan dan simpan parameter T serta versi metode. || Tangani null, P=0, F=0, A tidak positif, dan pembulatan tampilan sesuai spesifikasi. || Jalankan fixture expected result independen sebelum menggunakan dataset kandidat.',
       'Tidak ada Infinity/NaN, defisit negatif, atau pengurangan F administratif akibat missing koordinat.')
ticket('4.6.2', '4.6.1', 'hasil-unit-agregasi.md ; ringkasan-agregat-kandidat.json',
       'Kelompokkan fasilitas/penduduk menurut kode kabupaten dan provinsi pada rilis sama. || Hitung rasio dari total P/F dan defisit sesuai penjumlahan defisit kecamatan yang ditetapkan. || Hitung cakupan kelengkapan indikator; jangan menganggap total lengkap bila ada kecamatan null. || Bandingkan contoh agregat berbobot dan pastikan filter layanan marker tidak mengubah indikator administratif tanpa label terpisah.',
       'Contoh P 30000+90000 dan F 1+2 menghasilkan rasio 40000; cakupan input terlihat pada setiap agregat.')
ticket('4.6.3', '4.6.1 4.4.5 3.4.2', 'manifest-buffer-per-titik.json ; hasil-unit-radius.md',
       'Ambil hanya titik eligible dari release_id kandidat dan catat seluruh titik dikeluarkan. || Bangun buffer 1000/3000/5000 meter dengan metode serta ketelitian yang dibekukan. || Simpan radius, CRS/metode, parameter, versi kode, dan jumlah input sebagai analysis run. || Uji jarak pusat ke batas buffer pada fixture dan beberapa lokasi termasuk pulau.',
       'Radius dalam toleransi desain; tidak ada buffer centroid atau koordinat belum verified.')
ticket('4.6.4', '4.6.3 4.3.5', 'hasil-unit-union-clip.md ; hasil-cakupan-kandidat.json',
       'Union buffer agar area overlap hanya dihitung sekali. || Untuk tiap wilayah, gunakan seluruh fasilitas relevan dalam dataset sebelum clip, termasuk tetangga lintas kabupaten. || Hitung luas intersection dan luas geometri wilayah dengan metode konsisten lalu coverage persen. || Uji overlap, wilayah kosong, multipolygon, boundary, serta toleransi floating point; catat keterbatasan luar provinsi.',
       'Luas covered tidak melebihi penyebut dalam toleransi; cakupan tidak memakai luas statistik atau rata-rata persentase kecamatan.')
ticket('4.6.5', '4.6.2 4.6.4 3.4.3', 'manifest-analysis-run.json ; laporan-validasi-layer.md',
       'Simpan indikator, coverage, dan metadata run dengan FK yang sesuai release/boundary. || Hasilkan GeoJSON display berisi kode, metrik, unit, sumber, no-data, dan informasi kelengkapan. || Daftarkan artefak beserta hash dan pastikan geometri penuh analisis tidak digantikan versi display. || Jalankan unit/formula/spatial checks dan hanya tandai run succeeded jika semua validator lewat.',
       'Setiap tabel/layer dapat ditelusuri ke rilis dan run yang sama; gagal validasi tidak menghasilkan run sukses.')
ticket('4.7.1', '4.5.5 4.5.3 3.5.1', 'hasil-uji-API-referensi.md ; contoh-respons-referensi.json',
       'Buat endpoint rilis publik, pilihan wilayah bertingkat, dan katalog sumber. || Pastikan query runtime hanya membaca published dan boundary/source yang dirujuk rilis tersebut. || Sertakan release_id, periode, kualitas, dan metadata respons sesuai kontrak. || Uji parent wilayah, rilis tidak ditemukan/draft, serta keadaan belum ada rilis publik menggunakan fixture test.',
       'Guest tidak dapat menebak ID draft untuk memperoleh metadata internal; pilihan kecamatan sesuai kabupaten dan edisi rilis.')
ticket('4.7.2', '4.7.1 3.5.1', 'hasil-uji-API-fasilitas.md ; contoh-respons-fasilitas.json',
       'Implementasikan daftar dan detail fasilitas berdasarkan kode dan release_id. || Tambahkan pencarian nama/kode/alamat, filter kabupaten/kecamatan/layanan/karakter/status titik, dan pagination. || Validasi panjang q, batas per_page, parent filter, sort allowlist, dan parameter tak dikenal. || Uji fasilitas missing, kode ganda antar rilis, hasil kosong, serta input injeksi memakai query terparameterisasi.',
       'Jumlah tabel dan detail benar untuk rilis/filter; missing koordinat tidak menyebabkan identitas fasilitas menghilang.')
ticket('4.7.3', '4.7.1 4.6.5 3.5.1', 'hasil-uji-API-peta-statistik.md ; catatan-cache.md',
       'Implementasikan statistik, GeoJSON titik/polygon, dan pembacaan buffer hasil run publik. || Terapkan bbox/metric/radius allowlist serta penolakan run yang tidak cocok dengan rilis. || Susun cache key dari rilis, run, filter, metrik, dan detail geometri. || Uji konsistensi endpoint dan pemisahan filter marker dari rasio administratif; jangan memanggil Colab/geocoder dalam request peta.',
       'Semua respons satu tampilan memakai versi sama dan hasil batch dibaca tanpa menghitung ulang seluruh polygon setiap request.')
ticket('4.7.4', '4.1.2 4.5.3 3.2.3', 'hasil-uji-session-admin.md ; matriks-otorisasi-aktual.md',
       'Buat login/logout admin dengan mekanisme session Laravel dan provisioning akun internal yang terkontrol. || Terapkan middleware/policy, proteksi CSRF pada aksi web, rate limit login, serta konfigurasi cookie/session. || Hubungkan identitas admin ke command/operasi internal sesuai jalur yang dirancang tanpa mengungkap credential publisher. || Uji guest, sesi expired, login gagal, logout, dan percobaan mengubah role lewat input profil.',
       'Tidak ada registrasi publik atau role pengelola data; guest tidak dapat melakukan aksi tulis atau memperoleh data draft.')
ticket('4.7.5', '4.7.4 4.5.4 4.6.5 3.2.4', 'panduan-command-admin.md ; hasil-uji-lifecycle-rilis.md',
       'Implementasikan command terotorisasi untuk review, menjalankan analisis, validasi kandidat, publish, dan rollback. || Periksa mutu data, run/artefak, dan status review sebelum transisi publikasi. || Lakukan publish/pointer update secara atomik serta catat actor, alasan, versi, dan before/after yang relevan. || Uji penolakan kandidat gagal, publish ulang, rollback versi lama, serta larangan mengubah rilis published; gunakan DB test.',
       'Siklus pengelolaan P0 dapat dijalankan tanpa UI P1; audit tidak menyimpan password/token dan cache mengikuti rilis aktif.')
ticket('4.8.1', '4.7.1 4.7.3 3.5.2', 'bukti-dashboard-responsif.md',
       'Bangun layout Blade/CSS/JS, navigasi, dan beranda berbahasa Indonesia. || Tampilkan total fasilitas, jumlah terpetakan/verified/missing, ringkasan wilayah, dan periode sumber. || Hubungkan kartu statistik ke API dengan satu release_id yang dipertahankan selama tampilan. || Periksa 360/768/1366 px dan keadaan belum ada rilis atau API gagal.',
       'Kartu tidak menyebut jumlah marker sebagai jumlah fasilitas total; label periode dan kualitas tidak terpotong di layar kecil.')
ticket('4.8.2', '4.8.1 4.7.3', 'bukti-peta-marker-cluster.md',
       'Pasang Leaflet, tile provider terpilih, atribusi, kontrol zoom/layer, serta marker cluster. || Ubah koordinat GeoJSON ke pemanggilan LatLng dengan urutan yang benar. || Buat popup berisi identitas aman, layanan, status lokasi, dan tautan detail. || Uji cluster, dua fasilitas bertitik sama, pulau, dan missing; missing ditampilkan lewat tabel tanpa marker pengganti.',
       'Semua identitas fasilitas bertitik sama tetap dapat diakses dan teks popup berbahaya tidak dieksekusi sebagai script.')
ticket('4.8.3', '4.8.2 4.7.2 3.5.3', 'bukti-pencarian-filter.md',
       'Bangun pencarian serta pilihan kabupaten–kecamatan, layanan, karakter wilayah, dan kualitas koordinat. || Reset pilihan anak saat parent berubah serta sediakan tombol reset seluruh filter. || Sinkronkan parameter daftar/marker, tampilkan jumlah hasil, dan pertahankan release_id. || Tangani empty/error dan request lambat; abaikan respons lama ketika filter berubah cepat.',
       'Daftar/marker cocok dengan filter aktif dan pilihan kecamatan tidak tersisa dari kabupaten sebelumnya.')
ticket('4.8.4', '4.8.3 4.6.5 4.7.3', 'bukti-choropleth-buffer.md',
       'Tambahkan layer kabupaten/kecamatan dan pemilihan metrik sesuai kontrak GeoJSON. || Render kelas warna, unit, no-data, dan tooltip; pertahankan legenda yang jelas saat filter berubah. || Tambahkan pilihan radius yang tersedia dari analysis run dan tampilkan jumlah input serta batas cakupan. || Uji nilai nol/null, tanpa fasilitas, overlap, perpindahan layer, dan perbedaan filter marker versus indikator administratif.',
       'Legenda dan data konsisten; buffer tidak dinarasikan sebagai waktu tempuh atau persentase penduduk terlayani.')
ticket('4.8.5', '4.8.3 4.7.2 4.7.3', 'bukti-tabel-detail.md',
       'Buat tabel fasilitas dengan pagination, pencarian/filter konsisten, dan tautan detail. || Buat detail fasilitas dengan alamat, kode, layanan, sumber, serta status lokasi. || Buat detail kecamatan dengan indikator, tahun masing-masing sumber, kualitas data, dan daftar fasilitas. || Uji fasilitas tanpa titik, F=0, indikator null, link tidak ditemukan, serta akses keyboard.',
       'Guest tetap dapat melihat alamat fasilitas missing dan membedakan tanpa fasilitas dari data belum lengkap.')
ticket('4.8.6', '4.8.1 4.8.2 4.8.3 4.8.4 4.8.5 3.5.3', 'bukti-state-UI-dan-metode.md',
       'Bangun halaman sumber/metodologi dengan formula, periode, versi, cakupan, dan keterbatasan analisis. || Seragamkan loading/error/empty, retry, fallback tabel, serta pesan tile/API gagal pada seluruh layar. || Periksa label form, urutan fokus, navigasi keyboard, penutupan popup/panel, dan layar kecil. || Simulasikan request lama dan kegagalan jaringan untuk memastikan pesan akurat serta state tidak tertinggal.',
       'Sumber/versi mudah ditemukan dan kegagalan layanan tidak meninggalkan layar kosong atau statistik dari rilis berbeda.')
ticket('4.9.1', '4.6.5 3.4.4 4.1.3', 'manifest-input-notebook.json ; log-validasi-snapshot.md',
       'Ekspor snapshot kandidat yang disanitasi dengan release_id dan analysis_run_id. || Hubungkan sel input notebook ke snapshot berhash dan konfigurasi parameter yang eksplisit. || Validasi schema, periode, referensi wilayah, dan eligible point sebelum analisis. || Coba input salah hash/tidak lengkap dan pastikan notebook berhenti dengan pesan spesifik.',
       'Notebook tidak memerlukan password produksi dan tidak melanjutkan analisis saat input gagal validasi.')
ticket('4.9.2', '4.9.1 4.6.1 4.6.2 4.6.3 4.6.4', 'log-integrasi-modul-notebook.md',
       'Panggil modul perhitungan/analisis berversi dari notebook alih-alih menyalin formula tanpa kendali. || Tampilkan parameter T, radius, CRS/metode, ketelitian, dan jumlah data yang digunakan. || Jalankan fixture formula/spasial lalu kandidat snapshot dengan urutan sel yang dirancang. || Bandingkan ringkasan output terhadap hasil backend/run dan jelaskan selisih dalam toleransi.',
       'Definisi indikator, input titik, dan cara agregasi sama dengan aplikasi; notebook tidak bergantung pada variabel sisa sesi sebelumnya.')
ticket('4.9.3', '4.9.2 3.4.3', 'manifest-ekspor-Folium.json ; bukti-HTML-kandidat.md',
       'Bangun Folium marker/cluster, polygon tematik, buffer, legenda, dan popup dari snapshot yang sama. || Sertakan sumber, tahun, release_id, run, jumlah lokasi layak, serta batas interpretasi. || Ekspor HTML dan tabel hasil ke direktori rilis berversi tanpa raw response/secret internal. || Buka HTML hasil ekspor dan periksa jumlah, layer, legenda, serta tautan yang diperlukan.',
       'HTML dapat digunakan sesuai kebutuhan internet yang dijelaskan dan tidak memakai angka atau legenda dari rilis lain.')
ticket('4.9.4', '4.9.3 3.4.4', 'panduan-Run-all.md ; manifest-output-notebook.json',
       'Tambahkan metadata versi paket, code revision, parameter, hash input/output, dan timestamp run. || Tulis langkah membuka runtime bersih, memasang dependensi, menyediakan snapshot, Run all, dan mengambil hasil. || Jelaskan tile/CDN yang memerlukan internet serta ketentuan bila demo offline dipilih. || Minta anggota lain mengikuti panduan sampai artefak terbentuk dan catat bagian yang perlu diperjelas.',
       'Tidak ada langkah tersembunyi atau rahasia dalam notebook/HTML; konten deterministik dapat dibandingkan tanpa terpengaruh timestamp.')
ticket('4.10.1', '2.4.4 4.7.4 4.7.5 3.5.4', 'bukti-dashboard-admin-P1.md',
       'Baca keputusan scope WF-G2; jika tidak dipilih, catat deferred dan alasan sebelum menjalankan pembangunan. || Bangun layar admin untuk memulai job scraping/impor/analisis yang diizinkan oleh backend. || Tampilkan status, waktu, jumlah diterima/ditolak, dan error yang aman tanpa credential. || Uji izin guest, klik ganda, kegagalan job, dan retry agar UI tidak melewati validator backend.',
       'Jika dipilih, dashboard menjalankan layanan P0 yang sama dan guest ditolak; jika ditunda, keputusan scope menjadi bukti, bukan klaim fitur lulus.')
ticket('4.10.2', '2.4.4 4.10.1 4.7.5 3.5.4', 'bukti-review-publish-UI-P1.md',
       'Baca keputusan scope; tandai deferred bila layar review tidak termasuk rilis. || Bangun antrean masalah mapping/koordinat dengan kandidat, bukti, dan alasan keputusan. || Tambahkan preview kualitas rilis, publish, rollback, dan riwayat audit melalui endpoint terotorisasi. || Uji kandidat tidak valid, aksi ulang, konflik versi, serta guest yang mencoba operasi admin.',
       'Jika dipilih, keputusan UI tercatat dengan actor dan rilis tepat serta tidak dapat mengubah published di tempat; dependensi dashboard yang ditunda harus diputuskan ulang bila diperlukan.')
ticket('4.10.3', '2.4.4 4.7.2 4.8.5', 'bukti-ekspor-CSV-P1.md ; sampel-ekspor-aman.txt',
       'Periksa keputusan scope ekspor; catat deferred bila tidak dipilih. || Implementasikan endpoint ekspor mengikuti filter dan release_id daftar, termasuk data di luar halaman aktif. || Pertahankan identitas teks/tahun/unit dan netralkan sel string berawalan pemicu formula spreadsheet. || Bandingkan jumlah/kode hasil ekspor dengan seluruh hasil query serta uji teks khusus, Unicode, dan rilis draft.',
       'Jika dipilih, ekspor tidak hanya menyalin satu halaman dan tidak membocorkan draft; formula injection ditangani tanpa mengubah arti atribut sumber.')
ticket('4.10.4', '2.4.4 4.6.1 4.6.2 4.8.5', 'bukti-prioritas-kecamatan-P1.md',
       'Periksa keputusan scope ranking; catat deferred bila tidak dipilih. || Susun urutan defisit menurun, rasio sesuai definisi, dan kode wilayah sebagai tie-breaker stabil. || Pisahkan kecamatan input null/tanpa fasilitas dengan status yang jelas dan tampilkan definisi urutan. || Uji nilai sama, F=0, input tidak lengkap, serta perubahan parameter T yang membentuk run baru.',
       'Jika dipilih, hasil dapat dihitung ulang dari indikator; data null tidak diberi skor nol atau diperingkat sebagai hasil pasti.')
ticket('4.11.1', '4.5.5 4.6.5 4.7.5 4.8.6 4.9.4 4.10.1 4.10.2 4.10.3 4.10.4', 'matriks-integrasi-rilis.md ; log-alur-end-to-end.md',
       'Periksa seluruh P0 dan keputusan setiap P1; hanya fitur terpilih yang harus tersedia di kandidat. || Hubungkan hasil kurasi, impor, run, API, UI, dan HTML menggunakan satu rilis kandidat. || Jalankan alur admin dari kandidat ke published pada staging lalu telusuri sebagai guest. || Cocokkan kode/jumlah/tahun/rilis pada dataset, response, tampilan, dan artefak; daftar setiap ketidaksesuaian untuk perbaikan.',
       'Tidak ada komponen mengambil rilis berbeda secara diam-diam; deferred P1 tidak memblokir integrasi bila keputusannya sah.')
ticket('4.11.2', '4.11.1 3.6.1', 'laporan-unit-component-final.md',
       'Inventarisasi modul yang berubah dan kaitkan ke parser, formula, geometri, izin, impor, serta lifecycle rilis. || Lengkapi unit/component test pada perilaku berisiko memakai fixture acuan independen. || Jalankan suite pada dependency lock dan DB test yang digunakan kandidat. || Perbaiki kegagalan, jalankan ulang bagian terdampak, dan simpan revision serta hasil aktual.',
       'Suite relevan lulus tanpa menonaktifkan assertion agar hijau; hasil terkait revision kandidat yang sama.')
ticket('4.11.3', '4.11.2', 'laporan-smoke-staging.md ; daftar-defect-integrasi.md',
       'Pasang kandidat di staging yang konfigurasinya mewakili target deployment. || Uji login/admin command, beranda, peta, filter, detail, sumber, dan HTML dengan satu rilis. || Rekam error console/server, response gagal, serta mismatch data sebagai defect berowner. || Perbaiki kegagalan penghalang dan retest alur terdampak sampai kandidat bisa diuji sistem secara utuh.',
       'Tidak ada kegagalan dasar yang mencegah suite sistem dijalankan; isu minor tetap dicatat, bukan disembunyikan.')
ticket('4.11.4', '4.11.1 4.11.2 4.11.3 4.4.5', 'manifest-kandidat-uji.json ; penerimaan-WF-G4.md',
       'Bekukan revision, lockfile, release_id, run, hash dataset/artefak, serta konfigurasi staging. || Kumpulkan bukti unit/component/smoke dan laporan kualitas data terhadap SRS. || Periksa seluruh pekerjaan fase 4 termasuk status empat P1 serta isu yang dapat memblokir uji. || Rekam keputusan penerima WF-G4; perubahan kandidat setelah diterima harus mempunyai versi baru dan jejak retest.',
       'Kandidat dapat direproduksi dan semua prasyarat uji sistem tersedia sebelum fase 5 dibuka.')

# Fase 5: setiap tiket menghasilkan laporan aktual, bukan hanya daftar skenario.
ticket('5.1.1', '4.11.4 3.6.2', 'hasil-uji-scraping-SC01-SC06.md ; log-simulasi-sumber.txt',
       'Siapkan fixture SC01 timeout, SC02 rate limit, SC03 halaman kosong, SC04 schema berubah, SC05 pagination terputus, dan SC06 cache/retry. || Jalankan masing-masing terhadap adapter dengan sumber eksternal dimock dan parameter batch terkontrol. || Periksa status batch, jumlah accepted/rejected, batas retry, penggunaan cache, serta pesan kesalahan. || Catat expected/actual dan defect; pastikan input parsial tidak masuk jalur publikasi.',
       'SC01–SC06 lulus sesuai kontrak; sumber eksternal tidak dibebani untuk mensimulasikan kegagalan atau load.')
ticket('5.1.2', '4.11.4 4.3.3 4.5.5', 'hasil-uji-D01-D04-D10.md ; hasil-query-rekonsiliasi.txt',
       'Pilih snapshot kandidat dan jalankan pemeriksaan kode kosong/duplikat serta kesamaan himpunan master dan koordinat. || Hitung 973 fasilitas, 38 kabupaten/kota, layanan 616+357, dan karakteristik 658+294+16+5 pada baseline historis. || Uji 665 detail dan 39 agregat pada CSV audit, lalu buktikan total detail 973 tanpa menjumlah subtotal. || Cocokkan CSV/XLSX/sumber primer dan kaitkan setiap koreksi sah ke bukti kurasi.',
       'D01–D04/D10 lulus; perbedaan yang diterima harus berjejak keputusan sumber, bukan mengubah expected tanpa alasan.')
ticket('5.1.3', '4.11.4 4.3.2 4.3.4 4.3.5', 'hasil-uji-D05-D09.md ; bukti-pemeriksaan-nilai.md',
       'Uji nama kecamatan sama di dua kabupaten dan alias Sempol–Ijen terhadap crosswalk approved. || Bandingkan himpunan kode master/polygon/fakta serta kelengkapan seluruh wilayah target. || Audit tahun, unit, locator, nilai OCR, sumber luas alternatif, dan konversi hektar. || Uji null, nol, negatif, dan angka lokal; simpan bukti per kasus beserta input/output.',
       'D05–D09 lulus; jumlah kecamatan tidak dipaksa dengan menghapus baris dan nilai hilang tidak menjadi nol.')
ticket('5.1.4', '5.1.1 5.1.2 5.1.3', 'hasil-uji-D11-dan-manifest.md ; perbandingan-run-ETL.json',
       'Bekukan input/hash/versi pipeline lalu jalankan ETL dua kali pada lingkungan test bersih atau batch idempotent. || Bandingkan konten output, jumlah/kode, mapping, sumber, dan hash dengan field nondeterministik ditangani eksplisit. || Ulang impor hasil yang sama dan periksa tidak ada penambahan fasilitas/observasi. || Catat perbedaan aktual serta defect dan simpan manifest kedua run.',
       'D11 lulus dan provenance tetap utuh; timestamp baru tidak disalahartikan sebagai perubahan data substansial.')
ticket('5.2.1', '4.11.4 3.4.1 4.6.1 4.6.2', 'hasil-uji-A01-A07.md',
       'Jalankan fixture batas ceil 30000/30001, defisit tidak negatif, P/F/A null dan nol. || Periksa flag tanpa puskesmas dan bahwa F administratif tetap sama ketika marker missing bertambah. || Bandingkan agregat berbobot dengan expected result independen serta indikator SQL/Python. || Simpan hasil sebelum formatting, toleransi yang dipakai, dan defect untuk setiap ketidaksesuaian.',
       'A01–A07 lulus; rasio agregat contoh 40000 dan kesetaraan numerik mengikuti toleransi yang dibekukan.')
ticket('5.2.2', '4.11.4 4.4.5 4.6.5', 'hasil-uji-G01-G05.md ; audit-eligibilitas-titik.md',
       'Uji koordinat global/urutan lon-lat, kandidat centroid, dan verified tanpa bukti pada fixture. || Audit kelengkapan review seluruh kandidat serta lima grup identik; bedakan pemeriksaan mesin dan keputusan manusia. || Periksa titik tepat di batas, di luar polygon, dan fasilitas pulau dengan aturan yang dibekukan. || Uji join choropleth satu feature per kode serta perbedaan no-data/nol.',
       'G01–G05 lulus; hanya precision facility verified masuk buffer dan pemeriksaan otomatis tidak diklaim sebagai verifikasi lokasi lapangan.')
ticket('5.2.3', '5.2.2 4.6.3 4.6.4 3.4.2', 'hasil-uji-G06-G10.md ; geometri-fixture-dan-output.json',
       'Ukur jarak pusat ke batas untuk buffer 1/3/5 km dengan toleransi yang ditetapkan. || Jalankan dua buffer overlap dan bandingkan luas union dengan jumlah luas terpisah. || Uji clip, covered area, wilayah kosong, polygon invalid, CRS salah, multipolygon, dan pulau. || Periksa fasilitas tetangga lintas kabupaten serta dokumentasikan batas fasilitas luar provinsi.',
       'G06–G10 lulus; coverage 0–100 dalam toleransi dan geometri invalid tidak diterima tanpa koreksi berjejak.')
ticket('5.2.4', '5.2.3 3.4.2', 'hasil-uji-G11.md ; perbandingan-PostGIS-GeoPandas.json',
       'Pilih fixture dan sampel wilayah yang sama, termasuk overlap, boundary, serta pulau. || Hitung radius/luas menggunakan jalur PostGIS dan referensi GeoPandas/pyproj sesuai metode desain. || Bandingkan selisih absolut/relatif dengan toleransi yang sudah dibekukan dan jelaskan efek proyeksi/ketelitian kurva. || Jika melampaui toleransi, telusuri metode/parameter dan perbaiki sebelum retest tanpa melonggarkan ambang secara sepihak.',
       'G11 lulus dengan bukti dua implementasi; pembanding tidak memanggil kembali fungsi yang sama dengan sistem yang diuji.')
ticket('5.3.1', '4.11.4 4.5.2 4.5.4', 'hasil-uji-I01-I04.md',
       'Bangun database PostgreSQL/PostGIS test kosong dari migration dan periksa SSL serta objek skema. || Coba kode ganda, FK tidak ada, nilai negatif, verified tanpa bukti, dan district dari boundary set lain. || Impor fixture valid dua kali dan simulasikan kegagalan di tengah transaksi. || Periksa rollback, error per baris, row count, dan immutability rilis terbit; simpan hasil query.',
       'I01–I04 lulus pada PostgreSQL/PostGIS; pengujian SQLite saja tidak diterima sebagai bukti constraint spasial/akses.')
ticket('5.3.2', '5.3.1 4.7.5 4.7.3', 'hasil-uji-I05-I08.md',
       'Jalankan operasi baca/tulis dengan runtime, worker, publisher, dan guest sesuai matriks izin. || Publish kandidat test, baca endpoint terkait, lalu rollback pointer dan periksa cache/release_id. || Uji parameter SQL injection, sort tak dikenal, bbox/radius invalid, serta akses draft. || Simulasikan DB timeout/worker gagal dan periksa respons bersih serta tidak ada partial publish.',
       'I05–I08 lulus; seluruh endpoint konsisten dan kegagalan tidak membocorkan konfigurasi atau menerbitkan hasil separuh.')
ticket('5.3.3', '5.3.2 4.7.4 4.8.2', 'hasil-uji-S01-S03.md ; hasil-uji-command-internal.md',
       'Gunakan akun admin, guest tanpa session, dan akun DB teknis; hapus fixture role pengelola lama. || Coba membuka route internal, ID rilis draft, command publikasi, dan aksi tulis tanpa otorisasi. || Uji XSS pada nama/alamat/popup serta request tanpa CSRF/session dan login berulang. || Periksa cookie/session, logout, expiry, rate limit, dan respons penolakan tanpa kebocoran data.',
       'S01–S03 dan akses command lulus; input berbahaya tidak dieksekusi dan guest tidak memperoleh wewenang admin.')
ticket('5.3.4', '5.3.3 4.5.3 4.9.3', 'hasil-uji-S04-S07.md ; matriks-izin-terverifikasi.md',
       'Periksa bundle JS, HTML Folium, log, error publik, berkas konfigurasi yang terlayani, dan endpoint Data API. || Jalankan query allow/deny sebagai anon/authenticated bila tersedia, runtime non-owner, worker, dan publisher. || Pastikan sumber/boundary internal tidak terbaca hanya karena satu subsetnya terkait rilis publik. || Simpan bukti yang disanitasi; bila secret ditemukan, perbaiki sumber kebocoran dan ikuti prosedur penggantian credential.',
       'S04/S07 lulus dengan role aktual, bukan hanya owner; bukti uji sendiri tidak menyalin nilai rahasia.')
ticket('5.4.1', '4.11.4 4.8.3 4.8.5', 'hasil-uji-W01-W04.md',
       'Buka beranda/peta, gunakan zoom/pan/layer, dan temukan fasilitas berdasarkan nama serta kode. || Ganti kabupaten/kecamatan, layanan, karakteristik, lalu reset dan bandingkan tabel/marker dengan API. || Buka cluster serta dua fasilitas bertitik sama dan pastikan semua identitas dapat dipilih. || Cari fasilitas tanpa koordinat melalui tabel dan catat bahwa tidak ada marker palsu.',
       'W01–W04 lulus dengan screenshot/filter/rilis tercatat; jumlah hasil cocok query yang diizinkan.')
ticket('5.4.2', '5.4.1 4.8.4 4.8.6', 'hasil-uji-W05-W07.md',
       'Ganti metrik choropleth dan bandingkan label/unit/kelas legenda dengan angka detail. || Uji kecamatan F=0, indikator null, serta periode sumber campuran. || Buka sumber/metode/rilis dan pastikan pengguna dapat menemukan keterbatasan buffer. || Putus tile/API secara terkendali dan periksa pesan/fallback tanpa mengganti data gagal dengan nol.',
       'W05–W07 lulus; semua layar mengacu rilis sama dan no-data tidak tampil sebagai tanpa fasilitas.')
ticket('5.4.3', '5.4.2 3.5.3 2.4.1', 'hasil-uji-W09-W10.md',
       'Uji viewport 360, 768, dan 1366 pada browser sasaran dengan peta/panel/popup terbuka. || Jalankan navigasi keyboard, label form, fokus, serta buka-tutup kontrol tanpa mouse. || Simulasikan jaringan lambat dan perubahan filter cepat dengan urutan respons dibalik. || Rekam kontrol terpotong, state tertinggal, dan respons lama yang menimpa hasil terbaru sebagai defect.',
       'W09–W10 lulus; halaman dapat digunakan pada seluruh profil baseline dan request lama tidak mengganti filter aktif.')
ticket('5.4.4', '5.4.3 4.10.1 4.10.2 4.10.3 4.10.4 4.5.4', 'hasil-uji-P1-dan-input-backend.md',
       'Baca keputusan WF-G2 dan tandai P1 ditunda sebagai not_in_scope_for_release, bukan passed. || Untuk P1 terpilih, jalankan dashboard/review/publish UI end-to-end, W08 ekspor, dan A08 ranking/parameter. || Jalankan S05 validasi file salah header/ukuran/ekstensi pada command/API impor P0 meskipun UI tidak dipilih. || Uji formula injection pada ekspor terpilih dan gabungkan hasil per fitur dengan release_id serta bukti.',
       'Semua P1 terpilih lulus; validasi input backend P0 tidak ikut dilewati ketika seluruh P1 ditunda.')
ticket('5.5.1', '5.4.3 5.3.4 2.4.1', 'hasil-uji-P01-P03.md ; metrik-performa.json',
       'Siapkan data target dan catat perangkat/browser/jaringan serta cache dingin/hangat sesuai baseline. || Ukur waktu peta operasional, ukuran payload, dan perilaku filter/zoom di mobile. || Jalankan beban staging sesuai profil yang diterima, misalnya 20 pengguna dengan ramp-up dan steady terukur; mock layanan eksternal. || Rekam p95, error rate, koneksi DB, freeze, dan efek simplifikasi; perbaiki bottleneck lalu ulang bagian terdampak.',
       'P01–P03 memenuhi target yang disepakati, bukan target baru setelah gagal; raw metrics dan konfigurasi beban tersedia.')
ticket('5.5.2', '5.3.4 3.2.4 2.4.2', 'hasil-uji-S06.md ; laporan-restore-dan-waktu.md',
       'Buat backup DB dan semua berkas/artefak yang diperlukan dari kandidat yang diketahui versinya. || Siapkan environment kosong terpisah dan catat waktu mulai pemulihan. || Restore DB, storage/artefak, konfigurasi aman, lalu periksa jumlah/hash/FK/login/peta. || Ukur usia titik backup terhadap RPO dan waktu layanan pulih terhadap RTO; simpan kegagalan serta retest.',
       'S06 lulus dengan restore nyata, bukan sekadar keberhasilan membuat backup; data dan artefak sama-sama pulih.')
ticket('5.5.3', '5.2.4 4.9.4', 'hasil-uji-R01-R02.md ; manifest-dua-run-notebook.json',
       'Mulai Colab runtime bersih dan ikuti panduan instalasi/input tanpa menggunakan state sesi lama. || Jalankan Run all pada fixture lalu snapshot kandidat dan simpan versi, parameter, log, serta hash. || Ulangi dari runtime bersih kedua dengan input yang sama. || Bandingkan tabel identik dan geometri ekuivalen sesuai toleransi; pisahkan timestamp dari konten deterministik.',
       'R01–R02 lulus tanpa langkah manual tersembunyi; kegagalan sumber menghasilkan pesan dan tidak menciptakan hasil palsu.')
ticket('5.5.4', '5.5.3 4.8.6', 'hasil-uji-R03.md ; matriks-kesetaraan-HTML-aplikasi.md',
       'Buka HTML ekspor di dua browser yang ditentukan dan aplikasi dengan release_id/run yang sama. || Bandingkan jumlah fasilitas/kategori, indikator sampel, layer, legenda, tahun, dan sumber. || Periksa tile/CDN serta perilaku saat internet tidak tersedia sesuai batas ekspor yang dijelaskan. || Catat perbedaan dan retest setelah perbaikan tanpa menukar artefak ke rilis yang tidak diterima.',
       'R03 lulus dan kebutuhan internet jelas; kesetaraan mencakup isi data, bukan hanya tampilan serupa.')
ticket('5.6.1', '5.1.4 5.2.4 5.3.4 5.4.4 5.5.1 5.5.2 5.5.4 3.6.3', 'daftar-peserta-UAT.md ; paket-pelaksanaan-UAT.md',
       'Pastikan kandidat stabil dan semua penghalang teknis untuk skenario UAT telah diselesaikan. || Tetapkan peserta aktual serta jadwal; catat perbedaan dari target SRS dan minta keputusan bila perlu. || Siapkan instruksi, formulir, perangkat, akun admin jika skenario memerlukannya, dan release_id. || Lakukan dry run instrumen oleh tim tanpa memasukkannya sebagai hasil peserta.',
       'Peserta/jadwal nyata tersedia dan instrumen tidak membimbing langkah solusi untuk tugas yang diukur mandiri.')
ticket('5.6.2', '5.6.1', 'hasil-UAT-per-peserta.md ; rekap-temuan-UAT.md',
       'Berikan orientasi singkat yang sama lalu minta peserta mengerjakan tugas sesuai skrip. || Catat waktu, keberhasilan mandiri, bantuan, kesalahan, dan komentar per tugas. || Periksa pemahaman radius geometris, tahun/sumber, serta no-data agar salah tafsir kritis teridentifikasi. || Hitung capaian terhadap baseline, susun temuan berseverity, dan tautkan ke modul/owner perbaikan.',
       'Rekap dapat dihitung ulang dari catatan peserta; tugas dibantu tidak dihitung mandiri dan hasil tidak diklaim SUS tanpa instrumen yang benar.')
ticket('5.6.3', '5.6.2', 'register-defect-final.md ; hasil-retest-regresi.md',
       'Konsolidasikan defect dari seluruh suite dan UAT; tetapkan owner BE/FE/DG/OP sesuai akar masalah. || Perbaiki kritis/tinggi terlebih dahulu, versi ulang kode/data bila berubah, dan catat dampaknya pada kandidat. || Retest kasus gagal dan jalankan regresi relevan; ulang UAT bagian terdampak bila perubahan menyentuh alur/pemahaman. || Tinjau isu sedang/rendah bersama penerima serta simpan keputusan dan batasannya.',
       'Tidak ada defect kritis/tinggi terbuka atau blocked yang disamarkan sebagai passed; kandidat akhir memiliki bukti retest sesuai revisinya.')
ticket('5.6.4', '5.1.4 5.2.4 5.3.4 5.4.4 5.5.1 5.5.2 5.5.4 5.6.3', 'laporan-pengujian-final.md ; manifest-kandidat-deployment.json ; penerimaan-WF-G5.md',
       'Gabungkan hasil aktual seluruh suite dan UAT dengan matriks FR/NFR serta keputusan P1. || Pastikan revisi kode, data, run, dan artefak final cocok dengan bukti uji setelah retest. || Review kualitas data, keamanan, performa, restore, reproduksi, dan daftar isu yang diterima. || Bekukan kandidat deployment dan catat keputusan penerima WF-G5; deploy hanya jika accepted.',
       'Semua P0 dan P1 terpilih diterima dengan bukti; kandidat yang diterapkan nanti tepat sama dengan manifest ini.')

# Fase 6: urutan akun admin disesuaikan setelah migration.
ticket('6.1.1', '5.6.4 3.1.2 1.2.4', 'inventaris-produksi.md ; hasil-pemeriksaan-host-HTTPS.md',
       'Siapkan hosting dengan akun/anggaran yang sudah ditetapkan dan catat pemilik serta spesifikasi runtime. || Konfigurasi document root Laravel, jaringan outbound DB, domain bila diperlukan, dan HTTPS. || Periksa versi/ekstensi, hak berkas, lokasi log, dan fasilitas worker/cron sesuai desain. || Simpan konfigurasi nonrahasia dan hasil health check awal; jangan menyebut aplikasi live sebelum kode/data diterapkan.',
       'Host memenuhi desain dan HTTPS valid; path konfigurasi/arsip tidak terlayani sebagai direktori publik.')
ticket('6.1.2', '6.1.1 3.2.3 3.2.4', 'inventaris-Supabase-produksi.md ; hasil-koneksi-produksi.md',
       'Siapkan project/database produksi dan storage artefak terpisah dari test. || Aktifkan PostGIS, catat region/versi, batas kapasitas, dan schema extension. || Siapkan akses operator migration serta koneksi SSL awal secara aman; jangan mengandalkan akun runtime untuk DDL. || Periksa keterjangkauan dari host dan kesiapan backup/penyimpanan tanpa memasukkan data fixture.',
       'Lingkungan produksi siap menerima migration; credential operasional awal tersedia hanya bagi operator berwenang dan tidak masuk bukti teks.')
ticket('6.1.3', '6.2.2 6.1.1 6.1.2 4.7.4', 'checklist-konfigurasi-final.md ; bukti-provisioning-admin.md',
       'Setelah migration tersedia, pasang konfigurasi runtime/worker/publisher yang dibutuhkan dengan secret di server. || Tetapkan APP_ENV/DEBUG, URL/HTTPS, cookie/session, logging, queue, dan cache sesuai produksi. || Buat akun admin awal melalui jalur provisioning terotorisasi pada tabel yang sudah ada. || Uji koneksi runtime serta login/logout dan serahkan akses awal lewat jalur aman tanpa menaruh password pada tiket.',
       'Debug publik mati, admin bisa login, runtime memakai hak minimum, dan tidak ada akun fixture yang terbawa ke produksi.')
ticket('6.1.4', '6.1.1 6.1.2 5.5.2 5.6.4', 'runbook-deployment.md ; manifest-titik-pemulihan.json',
       'Tulis urutan deploy kode, migration/data, konfigurasi final/admin, publikasi, worker, dan smoke test sesuai tiket. || Tetapkan operator, jendela penerapan, checklist pra-rilis, dan kondisi rollback. || Buat/validasi backup DB serta artefak sebelum perubahan; untuk rilis pertama catat bahwa belum ada rilis aplikasi sebelumnya. || Siapkan tindakan pemulihan instalasi pertama berbeda dari rollback rilis lanjutan dan cocokkan dengan rehearsal restore.',
       'Runbook dapat diikuti operator lain dan tidak memerintahkan membuat akun admin sebelum migration.')
ticket('6.2.1', '6.1.4 5.6.4', 'log-pemasangan-aplikasi.md ; manifest-build-terpasang.json',
       'Ambil revision dan dependency lock tepat dari manifest WF-G5. || Build atau salin artefak build yang telah diterima sesuai runbook; verifikasi checksum. || Pasang kode/assets, hak file, dan titik layanan dengan akses publik ditahan sampai data/konfigurasi siap. || Catat revision, waktu, operator, dan setiap deviasi; perubahan kode baru harus kembali melalui pengujian relevan.',
       'Versi terpasang identik dengan kandidat yang diterima; proses deploy tidak diam-diam memperbarui dependency terbaru.')
ticket('6.2.2', '6.2.1 6.1.2 6.1.4 4.5.5', 'log-migration-impor-produksi.md ; rekonsiliasi-produksi.md',
       'Verifikasi target produksi dan titik pemulihan sebelum menjalankan migration yang telah diuji. || Terapkan schema, constraint, indeks, grants, dan policy menggunakan akun migration yang sesuai. || Muat dataset final serta metadata kurasi sesuai manifest, tanpa seed sintetis. || Cocokkan jumlah/kode/FK/hash/tahun/edisi dengan kandidat dan tahan publikasi bila ada selisih.',
       'Struktur dan dataset cocok dengan manifest WF-G5; seluruh referensi valid sebelum admin awal dan rilis publik diaktifkan.')
ticket('6.2.3', '6.2.2 6.1.3 6.2.1 5.6.4', 'log-publikasi-produksi.md ; manifest-rilis-aktif.json',
       'Pasang hasil analysis run, GeoJSON, HTML, dan artefak yang tercantum pada kandidat diterima. || Verifikasi FK/hash/rilis/run serta jalankan validator publikasi menggunakan akun penerbit. || Publikasikan dan ganti pointer aktif atomik, lalu perbarui cache sesuai versi. || Periksa respons API dan metadata HTML menggunakan akun guest sebelum membuka seluruh alur publik.',
       'Data/analisis/HTML aktif berasal dari kandidat yang sama dan rilis sebelumnya tidak diubah di tempat.')
ticket('6.2.4', '6.2.3 6.1.3 3.2.4', 'checklist-operasi-aktif.md ; bukti-backup-awal.md',
       'Aktifkan worker/scheduler sesuai job yang benar-benar diperlukan oleh aplikasi. || Konfigurasi health check, log, notifikasi error job/koneksi, serta pemantauan kapasitas. || Jadwalkan backup DB dan berkas/artefak dengan retensi serta owner yang ditetapkan. || Jalankan pekerjaan aman dan backup pertama; periksa timestamp, keberhasilan, dan lokasi penyimpanan.',
       'Operasi aktif memiliki bukti, bukan hanya konfigurasi tersimpan; backup mencakup artefak selain database.')
ticket('6.3.1', '6.2.4', 'hasil-smoke-produksi.md',
       'Buka URL HTTPS sebagai guest dan verifikasi rilis aktif/metadata yang diharapkan. || Jalankan beranda, peta, pencarian/filter, detail, sumber, serta HTML pada data produksi yang diterima. || Uji login/logout admin dengan aksi aman; hindari mempublikasikan dataset dummy. || Rekam response/screenshot/log, lalu tandai kegagalan inti sebagai pemicu tindakan runbook.',
       'Seluruh alur inti berfungsi pada produksi dan tidak bergantung pada URL/path staging.')
ticket('6.3.2', '6.3.1 6.2.4 6.1.3', 'hasil-verifikasi-akses-operasi-produksi.md',
       'Periksa guest ditolak pada draft/admin/write serta konfigurasi publik tidak menampilkan rahasia. || Pastikan admin dan akun teknis menggunakan hak yang sesuai, debug mati, dan session HTTPS bekerja. || Periksa worker/monitoring serta bukti backup pertama beserta cakupan DB/berkas. || Catat isu konfigurasi, perbaiki, dan ulang pemeriksaan yang terdampak.',
       'Konfigurasi produksi tidak lebih longgar dari konfigurasi yang diuji; backup/monitoring benar-benar berjalan.')
ticket('6.3.3', '6.3.1 6.3.2 6.1.4', 'laporan-rollback-atau-kesiapan-pemulihan.md',
       'Bandingkan hasil smoke/akses dengan kriteria rollback pada runbook. || Jika deploy gagal, hentikan penyajian hasil invalid dan pulihkan titik valid sesuai prosedur; rilis pertama memakai prosedur pemulihan instalasi. || Jika deploy berhasil, verifikasi ketersediaan backup/artefak dan rehearsal staging tanpa sengaja merusak produksi. || Catat jalur yang dijalankan, versi/titik pemulihan, waktu, serta hasil smoke ulang bila pemulihan dilakukan.',
       'Status siap rollback didukung bukti rehearsal dan titik tersedia; tidak mengklaim rollback produksi dilakukan bila hanya kesiapan yang diperiksa.')
ticket('6.3.4', '6.3.1 6.3.2 6.3.3', 'catatan-rilis-produksi.md ; penerimaan-WF-G6.md',
       'Kumpulkan URL, revision, release_id/run, log penerapan, smoke, akses, backup, dan pemulihan. || Pastikan tidak ada kegagalan inti/rahasia/korupsi data yang belum selesai. || Tulis known issues diterima, owner operasi, dan cara menghubungi penanggung jawab dukungan. || Catat keputusan penerima WF-G6 dengan versi yang benar-benar aktif.',
       'Produksi terverifikasi dan penerimaan berkaitan dengan versi aktif, bukan kandidat staging yang berbeda.')

# Fase 7: finalisasi dokumen yang mengikuti sistem aktual.
ticket('7.1.1', '6.3.4 4.8.6 4.7.5', 'panduan-guest.md ; panduan-admin.md',
       'Ambil screenshot versi produksi dan tulis langkah membuka peta, filter, detail, sumber, serta radius. || Jelaskan no-data, koordinat missing, tahun campuran, dan batas interpretasi analisis. || Tulis login/logout dan operasi admin yang tersedia, termasuk command P0 serta UI P1 jika dipilih. || Minta pembaca lain mengikuti panduan dan perbaiki langkah/label yang tidak cocok dengan aplikasi aktual.',
       'Panduan tidak mendeskripsikan P1 ditunda sebagai fitur tersedia dan semua langkah dapat diikuti pada versi final.')
ticket('7.1.2', '6.3.4 6.1.4 5.5.2', 'panduan-instalasi-operasi.md ; panduan-troubleshooting.md',
       'Gabungkan versi runtime, instalasi dependensi, contoh konfigurasi aman, build, dan migration. || Rinci deployment, worker/cron, log, monitoring, backup DB/artefak, dan restore berdasarkan hasil nyata. || Tulis gejala, pemeriksaan, serta tindakan untuk koneksi gagal, job macet, tile gagal, dan rilis tidak tampil. || Uji keterbacaan runbook dengan operator lain tanpa mencantumkan credential.',
       'Urutan admin setelah migration benar dan panduan restore merujuk prosedur yang telah terbukti, bukan asumsi layanan.')
ticket('7.1.3', '6.3.4 3.6.4 4.11.1', 'arsitektur-as-built.md ; kamus-data-as-built.md ; kontrak-API-as-built.md',
       'Bandingkan implementasi final dengan diagram, ERD, schema, endpoint, dan policy baseline. || Perbarui dokumentasi untuk tabel/kolom/index, status, validasi, serta error aktual. || Catat perubahan desain beserta alasan/keputusan dan hilangkan contoh endpoint yang tidak diterapkan. || Cocokkan contoh respons serta hak akses dengan bukti uji dan kode revision final.',
       'Dokumen teknis mewakili versi terpasang dan pemisahan role admin/guest dari akun DB tetap jelas.')
ticket('7.1.4', '6.3.4 4.9.4 5.5.3 5.5.4', 'panduan-data-dan-reproduksi.md ; katalog-sumber-final.md',
       'Rangkum sumber/periode/lisensi, adapter scraping, ETL, crosswalk, serta proses review lokasi. || Dokumentasikan rumus, CRS, radius, luas, toleransi, dan jumlah lokasi yang dikeluarkan. || Sertakan manifest input/output dan langkah menjalankan ulang notebook serta ekspor rilis yang tepat. || Tinjau seluruh batas historis/parsial dan bedakan berkas raw, staging, processed, serta publik.',
       'Pembaca dapat menelusuri satu indikator dan satu titik sampai sumber/keputusan review serta menjalankan ulang tanpa secret produksi.')
ticket('7.2.1', '7.1.4 4.6.5 5.2.4', 'hasil-dan-pembahasan-penelitian.md',
       'Ambil tabel/peta dari rilis/run final dan catat pertanyaan penelitian yang dijawab. || Jelaskan distribusi, rasio, kebutuhan indikatif, dan radius berdasarkan angka yang sudah diterima. || Nyatakan tahun sumber, kelengkapan koordinat, dan keterbatasan cakupan pada gambar/tabel serta narasi. || Tinjau kesimpulan dengan reviewer data agar tidak melampaui klaim jarak geometris atau menjanjikan penempatan fasilitas optimal.',
       'Seluruh angka dapat dilacak ke artefak final dan tidak ada klaim cakupan penuh dari subset titik.')
ticket('7.2.2', '7.1.3 5.6.4 7.2.1', 'laporan-implementasi-pengujian.md',
       'Jelaskan tahapan waterfall, keluaran tiap gerbang, serta perubahan scope yang benar-benar terjadi. || Rangkum implementasi akhir dan hubungan kebutuhan–fitur–bukti uji. || Sajikan hasil aktual suite, performa, restore, reproduksi, UAT, defect, dan retest. || Bedakan passed, failed, blocked, dan not_in_scope; periksa konsistensi seluruh revision/rilis pada laporan.',
       'Laporan tidak menyalin rencana uji seolah hasil eksekusi dan tidak menyembunyikan P1 yang ditunda.')
ticket('7.2.3', '7.1.1 7.2.1 7.2.2', 'skenario-demo.md ; materi-presentasi.md',
       'Susun alur presentasi masalah, data, metode waterfall, aplikasi, hasil, dan keterbatasan. || Siapkan demo pencarian/filter/detail, radius, no-data, sumber, serta alur admin yang tersedia. || Tampilkan notebook/HTML pada rilis yang sama dan siapkan artefak cadangan bila koneksi gagal. || Lakukan rehearsal dengan durasi yang disepakati dan catat koreksi materi serta label.',
       'Demo menggunakan data final; materi cadangan diberi label jelas dan tidak mengklaim interaksi live ketika menggunakan screenshot.')
ticket('7.2.4', '7.1.1 7.1.2 7.1.3 7.1.4 7.2.1 7.2.2 7.2.3', 'manifest-paket-serah-terima.json ; checklist-paket.md',
       'Kumpulkan source revision, migration, lockfile, notebook, HTML, data yang boleh dibagikan, panduan, dan laporan. || Pisahkan backup/artefak besar dari kode bila perlu dan catat lokasi serta hak akses yang sesuai. || Hitung checksum/ukuran, periksa lisensi redistribusi, serta pindai rahasia yang tidak boleh masuk paket. || Buka paket pada lokasi uji untuk memeriksa kelengkapan dan petunjuk penggunaan; catat versi final.',
       'Manifest menunjuk file yang benar-benar ada dan dapat diakses penerima; password/token diserahkan terpisah dari dokumen/paket.')
ticket('7.3.1', '7.2.3 7.2.4', 'notulen-demo-dan-orientasi.md',
       'Jadwalkan sesi dengan penerima aktual dan siapkan aplikasi/artefak versi final. || Demonstrasikan alur guest dan admin yang relevan lalu minta penerima mencoba langkah utama. || Jelaskan arti radius, sumber, periode, dan data belum lengkap serta cara melaporkan masalah. || Catat peserta, pertanyaan, tindak lanjut, owner, dan bukti orientasi telah dilakukan.',
       'Penerima memahami akses dan batas hasil; demonstrasi tidak dicatat selesai hanya karena materi sudah dibuat.')
ticket('7.3.2', '7.3.1 7.1.2 7.2.4', 'register-serah-akses.md',
       'Daftar repositori, hosting/domain, Supabase, backup, dan kanal monitoring yang harus dikuasai penerima. || Berikan akses sesuai wewenang melalui mekanisme akun/undangan yang ditetapkan dan jalur rahasia terpisah. || Minta penerima menguji login serta akses operasional yang diperlukan. || Catat penerima, waktu, izin, dan hasil verifikasi tanpa menuliskan credential; pertahankan akses dukungan yang masih diperlukan.',
       'Penerima benar-benar bisa mengakses aset, bukan hanya mendapat daftar URL; pencabutan akses tim menunggu transisi final.')
ticket('7.3.3', '7.2.4 7.3.1 7.3.2', 'hasil-checklist-serah-terima.md ; register-known-issues.md',
       'Cocokkan setiap keluaran charter/SRS dengan manifest paket dan lokasi akses. || Buka tautan, notebook, HTML, laporan, serta contoh berkas untuk memeriksa integritas. || Rangkum known issues, keputusan P1 ditunda, batas analisis, dan pekerjaan dukungan yang masih wajib. || Perbaiki kekurangan paket atau catat keputusan penerima sebelum berita acara ditandatangani.',
       'Tidak ada keluaran wajib tanpa file/bukti dan isu yang diterima mempunyai alasan serta owner.')
ticket('7.3.4', '7.3.1 7.3.2 7.3.3', 'berita-acara-serah-terima.md ; kesepakatan-dukungan-awal.md ; penerimaan-WF-G7.md',
       'Tulis daftar keluaran/versi yang diserahkan dan hasil pemeriksaan penerima. || Tetapkan tanggal mulai/akhir dukungan, jam layanan, kanal laporan, owner, dan batas perbaikan bug versus fitur baru. || Nyatakan kewajiban tersisa serta kriteria akhir dukungan yang akan dipakai fase 8. || Catat penerimaan nyata WF-G7 dan simpan berita acara serta kesepakatan yang disetujui.',
       'Masa dukungan mempunyai batas waktu nyata sebelum fase 8 dijalankan; tidak diasumsikan tanpa batas.')

# Fase 8: empat tiket dukungan dijalankan sebagai siklus, penutupan setelah periode selesai.
ticket('8.1.1', '7.3.4 6.2.4', 'log-monitoring-dukungan.md ; ringkasan-backup-dukungan.md',
       'Mulai pemantauan pada tanggal dukungan dan frekuensi yang disepakati, tanpa menunggu periode berakhir untuk melaporkan insiden. || Periksa health, error/job, koneksi, kapasitas, serta waktu/kelengkapan backup. || Teruskan setiap anomali segera ke 8.1.2 dengan waktu dan konteks rilis. || Simpan log setiap siklus dan tutup rekap setelah masa dukungan selesai serta seluruh tindak lanjut tercatat.',
       'Seluruh interval pemantauan yang disepakati mempunyai catatan atau penjelasan; insiden diteruskan saat ditemukan.')
ticket('8.1.2', '8.1.1 7.3.4', 'register-insiden-dukungan.md',
       'Buka pencatatan insiden bersamaan dengan monitoring yang sudah dimulai. || Untuk setiap laporan, rekam gejala, langkah reproduksi, dampak, versi, severity, dan sumber laporan. || Tentukan bug dalam scope, koreksi data, atau permintaan fitur; berikan owner dan tindak lanjut. || Kirim bug yang diterima ke 8.1.3 pada siklus berjalan dan rekap termasuk catatan tidak ada insiden bila memang demikian.',
       'Setiap laporan memiliki keputusan; pekerjaan P2 tidak otomatis dimasukkan sebagai kewajiban dukungan.')
ticket('8.1.3', '8.1.2', 'log-perbaikan-dukungan.md ; manifest-kandidat-perbaikan.json',
       'Ambil insiden berowner dari 8.1.2 dan reproduksi pada environment aman dengan bukti. || Perbaiki modul terkait bersama BE/FE/DG/OP; koreksi data dibuat sebagai rilis baru. || Jalankan unit/integrasi terdampak dan dokumentasikan risiko serta versi kandidat perbaikan. || Serahkan kandidat ke 8.1.4; bila sepanjang periode tidak ada insiden yang perlu diperbaiki, catat no_change_required dengan persetujuan reviewer tanpa mengarang patch.',
       'Perbaikan terhubung ke insiden dan tidak mengubah sejarah published; tidak ada perubahan juga harus dibuktikan lewat register insiden.')
ticket('8.1.4', '8.1.3', 'hasil-verifikasi-perbaikan.md ; catatan-rilis-dukungan.md',
       'Retest kasus insiden dan regresi relevan terhadap kandidat perbaikan setiap siklus. || Terapkan kandidat yang diterima menggunakan runbook deployment dan jalankan smoke pascaperbaikan. || Perbarui catatan rilis, panduan/known issues, lalu kembalikan pemantauan ke 8.1.1 hingga akhir periode. || Jika tidak ada perubahan, nyatakan pengujian patch tidak berlaku, tinjau log monitoring, dan tutup rekap tanpa klaim test patch lulus.',
       'Setiap perbaikan punya bukti retest serta versi produksi; tiket selesai hanya setelah rekap seluruh siklus dukungan ditutup.')
ticket('8.2.1', '8.1.1 8.1.2 8.1.3 8.1.4 1.2.3', 'evaluasi-realisasi-proyek.md',
       'Kumpulkan jam aktual, tanggal, biaya, hasil gerbang, perubahan scope, dan defect yang benar-benar dicatat. || Bandingkan dengan baseline serta revisi resmi, bukan hanya usulan awal delapan minggu. || Hitung deviasi dan jelaskan pengaruh kurasi lokasi, sumber, kapasitas, serta perubahan kebutuhan. || Tandai data realisasi yang tidak tercatat sebagai tidak tersedia dan hindari perkiraan yang disajikan sebagai aktual.',
       'Evaluasi mempunyai sumber angka dan membedakan usaha jam orang dari durasi kalender.')
ticket('8.2.2', '8.2.1', 'lessons-learned.md ; backlog-lanjutan.md',
       'Kumpulkan pengalaman tim tentang sumber, crosswalk, lokasi, analisis, deployment, dan penerimaan. || Catat masalah, akar penyebab, tindakan yang membantu, serta saran spesifik untuk proyek serupa. || Susun P1 ditunda/P2 sebagai backlog dengan manfaat, dependensi, dan batas scope baru. || Tinjau bersama tim/penerima dan pastikan backlog tidak dianggap utang rilis awal tanpa kesepakatan.',
       'Pelajaran didukung kejadian proyek dan backlog memisahkan perbaikan wajib dari pengembangan masa depan.')
ticket('8.2.3', '8.2.1 8.2.2 7.3.2 7.2.4', 'manifest-arsip-final.json ; register-transisi-akses-final.md',
       'Arsipkan versi terakhir kode/data/notebook/HTML, panduan, laporan, keputusan, dan bukti penerimaan. || Verifikasi backup serta lokasi arsip dapat diakses penerima sesuai retensi yang disepakati. || Uji ulang akses penerima sebelum mencabut token/akun sementara yang tidak lagi diperlukan. || Catat siapa memegang operasi berkelanjutan dan simpan register akses tanpa rahasia.',
       'Arsip sesuai versi pascadukungan dan pencabutan akses tim tidak mengunci penerima dari asetnya.')
ticket('8.2.4', '8.1.1 8.1.2 8.1.3 8.1.4 8.2.1 8.2.2 8.2.3', 'berita-acara-penutupan.md ; penerimaan-WF-G8.md',
       'Pastikan tanggal akhir dukungan telah tercapai dan seluruh kewajiban rilis/dukungan diperiksa. || Tinjau isu wajib yang tersisa; selesaikan atau alihkan secara tertulis kepada pihak yang menerima tanggung jawab. || Kumpulkan evaluasi, lessons learned, arsip, dan bukti transisi operasi. || Catat penerimaan penutupan WF-G8, tanggal, serta pihak penerima; jangan menutup hanya karena waktu kerja tim habis.',
       'Tidak ada kewajiban tanpa owner/penerimaan dan operasi setelah proyek memiliki penanggung jawab jelas.')

PHASES = {
    1: ('01-inisiasi', 'Inisiasi dan perencanaan proyek'),
    2: ('02-kebutuhan', 'Analisis kebutuhan'),
    3: ('03-desain', 'Perancangan sistem'),
    4: ('04-implementasi', 'Implementasi dan penyiapan data'),
    5: ('05-pengujian', 'Pengujian dan penerimaan'),
    6: ('06-deployment', 'Deployment dan verifikasi produksi'),
    7: ('07-serah-terima', 'Dokumentasi akhir dan serah terima'),
    8: ('08-penutupan', 'Pemeliharaan awal dan penutupan'),
}
GATES = {1: '1.3.4', 2: '2.4.4', 3: '3.6.4', 4: '4.11.4',
         5: '5.6.4', 6: '6.3.4', 7: '7.3.4', 8: '8.2.4'}
SUPPORT = {'8.1.1', '8.1.2', '8.1.3', '8.1.4'}
REVIEWERS = {'PM': 'Penerima proyek yang ditetapkan pada 1.1.2',
             'AN': 'PM', 'DG': 'QA atau DG lain yang bukan pembuat',
             'BE': 'QA; reviewer BE untuk skema/keamanan', 'FE': 'QA',
             'QA': 'Pemilik modul dan PM; reviewer berbeda dari pelaksana',
             'OP': 'BE/QA yang bukan operator pelaksana'}
REF_NAMES = {
    'needs': '01-kebutuhan-dan-ruang-lingkup.md',
    'data': '02-dataset-dan-audit.md',
    'arch': '03-arsitektur-dan-analisis.md',
    'db': '04-supabase-dan-kamus-data.md',
    'test': '05-rencana-pengujian.md',
    'plan': '06-tahapan-dan-kebutuhan.md',
    'decisions': '07-sumber-dan-keputusan.md',
    'revision': 'revisi.txt',
}
GROUP_REFS = {
    '1': ['needs', 'plan', 'decisions', 'revision'],
    '2': ['needs', 'data', 'arch', 'test', 'revision'],
    '3': ['arch', 'db', 'data', 'test', 'revision'],
    '4.1': ['arch', 'test'], '4.2': ['data', 'decisions', 'revision'],
    '4.3': ['data', 'db'], '4.4': ['data', 'arch'],
    '4.5': ['db', 'data'], '4.6': ['arch', 'test'],
    '4.7': ['arch', 'db', 'revision'], '4.8': ['needs', 'arch'],
    '4.9': ['arch', 'test'], '4.10': ['needs', 'revision', 'test'],
    '4.11': ['needs', 'test', 'db'],
    '5': ['test', 'needs', 'revision'], '6': ['db', 'arch', 'test'],
    '7': ['needs', 'data', 'arch', 'test'], '8': ['plan', 'test'],
}
BLOCKERS = {
    1: 'Jika pihak penerima, kapasitas, biaya, atau keputusan mandat belum tersedia, catat isu dan owner. Jangan mengisi nama, persetujuan, tanggal, atau angka aktual fiktif.',
    2: 'Jika sumber, cakupan penuh/parsial, fitur P1, atau target penerimaan belum diputuskan, catat keputusan terbuka dan eskalasi ke PM. Kebutuhan yang memblokir desain harus selesai sebelum WF-G2.',
    3: 'Jika rancangan bertentangan dengan SRS atau antarkomponen, catat konflik dan kembalikan ke pemilik desain. Perubahan kebutuhan yang sudah dibekukan memakai change request sebelum implementasi bergantung padanya.',
    4: 'Jika input, sumber, akses, atau hasil validasi gagal, simpan error dan contoh minimal; tandai blocked bila pekerjaan tidak dapat dilanjutkan. Perbaiki akar masalah atau minta keputusan perubahan scope; jangan memaksa status data valid atau menimpa arsip asli.',
    5: 'Jika test gagal, catat expected/actual, severity, langkah reproduksi, versi, serta owner modul. Perbaikan yang menghalangi tiket berikutnya dilakukan segera pada tiket/modul terkait lalu retest; tidak menunggu 5.6.3. Tiket 5.6.3 mengonsolidasikan penutupan defect, bukan menunda semua perbaikan.',
    6: 'Jika hash, akses, integritas data, atau smoke test tidak sesuai kandidat diterima, hentikan kelanjutan penerapan dan gunakan runbook pemulihan. Jangan menerbitkan dataset separuh atau mencatat layanan sehat tanpa bukti.',
    7: 'Jika paket, akses penerima, atau panduan belum cocok dengan versi aktif, perbaiki sebelum penerimaan. Catat known issues dan keputusan scope secara terbuka; jangan menuliskan credential dalam tiket atau laporan.',
    8: 'Jika kewajiban dukungan belum selesai, pertahankan isu dengan owner dan tenggat. Penutupan memerlukan penyelesaian atau pengalihan tertulis yang diterima; berakhirnya periode saja tidak menutup insiden wajib.',
}

def link(from_file, to_file, label):
    return f'[{label}]({Path(os.path.relpath(to_file, from_file.parent)).as_posix()})'

def generate():
    wbs_path = BASE / '01-WBS-waterfall.md'
    source = wbs_path.read_text(encoding='utf-8')
    rows = re.findall(r'^\| (\d+\.\d+\.\d+) \| (.*?) \| (.*?) \| (.*?) \|$', source, re.M)
    tasks = {code: {'wbs': code, 'title': title, 'owner': owner, 'acceptance': proof,
                    'phase': int(code.split('.')[0]), **DETAILS.get(code, {})}
             for code, title, owner, proof in rows}
    assert len(rows) == len(tasks) == len(DETAILS) == 160
    assert set(tasks) == set(DETAILS), ('missing/extra', set(tasks) ^ set(DETAILS))
    order = [r[0] for r in rows]
    # Kebutuhan alat/biaya menjadi input estimasi, bukan muncul setelah estimasi dibekukan.
    order.remove('1.2.4')
    order.insert(order.index('1.2.3'), '1.2.4')
    # Tabel akun harus tersedia sebelum provisioning admin produksi.
    order.remove('6.1.3')
    order.insert(order.index('6.2.2') + 1, '6.1.3')
    positions = {code: n for n, code in enumerate(order)}
    target = BASE / 'Tiket'
    assert not target.exists(), 'Folder Tiket sudah ada; generator tidak menimpa tiket atau status kerja.'
    for n, code in enumerate(order, 1):
        t = tasks[code]
        t['id'] = f'WF-{n:03d}'
        t['sequence'] = n
        t['priority'] = 'P1' if code.startswith('4.10.') else 'P0'
        t['previous'] = order[n-2] if n > 1 else None
        t['next'] = order[n] if n < len(order) else None
        t['gate_in'] = f"WF-G{t['phase']-1}" if t['phase'] > 1 else None
        t['gate_out'] = f"WF-G{t['phase']}" if GATES[t['phase']] == code else None
        t['path'] = target / PHASES[t['phase']][0] / f"{t['id']}-WBS-{code}.md"
        if t['gate_out']:
            t['dependencies'] = list(dict.fromkeys(t['dependencies'] + [
                c for c in order if tasks[c]['phase'] == t['phase'] and c != code]))
        assert len(t['steps']) >= 4 and all(x.strip() for x in t['steps']), code
        assert t['artifacts'] and t['verification']
        for dep in t['dependencies']:
            assert dep in tasks and positions[dep] < positions[code], (code, dep)
    target.mkdir()
    records = []
    for code in order:
        t = tasks[code]
        dest = t['path']
        dest.parent.mkdir(exist_ok=True)
        is_support = code in SUPPORT
        refs = GROUP_REFS.get(code.rsplit('.', 1)[0], GROUP_REFS.get(str(t['phase']), []))
        ref_links = [link(dest, BASE.parent / REF_NAMES[k], REF_NAMES[k]) for k in refs]
        wbs_anchor = '#'+code.rsplit('.', 1)[0].replace('.', '')
        previous = tasks[t['previous']] if t['previous'] else None
        next_t = tasks[t['next']] if t['next'] else None
        dep_refs = [link(dest, tasks[d]['path'], f"{tasks[d]['id']} / WBS {d} — {tasks[d]['title']}") for d in t['dependencies']]
        reviewer = 'Penerima gerbang yang ditetapkan pada 1.1.2' if t['gate_out'] else REVIEWERS[t['owner']]
        mode = 'Siklus dukungan; urutan mulai dan keluaran per insiden' if is_support else 'Finish-to-start pada antrean utama'
        text = [f"# {t['id']} — {t['title']}", '',
                f"Tiket untuk **WBS {code}**, urutan eksekusi **{t['sequence']:03d}/160**. "
                'Dokumen ini adalah instruksi pelaksanaan; langkah dan bukti di bawah belum dinyatakan sudah dikerjakan.', '',
                '## Identitas dan kendali', '',
                '| Atribut | Nilai |', '|---|---|',
                f"| Fase | {t['phase']} — {PHASES[t['phase']][1]} |",
                f"| Prioritas | {t['priority']}" + (' — hanya dikerjakan bila dipilih pada WF-G2 |' if t['priority']=='P1' else ' — wajib untuk rilis/cakupan yang diterima |'),
                '| Status | `not_started` |',
                f"| PIC peran | {t['owner']} |", '| PIC bernama | Ditunjuk saat mulai; penugasan tim diformalkan pada WBS 1.2.2 |',
                f'| Reviewer | {reviewer}; nama diisi saat penugasan |',
                '| Estimasi usaha | Belum ditetapkan; estimasi jam orang melalui WBS 1.2.3 |',
                '| Tanggal rencana / aktual | Belum ditetapkan / belum dimulai |',
                f'| Pola pelaksanaan | {mode} |',
                '| Sasaran | Rilis awal menurut SRS; fase 8 mengikuti masa dukungan yang disepakati |', '',
                '## Tujuan dan batas pekerjaan', '', t['acceptance'], '',
                'Kerjakan langkah di tiket ini dan serahkan keluaran yang disebutkan. '
                'Batas keseluruhan mengikuti SRS/WBS: admin dan guest, scraping sumber terpilih, '
                'snapshot historis, serta fitur P1 sesuai keputusan scope. '
                'Perubahan kebutuhan atau kriteria yang sudah dibekukan dicatat lewat change request.', '',
                '## Urutan dan syarat mulai', '']
        if previous:
            text.append('- **Pendahulu urutan:** ' + link(dest, previous['path'], f"{previous['id']} / WBS {previous['wbs']}") + '.')
        else:
            text.append('- **Pendahulu urutan:** tidak ada; mulai dari tiket ini setelah proposal dan planning dapat dibaca.')
        if t['gate_in']:
            gt = tasks[GATES[t['phase']-1]]
            text.append(f"- **Gerbang masuk:** {t['gate_in']} berstatus `accepted`; bukti pada " + link(dest, gt['path'], gt['id']) + '.')
        else:
            text.append('- **Gerbang masuk:** belum ada; fase ini menyiapkan penerimaan WF-G1.')
        if is_support:
            text.append('- **Aturan siklus:** mulai monitoring 8.1.1, kemudian triase 8.1.2 → perbaikan 8.1.3 → verifikasi 8.1.4 per insiden, lalu kembali ke monitoring. Tiket sebelumnya boleh `in_progress` jika keluaran siklus yang dibutuhkan sudah tersedia. Jangan menunggu seluruh masa dukungan selesai untuk merespons insiden. Tutup keempat rekap setelah periode dan kewajibannya selesai sebelum 8.2.1.')
        else:
            text.append('- **Aturan antrean:** pendahulu urutan dan dependensi hasil harus `done`. P1 boleh dilewati hanya bila `deferred` dengan keputusan scope tertaut; tiket wajib tidak boleh dilewati. Sebelum 8.2.1, semua rekap dukungan 8.1.1–8.1.4 harus selesai.')
        if t['priority'] == 'P1':
            text.append('- **Keputusan P1:** periksa keputusan WF-G2 dahulu. Jika tidak dipilih, isi `deferred`, alasan, pihak penerima, serta tautan keputusan; lanjutkan antrean tanpa mengklaim implementasi/test selesai. Bila fitur terpilih membutuhkan komponen P1 lain yang ditunda, selesaikan desain alternatif atau perubahan scope sebelum membangun.')
        text.extend(['- **Kesiapan:** input dapat diakses, PIC/reviewer ditunjuk, dan environment yang diperlukan tersedia sesuai fase. Sebelum WBS 1.2.2 selesai, gunakan penanggung jawab sementara yang dicatat saat tiket mulai; penetapan formal tidak memblokir tiket awal. Semua lokasi keluaran di bawah adalah target yang dibuat saat tiket dijalankan.', '',
                     '## Input dan dependensi hasil', '',
                     '- WBS sumber: ' + link(dest, wbs_path, 'WBS waterfall tiga level') + '.',
                     '- Referensi pendukung: ' + '; '.join(ref_links) + '.'])
        if t['dependencies']:
            text.append('- Ambil versi artefak yang sudah direview dari tiket berikut. Detail nama file tercantum pada tiket sumber; untuk dukungan gunakan keluaran per siklus yang relevan:')
            text.append('')
            for d, dl in zip(t['dependencies'], dep_refs):
                if t['gate_out']:
                    text.append(f'  - {dl}.')
                else:
                    filenames = ', '.join('`'+a+'`' for a in tasks[d]['artifacts'])
                    text.append(f'  - {dl}: {filenames}.')
        else:
            text.append('- Input awal: `Archives/Proposal.docx`, paket `Planning/`, `Planning/revisi.txt`, dan arahan pengguna yang sudah tercatat.')
        text.extend(['', '## Langkah pelaksanaan', ''])
        text.extend(f'{i}. {step}' for i, step in enumerate(t['steps'], 1))
        if code in {'4.4.2', '4.4.3', '4.4.4'}:
            text.extend(['', '**Checklist berulang per fasilitas:** catat kode, kabupaten/kecamatan, status awal, kandidat/query, sumber/URL bukti, precision, keputusan, alasan, reviewer, tanggal, dan tindak lanjut. Rekonsiliasi total per batch dengan antrean awal. Pekerjaan dapat dibagi menurut kabupaten tanpa menambah kode WBS level 4.'])
        if t['gate_out']:
            text.extend(['', f"**Pemeriksaan gerbang {t['gate_out']}:** tinjau seluruh tiket fase {t['phase']}, selain tiket gerbang ini, bukan hanya pendahulu terakhir. Semua P0 pendahulu wajib `done`, P1 yang dipilih wajib `done`, dan P1 ditunda mempunyai keputusan. Tiket gerbang ini menjadi `done` setelah keputusan `accepted` tercatat. Simpan keputusan `accepted` atau `rework`, nama penerima, tanggal, serta daftar versi yang diterima. `rework` tetap menahan fase berikutnya."])
        text.extend(['', '## Keluaran yang diserahkan', '',
                     f"Lokasi bukti yang diusulkan: `docs/pekerjaan/{t['id']}/`. Direktori dan berkas ini **belum dibuat oleh penyusunan tiket**; pelaksana membuatnya saat eksekusi. Kode aplikasi/data tetap di direktori desain, sedangkan catatan/hash/tautan bukti disimpan di sini.", ''])
        text.extend('- `'+name+'`.' for name in t['artifacts'])
        text.extend(['', '## Kriteria penerimaan dan verifikasi', '',
                     '- [ ] ' + t['acceptance'], '- [ ] ' + t['verification'],
                     '- [ ] Seluruh keluaran di atas tersedia, memiliki versi/tanggal, dan tautannya dicatat pada log kerja tiket.',
                     '- [ ] Reviewer memeriksa bukti aktual; tidak ada penghalang wajib yang disamarkan sebagai selesai.',
                     '', 'Cara verifikasi: ikuti pemeriksaan spesifik pada langkah dan kriteria di atas. '
                     'Untuk dokumen, lakukan penelusuran silang ke sumber/baseline; untuk kode/data, simpan perintah, input, '
                     'expected/actual, versi, dan log hasil; untuk gerbang, simpan keputusan penerima yang nyata. '
                     'Tiket uji yang terhambat tetap `blocked`, bukan `passed`.', '',
                     '## Jika terhambat atau gagal', '', BLOCKERS[t['phase']], '',
                     'Tulis masalah pada log kerja dengan dampak, owner tindak lanjut, dan dependensi yang tertahan. '
                     'Jangan mengubah expected result agar sesuai hasil gagal. Setelah perbaikan, ulangi pemeriksaan yang terdampak dan simpan bukti retest.', '',
                     '## Log kerja dan penutupan', '',
                     '| Tanggal | Pelaksana | Tindakan / hasil aktual | Tautan bukti / defect |',
                     '|---|---|---|---|', '| Belum ada | — | Belum dijalankan | — |', '',
                     '- PIC aktual: belum ditetapkan.', '- Jam aktual: belum dicatat.',
                     '- Versi kode / release_id / analysis_run_id: isi bila relevan saat eksekusi.',
                     '- Keputusan review: belum direview.', '- Reviewer dan tanggal penerimaan: belum tersedia.',
                     '- Isu tersisa / change request: belum dievaluasi.', ''])
        text.append(render_push_closure(t['id'], t['title']))
        if next_t:
            text.append('**Lanjut setelah syarat terpenuhi:** ' + link(dest, next_t['path'], f"{next_t['id']} — {next_t['title']}") + '.')
        else:
            text.append('**Akhir antrean:** proyek hanya dinyatakan ditutup setelah WF-G8 diterima; operasi berikutnya mengikuti penanggung jawab hasil transisi.')
        text.extend(['', link(dest, target / 'README.md', 'Kembali ke indeks dan aturan eksekusi'), ''])
        dest.write_text('\n'.join(text), encoding='utf-8')
        records.append({
            'id': t['id'], 'sequence': t['sequence'], 'wbs': code, 'title': t['title'],
            'phase': t['phase'], 'priority': t['priority'], 'owner_role': t['owner'],
            'reviewer_role': reviewer, 'initial_status': 'not_started',
            'file': dest.relative_to(target).as_posix(),
            'previous_ticket': previous['id'] if previous else None,
            'next_ticket': next_t['id'] if next_t else None,
            'gate_in': t['gate_in'], 'gate_out': t['gate_out'],
            'execution_mode': 'support_cycle' if is_support else 'finish_to_start',
            'dependencies': [
                {'ticket': tasks[d]['id'], 'wbs': d,
                 'condition': 'per_cycle_output' if code in SUPPORT and d in SUPPORT else
                 'done_or_approved_deferred' if tasks[d]['priority'] == 'P1' else 'done'}
                for d in t['dependencies']],
            'planned_evidence_directory': f"docs/pekerjaan/{t['id']}",
            'planned_artifacts': t['artifacts'], 'steps': t['steps'],
            'acceptance_from_wbs': t['acceptance'], 'verification': t['verification'],
            'additional_closing_task': closing_metadata(t['id']),
        })
    manifest = {
        'title': 'Katalog awal 160 tiket WBS waterfall GIS Puskesmas',
        'version': 2, 'date': '2026-10-22', 'wbs_sha256': hashlib.sha256(wbs_path.read_bytes()).hexdigest(),
        'status_policy': 'Status kerja aktual diedit pada file tiket. initial_status di katalog adalah snapshot penyusunan, bukan status live.',
        'sequence_policy': 'Urutan rekomendasi serial; dua penyesuaian prasyarat, empat P1 dapat deferred resmi, empat tiket dukungan berjalan sebagai siklus.',
        'github_closure_required': True,
        'tickets': records,
    }
    (target / 'daftar-tiket.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    index = ['# Tiket pelaksanaan waterfall — GIS Puskesmas', '',
             '**160 tiket untuk 160 tugas level 3**: 156 tiket inti P0 dan 4 tiket pembangunan P1 bersyarat, dalam 8 fase. '
             'Setiap tiket adalah satu file Markdown yang dapat langsung ditugaskan atau disalin ke issue tracker. '
             'Penyusunan ini tidak membuat issue pada layanan eksternal dan tidak menjalankan pekerjaan aplikasinya.', '',
             '**Mulai di ' + link(target/'README.md', tasks[order[0]]['path'], 'WF-001 — Menelaah proposal, planning awal, dan revisi pengguna') + '.** '
             'Ikuti tautan tiket berikutnya setelah memenuhi syarat selesai. Kode WBS menjaga hubungan dengan perencanaan; nomor WF menunjukkan urutan pelaksanaan.', '',
             '## Cara menjalankan antrean', '',
             '1. Baca tiket dan cek pendahulu urutan, gerbang masuk, serta dependensi hasil. Urutan WF adalah rekomendasi serial agar bisa diikuti satu per satu; dependensi hasil menunjukkan dokumen/data yang benar-benar digunakan.',
             '2. Tunjuk PIC/reviewer sementara saat memulai tiket awal; jangan menunggu WBS 1.2.2 untuk menjalankan WF-001. Formalisasikan penugasan seluruh tim pada 1.2.2 dan estimasi/jadwal pada 1.2.3. Semua tiket awalnya `not_started`; tanggal dan jam aktual tidak diisi sebelum eksekusi.',
             '3. Kerjakan langkah, simpan artefak di lokasi bukti yang diusulkan atau lokasi yang disepakati, lalu tautkan hasil aktual pada tiket. Lokasi artefak adalah target, bukan klaim bahwa file sudah ada.',
             '4. Ajukan `in_review` setelah kriteria terpenuhi. Reviewer menerima bukti sebelum status menjadi `done`. Bila gagal atau tidak punya input, gunakan `blocked` dengan alasan/owner; jangan melompati P0.',
             '5. Di akhir setiap fase, selesaikan tiket gerbang dan catat `accepted`/`rework`. Fase berikutnya hanya dimulai jika gerbang sebelumnya `accepted`.',
             '6. P1 yang tidak dipilih pada WF-G2 diberi `deferred` beserta keputusan, lalu dilewati. Empat P1 tidak berarti semua pengujian fitur tambahan boleh dilewati: validasi file backend pada WBS 5.4.4 tetap P0.',
             '7. Khusus WBS 8.1.1–8.1.4, mulai menurut urutan tetapi jalankan sebagai siklus selama masa dukungan. Output setiap insiden boleh diteruskan saat tiket masih `in_progress`; seluruh rekap harus `done` sebelum 8.2.1. Jika tak ada insiden, catat fakta tersebut, bukan menciptakan perbaikan atau hasil uji palsu.', '',
             'Perbaikan defect yang memblokir dependensi dikerjakan segera pada tiket/modul terkait dan diretest. WBS 5.6.3 mengonsolidasikan seluruh penutupan defect setelah UAT; bukan alasan menunggu sampai semua uji selesai untuk memperbaiki bug. Subcatatan defect/checklist fasilitas bukan tambahan tiket WBS level 3.', '',
             '## Penyesuaian urutan dari nomor WBS', '',
             '- WBS **1.2.4** dilaksanakan sebelum **1.2.3**: kebutuhan alat, layanan, dan biaya menjadi input estimasi usaha/jadwal.',
             '- WBS **6.1.3** dilaksanakan setelah **6.2.2** dan sebelum **6.2.3**: tabel akun tersedia setelah migration; baru konfigurasi final dan akun admin dibuat sebelum publikasi. Akses operator migration awal disiapkan pada 6.1.2.',
             '- WBS **8.1.1–8.1.4** mengikuti siklus pemeliharaan, sehingga pemantauan tidak perlu selesai satu periode sebelum insiden ditangani. Tidak ada perubahan kode maupun cakupan WBS.', '',
             '## Peran dan prioritas', '',
             'PM = koordinator proyek; AN = analis kebutuhan; DG = data/GIS; BE = backend/database; FE = frontend; QA = pengujian; OP = operasi. '
             'Peran kerja dapat dirangkap anggota tim; peran aplikasi tetap admin dan user/guest. Reviewer data/metode/keamanan sebisa mungkin berbeda dari pembuat.', '',
             'P0 berarti wajib dalam baseline rilis/proyek. P1 hanya empat tiket 4.10.1–4.10.4; desain/uji/penerimaan yang memuat bagian P1 tetap dikerjakan untuk bagian wajibnya. '
             'Keputusan P1 tidak boleh membuat fitur terpilih kehilangan komponen prasyarat: selesaikan desain alternatif atau revisi scope jika dependensi P1 lain ditunda.', '',
             '## Status, bukti, dan pemeliharaan dokumen', '',
             '- Status resmi ada di tabel identitas **masing-masing file tiket**, dengan riwayat aktual pada log kerja. Nilai awal bukan bukti pekerjaan sudah dimulai.',
             '- Urutan status normal: `not_started` → `in_progress` → `in_review` → `done`. Status `blocked` mencatat penghalang; `deferred` memerlukan keputusan scope.',
             '- Bukti minimal: versi/identitas input, tindakan, expected/actual untuk uji, keluaran, masalah, reviewer, dan tanggal penerimaan. Rahasia tidak ditulis ke bukti.',
             '- Direktori `docs/pekerjaan/WF-xxx/` di tiket adalah usulan tempat bukti saat proyek berjalan. Saat ini yang dibuat adalah tiket dan katalog, bukan artefak pelaksanaannya.',
             '- [daftar-tiket.json](daftar-tiket.json) adalah katalog metadata awal untuk diproses alat lain, bukan tracker status live atau format impor khusus Jira/Trello. Jika ID/dependensi berubah, perbarui katalog dan tautan terkait lalu validasi ulang.',
             '- Generator di `../bahan-tiket/susun_tiket.py` menolak menimpa folder tiket yang sudah ada agar status dan catatan manual tidak hilang. Pemeriksaan ulang memakai validator, bukan regenerasi.', '',
             '## Ringkasan fase', '', '| Fase | Kelompok | Jumlah tiket | Rentang urutan | Gerbang akhir |', '|---|---|---:|---|---|']
    for phase, (_, title) in PHASES.items():
        phase_tasks = [tasks[c] for c in order if tasks[c]['phase'] == phase]
        gate = tasks[GATES[phase]]
        index.append(f"| {phase} | {title} | {len(phase_tasks)} | {phase_tasks[0]['id']}–{phase_tasks[-1]['id']} | " + link(target/'README.md', gate['path'], f'WF-G{phase}') + ' |')
    for phase, (_, title) in PHASES.items():
        index.extend(['', f'## Fase {phase} — {title}', '',
                      '| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |',
                      '|---|---|---|---|---|---|'])
        for c in order:
            t = tasks[c]
            if t['phase'] != phase:
                continue
            prev = tasks[t['previous']]['id'] if t['previous'] else 'Mulai'
            if c in SUPPORT and c != '8.1.1':
                prev += ' (output per siklus)'
            index.append('| ' + link(target/'README.md', t['path'], t['id']) + f" | {c} | {t['title']} | {t['owner']} | {t['priority']} | {prev} |")
    index.extend(['', '## Referensi', '',
                  '- [WBS tiga level](../01-WBS-waterfall.md).',
                  '- [Indeks variasi waterfall](../README.md).',
                  '- [Planning awal](../../README.md).',
                  '- [Laporan pemeriksaan paket tiket](verifikasi-tiket.json).', '',
                  'Dokumen disusun 22 Oktober 2026. Penerimaan gerbang, akun/anggaran, tanggal, hasil uji, serta deployment adalah pekerjaan pada tiket terkait dan belum dinyatakan terlaksana.', ''])
    index.insert(index.index('## Ringkasan fase'), POLICY)
    (target / 'README.md').write_text('\n'.join(index), encoding='utf-8')
    print(json.dumps({'generated_tickets': len(records), 'priority_counts': dict(Counter(r['priority'] for r in records)), 'output': str(target)}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    generate()
