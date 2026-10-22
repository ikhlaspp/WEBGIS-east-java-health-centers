# Tiket pelaksanaan waterfall — GIS Puskesmas

**160 tiket untuk 160 tugas level 3**: 156 tiket inti P0 dan 4 tiket pembangunan P1 bersyarat, dalam 8 fase. Setiap tiket adalah satu file Markdown yang dapat langsung ditugaskan atau disalin ke issue tracker. Penyusunan ini tidak membuat issue pada layanan eksternal dan tidak menjalankan pekerjaan aplikasinya.

**Mulai di [WF-001 — Menelaah proposal, planning awal, dan revisi pengguna](01-inisiasi/WF-001-WBS-1.1.1.md).** Ikuti tautan tiket berikutnya setelah memenuhi syarat selesai. Kode WBS menjaga hubungan dengan perencanaan; nomor WF menunjukkan urutan pelaksanaan.

## Cara menjalankan antrean

1. Baca tiket dan cek pendahulu urutan, gerbang masuk, serta dependensi hasil. Urutan WF adalah rekomendasi serial agar bisa diikuti satu per satu; dependensi hasil menunjukkan dokumen/data yang benar-benar digunakan.
2. Tunjuk PIC/reviewer sementara saat memulai tiket awal; jangan menunggu WBS 1.2.2 untuk menjalankan WF-001. Formalisasikan penugasan seluruh tim pada 1.2.2 dan estimasi/jadwal pada 1.2.3. Semua tiket awalnya `not_started`; tanggal dan jam aktual tidak diisi sebelum eksekusi.
3. Kerjakan langkah, simpan artefak di lokasi bukti yang diusulkan atau lokasi yang disepakati, lalu tautkan hasil aktual pada tiket. Lokasi artefak adalah target, bukan klaim bahwa file sudah ada.
4. Ajukan `in_review` setelah kriteria terpenuhi. Reviewer menerima bukti sebelum status menjadi `done`. Bila gagal atau tidak punya input, gunakan `blocked` dengan alasan/owner; jangan melompati P0.
5. Di akhir setiap fase, selesaikan tiket gerbang dan catat `accepted`/`rework`. Fase berikutnya hanya dimulai jika gerbang sebelumnya `accepted`.
6. P1 yang tidak dipilih pada WF-G2 diberi `deferred` beserta keputusan, lalu dilewati. Empat P1 tidak berarti semua pengujian fitur tambahan boleh dilewati: validasi file backend pada WBS 5.4.4 tetap P0.
7. Khusus WBS 8.1.1–8.1.4, mulai menurut urutan tetapi jalankan sebagai siklus selama masa dukungan. Output setiap insiden boleh diteruskan saat tiket masih `in_progress`; seluruh rekap harus `done` sebelum 8.2.1. Jika tak ada insiden, catat fakta tersebut, bukan menciptakan perbaikan atau hasil uji palsu.

Perbaikan defect yang memblokir dependensi dikerjakan segera pada tiket/modul terkait dan diretest. WBS 5.6.3 mengonsolidasikan seluruh penutupan defect setelah UAT; bukan alasan menunggu sampai semua uji selesai untuk memperbaiki bug. Subcatatan defect/checklist fasilitas bukan tambahan tiket WBS level 3.

## Penyesuaian urutan dari nomor WBS

- WBS **1.2.4** dilaksanakan sebelum **1.2.3**: kebutuhan alat, layanan, dan biaya menjadi input estimasi usaha/jadwal.
- WBS **6.1.3** dilaksanakan setelah **6.2.2** dan sebelum **6.2.3**: tabel akun tersedia setelah migration; baru konfigurasi final dan akun admin dibuat sebelum publikasi. Akses operator migration awal disiapkan pada 6.1.2.
- WBS **8.1.1–8.1.4** mengikuti siklus pemeliharaan, sehingga pemantauan tidak perlu selesai satu periode sebelum insiden ditangani. Tidak ada perubahan kode maupun cakupan WBS.

## Peran dan prioritas

PM = koordinator proyek; AN = analis kebutuhan; DG = data/GIS; BE = backend/database; FE = frontend; QA = pengujian; OP = operasi. Peran kerja dapat dirangkap anggota tim; peran aplikasi tetap admin dan user/guest. Reviewer data/metode/keamanan sebisa mungkin berbeda dari pembuat.

P0 berarti wajib dalam baseline rilis/proyek. P1 hanya empat tiket 4.10.1–4.10.4; desain/uji/penerimaan yang memuat bagian P1 tetap dikerjakan untuk bagian wajibnya. Keputusan P1 tidak boleh membuat fitur terpilih kehilangan komponen prasyarat: selesaikan desain alternatif atau revisi scope jika dependensi P1 lain ditunda.

## Status, bukti, dan pemeliharaan dokumen

- Status resmi ada di tabel identitas **masing-masing file tiket**, dengan riwayat aktual pada log kerja. Nilai awal bukan bukti pekerjaan sudah dimulai.
- Urutan status normal: `not_started` → `in_progress` → `in_review` → `done`. Status `blocked` mencatat penghalang; `deferred` memerlukan keputusan scope.
- Bukti minimal: versi/identitas input, tindakan, expected/actual untuk uji, keluaran, masalah, reviewer, dan tanggal penerimaan. Rahasia tidak ditulis ke bukti.
- Direktori `docs/pekerjaan/WF-xxx/` di tiket adalah usulan tempat bukti saat proyek berjalan. Saat ini yang dibuat adalah tiket dan katalog, bukan artefak pelaksanaannya.
- [daftar-tiket.json](daftar-tiket.json) adalah katalog metadata awal untuk diproses alat lain, bukan tracker status live atau format impor khusus Jira/Trello. Jika ID/dependensi berubah, perbarui katalog dan tautan terkait lalu validasi ulang.
- Generator di `../bahan-tiket/susun_tiket.py` menolak menimpa folder tiket yang sudah ada agar status dan catatan manual tidak hilang. Pemeriksaan ulang memakai validator, bukan regenerasi.

## Commit dan push setelah setiap tiket

Setiap tiket ditutup dengan task tambahan commit dan push GitHub. Ini checklist penutup pada tiket yang sama, bukan tiket WBS baru; jumlah tetap 160. Pelaksana menjalankannya setelah keluaran dan review tiket selesai. Seluruh langkah Git di dokumen ini masih rencana, bukan bukti commit/push sudah dilakukan.

**Persiapan satu kali sebelum WF-001:** pemilik proyek menautkan repository, menetapkan remote/branch tujuan, dan menyediakan autentikasi GitHub. Git lokal harus sudah diinisialisasi agar push tiket awal bisa berjalan; pekerjaan WBS 4.1.1 kemudian memeriksa dan melengkapi struktur repo yang sudah ada, tanpa menginisialisasi ulang atau menghapus riwayat. Remote/branch belum ditetapkan dalam paket ini dan tidak boleh ditebak.

Setelah konfigurasi tujuan dan akses tersedia, instruksi pengguna ini menjadi dasar menjalankan commit/push per tiket tanpa meminta konfirmasi rutin lagi. Larangan/izin teknis environment tetap berlaku; penolakan akses dicatat sebagai penghalang, bukan dianggap push berhasil.

Urutan penutup:

1. Selesaikan pemeriksaan/review teknis, catat hasil aktual, lalu perbarui status pekerjaan tiket. Status pekerjaan `done` berarti keluaran telah diterima secara lokal; **penutupan pengiriman tiket masih menunggu push terverifikasi**. P1 `deferred` tetap memerlukan commit/push keputusan penundaannya.
2. Periksa remote, branch, identitas Git efektif, dan perubahan yang akan dikirim. Stage hanya file terkait tiket serta bukti yang boleh masuk repo; jangan ikut memasukkan rahasia, dump, atau perubahan lain tanpa sengaja.
3. Buat commit bertanda ID tiket, misalnya `WF-001: selesaikan telaah proposal`. Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau trailer co-author. Periksa kembali metadata commit aktual karena hook/konfigurasi dapat memengaruhinya.
4. Push commit ke remote/branch yang ditetapkan dan periksa kode keluar. Tidak menggunakan force push. Jika remote telah berubah, fetch, integrasikan perubahan secara aman, ulangi pemeriksaan yang terdampak, lalu push kembali.
5. Verifikasi commit ada pada riwayat branch remote, lalu laporkan ID tiket, SHA/tautan commit, branch, dan hasil push. Antrean serial baru maju setelah bukti pengiriman tersedia; exception siklus dukungan tetap berjalan agar insiden tidak ditelantarkan, dengan pengiriman dilakukan per paket perbaikan.

**Jika repository/akses belum siap atau push gagal:** hasil kerja lokal tidak hilang; catat pengiriman `pending`/`blocked` dalam laporan pelaksanaan, jelaskan penyebab, dan jangan mengklaim tiket sudah terkirim. Pekerjaan teknis yang sudah diterima tidak perlu dijalankan ulang hanya karena koneksi gagal. Setelah hambatan selesai, kirim commit yang tertahan dan verifikasi.

**Bukti tanpa lingkaran commit:** simpan hasil push dan tautan SHA pada laporan percakapan, issue, atau log CI setelah push. Hash sebuah commit tidak bisa disisipkan ke dalam commit yang sama. Bila bukti perlu disimpan di repository, catat pada commit berikutnya sebagai catatan pengiriman tiket sebelumnya; jangan membuat rangkaian commit/amend hanya untuk memperbarui hash itu sendiri. Checklist penutup merupakan instruksi; bukti keberhasilan aktual adalah verifikasi remote dan laporan pengiriman.

Status/file tiket adalah sumber status pekerjaan, sedangkan laporan push adalah sumber status pengiriman. `daftar-tiket.json` hanya mencatat kebijakan penutup dan status awal, bukan status push live. Untuk tiket gerbang, syarat melanjutkan fase adalah keputusan `accepted` **dan** pengiriman paket bukti terverifikasi. Untuk WBS 8.1.1–8.1.4, kirim checkpoint yang selesai per siklus dan rekap final pada akhir dukungan.

## Ringkasan fase

| Fase | Kelompok | Jumlah tiket | Rentang urutan | Gerbang akhir |
|---|---|---:|---|---|
| 1 | Inisiasi dan perencanaan proyek | 12 | WF-001–WF-012 | [WF-G1](01-inisiasi/WF-012-WBS-1.3.4.md) |
| 2 | Analisis kebutuhan | 16 | WF-013–WF-028 | [WF-G2](02-kebutuhan/WF-028-WBS-2.4.4.md) |
| 3 | Perancangan sistem | 24 | WF-029–WF-052 | [WF-G3](03-desain/WF-052-WBS-3.6.4.md) |
| 4 | Implementasi dan penyiapan data | 52 | WF-053–WF-104 | [WF-G4](04-implementasi/WF-104-WBS-4.11.4.md) |
| 5 | Pengujian dan penerimaan | 24 | WF-105–WF-128 | [WF-G5](05-pengujian/WF-128-WBS-5.6.4.md) |
| 6 | Deployment dan verifikasi produksi | 12 | WF-129–WF-140 | [WF-G6](06-deployment/WF-140-WBS-6.3.4.md) |
| 7 | Dokumentasi akhir dan serah terima | 12 | WF-141–WF-152 | [WF-G7](07-serah-terima/WF-152-WBS-7.3.4.md) |
| 8 | Pemeliharaan awal dan penutupan | 8 | WF-153–WF-160 | [WF-G8](08-penutupan/WF-160-WBS-8.2.4.md) |

## Fase 1 — Inisiasi dan perencanaan proyek

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-001](01-inisiasi/WF-001-WBS-1.1.1.md) | 1.1.1 | Menelaah proposal, planning awal, dan revisi pengguna | AN | P0 | Mulai |
| [WF-002](01-inisiasi/WF-002-WBS-1.1.2.md) | 1.1.2 | Mengidentifikasi stakeholder dan penerima hasil | PM | P0 | WF-001 |
| [WF-003](01-inisiasi/WF-003-WBS-1.1.3.md) | 1.1.3 | Menentukan sasaran dan ukuran keberhasilan proyek | PM | P0 | WF-002 |
| [WF-004](01-inisiasi/WF-004-WBS-1.1.4.md) | 1.1.4 | Menyusun dan meninjau project charter | PM | P0 | WF-003 |
| [WF-005](01-inisiasi/WF-005-WBS-1.2.1.md) | 1.2.1 | Memeriksa kelengkapan WBS bersama tim | PM | P0 | WF-004 |
| [WF-006](01-inisiasi/WF-006-WBS-1.2.2.md) | 1.2.2 | Menetapkan penanggung jawab dan reviewer paket kerja | PM | P0 | WF-005 |
| [WF-007](01-inisiasi/WF-007-WBS-1.2.4.md) | 1.2.4 | Menyusun kebutuhan biaya, alat, akun, dan lingkungan | OP | P0 | WF-006 |
| [WF-008](01-inisiasi/WF-008-WBS-1.2.3.md) | 1.2.3 | Menaksir usaha, dependensi, dan durasi dari paket kerja | PM | P0 | WF-007 |
| [WF-009](01-inisiasi/WF-009-WBS-1.3.1.md) | 1.3.1 | Membuat daftar risiko dan rencana penanganannya | PM | P0 | WF-008 |
| [WF-010](01-inisiasi/WF-010-WBS-1.3.2.md) | 1.3.2 | Menetapkan tata cara perubahan scope dan keputusan | PM | P0 | WF-009 |
| [WF-011](01-inisiasi/WF-011-WBS-1.3.3.md) | 1.3.3 | Menetapkan standar bukti selesai dan penyimpanan artefak | QA | P0 | WF-010 |
| [WF-012](01-inisiasi/WF-012-WBS-1.3.4.md) | 1.3.4 | Menetapkan pelaporan rutin dan menerima WF-G1 | PM | P0 | WF-011 |

## Fase 2 — Analisis kebutuhan

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-013](02-kebutuhan/WF-013-WBS-2.1.1.md) | 2.1.1 | Menggali skenario penggunaan admin dan guest | AN | P0 | WF-012 |
| [WF-014](02-kebutuhan/WF-014-WBS-2.1.2.md) | 2.1.2 | Menetapkan kebutuhan fungsional dan prioritas rilis | AN | P0 | WF-013 |
| [WF-015](02-kebutuhan/WF-015-WBS-2.1.3.md) | 2.1.3 | Menetapkan batas akses aplikasi | BE | P0 | WF-014 |
| [WF-016](02-kebutuhan/WF-016-WBS-2.1.4.md) | 2.1.4 | Menentukan isi setiap halaman dan alur navigasi | FE | P0 | WF-015 |
| [WF-017](02-kebutuhan/WF-017-WBS-2.2.1.md) | 2.2.1 | Menginventarisasi arsip dan kesenjangan dataset | DG | P0 | WF-016 |
| [WF-018](02-kebutuhan/WF-018-WBS-2.2.2.md) | 2.2.2 | Memeriksa kelayakan sumber untuk scraping/pengunduhan | DG | P0 | WF-017 |
| [WF-019](02-kebutuhan/WF-019-WBS-2.2.3.md) | 2.2.3 | Menetapkan periode, satuan, dan identitas sumber | DG | P0 | WF-018 |
| [WF-020](02-kebutuhan/WF-020-WBS-2.2.4.md) | 2.2.4 | Menentukan aturan kelengkapan dan penanganan data bermasalah | DG | P0 | WF-019 |
| [WF-021](02-kebutuhan/WF-021-WBS-2.3.1.md) | 2.3.1 | Menentukan indikator tabular dan cara agregasinya | DG | P0 | WF-020 |
| [WF-022](02-kebutuhan/WF-022-WBS-2.3.2.md) | 2.3.2 | Menentukan kebutuhan peta tematik dan legenda | DG | P0 | WF-021 |
| [WF-023](02-kebutuhan/WF-023-WBS-2.3.3.md) | 2.3.3 | Menentukan kebutuhan analisis radius | DG | P0 | WF-022 |
| [WF-024](02-kebutuhan/WF-024-WBS-2.3.4.md) | 2.3.4 | Menetapkan keluaran penelitian dan batas kesimpulan | AN | P0 | WF-023 |
| [WF-025](02-kebutuhan/WF-025-WBS-2.4.1.md) | 2.4.1 | Menetapkan target performa dan kegunaan | QA | P0 | WF-024 |
| [WF-026](02-kebutuhan/WF-026-WBS-2.4.2.md) | 2.4.2 | Menetapkan target keamanan, backup, dan reproduksibilitas | BE | P0 | WF-025 |
| [WF-027](02-kebutuhan/WF-027-WBS-2.4.3.md) | 2.4.3 | Menyusun strategi UAT serta matriks kebutuhan–uji | QA | P0 | WF-026 |
| [WF-028](02-kebutuhan/WF-028-WBS-2.4.4.md) | 2.4.4 | Menyelesaikan SRS dan menerima WF-G2 | PM | P0 | WF-027 |

## Fase 3 — Perancangan sistem

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-029](03-desain/WF-029-WBS-3.1.1.md) | 3.1.1 | Merancang hubungan Laravel, Leaflet, Supabase, dan Colab | BE | P0 | WF-028 |
| [WF-030](03-desain/WF-030-WBS-3.1.2.md) | 3.1.2 | Merancang lingkungan development, test/staging, dan produksi | OP | P0 | WF-029 |
| [WF-031](03-desain/WF-031-WBS-3.1.3.md) | 3.1.3 | Merancang struktur kode dan alur integrasi | BE | P0 | WF-030 |
| [WF-032](03-desain/WF-032-WBS-3.1.4.md) | 3.1.4 | Merancang proses batch dan penanganan kegagalan | BE | P0 | WF-031 |
| [WF-033](03-desain/WF-033-WBS-3.2.1.md) | 3.2.1 | Membuat ERD dan kamus data final | BE | P0 | WF-032 |
| [WF-034](03-desain/WF-034-WBS-3.2.2.md) | 3.2.2 | Merancang constraint, indeks, dan migrasi | BE | P0 | WF-033 |
| [WF-035](03-desain/WF-035-WBS-3.2.3.md) | 3.2.3 | Merancang otorisasi admin dan akun teknis database | BE | P0 | WF-034 |
| [WF-036](03-desain/WF-036-WBS-3.2.4.md) | 3.2.4 | Merancang versi rilis, publikasi, dan pemulihan | BE | P0 | WF-035 |
| [WF-037](03-desain/WF-037-WBS-3.3.1.md) | 3.3.1 | Merancang adapter pengambilan tiap sumber | DG | P0 | WF-036 |
| [WF-038](03-desain/WF-038-WBS-3.3.2.md) | 3.3.2 | Merancang normalisasi dan crosswalk wilayah | DG | P0 | WF-037 |
| [WF-039](03-desain/WF-039-WBS-3.3.3.md) | 3.3.3 | Merancang pencarian dan review koordinat | DG | P0 | WF-038 |
| [WF-040](03-desain/WF-040-WBS-3.3.4.md) | 3.3.4 | Merancang staging dan laporan kualitas | DG | P0 | WF-039 |
| [WF-041](03-desain/WF-041-WBS-3.4.1.md) | 3.4.1 | Menulis spesifikasi rumus dan contoh hasil acuan | DG | P0 | WF-040 |
| [WF-042](03-desain/WF-042-WBS-3.4.2.md) | 3.4.2 | Merancang operasi spasial dan toleransi | DG | P0 | WF-041 |
| [WF-043](03-desain/WF-043-WBS-3.4.3.md) | 3.4.3 | Merancang GeoJSON dan kelas choropleth | DG | P0 | WF-042 |
| [WF-044](03-desain/WF-044-WBS-3.4.4.md) | 3.4.4 | Merancang notebook dan manifest hasil | DG | P0 | WF-043 |
| [WF-045](03-desain/WF-045-WBS-3.5.1.md) | 3.5.1 | Menentukan kontrak endpoint dan respons | BE | P0 | WF-044 |
| [WF-046](03-desain/WF-046-WBS-3.5.2.md) | 3.5.2 | Membuat wireframe halaman publik | FE | P0 | WF-045 |
| [WF-047](03-desain/WF-047-WBS-3.5.3.md) | 3.5.3 | Merancang interaksi dan keadaan antarmuka | FE | P0 | WF-046 |
| [WF-048](03-desain/WF-048-WBS-3.5.4.md) | 3.5.4 | Merancang login admin dan fitur P1 terpilih | FE | P0 | WF-047 |
| [WF-049](03-desain/WF-049-WBS-3.6.1.md) | 3.6.1 | Menyiapkan spesifikasi fixture dan expected result | QA | P0 | WF-048 |
| [WF-050](03-desain/WF-050-WBS-3.6.2.md) | 3.6.2 | Menyusun prosedur uji integrasi dan nonfungsional | QA | P0 | WF-049 |
| [WF-051](03-desain/WF-051-WBS-3.6.3.md) | 3.6.3 | Menyusun prosedur UAT dan kriteria gerbang rilis | QA | P0 | WF-050 |
| [WF-052](03-desain/WF-052-WBS-3.6.4.md) | 3.6.4 | Meninjau konsistensi desain dan menerima WF-G3 | PM | P0 | WF-051 |

## Fase 4 — Implementasi dan penyiapan data

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-053](04-implementasi/WF-053-WBS-4.1.1.md) | 4.1.1 | Membuat repositori dan struktur proyek | BE | P0 | WF-052 |
| [WF-054](04-implementasi/WF-054-WBS-4.1.2.md) | 4.1.2 | Menyiapkan Laravel dan build frontend | BE | P0 | WF-053 |
| [WF-055](04-implementasi/WF-055-WBS-4.1.3.md) | 4.1.3 | Menyiapkan Python, Colab, dan alat pengujian | DG | P0 | WF-054 |
| [WF-056](04-implementasi/WF-056-WBS-4.1.4.md) | 4.1.4 | Menyiapkan pipeline pemeriksaan otomatis | QA | P0 | WF-055 |
| [WF-057](04-implementasi/WF-057-WBS-4.2.1.md) | 4.2.1 | Mengimplementasikan pengunduh dan parser data fasilitas | DG | P0 | WF-056 |
| [WF-058](04-implementasi/WF-058-WBS-4.2.2.md) | 4.2.2 | Mengimplementasikan pengambilan data penduduk dan luas | DG | P0 | WF-057 |
| [WF-059](04-implementasi/WF-059-WBS-4.2.3.md) | 4.2.3 | Mengimplementasikan pengambilan kode dan polygon wilayah | DG | P0 | WF-058 |
| [WF-060](04-implementasi/WF-060-WBS-4.2.4.md) | 4.2.4 | Menambahkan cache, retry, dan pemeriksaan kelengkapan scraping | DG | P0 | WF-059 |
| [WF-061](04-implementasi/WF-061-WBS-4.2.5.md) | 4.2.5 | Menjalankan pengambilan sumber dan membekukan input mentah | DG | P0 | WF-060 |
| [WF-062](04-implementasi/WF-062-WBS-4.3.1.md) | 4.3.1 | Mengekstrak dan menormalisasi tabel sumber | DG | P0 | WF-061 |
| [WF-063](04-implementasi/WF-063-WBS-4.3.2.md) | 4.3.2 | Menyelesaikan crosswalk kode serta alias wilayah | DG | P0 | WF-062 |
| [WF-064](04-implementasi/WF-064-WBS-4.3.3.md) | 4.3.3 | Memisahkan subtotal dan merekonsiliasi master fasilitas | DG | P0 | WF-063 |
| [WF-065](04-implementasi/WF-065-WBS-4.3.4.md) | 4.3.4 | Memverifikasi angka penduduk, luas, tahun, dan unit | DG | P0 | WF-064 |
| [WF-066](04-implementasi/WF-066-WBS-4.3.5.md) | 4.3.5 | Memvalidasi polygon dan kelengkapan master wilayah | DG | P0 | WF-065 |
| [WF-067](04-implementasi/WF-067-WBS-4.4.1.md) | 4.4.1 | Menyiapkan antrean geocoding dan pencatatan bukti | DG | P0 | WF-066 |
| [WF-068](04-implementasi/WF-068-WBS-4.4.2.md) | 4.4.2 | Mereview 565 pasangan koordinat yang sudah tersedia | DG | P0 | WF-067 |
| [WF-069](04-implementasi/WF-069-WBS-4.4.3.md) | 4.4.3 | Menelusuri 408 fasilitas tanpa koordinat | DG | P0 | WF-068 |
| [WF-070](04-implementasi/WF-070-WBS-4.4.4.md) | 4.4.4 | Menyelesaikan anomali koordinat dan konflik wilayah | DG | P0 | WF-069 |
| [WF-071](04-implementasi/WF-071-WBS-4.4.5.md) | 4.4.5 | Membekukan laporan kelayakan data spasial | DG | P0 | WF-070 |
| [WF-072](04-implementasi/WF-072-WBS-4.5.1.md) | 4.5.1 | Menyiapkan database development dan test dengan PostGIS | BE | P0 | WF-071 |
| [WF-073](04-implementasi/WF-073-WBS-4.5.2.md) | 4.5.2 | Membuat migration tabel, constraint, dan indeks | BE | P0 | WF-072 |
| [WF-074](04-implementasi/WF-074-WBS-4.5.3.md) | 4.5.3 | Mengimplementasikan grants dan pembatasan akses data | BE | P0 | WF-073 |
| [WF-075](04-implementasi/WF-075-WBS-4.5.4.md) | 4.5.4 | Membuat impor staging dan promosi data tervalidasi | BE | P0 | WF-074 |
| [WF-076](04-implementasi/WF-076-WBS-4.5.5.md) | 4.5.5 | Memuat kandidat dataset hasil kurasi | BE | P0 | WF-075 |
| [WF-077](04-implementasi/WF-077-WBS-4.6.1.md) | 4.6.1 | Membuat perhitungan indikator kecamatan | DG | P0 | WF-076 |
| [WF-078](04-implementasi/WF-078-WBS-4.6.2.md) | 4.6.2 | Membuat agregasi kabupaten dan provinsi | DG | P0 | WF-077 |
| [WF-079](04-implementasi/WF-079-WBS-4.6.3.md) | 4.6.3 | Membuat buffer radius titik yang terverifikasi | DG | P0 | WF-078 |
| [WF-080](04-implementasi/WF-080-WBS-4.6.4.md) | 4.6.4 | Membuat union, clip, dan luas cakupan wilayah | DG | P0 | WF-079 |
| [WF-081](04-implementasi/WF-081-WBS-4.6.5.md) | 4.6.5 | Menyimpan hasil run dan layer tematik | DG | P0 | WF-080 |
| [WF-082](04-implementasi/WF-082-WBS-4.7.1.md) | 4.7.1 | Membuat API rilis, wilayah, dan katalog sumber | BE | P0 | WF-081 |
| [WF-083](04-implementasi/WF-083-WBS-4.7.2.md) | 4.7.2 | Membuat API fasilitas, pencarian, filter, dan detail | BE | P0 | WF-082 |
| [WF-084](04-implementasi/WF-084-WBS-4.7.3.md) | 4.7.3 | Membuat API statistik, GeoJSON, dan buffer | BE | P0 | WF-083 |
| [WF-085](04-implementasi/WF-085-WBS-4.7.4.md) | 4.7.4 | Membuat login/logout admin dan otorisasi operasi internal | BE | P0 | WF-084 |
| [WF-086](04-implementasi/WF-086-WBS-4.7.5.md) | 4.7.5 | Membuat command review, analisis, publish, rollback, dan audit | BE | P0 | WF-085 |
| [WF-087](04-implementasi/WF-087-WBS-4.8.1.md) | 4.8.1 | Membuat layout, navigasi, dan dashboard | FE | P0 | WF-086 |
| [WF-088](04-implementasi/WF-088-WBS-4.8.2.md) | 4.8.2 | Membuat peta dasar, marker, cluster, dan popup | FE | P0 | WF-087 |
| [WF-089](04-implementasi/WF-089-WBS-4.8.3.md) | 4.8.3 | Membuat pencarian dan filter bertingkat | FE | P0 | WF-088 |
| [WF-090](04-implementasi/WF-090-WBS-4.8.4.md) | 4.8.4 | Membuat layer choropleth, buffer, dan legenda | FE | P0 | WF-089 |
| [WF-091](04-implementasi/WF-091-WBS-4.8.5.md) | 4.8.5 | Membuat tabel dan halaman detail fasilitas/kecamatan | FE | P0 | WF-090 |
| [WF-092](04-implementasi/WF-092-WBS-4.8.6.md) | 4.8.6 | Membuat halaman metodologi dan penanganan state UI | FE | P0 | WF-091 |
| [WF-093](04-implementasi/WF-093-WBS-4.9.1.md) | 4.9.1 | Menghubungkan notebook ke snapshot rilis yang aman | DG | P0 | WF-092 |
| [WF-094](04-implementasi/WF-094-WBS-4.9.2.md) | 4.9.2 | Mengintegrasikan modul analisis ke notebook | DG | P0 | WF-093 |
| [WF-095](04-implementasi/WF-095-WBS-4.9.3.md) | 4.9.3 | Membuat visualisasi Folium dan ekspor HTML/tabel | DG | P0 | WF-094 |
| [WF-096](04-implementasi/WF-096-WBS-4.9.4.md) | 4.9.4 | Menambahkan manifest dan panduan Run all | DG | P0 | WF-095 |
| [WF-097](04-implementasi/WF-097-WBS-4.10.1.md) | 4.10.1 | Membuat dashboard admin untuk menjalankan dan memantau batch | FE | P1 | WF-096 |
| [WF-098](04-implementasi/WF-098-WBS-4.10.2.md) | 4.10.2 | Membuat layar review data dan publikasi rilis | FE | P1 | WF-097 |
| [WF-099](04-implementasi/WF-099-WBS-4.10.3.md) | 4.10.3 | Membuat ekspor CSV hasil filter | BE | P1 | WF-098 |
| [WF-100](04-implementasi/WF-100-WBS-4.10.4.md) | 4.10.4 | Membuat daftar prioritas kecamatan | FE | P1 | WF-099 |
| [WF-101](04-implementasi/WF-101-WBS-4.11.1.md) | 4.11.1 | Menghubungkan pipeline, database, API, UI, dan artefak | BE | P0 | WF-100 |
| [WF-102](04-implementasi/WF-102-WBS-4.11.2.md) | 4.11.2 | Melengkapi unit/component test modul yang berubah | QA | P0 | WF-101 |
| [WF-103](04-implementasi/WF-103-WBS-4.11.3.md) | 4.11.3 | Menjalankan smoke test dan memperbaiki kegagalan integrasi | QA | P0 | WF-102 |
| [WF-104](04-implementasi/WF-104-WBS-4.11.4.md) | 4.11.4 | Membekukan kandidat uji dan menerima WF-G4 | PM | P0 | WF-103 |

## Fase 5 — Pengujian dan penerimaan

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-105](05-pengujian/WF-105-WBS-5.1.1.md) | 5.1.1 | Menguji kegagalan sumber dan perubahan struktur scraping | QA | P0 | WF-104 |
| [WF-106](05-pengujian/WF-106-WBS-5.1.2.md) | 5.1.2 | Menguji integritas identitas, jumlah, dan kategori | QA | P0 | WF-105 |
| [WF-107](05-pengujian/WF-107-WBS-5.1.3.md) | 5.1.3 | Menguji mapping, tahun, unit, dan nilai berisiko | QA | P0 | WF-106 |
| [WF-108](05-pengujian/WF-108-WBS-5.1.4.md) | 5.1.4 | Menguji pengulangan ETL dan konsistensi provenance | QA | P0 | WF-107 |
| [WF-109](05-pengujian/WF-109-WBS-5.2.1.md) | 5.2.1 | Menguji formula, pembulatan, null, nol, dan agregasi | QA | P0 | WF-108 |
| [WF-110](05-pengujian/WF-110-WBS-5.2.2.md) | 5.2.2 | Menguji kelayakan koordinat dan join peta | QA | P0 | WF-109 |
| [WF-111](05-pengujian/WF-111-WBS-5.2.3.md) | 5.2.3 | Menguji radius, overlap, clip, geometri, dan pulau | QA | P0 | WF-110 |
| [WF-112](05-pengujian/WF-112-WBS-5.2.4.md) | 5.2.4 | Membandingkan hasil spasial lintas implementasi | DG | P0 | WF-111 |
| [WF-113](05-pengujian/WF-113-WBS-5.3.1.md) | 5.3.1 | Menguji migration, constraint, dan impor | QA | P0 | WF-112 |
| [WF-114](05-pengujian/WF-114-WBS-5.3.2.md) | 5.3.2 | Menguji konsistensi rilis, rollback, dan kegagalan layanan | QA | P0 | WF-113 |
| [WF-115](05-pengujian/WF-115-WBS-5.3.3.md) | 5.3.3 | Menguji session, otorisasi, injeksi, dan keamanan popup | QA | P0 | WF-114 |
| [WF-116](05-pengujian/WF-116-WBS-5.3.4.md) | 5.3.4 | Menguji paparan rahasia dan izin database aktual | QA | P0 | WF-115 |
| [WF-117](05-pengujian/WF-117-WBS-5.4.1.md) | 5.4.1 | Menguji navigasi, peta, pencarian, dan filter | QA | P0 | WF-116 |
| [WF-118](05-pengujian/WF-118-WBS-5.4.2.md) | 5.4.2 | Menguji choropleth, statistik, detail, dan metode | QA | P0 | WF-117 |
| [WF-119](05-pengujian/WF-119-WBS-5.4.3.md) | 5.4.3 | Menguji responsivitas, aksesibilitas, dan request bersaing | QA | P0 | WF-118 |
| [WF-120](05-pengujian/WF-120-WBS-5.4.4.md) | 5.4.4 | Menguji fitur P1 terpilih dan validasi file backend P0 | QA | P0 | WF-119 |
| [WF-121](05-pengujian/WF-121-WBS-5.5.1.md) | 5.5.1 | Mengukur waktu muat, respons API, dan beban staging | QA | P0 | WF-120 |
| [WF-122](05-pengujian/WF-122-WBS-5.5.2.md) | 5.5.2 | Menguji backup dan restore database serta artefak | OP | P0 | WF-121 |
| [WF-123](05-pengujian/WF-123-WBS-5.5.3.md) | 5.5.3 | Menjalankan Colab dari runtime bersih dan mengulang run | QA | P0 | WF-122 |
| [WF-124](05-pengujian/WF-124-WBS-5.5.4.md) | 5.5.4 | Membandingkan HTML Folium dengan aplikasi | QA | P0 | WF-123 |
| [WF-125](05-pengujian/WF-125-WBS-5.6.1.md) | 5.6.1 | Menyiapkan peserta, kandidat rilis, dan instrumen UAT | QA | P0 | WF-124 |
| [WF-126](05-pengujian/WF-126-WBS-5.6.2.md) | 5.6.2 | Melaksanakan UAT dan merangkum temuan | QA | P0 | WF-125 |
| [WF-127](05-pengujian/WF-127-WBS-5.6.3.md) | 5.6.3 | Memperbaiki defect dan menjalankan retest/regresi | QA | P0 | WF-126 |
| [WF-128](05-pengujian/WF-128-WBS-5.6.4.md) | 5.6.4 | Menyelesaikan laporan uji dan menerima WF-G5 | PM | P0 | WF-127 |

## Fase 6 — Deployment dan verifikasi produksi

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-129](06-deployment/WF-129-WBS-6.1.1.md) | 6.1.1 | Menyiapkan hosting, domain bila diperlukan, dan HTTPS | OP | P0 | WF-128 |
| [WF-130](06-deployment/WF-130-WBS-6.1.2.md) | 6.1.2 | Menyiapkan Supabase produksi dan penyimpanan artefak | BE | P0 | WF-129 |
| [WF-131](06-deployment/WF-131-WBS-6.1.4.md) | 6.1.4 | Menyiapkan runbook deployment dan titik pemulihan | OP | P0 | WF-130 |
| [WF-132](06-deployment/WF-132-WBS-6.2.1.md) | 6.2.1 | Memasang versi aplikasi yang telah diterima | OP | P0 | WF-131 |
| [WF-133](06-deployment/WF-133-WBS-6.2.2.md) | 6.2.2 | Menjalankan migration dan memuat dataset final | BE | P0 | WF-132 |
| [WF-134](06-deployment/WF-134-WBS-6.1.3.md) | 6.1.3 | Memasang konfigurasi rahasia dan akun admin awal | OP | P0 | WF-133 |
| [WF-135](06-deployment/WF-135-WBS-6.2.3.md) | 6.2.3 | Memasang hasil analisis dan menerbitkan rilis aktif | BE | P0 | WF-134 |
| [WF-136](06-deployment/WF-136-WBS-6.2.4.md) | 6.2.4 | Mengaktifkan worker, monitoring, dan backup | OP | P0 | WF-135 |
| [WF-137](06-deployment/WF-137-WBS-6.3.1.md) | 6.3.1 | Menjalankan smoke test produksi | QA | P0 | WF-136 |
| [WF-138](06-deployment/WF-138-WBS-6.3.2.md) | 6.3.2 | Memeriksa akses publik dan konfigurasi operasi | QA | P0 | WF-137 |
| [WF-139](06-deployment/WF-139-WBS-6.3.3.md) | 6.3.3 | Menangani kegagalan penerapan atau memvalidasi kesiapan rollback | OP | P0 | WF-138 |
| [WF-140](06-deployment/WF-140-WBS-6.3.4.md) | 6.3.4 | Mencatat hasil deployment dan menerima WF-G6 | PM | P0 | WF-139 |

## Fase 7 — Dokumentasi akhir dan serah terima

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-141](07-serah-terima/WF-141-WBS-7.1.1.md) | 7.1.1 | Memfinalisasi panduan guest dan admin | FE | P0 | WF-140 |
| [WF-142](07-serah-terima/WF-142-WBS-7.1.2.md) | 7.1.2 | Memfinalisasi panduan instalasi dan operasi | OP | P0 | WF-141 |
| [WF-143](07-serah-terima/WF-143-WBS-7.1.3.md) | 7.1.3 | Memfinalisasi dokumentasi desain as-built | BE | P0 | WF-142 |
| [WF-144](07-serah-terima/WF-144-WBS-7.1.4.md) | 7.1.4 | Memfinalisasi panduan data dan reproduksi analisis | DG | P0 | WF-143 |
| [WF-145](07-serah-terima/WF-145-WBS-7.2.1.md) | 7.2.1 | Menulis hasil analisis beserta keterbatasannya | DG | P0 | WF-144 |
| [WF-146](07-serah-terima/WF-146-WBS-7.2.2.md) | 7.2.2 | Menyusun bagian implementasi dan pengujian laporan | QA | P0 | WF-145 |
| [WF-147](07-serah-terima/WF-147-WBS-7.2.3.md) | 7.2.3 | Menyiapkan materi presentasi dan skenario demonstrasi | PM | P0 | WF-146 |
| [WF-148](07-serah-terima/WF-148-WBS-7.2.4.md) | 7.2.4 | Mengemas kode, data yang boleh dibagikan, dan bukti proyek | OP | P0 | WF-147 |
| [WF-149](07-serah-terima/WF-149-WBS-7.3.1.md) | 7.3.1 | Melaksanakan demonstrasi dan orientasi penggunaan | PM | P0 | WF-148 |
| [WF-150](07-serah-terima/WF-150-WBS-7.3.2.md) | 7.3.2 | Menyerahkan akses dan kepemilikan operasional | OP | P0 | WF-149 |
| [WF-151](07-serah-terima/WF-151-WBS-7.3.3.md) | 7.3.3 | Memeriksa kelengkapan paket dan isu yang diterima | QA | P0 | WF-150 |
| [WF-152](07-serah-terima/WF-152-WBS-7.3.4.md) | 7.3.4 | Menyepakati dukungan awal dan menerima WF-G7 | PM | P0 | WF-151 |

## Fase 8 — Pemeliharaan awal dan penutupan

| Urutan / tiket | WBS | Pekerjaan | PIC | Prioritas | Pendahulu urutan |
|---|---|---|---|---|---|
| [WF-153](08-penutupan/WF-153-WBS-8.1.1.md) | 8.1.1 | Memantau kesehatan layanan dan backup selama dukungan | OP | P0 | WF-152 |
| [WF-154](08-penutupan/WF-154-WBS-8.1.2.md) | 8.1.2 | Menerima dan mengklasifikasikan insiden | QA | P0 | WF-153 (output per siklus) |
| [WF-155](08-penutupan/WF-155-WBS-8.1.3.md) | 8.1.3 | Memperbaiki bug atau koreksi data yang diterima | BE | P0 | WF-154 (output per siklus) |
| [WF-156](08-penutupan/WF-156-WBS-8.1.4.md) | 8.1.4 | Memverifikasi perbaikan serta memperbarui catatan rilis | QA | P0 | WF-155 (output per siklus) |
| [WF-157](08-penutupan/WF-157-WBS-8.2.1.md) | 8.2.1 | Membandingkan realisasi dengan baseline proyek | PM | P0 | WF-156 |
| [WF-158](08-penutupan/WF-158-WBS-8.2.2.md) | 8.2.2 | Menyusun lessons learned dan backlog lanjutan | PM | P0 | WF-157 |
| [WF-159](08-penutupan/WF-159-WBS-8.2.3.md) | 8.2.3 | Mengarsipkan artefak dan menyelesaikan transisi akses | OP | P0 | WF-158 |
| [WF-160](08-penutupan/WF-160-WBS-8.2.4.md) | 8.2.4 | Menyelesaikan kewajiban dukungan dan menerima WF-G8 | PM | P0 | WF-159 |

## Referensi

- [WBS tiga level](../01-WBS-waterfall.md).
- [Indeks variasi waterfall](../README.md).
- [Planning awal](../../README.md).
- [Laporan pemeriksaan paket tiket](verifikasi-tiket.json).

Dokumen disusun 22 Oktober 2026. Penerimaan gerbang, akun/anggaran, tanggal, hasil uji, serta deployment adalah pekerjaan pada tiket terkait dan belum dinyatakan terlaksana.
