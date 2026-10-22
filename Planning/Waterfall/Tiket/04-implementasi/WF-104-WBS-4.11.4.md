# WF-104 — Membekukan kandidat uji dan menerima WF-G4

Tiket untuk **WBS 4.11.4**, urutan eksekusi **104/160**. Dokumen ini adalah instruksi pelaksanaan; langkah dan bukti di bawah belum dinyatakan sudah dikerjakan.

## Identitas dan kendali

| Atribut | Nilai |
|---|---|
| Fase | 4 — Implementasi dan penyiapan data |
| Prioritas | P0 — wajib untuk rilis/cakupan yang diterima |
| Status | `not_started` |
| PIC peran | PM |
| PIC bernama | Ditunjuk saat mulai; penugasan tim diformalkan pada WBS 1.2.2 |
| Reviewer | Penerima gerbang yang ditetapkan pada 1.1.2; nama diisi saat penugasan |
| Estimasi usaha | Belum ditetapkan; estimasi jam orang melalui WBS 1.2.3 |
| Tanggal rencana / aktual | Belum ditetapkan / belum dimulai |
| Pola pelaksanaan | Finish-to-start pada antrean utama |
| Sasaran | Rilis awal menurut SRS; fase 8 mengikuti masa dukungan yang disepakati |

## Tujuan dan batas pekerjaan

Revisi kode, release_id, analysis_run_id, laporan mutu, dan daftar scope tersedia; kandidat layak masuk uji sistem.

Kerjakan langkah di tiket ini dan serahkan keluaran yang disebutkan. Batas keseluruhan mengikuti SRS/WBS: admin dan guest, scraping sumber terpilih, snapshot historis, serta fitur P1 sesuai keputusan scope. Perubahan kebutuhan atau kriteria yang sudah dibekukan dicatat lewat change request.

## Urutan dan syarat mulai

- **Pendahulu urutan:** [WF-103 / WBS 4.11.3](WF-103-WBS-4.11.3.md).
- **Gerbang masuk:** WF-G3 berstatus `accepted`; bukti pada [WF-052](../03-desain/WF-052-WBS-3.6.4.md).
- **Aturan antrean:** pendahulu urutan dan dependensi hasil harus `done`. P1 boleh dilewati hanya bila `deferred` dengan keputusan scope tertaut; tiket wajib tidak boleh dilewati. Sebelum 8.2.1, semua rekap dukungan 8.1.1–8.1.4 harus selesai.
- **Kesiapan:** input dapat diakses, PIC/reviewer ditunjuk, dan environment yang diperlukan tersedia sesuai fase. Sebelum WBS 1.2.2 selesai, gunakan penanggung jawab sementara yang dicatat saat tiket mulai; penetapan formal tidak memblokir tiket awal. Semua lokasi keluaran di bawah adalah target yang dibuat saat tiket dijalankan.

## Input dan dependensi hasil

- WBS sumber: [WBS waterfall tiga level](../../01-WBS-waterfall.md).
- Referensi pendukung: [01-kebutuhan-dan-ruang-lingkup.md](../../../01-kebutuhan-dan-ruang-lingkup.md); [05-rencana-pengujian.md](../../../05-rencana-pengujian.md); [04-supabase-dan-kamus-data.md](../../../04-supabase-dan-kamus-data.md).
- Ambil versi artefak yang sudah direview dari tiket berikut. Detail nama file tercantum pada tiket sumber; untuk dukungan gunakan keluaran per siklus yang relevan:

  - [WF-101 / WBS 4.11.1 — Menghubungkan pipeline, database, API, UI, dan artefak](WF-101-WBS-4.11.1.md).
  - [WF-102 / WBS 4.11.2 — Melengkapi unit/component test modul yang berubah](WF-102-WBS-4.11.2.md).
  - [WF-103 / WBS 4.11.3 — Menjalankan smoke test dan memperbaiki kegagalan integrasi](WF-103-WBS-4.11.3.md).
  - [WF-071 / WBS 4.4.5 — Membekukan laporan kelayakan data spasial](WF-071-WBS-4.4.5.md).
  - [WF-053 / WBS 4.1.1 — Membuat repositori dan struktur proyek](WF-053-WBS-4.1.1.md).
  - [WF-054 / WBS 4.1.2 — Menyiapkan Laravel dan build frontend](WF-054-WBS-4.1.2.md).
  - [WF-055 / WBS 4.1.3 — Menyiapkan Python, Colab, dan alat pengujian](WF-055-WBS-4.1.3.md).
  - [WF-056 / WBS 4.1.4 — Menyiapkan pipeline pemeriksaan otomatis](WF-056-WBS-4.1.4.md).
  - [WF-057 / WBS 4.2.1 — Mengimplementasikan pengunduh dan parser data fasilitas](WF-057-WBS-4.2.1.md).
  - [WF-058 / WBS 4.2.2 — Mengimplementasikan pengambilan data penduduk dan luas](WF-058-WBS-4.2.2.md).
  - [WF-059 / WBS 4.2.3 — Mengimplementasikan pengambilan kode dan polygon wilayah](WF-059-WBS-4.2.3.md).
  - [WF-060 / WBS 4.2.4 — Menambahkan cache, retry, dan pemeriksaan kelengkapan scraping](WF-060-WBS-4.2.4.md).
  - [WF-061 / WBS 4.2.5 — Menjalankan pengambilan sumber dan membekukan input mentah](WF-061-WBS-4.2.5.md).
  - [WF-062 / WBS 4.3.1 — Mengekstrak dan menormalisasi tabel sumber](WF-062-WBS-4.3.1.md).
  - [WF-063 / WBS 4.3.2 — Menyelesaikan crosswalk kode serta alias wilayah](WF-063-WBS-4.3.2.md).
  - [WF-064 / WBS 4.3.3 — Memisahkan subtotal dan merekonsiliasi master fasilitas](WF-064-WBS-4.3.3.md).
  - [WF-065 / WBS 4.3.4 — Memverifikasi angka penduduk, luas, tahun, dan unit](WF-065-WBS-4.3.4.md).
  - [WF-066 / WBS 4.3.5 — Memvalidasi polygon dan kelengkapan master wilayah](WF-066-WBS-4.3.5.md).
  - [WF-067 / WBS 4.4.1 — Menyiapkan antrean geocoding dan pencatatan bukti](WF-067-WBS-4.4.1.md).
  - [WF-068 / WBS 4.4.2 — Mereview 565 pasangan koordinat yang sudah tersedia](WF-068-WBS-4.4.2.md).
  - [WF-069 / WBS 4.4.3 — Menelusuri 408 fasilitas tanpa koordinat](WF-069-WBS-4.4.3.md).
  - [WF-070 / WBS 4.4.4 — Menyelesaikan anomali koordinat dan konflik wilayah](WF-070-WBS-4.4.4.md).
  - [WF-072 / WBS 4.5.1 — Menyiapkan database development dan test dengan PostGIS](WF-072-WBS-4.5.1.md).
  - [WF-073 / WBS 4.5.2 — Membuat migration tabel, constraint, dan indeks](WF-073-WBS-4.5.2.md).
  - [WF-074 / WBS 4.5.3 — Mengimplementasikan grants dan pembatasan akses data](WF-074-WBS-4.5.3.md).
  - [WF-075 / WBS 4.5.4 — Membuat impor staging dan promosi data tervalidasi](WF-075-WBS-4.5.4.md).
  - [WF-076 / WBS 4.5.5 — Memuat kandidat dataset hasil kurasi](WF-076-WBS-4.5.5.md).
  - [WF-077 / WBS 4.6.1 — Membuat perhitungan indikator kecamatan](WF-077-WBS-4.6.1.md).
  - [WF-078 / WBS 4.6.2 — Membuat agregasi kabupaten dan provinsi](WF-078-WBS-4.6.2.md).
  - [WF-079 / WBS 4.6.3 — Membuat buffer radius titik yang terverifikasi](WF-079-WBS-4.6.3.md).
  - [WF-080 / WBS 4.6.4 — Membuat union, clip, dan luas cakupan wilayah](WF-080-WBS-4.6.4.md).
  - [WF-081 / WBS 4.6.5 — Menyimpan hasil run dan layer tematik](WF-081-WBS-4.6.5.md).
  - [WF-082 / WBS 4.7.1 — Membuat API rilis, wilayah, dan katalog sumber](WF-082-WBS-4.7.1.md).
  - [WF-083 / WBS 4.7.2 — Membuat API fasilitas, pencarian, filter, dan detail](WF-083-WBS-4.7.2.md).
  - [WF-084 / WBS 4.7.3 — Membuat API statistik, GeoJSON, dan buffer](WF-084-WBS-4.7.3.md).
  - [WF-085 / WBS 4.7.4 — Membuat login/logout admin dan otorisasi operasi internal](WF-085-WBS-4.7.4.md).
  - [WF-086 / WBS 4.7.5 — Membuat command review, analisis, publish, rollback, dan audit](WF-086-WBS-4.7.5.md).
  - [WF-087 / WBS 4.8.1 — Membuat layout, navigasi, dan dashboard](WF-087-WBS-4.8.1.md).
  - [WF-088 / WBS 4.8.2 — Membuat peta dasar, marker, cluster, dan popup](WF-088-WBS-4.8.2.md).
  - [WF-089 / WBS 4.8.3 — Membuat pencarian dan filter bertingkat](WF-089-WBS-4.8.3.md).
  - [WF-090 / WBS 4.8.4 — Membuat layer choropleth, buffer, dan legenda](WF-090-WBS-4.8.4.md).
  - [WF-091 / WBS 4.8.5 — Membuat tabel dan halaman detail fasilitas/kecamatan](WF-091-WBS-4.8.5.md).
  - [WF-092 / WBS 4.8.6 — Membuat halaman metodologi dan penanganan state UI](WF-092-WBS-4.8.6.md).
  - [WF-093 / WBS 4.9.1 — Menghubungkan notebook ke snapshot rilis yang aman](WF-093-WBS-4.9.1.md).
  - [WF-094 / WBS 4.9.2 — Mengintegrasikan modul analisis ke notebook](WF-094-WBS-4.9.2.md).
  - [WF-095 / WBS 4.9.3 — Membuat visualisasi Folium dan ekspor HTML/tabel](WF-095-WBS-4.9.3.md).
  - [WF-096 / WBS 4.9.4 — Menambahkan manifest dan panduan Run all](WF-096-WBS-4.9.4.md).
  - [WF-097 / WBS 4.10.1 — Membuat dashboard admin untuk menjalankan dan memantau batch](WF-097-WBS-4.10.1.md).
  - [WF-098 / WBS 4.10.2 — Membuat layar review data dan publikasi rilis](WF-098-WBS-4.10.2.md).
  - [WF-099 / WBS 4.10.3 — Membuat ekspor CSV hasil filter](WF-099-WBS-4.10.3.md).
  - [WF-100 / WBS 4.10.4 — Membuat daftar prioritas kecamatan](WF-100-WBS-4.10.4.md).

## Langkah pelaksanaan

1. Bekukan revision, lockfile, release_id, run, hash dataset/artefak, serta konfigurasi staging.
2. Kumpulkan bukti unit/component/smoke dan laporan kualitas data terhadap SRS.
3. Periksa seluruh pekerjaan fase 4 termasuk status empat P1 serta isu yang dapat memblokir uji.
4. Rekam keputusan penerima WF-G4; perubahan kandidat setelah diterima harus mempunyai versi baru dan jejak retest.

**Pemeriksaan gerbang WF-G4:** tinjau seluruh tiket fase 4, selain tiket gerbang ini, bukan hanya pendahulu terakhir. Semua P0 pendahulu wajib `done`, P1 yang dipilih wajib `done`, dan P1 ditunda mempunyai keputusan. Tiket gerbang ini menjadi `done` setelah keputusan `accepted` tercatat. Simpan keputusan `accepted` atau `rework`, nama penerima, tanggal, serta daftar versi yang diterima. `rework` tetap menahan fase berikutnya.

## Keluaran yang diserahkan

Lokasi bukti yang diusulkan: `docs/pekerjaan/WF-104/`. Direktori dan berkas ini **belum dibuat oleh penyusunan tiket**; pelaksana membuatnya saat eksekusi. Kode aplikasi/data tetap di direktori desain, sedangkan catatan/hash/tautan bukti disimpan di sini.

- `manifest-kandidat-uji.json`.
- `penerimaan-WF-G4.md`.

## Kriteria penerimaan dan verifikasi

- [ ] Revisi kode, release_id, analysis_run_id, laporan mutu, dan daftar scope tersedia; kandidat layak masuk uji sistem.
- [ ] Kandidat dapat direproduksi dan semua prasyarat uji sistem tersedia sebelum fase 5 dibuka.
- [ ] Seluruh keluaran di atas tersedia, memiliki versi/tanggal, dan tautannya dicatat pada log kerja tiket.
- [ ] Reviewer memeriksa bukti aktual; tidak ada penghalang wajib yang disamarkan sebagai selesai.

Cara verifikasi: ikuti pemeriksaan spesifik pada langkah dan kriteria di atas. Untuk dokumen, lakukan penelusuran silang ke sumber/baseline; untuk kode/data, simpan perintah, input, expected/actual, versi, dan log hasil; untuk gerbang, simpan keputusan penerima yang nyata. Tiket uji yang terhambat tetap `blocked`, bukan `passed`.

## Jika terhambat atau gagal

Jika input, sumber, akses, atau hasil validasi gagal, simpan error dan contoh minimal; tandai blocked bila pekerjaan tidak dapat dilanjutkan. Perbaiki akar masalah atau minta keputusan perubahan scope; jangan memaksa status data valid atau menimpa arsip asli.

Tulis masalah pada log kerja dengan dampak, owner tindak lanjut, dan dependensi yang tertahan. Jangan mengubah expected result agar sesuai hasil gagal. Setelah perbaikan, ulangi pemeriksaan yang terdampak dan simpan bukti retest.

## Log kerja dan penutupan

| Tanggal | Pelaksana | Tindakan / hasil aktual | Tautan bukti / defect |
|---|---|---|---|
| Belum ada | — | Belum dijalankan | — |

- PIC aktual: belum ditetapkan.
- Jam aktual: belum dicatat.
- Versi kode / release_id / analysis_run_id: isi bila relevan saat eksekusi.
- Keputusan review: belum direview.
- Reviewer dan tanggal penerimaan: belum tersedia.
- Isu tersisa / change request: belum dievaluasi.

## Task tambahan — Commit dan push ke GitHub

**ID tambahan:** `WF-104-GIT` (checklist penutup, bukan tugas WBS baru). **Pelaksana:** PIC tiket; **reviewer:** reviewer tiket atau pengelola repository. **Status pengiriman awal:** `not_started`; remote dan branch diisi setelah repository ditautkan.

**Contoh pesan commit:** `WF-104: membekukan kandidat uji dan menerima WF-G4`. Untuk P1 yang ditunda, gunakan pesan yang menyatakan keputusan penundaan, bukan penyelesaian fitur.

1. Pastikan keluaran/kriteria tiket sudah diterima dan catatan aktual sudah diperbarui. Untuk P1 deferred, siapkan bukti keputusan scope. Untuk tiket gerbang, pastikan keputusan accepted tercatat; untuk dukungan, gunakan paket perbaikan/rekap siklus yang selesai.
2. Periksa repository, remote dan branch tujuan, serta identitas efektif author/committer (`git var GIT_AUTHOR_IDENT` dan `git var GIT_COMMITTER_IDENT`). Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau `Co-authored-by`.
3. Tinjau `git status` dan diff; stage file terkait tiket secara eksplisit. Periksa `git diff --cached` serta `git diff --cached --check`, pastikan tidak ada secret, dump, data yang tidak boleh dibagikan, atau perubahan tiket lain yang ikut tanpa sengaja.
4. Buat commit dengan ID `WF-104` setelah pemeriksaan relevan lulus. Periksa `git show -s --format=fuller HEAD` dan pesan commit untuk memastikan author/committer/trailer benar. Catat SHA; jangan mengubah identitas global atau riwayat commit lama.
5. Jalankan `git push <remote> HEAD:refs/heads/<branch>` dengan remote/branch yang sudah ditetapkan. Ganti placeholder sebelum eksekusi dan periksa hasilnya. Jika ditolak karena autentikasi, izin, atau non-fast-forward, catat penyebab dan selesaikan dengan fetch/integrasi serta pemeriksaan ulang yang relevan; jangan force push atau menganggap push berhasil.
6. Verifikasi SHA commit tersedia pada branch remote: cocokkan dengan `git ls-remote <remote> refs/heads/<branch>`. Jika ujung branch sudah maju, fetch branch tersebut dan buktikan commit berada dalam riwayatnya dengan `git merge-base --is-ancestor <sha> FETCH_HEAD` (exit code 0 berarti commit tercakup).
7. Laporkan ID tiket, remote/branch, SHA/tautan commit, waktu, dan status push aktual. Simpan bukti akhir di laporan percakapan/issue/CI agar tidak perlu membuat commit hanya untuk mencatat hash dirinya sendiri. Jika dicatat di repo, bawa catatan itu pada commit berikutnya.

**Kriteria selesai tambahan:** keluaran tiket telah direview, commit memakai identitas pengguna dan hanya perubahan yang tepat, serta commit terbukti ada pada branch GitHub tujuan. Jika remote/akses belum siap, catat pengiriman `pending`/`blocked`; pekerjaan lokal yang selesai tetap tersimpan, tetapi penutupan pengiriman belum terpenuhi. Jangan lanjut antrean serial sebelum pengiriman terverifikasi; dukungan insiden tetap mengikuti aturan siklus.

**Bukti pengiriman yang harus dilaporkan:** ID tiket, SHA/tautan, branch tujuan, hasil verifikasi remote, dan kendala bila ada. Belum ada bukti pengiriman saat tiket ini disusun.

**Lanjut setelah syarat terpenuhi:** [WF-105 — Menguji kegagalan sumber dan perubahan struktur scraping](../05-pengujian/WF-105-WBS-5.1.1.md).

[Kembali ke indeks dan aturan eksekusi](../README.md)
