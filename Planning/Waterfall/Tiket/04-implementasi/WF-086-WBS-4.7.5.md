# WF-086 — Membuat command review, analisis, publish, rollback, dan audit

Tiket untuk **WBS 4.7.5**, urutan eksekusi **086/160**. Dokumen ini adalah instruksi pelaksanaan; langkah dan bukti di bawah belum dinyatakan sudah dikerjakan.

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

Admin dapat menjalankan siklus rilis via jalur terotorisasi; publikasi atomik, rilis terbit immutable, dan audit tersedia.

Kerjakan langkah di tiket ini dan serahkan keluaran yang disebutkan. Batas keseluruhan mengikuti SRS/WBS: admin dan guest, scraping sumber terpilih, snapshot historis, serta fitur P1 sesuai keputusan scope. Perubahan kebutuhan atau kriteria yang sudah dibekukan dicatat lewat change request.

## Urutan dan syarat mulai

- **Pendahulu urutan:** [WF-085 / WBS 4.7.4](WF-085-WBS-4.7.4.md).
- **Gerbang masuk:** WF-G3 berstatus `accepted`; bukti pada [WF-052](../03-desain/WF-052-WBS-3.6.4.md).
- **Aturan antrean:** pendahulu urutan dan dependensi hasil harus `done`. P1 boleh dilewati hanya bila `deferred` dengan keputusan scope tertaut; tiket wajib tidak boleh dilewati. Sebelum 8.2.1, semua rekap dukungan 8.1.1–8.1.4 harus selesai.
- **Kesiapan:** input dapat diakses, PIC/reviewer ditunjuk, dan environment yang diperlukan tersedia sesuai fase. Sebelum WBS 1.2.2 selesai, gunakan penanggung jawab sementara yang dicatat saat tiket mulai; penetapan formal tidak memblokir tiket awal. Semua lokasi keluaran di bawah adalah target yang dibuat saat tiket dijalankan.

## Input dan dependensi hasil

- WBS sumber: [WBS waterfall tiga level](../../01-WBS-waterfall.md).
- Referensi pendukung: [03-arsitektur-dan-analisis.md](../../../03-arsitektur-dan-analisis.md); [04-supabase-dan-kamus-data.md](../../../04-supabase-dan-kamus-data.md); [revisi.txt](../../../revisi.txt).
- Ambil versi artefak yang sudah direview dari tiket berikut. Detail nama file tercantum pada tiket sumber; untuk dukungan gunakan keluaran per siklus yang relevan:

  - [WF-085 / WBS 4.7.4 — Membuat login/logout admin dan otorisasi operasi internal](WF-085-WBS-4.7.4.md): `hasil-uji-session-admin.md`, `matriks-otorisasi-aktual.md`.
  - [WF-075 / WBS 4.5.4 — Membuat impor staging dan promosi data tervalidasi](WF-075-WBS-4.5.4.md): `log-uji-impor-idempotent.md`, `contoh-laporan-error-impor.json`.
  - [WF-081 / WBS 4.6.5 — Menyimpan hasil run dan layer tematik](WF-081-WBS-4.6.5.md): `manifest-analysis-run.json`, `laporan-validasi-layer.md`.
  - [WF-036 / WBS 3.2.4 — Merancang versi rilis, publikasi, dan pemulihan](../03-desain/WF-036-WBS-3.2.4.md): `desain-lifecycle-rilis.md`, `desain-backup-rollback.md`.

## Handoff dan checkpoint eksekusi

Ikuti [panduan eksekusi](../../panduan-eksekusi.md) dan [register prasyarat](../../prasyarat-eksekusi.md). Simpan handoff aktual pada `docs/pekerjaan/WF-086/handoff.md` dan progres pada `docs/pekerjaan/WF-086/checkpoint.json` saat tiket dimulai. Keduanya masih target; bukan bukti pekerjaan sudah berjalan.

Catat input/versi yang benar-benar tersedia, keputusan prasyarat yang berlaku, batas perubahan, pemeriksaan expected/actual, penghalang, dan langkah berikutnya. Gunakan persetujuan pengguna yang sudah tercatat; jangan meminta ulang keputusan yang sama. Bukti penerimaan eksternal tetap harus berasal dari pihak sebenarnya.

**Kontrak implementasi usulan:** sahkan melalui WF-031/WF-G3 dan resolusikan ke file aktual sebelum mengubah kode. Jangan membuat modul paralel jika fungsi yang sama sudah tersedia; catat pemetaan path yang berubah.

- Target file/modul: `app/Console/Commands/`, `app/Services/ReleaseLifecycleService.php`, `app/Services/ReleaseAuditService.php`.
- Fixture sintetis bila diperlukan: `tests/data/wf-086/`; gunakan kasus normal/negatif pada langkah tiket dan expected result dari WF-049. Jangan salin rumus implementasi sebagai oracle.
- Pemeriksaan spesifik: tests/Feature/ReleaseLifecycleTest.php.
- Syarat selesai: kode/data aktual pada target yang disepakati tersedia bersama bukti verifikasi; laporan saja tidak menggantikan implementasi.
- Perintah usulan dari root repo, setelah toolchain dan test di atas tersedia: `php artisan test tests/Feature/ReleaseLifecycleTest.php`. Catat perintah final dan exit code; test tidak ditemukan/0 test bukan lulus. PHP memakai DB test PostgreSQL/PostGIS untuk kasus DB/spasial.

**Lokasi input pendahulu yang direncanakan (root repo):**
- `docs/pekerjaan/WF-085/hasil-uji-session-admin.md`.
- `docs/pekerjaan/WF-085/matriks-otorisasi-aktual.md`.
- `docs/pekerjaan/WF-075/log-uji-impor-idempotent.md`.
- `docs/pekerjaan/WF-075/contoh-laporan-error-impor.json`.
- `docs/pekerjaan/WF-081/manifest-analysis-run.json`.
- `docs/pekerjaan/WF-081/laporan-validasi-layer.md`.
- `docs/pekerjaan/WF-036/desain-lifecycle-rilis.md`.
- `docs/pekerjaan/WF-036/desain-backup-rollback.md`.
Jika lokasi aktual berbeda, ambil tautan dari log tiket sumber; cek versi dan penerimaan, bukan sekadar keberadaan nama file.

**Checkpoint lifecycle, dikerjakan berurutan dalam tiket yang sama:**

- C1 Review: simpan actor, bukti, alasan dan versi kandidat; tolak guest, bukti milik fasilitas lain, dan perubahan published.
- C2 Analisis: jalankan input berhash dengan run_id dan parameter; uji retry/idempotensi serta gagal tanpa run succeeded palsu.
- C3 Validasi: periksa kualitas, eligibility, FK, hash artefak dan kecocokan release/run; setiap kegagalan menahan publish.
- C4 Publish: transaksi dan lock/pemeriksaan versi mencegah dua publish bersaing; uji dua koneksi bersamaan dan gagal di tengah transaksi. Pointer, status serta audit harus commit bersama atau rollback bersama; cache hanya diperbarui setelah commit.
- C5 Rollback: pilih rilis lama valid tanpa mengubah sejarah; uji balapan publish/rollback dan konsistensi cache serta pembacaan release_id.
- C6 Audit/integrasi: identitas operator CLI ditentukan lewat jalur desain (bukan session HTTP yang diasumsikan ada); uji seluruh allow/deny sebagai non-owner serta alur lengkap tanpa UI P1. Audit tidak memuat rahasia.

Simpan hasil uji dan revision per checkpoint; keenam checkpoint beserta integrasi harus selesai sebelum tiket diajukan untuk review.

## Langkah pelaksanaan

1. Implementasikan command terotorisasi untuk review, menjalankan analisis, validasi kandidat, publish, dan rollback.
2. Periksa mutu data, run/artefak, dan status review sebelum transisi publikasi.
3. Lakukan publish/pointer update secara atomik serta catat actor, alasan, versi, dan before/after yang relevan.
4. Uji penolakan kandidat gagal, publish ulang, rollback versi lama, serta larangan mengubah rilis published; gunakan DB test.

## Keluaran yang diserahkan

Lokasi bukti yang diusulkan: `docs/pekerjaan/WF-086/`. Direktori dan berkas ini **belum dibuat oleh penyusunan tiket**; pelaksana membuatnya saat eksekusi. Kode aplikasi/data tetap di direktori desain, sedangkan catatan/hash/tautan bukti disimpan di sini.

- `panduan-command-admin.md`.
- `hasil-uji-lifecycle-rilis.md`.

## Kriteria penerimaan dan verifikasi

- [ ] Admin dapat menjalankan siklus rilis via jalur terotorisasi; publikasi atomik, rilis terbit immutable, dan audit tersedia.
- [ ] Siklus pengelolaan P0 dapat dijalankan tanpa UI P1; audit tidak menyimpan password/token dan cache mengikuti rilis aktif.
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

**ID tambahan:** `WF-086-GIT` (checklist penutup, bukan tugas WBS baru). **Pelaksana:** PIC tiket; **reviewer:** reviewer tiket atau pengelola repository. **Status pengiriman awal:** `not_started`; remote dan branch diisi setelah repository ditautkan.

**Contoh pesan commit:** `WF-086: membuat command review, analisis, publish, rollback, dan audit`. Untuk P1 yang ditunda, gunakan pesan yang menyatakan keputusan penundaan, bukan penyelesaian fitur.

1. Pastikan keluaran/kriteria tiket sudah diterima dan catatan aktual sudah diperbarui. Untuk P1 deferred, siapkan bukti keputusan scope. Untuk tiket gerbang, pastikan keputusan accepted tercatat; untuk dukungan, gunakan paket perbaikan/rekap siklus yang selesai.
2. Periksa repository, remote dan branch tujuan, serta identitas efektif author/committer (`git var GIT_AUTHOR_IDENT` dan `git var GIT_COMMITTER_IDENT`). Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau `Co-authored-by`.
3. Tinjau `git status` dan diff; stage file terkait tiket secara eksplisit. Periksa `git diff --cached` serta `git diff --cached --check`, pastikan tidak ada secret, dump, data yang tidak boleh dibagikan, atau perubahan tiket lain yang ikut tanpa sengaja.
4. Buat commit dengan ID `WF-086` setelah pemeriksaan relevan lulus. Periksa `git show -s --format=fuller HEAD` dan pesan commit untuk memastikan author/committer/trailer benar. Catat SHA; jangan mengubah identitas global atau riwayat commit lama.
5. Jalankan `git push <remote> HEAD:refs/heads/<branch>` dengan remote/branch yang sudah ditetapkan. Ganti placeholder sebelum eksekusi dan periksa hasilnya. Jika ditolak karena autentikasi, izin, atau non-fast-forward, catat penyebab dan selesaikan dengan fetch/integrasi serta pemeriksaan ulang yang relevan; jangan force push atau menganggap push berhasil.
6. Verifikasi SHA commit tersedia pada branch remote: cocokkan dengan `git ls-remote <remote> refs/heads/<branch>`. Jika ujung branch sudah maju, fetch branch tersebut dan buktikan commit berada dalam riwayatnya dengan `git merge-base --is-ancestor <sha> FETCH_HEAD` (exit code 0 berarti commit tercakup).
7. Laporkan ID tiket, remote/branch, SHA/tautan commit, waktu, dan status push aktual. Simpan bukti akhir di laporan percakapan/issue/CI agar tidak perlu membuat commit hanya untuk mencatat hash dirinya sendiri. Jika dicatat di repo, bawa catatan itu pada commit berikutnya.

**Kriteria selesai tambahan:** keluaran tiket telah direview, commit memakai identitas pengguna dan hanya perubahan yang tepat, serta commit terbukti ada pada branch GitHub tujuan. Jika remote/akses belum siap, catat pengiriman `pending`/`blocked`; pekerjaan lokal yang selesai tetap tersimpan, tetapi penutupan pengiriman belum terpenuhi. Jangan lanjut antrean serial sebelum pengiriman terverifikasi; dukungan insiden tetap mengikuti aturan siklus.

**Bukti pengiriman yang harus dilaporkan:** ID tiket, SHA/tautan, branch tujuan, hasil verifikasi remote, dan kendala bila ada. Belum ada bukti pengiriman saat tiket ini disusun.

**Lanjut setelah syarat terpenuhi:** [WF-087 — Membuat layout, navigasi, dan dashboard](WF-087-WBS-4.8.1.md).

[Kembali ke indeks dan aturan eksekusi](../README.md)
