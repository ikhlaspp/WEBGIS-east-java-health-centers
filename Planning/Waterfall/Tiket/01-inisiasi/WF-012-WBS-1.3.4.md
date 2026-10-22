# WF-012 — Menetapkan pelaporan rutin dan menerima WF-G1

Tiket untuk **WBS 1.3.4**, urutan eksekusi **012/160**. Dokumen ini adalah instruksi pelaksanaan; langkah dan bukti di bawah belum dinyatakan sudah dikerjakan.

## Identitas dan kendali

| Atribut | Nilai |
|---|---|
| Fase | 1 — Inisiasi dan perencanaan proyek |
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

Jadwal laporan status/risiko dan format notulen aktif; charter serta rencana awal memiliki catatan penerimaan.

Kerjakan langkah di tiket ini dan serahkan keluaran yang disebutkan. Batas keseluruhan mengikuti SRS/WBS: admin dan guest, scraping sumber terpilih, snapshot historis, serta fitur P1 sesuai keputusan scope. Perubahan kebutuhan atau kriteria yang sudah dibekukan dicatat lewat change request.

## Urutan dan syarat mulai

- **Pendahulu urutan:** [WF-011 / WBS 1.3.3](WF-011-WBS-1.3.3.md).
- **Gerbang masuk:** belum ada; fase ini menyiapkan penerimaan WF-G1.
- **Aturan antrean:** pendahulu urutan dan dependensi hasil harus `done`. P1 boleh dilewati hanya bila `deferred` dengan keputusan scope tertaut; tiket wajib tidak boleh dilewati. Sebelum 8.2.1, semua rekap dukungan 8.1.1–8.1.4 harus selesai.
- **Kesiapan:** input dapat diakses, PIC/reviewer ditunjuk, dan environment yang diperlukan tersedia sesuai fase. Sebelum WBS 1.2.2 selesai, gunakan penanggung jawab sementara yang dicatat saat tiket mulai; penetapan formal tidak memblokir tiket awal. Semua lokasi keluaran di bawah adalah target yang dibuat saat tiket dijalankan.

## Input dan dependensi hasil

- WBS sumber: [WBS waterfall tiga level](../../01-WBS-waterfall.md).
- Referensi pendukung: [01-kebutuhan-dan-ruang-lingkup.md](../../../01-kebutuhan-dan-ruang-lingkup.md); [06-tahapan-dan-kebutuhan.md](../../../06-tahapan-dan-kebutuhan.md); [07-sumber-dan-keputusan.md](../../../07-sumber-dan-keputusan.md); [revisi.txt](../../../revisi.txt).
- Ambil versi artefak yang sudah direview dari tiket berikut. Detail nama file tercantum pada tiket sumber; untuk dukungan gunakan keluaran per siklus yang relevan:

  - [WF-004 / WBS 1.1.4 — Menyusun dan meninjau project charter](WF-004-WBS-1.1.4.md).
  - [WF-005 / WBS 1.2.1 — Memeriksa kelengkapan WBS bersama tim](WF-005-WBS-1.2.1.md).
  - [WF-006 / WBS 1.2.2 — Menetapkan penanggung jawab dan reviewer paket kerja](WF-006-WBS-1.2.2.md).
  - [WF-008 / WBS 1.2.3 — Menaksir usaha, dependensi, dan durasi dari paket kerja](WF-008-WBS-1.2.3.md).
  - [WF-007 / WBS 1.2.4 — Menyusun kebutuhan biaya, alat, akun, dan lingkungan](WF-007-WBS-1.2.4.md).
  - [WF-009 / WBS 1.3.1 — Membuat daftar risiko dan rencana penanganannya](WF-009-WBS-1.3.1.md).
  - [WF-010 / WBS 1.3.2 — Menetapkan tata cara perubahan scope dan keputusan](WF-010-WBS-1.3.2.md).
  - [WF-011 / WBS 1.3.3 — Menetapkan standar bukti selesai dan penyimpanan artefak](WF-011-WBS-1.3.3.md).
  - [WF-001 / WBS 1.1.1 — Menelaah proposal, planning awal, dan revisi pengguna](WF-001-WBS-1.1.1.md).
  - [WF-002 / WBS 1.1.2 — Mengidentifikasi stakeholder dan penerima hasil](WF-002-WBS-1.1.2.md).
  - [WF-003 / WBS 1.1.3 — Menentukan sasaran dan ukuran keberhasilan proyek](WF-003-WBS-1.1.3.md).

## Langkah pelaksanaan

1. Tetapkan frekuensi laporan status, pembaruan risiko, rapat review, dan tempat menyimpan notulen.
2. Kumpulkan charter, WBS, penugasan, estimasi/jadwal, sumber daya, serta prosedur kendali versi yang telah direview.
3. Tinjau isu terbuka bersama penerima WF-G1 dan tetapkan owner/tenggat untuk hal yang belum selesai.
4. Catat keputusan accepted atau rework dengan bukti; hanya accepted membuka fase kebutuhan.

**Pemeriksaan gerbang WF-G1:** tinjau seluruh tiket fase 1, selain tiket gerbang ini, bukan hanya pendahulu terakhir. Semua P0 pendahulu wajib `done`, P1 yang dipilih wajib `done`, dan P1 ditunda mempunyai keputusan. Tiket gerbang ini menjadi `done` setelah keputusan `accepted` tercatat. Simpan keputusan `accepted` atau `rework`, nama penerima, tanggal, serta daftar versi yang diterima. `rework` tetap menahan fase berikutnya.

## Keluaran yang diserahkan

Lokasi bukti yang diusulkan: `docs/pekerjaan/WF-012/`. Direktori dan berkas ini **belum dibuat oleh penyusunan tiket**; pelaksana membuatnya saat eksekusi. Kode aplikasi/data tetap di direktori desain, sedangkan catatan/hash/tautan bukti disimpan di sini.

- `rencana-komunikasi.md`.
- `penerimaan-WF-G1.md`.

## Kriteria penerimaan dan verifikasi

- [ ] Jadwal laporan status/risiko dan format notulen aktif; charter serta rencana awal memiliki catatan penerimaan.
- [ ] Checklist WF-G1 seluruhnya terpenuhi dan identitas penerima serta tanggal keputusan nyata tersedia.
- [ ] Seluruh keluaran di atas tersedia, memiliki versi/tanggal, dan tautannya dicatat pada log kerja tiket.
- [ ] Reviewer memeriksa bukti aktual; tidak ada penghalang wajib yang disamarkan sebagai selesai.

Cara verifikasi: ikuti pemeriksaan spesifik pada langkah dan kriteria di atas. Untuk dokumen, lakukan penelusuran silang ke sumber/baseline; untuk kode/data, simpan perintah, input, expected/actual, versi, dan log hasil; untuk gerbang, simpan keputusan penerima yang nyata. Tiket uji yang terhambat tetap `blocked`, bukan `passed`.

## Jika terhambat atau gagal

Jika pihak penerima, kapasitas, biaya, atau keputusan mandat belum tersedia, catat isu dan owner. Jangan mengisi nama, persetujuan, tanggal, atau angka aktual fiktif.

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

**ID tambahan:** `WF-012-GIT` (checklist penutup, bukan tugas WBS baru). **Pelaksana:** PIC tiket; **reviewer:** reviewer tiket atau pengelola repository. **Status pengiriman awal:** `not_started`; remote dan branch diisi setelah repository ditautkan.

**Contoh pesan commit:** `WF-012: menetapkan pelaporan rutin dan menerima WF-G1`. Untuk P1 yang ditunda, gunakan pesan yang menyatakan keputusan penundaan, bukan penyelesaian fitur.

1. Pastikan keluaran/kriteria tiket sudah diterima dan catatan aktual sudah diperbarui. Untuk P1 deferred, siapkan bukti keputusan scope. Untuk tiket gerbang, pastikan keputusan accepted tercatat; untuk dukungan, gunakan paket perbaikan/rekap siklus yang selesai.
2. Periksa repository, remote dan branch tujuan, serta identitas efektif author/committer (`git var GIT_AUTHOR_IDENT` dan `git var GIT_COMMITTER_IDENT`). Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau `Co-authored-by`.
3. Tinjau `git status` dan diff; stage file terkait tiket secara eksplisit. Periksa `git diff --cached` serta `git diff --cached --check`, pastikan tidak ada secret, dump, data yang tidak boleh dibagikan, atau perubahan tiket lain yang ikut tanpa sengaja.
4. Buat commit dengan ID `WF-012` setelah pemeriksaan relevan lulus. Periksa `git show -s --format=fuller HEAD` dan pesan commit untuk memastikan author/committer/trailer benar. Catat SHA; jangan mengubah identitas global atau riwayat commit lama.
5. Jalankan `git push <remote> HEAD:refs/heads/<branch>` dengan remote/branch yang sudah ditetapkan. Ganti placeholder sebelum eksekusi dan periksa hasilnya. Jika ditolak karena autentikasi, izin, atau non-fast-forward, catat penyebab dan selesaikan dengan fetch/integrasi serta pemeriksaan ulang yang relevan; jangan force push atau menganggap push berhasil.
6. Verifikasi SHA commit tersedia pada branch remote: cocokkan dengan `git ls-remote <remote> refs/heads/<branch>`. Jika ujung branch sudah maju, fetch branch tersebut dan buktikan commit berada dalam riwayatnya dengan `git merge-base --is-ancestor <sha> FETCH_HEAD` (exit code 0 berarti commit tercakup).
7. Laporkan ID tiket, remote/branch, SHA/tautan commit, waktu, dan status push aktual. Simpan bukti akhir di laporan percakapan/issue/CI agar tidak perlu membuat commit hanya untuk mencatat hash dirinya sendiri. Jika dicatat di repo, bawa catatan itu pada commit berikutnya.

**Kriteria selesai tambahan:** keluaran tiket telah direview, commit memakai identitas pengguna dan hanya perubahan yang tepat, serta commit terbukti ada pada branch GitHub tujuan. Jika remote/akses belum siap, catat pengiriman `pending`/`blocked`; pekerjaan lokal yang selesai tetap tersimpan, tetapi penutupan pengiriman belum terpenuhi. Jangan lanjut antrean serial sebelum pengiriman terverifikasi; dukungan insiden tetap mengikuti aturan siklus.

**Bukti pengiriman yang harus dilaporkan:** ID tiket, SHA/tautan, branch tujuan, hasil verifikasi remote, dan kendala bila ada. Belum ada bukti pengiriman saat tiket ini disusun.

**Lanjut setelah syarat terpenuhi:** [WF-013 — Menggali skenario penggunaan admin dan guest](../02-kebutuhan/WF-013-WBS-2.1.1.md).

[Kembali ke indeks dan aturan eksekusi](../README.md)
