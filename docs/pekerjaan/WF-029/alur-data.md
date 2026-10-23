# Alur data dan batas kepercayaan

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

1. Operator memilih source_id/edisi/URL yang telah diperiksa. Adapter membekukan bytes dan SHA256; raw tidak ditimpa dan tidak otomatis public.
2. Import batch menghasilkan staging rows accepted/quarantined/aggregate. Manifest menjaga expected count, baris hilang dan locator; HTTP 200 bukan kelengkapan.
3. Crosswalk approved menautkan kode/parent/edisi. Fakta populasi/luas mempertahankan raw, unit, tahun, sumber dan locator. Missing bukan nol.
4. Release draft memuat fasilitas, fakta, review dan boundary_set. Hanya review facility accepted yang boleh menjadi selected review. Kandidat bukan verified hanya karena provider memberi angka.
5. Analisis mengikat input hash, revision, T, radius, metode dan dependency. Indikator/radius disimpan berdasarkan run; hasil gagal tidak bisa publish. Full/partial mengikuti keputusan cakupan, bukan persentase yang disembunyikan.
6. Artefak disiapkan immutable dan diverifikasi ukuran/hash sebelum transaksi publikasi. Validator membekukan release/run/report hash; perubahan input membatalkan validasi.
7. Publisher memeriksa actor, expected active version dan kualitas, mengunci pointer, kemudian status/pointer/audit/outbox berubah dalam satu transaksi. Notifikasi/cache sesudah commit dapat diulang dari outbox.
8. GET tanpa release memilih pointer published sekali; semua query request memakai pilihan itu. Respons mengembalikan release_id/default_analysis_run_id. Browser menggunakannya untuk permintaan berikutnya dan hanya beralih setelah pengguna memuat ulang.
9. Colab mendapat manifest publik dan snapshot sanitasi. Modul analisis yang sama menghasilkan keluaran penelitian baru yang ditinjau, tidak menulis langsung ke produksi. Perbandingan memastikan kode/parameter/eligibility/kelas sama.

Setiap lintasan membawa source_id/batch_id/release_id/run_id/correlation_id sesuai tahap, bukan parameter ambigu. Audit internal menyimpan actor dan keputusan tanpa rahasia; API publik hanya metadata yang diperlukan. Withdrawal membatalkan akses publik termasuk lewat cache/storage gateway; objek draft tidak tersedia lewat URL raw permanen. Rilis published lama tetap bisa dibaca selama tidak withdrawn. Detail transaksi di [lifecycle](../WF-036/desain-lifecycle-rilis.md).
