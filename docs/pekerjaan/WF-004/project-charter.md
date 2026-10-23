> Current baseline: accepted under [WF-G1](../WF-012/penerimaan-WF-G1.md) and [the college-project supplement](../WF-012/revisi-tugas-kuliah-untuk-persetujuan.md). The user is owner/approver; use free services and milestone-only scheduling. Earlier pending capacity, budget, and calendar statements below are historical assumptions superseded by that decision. No lecturer approval or team-hours commitment is implied.

# Project charter WebGIS Puskesmas Jawa Timur

Versi kandidat 1, 23 Oktober 2026. Status: disiapkan untuk review, belum menjadi baseline accepted. Mandat kerja fase 1 berasal dari instruksi pengguna dalam percakapan. Tidak ada pembelian atau deployment yang diotorisasi melalui dokumen ini.

## Tujuan dan hasil

Proyek menghasilkan WebGIS dan artefak penelitian untuk membaca persebaran 973 puskesmas historis Semester I 2024 pada 38 kabupaten/kota Jawa Timur, dikaitkan dengan penduduk, luas dan batas wilayah yang periodenya dinyatakan. Sasaran terukur mengikuti OBJ-01–10 pada WF-003.

Keluaran inti meliputi sumber terarsip/hash, adapter scraping, crosswalk, hasil kurasi dan review lokasi, Supabase PostgreSQL/PostGIS, aplikasi Laravel/Leaflet, analisis indikator dan radius, notebook Colab/HTML Folium, pengujian nyata, produksi, panduan, laporan dan dukungan awal. Guest membaca hasil terbit tanpa akun; admin mengelola proses internal. Akun teknis database bukan role aplikasi baru.

## Cakupan dan batas

P0 mencakup login/session, otorisasi dan command impor/review/analisis/publish/rollback/audit. Empat paket P1 adalah dashboard batch, layar review/publish, CSV publik dan ranking kecamatan; dipilih atau ditunda pada WF-G2. P2 meliputi rekam medis, registrasi publik, routing/waktu tempuh, optimasi lokasi dan analisis klaster statistik lanjutan. Perubahan P2 memerlukan change request.

Data missing tetap berada di master. Polygon, kode, tahun/unit dan lokasi harus ditelusuri. Buffer memakai meter, union overlap dan clip; hasil adalah cakupan geometris, bukan penduduk terlayani atau penetapan kepatuhan. Supabase menggantikan MySQL mengikuti revisi pengguna; proposal asli tetap disimpan.

## Organisasi dan kendali

Codex menyiapkan artefak teknis fase 1. Pengguna menjadi jalur keputusan yang tersedia. Tiga penulis proposal teridentifikasi tetapi pembagian peran dan kapasitas aktual masih menunggu konfirmasi. Tidak ada dinas, peserta UAT atau dosen yang dicatat telah menyetujui pekerjaan tanpa bukti.

Antrean 160 tiket dan gerbang WF-G1–G8 dipertahankan. Paket ini menyiapkan bahan fase 1 untuk ditinjau bersama; penyusunan bahan pendahulu tidak berarti tiket dependennya sudah diterima. Penutupan serial tetap memerlukan review dan pengiriman terverifikasi per tiket. Remote yang terkonfigurasi adalah origin/main; identitas commit memakai identitas Git pengguna.

## Milestone

| Gerbang | Keluaran | Tanggal |
|---|---|---|
| WF-G1 | Mandat, WBS, penugasan, sumber daya, estimasi dan kendali | Menunggu penerimaan paket ini |
| WF-G2 | Kebutuhan dan scope diterima | Relatif setelah G1; tanpa tanggal komitmen |
| WF-G3 | Desain dan handoff diterima | Setelah G2 |
| WF-G4 | Kandidat uji lengkap | Setelah implementasi/kurasi |
| WF-G5 | Uji/UAT/restore/reproduksi diterima | Setelah G4 dan retest |
| WF-G6 | Produksi terverifikasi | Setelah G5 dan akses layanan |
| WF-G7 | Serah terima dan dukungan disepakati | Setelah G6 |
| WF-G8 | Dukungan berakhir dan kewajiban ditutup | Sesuai periode yang disepakati di G7 |

Jadwal dan biaya menggunakan estimasi WF-007/008, bukan klaim delapan minggu atau anggaran yang belum disetujui. Risiko utama adalah pencarian lokasi, polygon historis, tahun indikator, kapasitas review dan akses layanan. Perubahan baseline mengikuti WF-010; bukti mengikuti WF-011.

## Syarat penerimaan charter

Pemilik proyek mengonfirmasi mandat, penerima, tim/kapasitas, pilihan sumber daya/batas biaya dan dasar jadwal. Keputusan sumber/periode/P1 yang memang menjadi pekerjaan fase 2 boleh tetap terbuka dengan owner dan batas WF-G2. Tidak ada keputusan accepted atau tanda tangan yang sudah diberikan untuk charter ini.
