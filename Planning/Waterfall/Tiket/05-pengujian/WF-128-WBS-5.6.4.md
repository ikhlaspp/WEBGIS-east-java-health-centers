# WF-128 — Menyelesaikan laporan uji dan menerima WF-G5

Tiket untuk **WBS 5.6.4**, urutan eksekusi **128/160**. Dokumen ini adalah instruksi pelaksanaan; langkah dan bukti di bawah belum dinyatakan sudah dikerjakan.

## Identitas dan kendali

| Atribut | Nilai |
|---|---|
| Fase | 5 — Pengujian dan penerimaan |
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

Semua P0 dan P1 terpilih lulus, UAT memenuhi baseline, batas data diterima; kandidat kode/data untuk deployment ditetapkan.

Kerjakan langkah di tiket ini dan serahkan keluaran yang disebutkan. Batas keseluruhan mengikuti SRS/WBS: admin dan guest, scraping sumber terpilih, snapshot historis, serta fitur P1 sesuai keputusan scope. Perubahan kebutuhan atau kriteria yang sudah dibekukan dicatat lewat change request.

## Urutan dan syarat mulai

- **Pendahulu urutan:** [WF-127 / WBS 5.6.3](WF-127-WBS-5.6.3.md).
- **Gerbang masuk:** WF-G4 berstatus `accepted`; bukti pada [WF-104](../04-implementasi/WF-104-WBS-4.11.4.md).
- **Aturan antrean:** pendahulu urutan dan dependensi hasil harus `done`. P1 boleh dilewati hanya bila `deferred` dengan keputusan scope tertaut; tiket wajib tidak boleh dilewati. Sebelum 8.2.1, semua rekap dukungan 8.1.1–8.1.4 harus selesai.
- **Kesiapan:** input dapat diakses, PIC/reviewer ditunjuk, dan environment yang diperlukan tersedia sesuai fase. Sebelum WBS 1.2.2 selesai, gunakan penanggung jawab sementara yang dicatat saat tiket mulai; penetapan formal tidak memblokir tiket awal. Semua lokasi keluaran di bawah adalah target yang dibuat saat tiket dijalankan.

## Input dan dependensi hasil

- WBS sumber: [WBS waterfall tiga level](../../01-WBS-waterfall.md).
- Referensi pendukung: [05-rencana-pengujian.md](../../../05-rencana-pengujian.md); [01-kebutuhan-dan-ruang-lingkup.md](../../../01-kebutuhan-dan-ruang-lingkup.md); [revisi.txt](../../../revisi.txt).
- Ambil versi artefak yang sudah direview dari tiket berikut. Detail nama file tercantum pada tiket sumber; untuk dukungan gunakan keluaran per siklus yang relevan:

  - [WF-108 / WBS 5.1.4 — Menguji pengulangan ETL dan konsistensi provenance](WF-108-WBS-5.1.4.md).
  - [WF-112 / WBS 5.2.4 — Membandingkan hasil spasial lintas implementasi](WF-112-WBS-5.2.4.md).
  - [WF-116 / WBS 5.3.4 — Menguji paparan rahasia dan izin database aktual](WF-116-WBS-5.3.4.md).
  - [WF-120 / WBS 5.4.4 — Menguji fitur P1 terpilih dan validasi file backend P0](WF-120-WBS-5.4.4.md).
  - [WF-121 / WBS 5.5.1 — Mengukur waktu muat, respons API, dan beban staging](WF-121-WBS-5.5.1.md).
  - [WF-122 / WBS 5.5.2 — Menguji backup dan restore database serta artefak](WF-122-WBS-5.5.2.md).
  - [WF-124 / WBS 5.5.4 — Membandingkan HTML Folium dengan aplikasi](WF-124-WBS-5.5.4.md).
  - [WF-127 / WBS 5.6.3 — Memperbaiki defect dan menjalankan retest/regresi](WF-127-WBS-5.6.3.md).
  - [WF-105 / WBS 5.1.1 — Menguji kegagalan sumber dan perubahan struktur scraping](WF-105-WBS-5.1.1.md).
  - [WF-106 / WBS 5.1.2 — Menguji integritas identitas, jumlah, dan kategori](WF-106-WBS-5.1.2.md).
  - [WF-107 / WBS 5.1.3 — Menguji mapping, tahun, unit, dan nilai berisiko](WF-107-WBS-5.1.3.md).
  - [WF-109 / WBS 5.2.1 — Menguji formula, pembulatan, null, nol, dan agregasi](WF-109-WBS-5.2.1.md).
  - [WF-110 / WBS 5.2.2 — Menguji kelayakan koordinat dan join peta](WF-110-WBS-5.2.2.md).
  - [WF-111 / WBS 5.2.3 — Menguji radius, overlap, clip, geometri, dan pulau](WF-111-WBS-5.2.3.md).
  - [WF-113 / WBS 5.3.1 — Menguji migration, constraint, dan impor](WF-113-WBS-5.3.1.md).
  - [WF-114 / WBS 5.3.2 — Menguji konsistensi rilis, rollback, dan kegagalan layanan](WF-114-WBS-5.3.2.md).
  - [WF-115 / WBS 5.3.3 — Menguji session, otorisasi, injeksi, dan keamanan popup](WF-115-WBS-5.3.3.md).
  - [WF-117 / WBS 5.4.1 — Menguji navigasi, peta, pencarian, dan filter](WF-117-WBS-5.4.1.md).
  - [WF-118 / WBS 5.4.2 — Menguji choropleth, statistik, detail, dan metode](WF-118-WBS-5.4.2.md).
  - [WF-119 / WBS 5.4.3 — Menguji responsivitas, aksesibilitas, dan request bersaing](WF-119-WBS-5.4.3.md).
  - [WF-123 / WBS 5.5.3 — Menjalankan Colab dari runtime bersih dan mengulang run](WF-123-WBS-5.5.3.md).
  - [WF-125 / WBS 5.6.1 — Menyiapkan peserta, kandidat rilis, dan instrumen UAT](WF-125-WBS-5.6.1.md).
  - [WF-126 / WBS 5.6.2 — Melaksanakan UAT dan merangkum temuan](WF-126-WBS-5.6.2.md).

## Langkah pelaksanaan

1. Gabungkan hasil aktual seluruh suite dan UAT dengan matriks FR/NFR serta keputusan P1.
2. Pastikan revisi kode, data, run, dan artefak final cocok dengan bukti uji setelah retest.
3. Review kualitas data, keamanan, performa, restore, reproduksi, dan daftar isu yang diterima.
4. Bekukan kandidat deployment dan catat keputusan penerima WF-G5; deploy hanya jika accepted.

**Pemeriksaan gerbang WF-G5:** tinjau seluruh tiket fase 5, selain tiket gerbang ini, bukan hanya pendahulu terakhir. Semua P0 pendahulu wajib `done`, P1 yang dipilih wajib `done`, dan P1 ditunda mempunyai keputusan. Tiket gerbang ini menjadi `done` setelah keputusan `accepted` tercatat. Simpan keputusan `accepted` atau `rework`, nama penerima, tanggal, serta daftar versi yang diterima. `rework` tetap menahan fase berikutnya.

## Keluaran yang diserahkan

Lokasi bukti yang diusulkan: `docs/pekerjaan/WF-128/`. Direktori dan berkas ini **belum dibuat oleh penyusunan tiket**; pelaksana membuatnya saat eksekusi. Kode aplikasi/data tetap di direktori desain, sedangkan catatan/hash/tautan bukti disimpan di sini.

- `laporan-pengujian-final.md`.
- `manifest-kandidat-deployment.json`.
- `penerimaan-WF-G5.md`.

## Kriteria penerimaan dan verifikasi

- [ ] Semua P0 dan P1 terpilih lulus, UAT memenuhi baseline, batas data diterima; kandidat kode/data untuk deployment ditetapkan.
- [ ] Semua P0 dan P1 terpilih diterima dengan bukti; kandidat yang diterapkan nanti tepat sama dengan manifest ini.
- [ ] Seluruh keluaran di atas tersedia, memiliki versi/tanggal, dan tautannya dicatat pada log kerja tiket.
- [ ] Reviewer memeriksa bukti aktual; tidak ada penghalang wajib yang disamarkan sebagai selesai.

Cara verifikasi: ikuti pemeriksaan spesifik pada langkah dan kriteria di atas. Untuk dokumen, lakukan penelusuran silang ke sumber/baseline; untuk kode/data, simpan perintah, input, expected/actual, versi, dan log hasil; untuk gerbang, simpan keputusan penerima yang nyata. Tiket uji yang terhambat tetap `blocked`, bukan `passed`.

## Jika terhambat atau gagal

Jika test gagal, catat expected/actual, severity, langkah reproduksi, versi, serta owner modul. Perbaikan yang menghalangi tiket berikutnya dilakukan segera pada tiket/modul terkait lalu retest; tidak menunggu 5.6.3. Tiket 5.6.3 mengonsolidasikan penutupan defect, bukan menunda semua perbaikan.

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

**ID tambahan:** `WF-128-GIT` (checklist penutup, bukan tugas WBS baru). **Pelaksana:** PIC tiket; **reviewer:** reviewer tiket atau pengelola repository. **Status pengiriman awal:** `not_started`; remote dan branch diisi setelah repository ditautkan.

**Contoh pesan commit:** `WF-128: menyelesaikan laporan uji dan menerima WF-G5`. Untuk P1 yang ditunda, gunakan pesan yang menyatakan keputusan penundaan, bukan penyelesaian fitur.

1. Pastikan keluaran/kriteria tiket sudah diterima dan catatan aktual sudah diperbarui. Untuk P1 deferred, siapkan bukti keputusan scope. Untuk tiket gerbang, pastikan keputusan accepted tercatat; untuk dukungan, gunakan paket perbaikan/rekap siklus yang selesai.
2. Periksa repository, remote dan branch tujuan, serta identitas efektif author/committer (`git var GIT_AUTHOR_IDENT` dan `git var GIT_COMMITTER_IDENT`). Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau `Co-authored-by`.
3. Tinjau `git status` dan diff; stage file terkait tiket secara eksplisit. Periksa `git diff --cached` serta `git diff --cached --check`, pastikan tidak ada secret, dump, data yang tidak boleh dibagikan, atau perubahan tiket lain yang ikut tanpa sengaja.
4. Buat commit dengan ID `WF-128` setelah pemeriksaan relevan lulus. Periksa `git show -s --format=fuller HEAD` dan pesan commit untuk memastikan author/committer/trailer benar. Catat SHA; jangan mengubah identitas global atau riwayat commit lama.
5. Jalankan `git push <remote> HEAD:refs/heads/<branch>` dengan remote/branch yang sudah ditetapkan. Ganti placeholder sebelum eksekusi dan periksa hasilnya. Jika ditolak karena autentikasi, izin, atau non-fast-forward, catat penyebab dan selesaikan dengan fetch/integrasi serta pemeriksaan ulang yang relevan; jangan force push atau menganggap push berhasil.
6. Verifikasi SHA commit tersedia pada branch remote: cocokkan dengan `git ls-remote <remote> refs/heads/<branch>`. Jika ujung branch sudah maju, fetch branch tersebut dan buktikan commit berada dalam riwayatnya dengan `git merge-base --is-ancestor <sha> FETCH_HEAD` (exit code 0 berarti commit tercakup).
7. Laporkan ID tiket, remote/branch, SHA/tautan commit, waktu, dan status push aktual. Simpan bukti akhir di laporan percakapan/issue/CI agar tidak perlu membuat commit hanya untuk mencatat hash dirinya sendiri. Jika dicatat di repo, bawa catatan itu pada commit berikutnya.

**Kriteria selesai tambahan:** keluaran tiket telah direview, commit memakai identitas pengguna dan hanya perubahan yang tepat, serta commit terbukti ada pada branch GitHub tujuan. Jika remote/akses belum siap, catat pengiriman `pending`/`blocked`; pekerjaan lokal yang selesai tetap tersimpan, tetapi penutupan pengiriman belum terpenuhi. Jangan lanjut antrean serial sebelum pengiriman terverifikasi; dukungan insiden tetap mengikuti aturan siklus.

**Bukti pengiriman yang harus dilaporkan:** ID tiket, SHA/tautan, branch tujuan, hasil verifikasi remote, dan kendala bila ada. Belum ada bukti pengiriman saat tiket ini disusun.

**Lanjut setelah syarat terpenuhi:** [WF-129 — Menyiapkan hosting, domain bila diperlukan, dan HTTPS](../06-deployment/WF-129-WBS-6.1.1.md).

[Kembali ke indeks dan aturan eksekusi](../README.md)
