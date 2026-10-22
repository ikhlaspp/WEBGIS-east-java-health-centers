# WF-134 — Memasang konfigurasi rahasia dan akun admin awal

Tiket untuk **WBS 6.1.3**, urutan eksekusi **134/160**. Dokumen ini adalah instruksi pelaksanaan; langkah dan bukti di bawah belum dinyatakan sudah dikerjakan.

## Identitas dan kendali

| Atribut | Nilai |
|---|---|
| Fase | 6 — Deployment dan verifikasi produksi |
| Prioritas | P0 — wajib untuk rilis/cakupan yang diterima |
| Status | `not_started` |
| PIC peran | OP |
| PIC bernama | Ditunjuk saat mulai; penugasan tim diformalkan pada WBS 1.2.2 |
| Reviewer | BE/QA yang bukan operator pelaksana; nama diisi saat penugasan |
| Estimasi usaha | Belum ditetapkan; estimasi jam orang melalui WBS 1.2.3 |
| Tanggal rencana / aktual | Belum ditetapkan / belum dimulai |
| Pola pelaksanaan | Finish-to-start pada antrean utama |
| Sasaran | Rilis awal menurut SRS; fase 8 mengikuti masa dukungan yang disepakati |

## Tujuan dan batas pekerjaan

Rahasia berada di server, debug publik mati, admin tersedia, dan akses teknis dibatasi sesuai desain.

Kerjakan langkah di tiket ini dan serahkan keluaran yang disebutkan. Batas keseluruhan mengikuti SRS/WBS: admin dan guest, scraping sumber terpilih, snapshot historis, serta fitur P1 sesuai keputusan scope. Perubahan kebutuhan atau kriteria yang sudah dibekukan dicatat lewat change request.

## Urutan dan syarat mulai

- **Pendahulu urutan:** [WF-133 / WBS 6.2.2](WF-133-WBS-6.2.2.md).
- **Gerbang masuk:** WF-G5 berstatus `accepted`; bukti pada [WF-128](../05-pengujian/WF-128-WBS-5.6.4.md).
- **Aturan antrean:** pendahulu urutan dan dependensi hasil harus `done`. P1 boleh dilewati hanya bila `deferred` dengan keputusan scope tertaut; tiket wajib tidak boleh dilewati. Sebelum 8.2.1, semua rekap dukungan 8.1.1–8.1.4 harus selesai.
- **Kesiapan:** input dapat diakses, PIC/reviewer ditunjuk, dan environment yang diperlukan tersedia sesuai fase. Sebelum WBS 1.2.2 selesai, gunakan penanggung jawab sementara yang dicatat saat tiket mulai; penetapan formal tidak memblokir tiket awal. Semua lokasi keluaran di bawah adalah target yang dibuat saat tiket dijalankan.

## Input dan dependensi hasil

- WBS sumber: [WBS waterfall tiga level](../../01-WBS-waterfall.md).
- Referensi pendukung: [04-supabase-dan-kamus-data.md](../../../04-supabase-dan-kamus-data.md); [03-arsitektur-dan-analisis.md](../../../03-arsitektur-dan-analisis.md); [05-rencana-pengujian.md](../../../05-rencana-pengujian.md).
- Ambil versi artefak yang sudah direview dari tiket berikut. Detail nama file tercantum pada tiket sumber; untuk dukungan gunakan keluaran per siklus yang relevan:

  - [WF-133 / WBS 6.2.2 — Menjalankan migration dan memuat dataset final](WF-133-WBS-6.2.2.md): `log-migration-impor-produksi.md`, `rekonsiliasi-produksi.md`.
  - [WF-129 / WBS 6.1.1 — Menyiapkan hosting, domain bila diperlukan, dan HTTPS](WF-129-WBS-6.1.1.md): `inventaris-produksi.md`, `hasil-pemeriksaan-host-HTTPS.md`.
  - [WF-130 / WBS 6.1.2 — Menyiapkan Supabase produksi dan penyimpanan artefak](WF-130-WBS-6.1.2.md): `inventaris-Supabase-produksi.md`, `hasil-koneksi-produksi.md`.
  - [WF-085 / WBS 4.7.4 — Membuat login/logout admin dan otorisasi operasi internal](../04-implementasi/WF-085-WBS-4.7.4.md): `hasil-uji-session-admin.md`, `matriks-otorisasi-aktual.md`.

## Langkah pelaksanaan

1. Setelah migration tersedia, pasang konfigurasi runtime/worker/publisher yang dibutuhkan dengan secret di server.
2. Tetapkan APP_ENV/DEBUG, URL/HTTPS, cookie/session, logging, queue, dan cache sesuai produksi.
3. Buat akun admin awal melalui jalur provisioning terotorisasi pada tabel yang sudah ada.
4. Uji koneksi runtime serta login/logout dan serahkan akses awal lewat jalur aman tanpa menaruh password pada tiket.

## Keluaran yang diserahkan

Lokasi bukti yang diusulkan: `docs/pekerjaan/WF-134/`. Direktori dan berkas ini **belum dibuat oleh penyusunan tiket**; pelaksana membuatnya saat eksekusi. Kode aplikasi/data tetap di direktori desain, sedangkan catatan/hash/tautan bukti disimpan di sini.

- `checklist-konfigurasi-final.md`.
- `bukti-provisioning-admin.md`.

## Kriteria penerimaan dan verifikasi

- [ ] Rahasia berada di server, debug publik mati, admin tersedia, dan akses teknis dibatasi sesuai desain.
- [ ] Debug publik mati, admin bisa login, runtime memakai hak minimum, dan tidak ada akun fixture yang terbawa ke produksi.
- [ ] Seluruh keluaran di atas tersedia, memiliki versi/tanggal, dan tautannya dicatat pada log kerja tiket.
- [ ] Reviewer memeriksa bukti aktual; tidak ada penghalang wajib yang disamarkan sebagai selesai.

Cara verifikasi: ikuti pemeriksaan spesifik pada langkah dan kriteria di atas. Untuk dokumen, lakukan penelusuran silang ke sumber/baseline; untuk kode/data, simpan perintah, input, expected/actual, versi, dan log hasil; untuk gerbang, simpan keputusan penerima yang nyata. Tiket uji yang terhambat tetap `blocked`, bukan `passed`.

## Jika terhambat atau gagal

Jika hash, akses, integritas data, atau smoke test tidak sesuai kandidat diterima, hentikan kelanjutan penerapan dan gunakan runbook pemulihan. Jangan menerbitkan dataset separuh atau mencatat layanan sehat tanpa bukti.

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

**ID tambahan:** `WF-134-GIT` (checklist penutup, bukan tugas WBS baru). **Pelaksana:** PIC tiket; **reviewer:** reviewer tiket atau pengelola repository. **Status pengiriman awal:** `not_started`; remote dan branch diisi setelah repository ditautkan.

**Contoh pesan commit:** `WF-134: memasang konfigurasi rahasia dan akun admin awal`. Untuk P1 yang ditunda, gunakan pesan yang menyatakan keputusan penundaan, bukan penyelesaian fitur.

1. Pastikan keluaran/kriteria tiket sudah diterima dan catatan aktual sudah diperbarui. Untuk P1 deferred, siapkan bukti keputusan scope. Untuk tiket gerbang, pastikan keputusan accepted tercatat; untuk dukungan, gunakan paket perbaikan/rekap siklus yang selesai.
2. Periksa repository, remote dan branch tujuan, serta identitas efektif author/committer (`git var GIT_AUTHOR_IDENT` dan `git var GIT_COMMITTER_IDENT`). Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau `Co-authored-by`.
3. Tinjau `git status` dan diff; stage file terkait tiket secara eksplisit. Periksa `git diff --cached` serta `git diff --cached --check`, pastikan tidak ada secret, dump, data yang tidak boleh dibagikan, atau perubahan tiket lain yang ikut tanpa sengaja.
4. Buat commit dengan ID `WF-134` setelah pemeriksaan relevan lulus. Periksa `git show -s --format=fuller HEAD` dan pesan commit untuk memastikan author/committer/trailer benar. Catat SHA; jangan mengubah identitas global atau riwayat commit lama.
5. Jalankan `git push <remote> HEAD:refs/heads/<branch>` dengan remote/branch yang sudah ditetapkan. Ganti placeholder sebelum eksekusi dan periksa hasilnya. Jika ditolak karena autentikasi, izin, atau non-fast-forward, catat penyebab dan selesaikan dengan fetch/integrasi serta pemeriksaan ulang yang relevan; jangan force push atau menganggap push berhasil.
6. Verifikasi SHA commit tersedia pada branch remote: cocokkan dengan `git ls-remote <remote> refs/heads/<branch>`. Jika ujung branch sudah maju, fetch branch tersebut dan buktikan commit berada dalam riwayatnya dengan `git merge-base --is-ancestor <sha> FETCH_HEAD` (exit code 0 berarti commit tercakup).
7. Laporkan ID tiket, remote/branch, SHA/tautan commit, waktu, dan status push aktual. Simpan bukti akhir di laporan percakapan/issue/CI agar tidak perlu membuat commit hanya untuk mencatat hash dirinya sendiri. Jika dicatat di repo, bawa catatan itu pada commit berikutnya.

**Kriteria selesai tambahan:** keluaran tiket telah direview, commit memakai identitas pengguna dan hanya perubahan yang tepat, serta commit terbukti ada pada branch GitHub tujuan. Jika remote/akses belum siap, catat pengiriman `pending`/`blocked`; pekerjaan lokal yang selesai tetap tersimpan, tetapi penutupan pengiriman belum terpenuhi. Jangan lanjut antrean serial sebelum pengiriman terverifikasi; dukungan insiden tetap mengikuti aturan siklus.

**Bukti pengiriman yang harus dilaporkan:** ID tiket, SHA/tautan, branch tujuan, hasil verifikasi remote, dan kendala bila ada. Belum ada bukti pengiriman saat tiket ini disusun.

**Lanjut setelah syarat terpenuhi:** [WF-135 — Memasang hasil analisis dan menerbitkan rilis aktif](WF-135-WBS-6.2.3.md).

[Kembali ke indeks dan aturan eksekusi](../README.md)
