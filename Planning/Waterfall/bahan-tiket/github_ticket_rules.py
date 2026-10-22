"""Instruksi penutup GitHub bersama; modul ini tidak mengeksekusi Git."""

SECTION = '## Task tambahan — Commit dan push ke GitHub'

POLICY = '''## Commit dan push setelah setiap tiket

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
'''

def render_push_closure(ticket_id, title):
    return '\n'.join([
        SECTION, '',
        f'**ID tambahan:** `{ticket_id}-GIT` (checklist penutup, bukan tugas WBS baru). '
        '**Pelaksana:** PIC tiket; **reviewer:** reviewer tiket atau pengelola repository. '
        '**Status pengiriman awal:** `not_started`; remote dan branch diisi setelah repository ditautkan.', '',
        f'**Contoh pesan commit:** `{ticket_id}: {title[0].lower()+title[1:]}`. '
        'Untuk P1 yang ditunda, gunakan pesan yang menyatakan keputusan penundaan, bukan penyelesaian fitur.', '',
        '1. Pastikan keluaran/kriteria tiket sudah diterima dan catatan aktual sudah diperbarui. '
        'Untuk P1 deferred, siapkan bukti keputusan scope. Untuk tiket gerbang, pastikan keputusan accepted tercatat; '
        'untuk dukungan, gunakan paket perbaikan/rekap siklus yang selesai.',
        '2. Periksa repository, remote dan branch tujuan, serta identitas efektif author/committer '
        '(`git var GIT_AUTHOR_IDENT` dan `git var GIT_COMMITTER_IDENT`). '
        'Gunakan identitas Git pengguna; jangan menambahkan ChatGPT/Codex sebagai author, committer, atau `Co-authored-by`.',
        '3. Tinjau `git status` dan diff; stage file terkait tiket secara eksplisit. '
        'Periksa `git diff --cached` serta `git diff --cached --check`, pastikan tidak ada secret, '
        'dump, data yang tidak boleh dibagikan, atau perubahan tiket lain yang ikut tanpa sengaja.',
        f'4. Buat commit dengan ID `{ticket_id}` setelah pemeriksaan relevan lulus. '
        'Periksa `git show -s --format=fuller HEAD` dan pesan commit untuk memastikan author/committer/trailer benar. '
        'Catat SHA; jangan mengubah identitas global atau riwayat commit lama.',
        '5. Jalankan `git push <remote> HEAD:refs/heads/<branch>` dengan remote/branch yang sudah ditetapkan. '
        'Ganti placeholder sebelum eksekusi dan periksa hasilnya. Jika ditolak karena autentikasi, izin, '
        'atau non-fast-forward, catat penyebab dan selesaikan dengan fetch/integrasi serta pemeriksaan ulang yang relevan; '
        'jangan force push atau menganggap push berhasil.',
        '6. Verifikasi SHA commit tersedia pada branch remote: cocokkan dengan '
        '`git ls-remote <remote> refs/heads/<branch>`. Jika ujung branch sudah maju, fetch branch tersebut '
        'dan buktikan commit berada dalam riwayatnya dengan `git merge-base --is-ancestor <sha> FETCH_HEAD` '
        '(exit code 0 berarti commit tercakup).',
        '7. Laporkan ID tiket, remote/branch, SHA/tautan commit, waktu, dan status push aktual. '
        'Simpan bukti akhir di laporan percakapan/issue/CI agar tidak perlu membuat commit hanya untuk '
        'mencatat hash dirinya sendiri. Jika dicatat di repo, bawa catatan itu pada commit berikutnya.', '',
        '**Kriteria selesai tambahan:** keluaran tiket telah direview, commit memakai identitas pengguna '
        'dan hanya perubahan yang tepat, serta commit terbukti ada pada branch GitHub tujuan. '
        'Jika remote/akses belum siap, catat pengiriman `pending`/`blocked`; pekerjaan lokal yang selesai '
        'tetap tersimpan, tetapi penutupan pengiriman belum terpenuhi. '
        'Jangan lanjut antrean serial sebelum pengiriman terverifikasi; dukungan insiden tetap mengikuti aturan siklus.', '',
        '**Bukti pengiriman yang harus dilaporkan:** ID tiket, SHA/tautan, branch tujuan, hasil verifikasi remote, '
        'dan kendala bila ada. Belum ada bukti pengiriman saat tiket ini disusun.', '',
    ])

def closing_metadata(ticket_id):
    return {
        'id': ticket_id + '-GIT',
        'type': 'commit_and_push_github',
        'required': True,
        'initial_delivery_status': 'not_started',
        'remote': None,
        'branch': None,
        'author_policy': 'Identitas Git pengguna; periksa author, committer, dan trailer tanpa menambahkan ChatGPT/Codex.',
        'verification': 'Commit tersedia pada riwayat branch remote tujuan.',
        'evidence': 'Laporan pengiriman eksternal setelah push, atau catatan pada commit berikutnya.',
    }
