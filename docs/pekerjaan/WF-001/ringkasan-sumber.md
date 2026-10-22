# Ringkasan sumber dan mandat proyek

Versi 1, 23 Oktober 2026. Disusun Codex atas instruksi pengguna untuk mengerjakan folder 01-inisiasi. Ini hasil telaah sumber; bukan hasil implementasi atau persetujuan akademik. Hash input tersedia pada `manifest-input.json` di folder ini.

## Sumber yang dibaca

Proposal dibaca dari paragraf dan tabel OOXML tanpa mengubah berkas. Nomor paragraf berikut menghitung seluruh elemen `w:p` pada `word/document.xml`, termasuk sel tabel. Tata letak Word tidak dinilai karena pekerjaan ini menelaah isi.

| Sumber | Lokasi | Hasil telaah |
|---|---|---|
| Archives/Proposal.docx | Paragraf 1, 16–31 | Penelitian persebaran puskesmas Jawa Timur; 38 kabupaten/kota, 973 fasilitas Semester I 2024; geocoding, choropleth, radius, Colab dan HTML |
| Archives/Proposal.docx | Paragraf 3–5 | Nama penulis: Ikhlas Putra Pambagyo, Ayudya Aldi Setiawan, Effandy Perwira Dwi Putra. Proposal tidak menetapkan kapasitas atau pembagian kerja |
| Archives/Proposal.docx | Paragraf 32–39 | Python, JavaScript, Laravel dan MySQL pada proposal; sumber Kemenkes/BPS |
| Planning/01-kebutuhan-dan-ruang-lingkup.md | Matriks FR, NFR dan Pemakai | 17 FR dan 8 NFR; membedakan asal P/U/R. Tabel role lama perlu dibaca dengan revisi pengguna |
| Planning/02-dataset-dan-audit.md | Temuan kuantitatif, tahun, geocoding | 565 pasangan kandidat, 408 kosong, 5 kelompok identik; nilai campuran tahun; belum ada bukti seluruh lokasi verified |
| Planning/03-arsitektur-dan-analisis.md | Stack, kontrak API, indikator, buffer | Laravel/Leaflet, Supabase/PostGIS, Python/Colab/Folium; rilis/run konsisten; buffer meter dan union/clip |
| Planning/04-supabase-dan-kamus-data.md | Tabel target dan izin DB | Staging berbeda dari produksi; runtime/worker/publisher adalah akun teknis; rilis published immutable |
| Planning/05-rencana-pengujian.md | Suite, fixture, UAT | Ekspektasi uji dan bukti actual; A08-PARAM wajib, A08-RANK bersyarat; belum ada aplikasi yang dinyatakan lulus |
| Planning/06-tahapan-dan-kebutuhan.md | Asumsi kapasitas dan backlog | 352 jam dan 8 minggu untuk tiga orang adalah estimasi awal, bukan komitmen. Harus dihitung ulang menurut WBS |
| Planning/07-sumber-dan-keputusan.md | ADR dan OPEN | Supabase adalah perubahan menurut pengguna; sumber/periode, cakupan, anggaran dan scope P1 masih perlu keputusan |
| Planning/revisi.txt | Baris 1 | Hanya admin dan user/guest; tidak ada role pemegang data; sumber diambil melalui scraping |
| Planning/Waterfall/01-WBS-waterfall.md | Dasar, 8 fase, 160 tugas | Variasi waterfall dengan gerbang WF-G1–G8; login admin dan command P0; empat tiket pembangunan P1 |
| Planning/Waterfall/panduan-eksekusi.md | Handoff, checkpoint, penutupan | Kerja satu tiket, bukti aktual, checkpoint lokasi/lifecycle, penutupan Git |

## Asal kebutuhan

| Asal | Kebutuhan | Keputusan pelaksanaan |
|---|---|---|
| P — proposal | 973 fasilitas/38 kabupaten-kota, snapshot 2024-S1 | Pertahankan master historis termasuk lokasi kosong; koreksi memerlukan bukti sumber |
| P — proposal | Geocoding, marker, choropleth, radius, Python/Colab/HTML, Laravel/JS | Masuk keluaran inti; marker cluster adalah pengelompokan visual |
| U — revisi pengguna yang tersimpan | Supabase menggantikan MySQL | PostgreSQL/PostGIS menjadi target; tidak membuat dua database aplikasi |
| U — revisi.txt | Admin dan guest; scraping | Admin menangani operasi internal; guest membaca hasil terbit tanpa registrasi. Scraping mempertahankan metadata dan snapshot historis |
| U — instruksi percakapan | Perbaiki paket lalu kerjakan folder 1 | Lingkup eksekusi saat ini adalah WF-001–012; fase 2 belum dibuka |
| R — planning | Search/filter, tabel/detail, metadata versi, immutability, audit, test, backup | Mendukung kebenaran dan operasional; rincian dibekukan dalam SRS/desain |
| R — planning | Dashboard/review UI admin, CSV dan ranking | Empat tiket WF-097–100 diputuskan satu per satu pada WF-G2 |

## Batas kesimpulan

Angka audit adalah temuan dari bahan lokal, bukan hasil scraping atau verifikasi lapangan baru. Tahun file tidak membuktikan tahun observasi. Lokasi missing tetap berada dalam jumlah administratif. Buffer hanya memakai titik facility yang memiliki bukti verified; radius geometris tidak membuktikan waktu tempuh, penduduk terlayani, atau keputusan pembangunan.

Laporan ini mencatat rasio 30.000 sebagai parameter dalam proposal/planning; tidak melakukan penetapan kepatuhan hukum. Rujukan regulasi dan metode harus diverifikasi pada penetapan kebutuhan terkait.

## Hasil pemeriksaan

Isi proposal, tujuh dokumen planning, revisi pengguna dan WBS telah ditelusuri. Konflik dan aturan prioritas dicatat pada `daftar-konflik.md`. Tidak ada tanggal penyerahan, budget, komitmen jam anggota, persetujuan dosen, atau hasil aplikasi yang diasumsikan sebagai fakta.
