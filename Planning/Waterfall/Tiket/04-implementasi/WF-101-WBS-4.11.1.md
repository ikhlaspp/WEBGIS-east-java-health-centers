# WF-101 — Menghubungkan pipeline, database, API, UI, dan artefak

Tiket untuk **WBS 4.11.1**, urutan eksekusi **101/160**. Dokumen ini adalah instruksi pelaksanaan; langkah dan bukti di bawah belum dinyatakan sudah dikerjakan.

## Identitas dan kendali

| Atribut | Nilai |
|---|---|
| Fase | 4 — Implementasi dan penyiapan data |
| Prioritas | P0 — wajib untuk rilis/cakupan yang diterima |
| Status | `not_started` |
| PIC peran | BE |
| PIC bernama | Ditunjuk saat mulai; penugasan tim diformalkan pada WBS 1.2.2 |
| Reviewer | QA; reviewer BE untuk skema/keamanan; nama diisi saat penugasan |
| Estimasi usaha | Belum ditetapkan; estimasi jam orang melalui WBS 1.2.3 |
| Tanggal rencana / aktual | Belum ditetapkan / belum dimulai |
| Pola pelaksanaan | Finish-to-start pada antrean utama |
| Sasaran | Rilis awal menurut SRS; fase 8 mengikuti masa dukungan yang disepakati |

## Tujuan dan batas pekerjaan

Satu kandidat rilis dapat ditelusuri dari sumber ke tabel, peta, statistik, dan HTML.

Kerjakan langkah di tiket ini dan serahkan keluaran yang disebutkan. Batas keseluruhan mengikuti SRS/WBS: admin dan guest, scraping sumber terpilih, snapshot historis, serta fitur P1 sesuai keputusan scope. Perubahan kebutuhan atau kriteria yang sudah dibekukan dicatat lewat change request.

## Urutan dan syarat mulai

- **Pendahulu urutan:** [WF-100 / WBS 4.10.4](WF-100-WBS-4.10.4.md).
- **Gerbang masuk:** WF-G3 berstatus `accepted`; bukti pada [WF-052](../03-desain/WF-052-WBS-3.6.4.md).
- **Aturan antrean:** pendahulu urutan dan dependensi hasil harus `done`. P1 boleh dilewati hanya bila `deferred` dengan keputusan scope tertaut; tiket wajib tidak boleh dilewati. Sebelum 8.2.1, semua rekap dukungan 8.1.1–8.1.4 harus selesai.
- **Kesiapan:** input dapat diakses, PIC/reviewer ditunjuk, dan environment yang diperlukan tersedia sesuai fase. Sebelum WBS 1.2.2 selesai, gunakan penanggung jawab sementara yang dicatat saat tiket mulai; penetapan formal tidak memblokir tiket awal. Semua lokasi keluaran di bawah adalah target yang dibuat saat tiket dijalankan.

## Input dan dependensi hasil

- WBS sumber: [WBS waterfall tiga level](../../01-WBS-waterfall.md).
- Referensi pendukung: [01-kebutuhan-dan-ruang-lingkup.md](../../../01-kebutuhan-dan-ruang-lingkup.md); [05-rencana-pengujian.md](../../../05-rencana-pengujian.md); [04-supabase-dan-kamus-data.md](../../../04-supabase-dan-kamus-data.md).
- Ambil versi artefak yang sudah direview dari tiket berikut. Detail nama file tercantum pada tiket sumber; untuk dukungan gunakan keluaran per siklus yang relevan:

  - [WF-076 / WBS 4.5.5 — Memuat kandidat dataset hasil kurasi](WF-076-WBS-4.5.5.md): `manifest-kandidat-dataset.json`, `rekonsiliasi-pasca-impor.md`.
  - [WF-081 / WBS 4.6.5 — Menyimpan hasil run dan layer tematik](WF-081-WBS-4.6.5.md): `manifest-analysis-run.json`, `laporan-validasi-layer.md`.
  - [WF-086 / WBS 4.7.5 — Membuat command review, analisis, publish, rollback, dan audit](WF-086-WBS-4.7.5.md): `panduan-command-admin.md`, `hasil-uji-lifecycle-rilis.md`.
  - [WF-092 / WBS 4.8.6 — Membuat halaman metodologi dan penanganan state UI](WF-092-WBS-4.8.6.md): `bukti-state-UI-dan-metode.md`.
  - [WF-096 / WBS 4.9.4 — Menambahkan manifest dan panduan Run all](WF-096-WBS-4.9.4.md): `panduan-Run-all.md`, `manifest-output-notebook.json`.
  - [WF-097 / WBS 4.10.1 — Membuat dashboard admin untuk menjalankan dan memantau batch](WF-097-WBS-4.10.1.md): `bukti-dashboard-admin-P1.md`.
  - [WF-098 / WBS 4.10.2 — Membuat layar review data dan publikasi rilis](WF-098-WBS-4.10.2.md): `bukti-review-publish-UI-P1.md`.
  - [WF-099 / WBS 4.10.3 — Membuat ekspor CSV hasil filter](WF-099-WBS-4.10.3.md): `bukti-ekspor-CSV-P1.md`, `sampel-ekspor-aman.txt`.
  - [WF-100 / WBS 4.10.4 — Membuat daftar prioritas kecamatan](WF-100-WBS-4.10.4.md): `bukti-prioritas-kecamatan-P1.md`.

## Handoff dan checkpoint eksekusi

Ikuti [panduan eksekusi](../../panduan-eksekusi.md) dan [register prasyarat](../../prasyarat-eksekusi.md). Simpan handoff aktual pada `docs/pekerjaan/WF-101/handoff.md` dan progres pada `docs/pekerjaan/WF-101/checkpoint.json` saat tiket dimulai. Keduanya masih target; bukan bukti pekerjaan sudah berjalan.

Catat input/versi yang benar-benar tersedia, keputusan prasyarat yang berlaku, batas perubahan, pemeriksaan expected/actual, penghalang, dan langkah berikutnya. Gunakan persetujuan pengguna yang sudah tercatat; jangan meminta ulang keputusan yang sama. Bukti penerimaan eksternal tetap harus berasal dari pihak sebenarnya.

**Kontrak implementasi usulan:** sahkan melalui WF-031/WF-G3 dan resolusikan ke file aktual sebelum mengubah kode. Jangan membuat modul paralel jika fungsi yang sama sudah tersedia; catat pemetaan path yang berubah.

- Target file/modul: `tests/Browser/release_flow.spec.js`.
- Fixture sintetis bila diperlukan: `tests/data/wf-101/`; gunakan kasus normal/negatif pada langkah tiket dan expected result dari WF-049. Jangan salin rumus implementasi sebagai oracle.
- Pemeriksaan spesifik: tests/Browser/release_flow.spec.js.
- Syarat selesai: kode/data aktual pada target yang disepakati tersedia bersama bukti verifikasi; laporan saja tidak menggantikan implementasi.
- Perintah usulan dari root repo, setelah toolchain dan test di atas tersedia: `npx --no-install playwright test tests/Browser/release_flow.spec.js`; `npm run build`. Catat perintah final dan exit code; test tidak ditemukan/0 test bukan lulus. PHP memakai DB test PostgreSQL/PostGIS untuk kasus DB/spasial.

**Lokasi input pendahulu yang direncanakan (root repo):**
- `docs/pekerjaan/WF-076/manifest-kandidat-dataset.json`.
- `docs/pekerjaan/WF-076/rekonsiliasi-pasca-impor.md`.
- `docs/pekerjaan/WF-081/manifest-analysis-run.json`.
- `docs/pekerjaan/WF-081/laporan-validasi-layer.md`.
- `docs/pekerjaan/WF-086/panduan-command-admin.md`.
- `docs/pekerjaan/WF-086/hasil-uji-lifecycle-rilis.md`.
- `docs/pekerjaan/WF-092/bukti-state-UI-dan-metode.md`.
- `docs/pekerjaan/WF-096/panduan-Run-all.md`.
- `docs/pekerjaan/WF-096/manifest-output-notebook.json`.
- `docs/pekerjaan/WF-097/bukti-dashboard-admin-P1.md`.
- `docs/pekerjaan/WF-098/bukti-review-publish-UI-P1.md`.
- `docs/pekerjaan/WF-099/bukti-ekspor-CSV-P1.md`.
- `docs/pekerjaan/WF-099/sampel-ekspor-aman.txt`.
- `docs/pekerjaan/WF-100/bukti-prioritas-kecamatan-P1.md`.
Jika lokasi aktual berbeda, ambil tautan dari log tiket sumber; cek versi dan penerimaan, bukan sekadar keberadaan nama file.

## Langkah pelaksanaan

1. Periksa seluruh P0 dan keputusan setiap P1; hanya fitur terpilih yang harus tersedia di kandidat.
2. Hubungkan hasil kurasi, impor, run, API, UI, dan HTML menggunakan satu rilis kandidat.
3. Jalankan alur admin dari kandidat ke published pada staging lalu telusuri sebagai guest.
4. Cocokkan kode/jumlah/tahun/rilis pada dataset, response, tampilan, dan artefak; daftar setiap ketidaksesuaian untuk perbaikan.

## Keluaran yang diserahkan

Lokasi bukti yang diusulkan: `docs/pekerjaan/WF-101/`. Direktori dan berkas ini **belum dibuat oleh penyusunan tiket**; pelaksana membuatnya saat eksekusi. Kode aplikasi/data tetap di direktori desain, sedangkan catatan/hash/tautan bukti disimpan di sini.

- `matriks-integrasi-rilis.md`.
- `log-alur-end-to-end.md`.

## Kriteria penerimaan dan verifikasi

- [ ] Satu kandidat rilis dapat ditelusuri dari sumber ke tabel, peta, statistik, dan HTML.
- [ ] Tidak ada komponen mengambil rilis berbeda secara diam-diam; deferred P1 tidak memblokir integrasi bila keputusannya sah.
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

**ID tambahan:** `WF-101-GIT` (checklist penutup, bukan tugas WBS baru). **Pelaksana:** PIC tiket; **reviewer:** reviewer tiket atau pengelola repository. **Status pengiriman awal:** `not_started`; remote dan branch diisi setelah repository ditautkan.

**Contoh pesan commit:** `WF-101: menghubungkan pipeline, database, API, UI, dan artefak`. Untuk P1 yang ditunda, gunakan pesan yang menyatakan keputusan penundaan, bukan penyelesaian fitur.

1. Pastikan keluaran/kriteria tiket sudah diterima dan catatan aktual sudah diperbarui. Untuk P1 deferred, siapkan bukti keputusan scope. Untuk tiket gerbang, pastikan keputusan accepted tercatat; untuk dukungan, gunakan paket perbaikan/rekap siklus yang selesai.
2. Periksa repository, remote dan branch tujuan, serta identitas efektif author/committer (`git var GIT_AUTHOR_IDENT` dan `git var GIT_COMMITTER_IDENT`). Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau `Co-authored-by`.
3. Tinjau `git status` dan diff; stage file terkait tiket secara eksplisit. Periksa `git diff --cached` serta `git diff --cached --check`, pastikan tidak ada secret, dump, data yang tidak boleh dibagikan, atau perubahan tiket lain yang ikut tanpa sengaja.
4. Buat commit dengan ID `WF-101` setelah pemeriksaan relevan lulus. Periksa `git show -s --format=fuller HEAD` dan pesan commit untuk memastikan author/committer/trailer benar. Catat SHA; jangan mengubah identitas global atau riwayat commit lama.
5. Jalankan `git push <remote> HEAD:refs/heads/<branch>` dengan remote/branch yang sudah ditetapkan. Ganti placeholder sebelum eksekusi dan periksa hasilnya. Jika ditolak karena autentikasi, izin, atau non-fast-forward, catat penyebab dan selesaikan dengan fetch/integrasi serta pemeriksaan ulang yang relevan; jangan force push atau menganggap push berhasil.
6. Verifikasi SHA commit tersedia pada branch remote: cocokkan dengan `git ls-remote <remote> refs/heads/<branch>`. Jika ujung branch sudah maju, fetch branch tersebut dan buktikan commit berada dalam riwayatnya dengan `git merge-base --is-ancestor <sha> FETCH_HEAD` (exit code 0 berarti commit tercakup).
7. Laporkan ID tiket, remote/branch, SHA/tautan commit, waktu, dan status push aktual. Simpan bukti akhir di laporan percakapan/issue/CI agar tidak perlu membuat commit hanya untuk mencatat hash dirinya sendiri. Jika dicatat di repo, bawa catatan itu pada commit berikutnya.

**Kriteria selesai tambahan:** keluaran tiket telah direview, commit memakai identitas pengguna dan hanya perubahan yang tepat, serta commit terbukti ada pada branch GitHub tujuan. Jika remote/akses belum siap, catat pengiriman `pending`/`blocked`; pekerjaan lokal yang selesai tetap tersimpan, tetapi penutupan pengiriman belum terpenuhi. Jangan lanjut antrean serial sebelum pengiriman terverifikasi; dukungan insiden tetap mengikuti aturan siklus.

**Bukti pengiriman yang harus dilaporkan:** ID tiket, SHA/tautan, branch tujuan, hasil verifikasi remote, dan kendala bila ada. Belum ada bukti pengiriman saat tiket ini disusun.

**Lanjut setelah syarat terpenuhi:** [WF-102 — Melengkapi unit/component test modul yang berubah](WF-102-WBS-4.11.2.md).

[Kembali ke indeks dan aturan eksekusi](../README.md)
