# Keamanan, pemulihan dan reproduksi

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Kandidat NFR-05/06/07; layanan dan pemilik operasi belum dikonfirmasi.

## Keamanan

Rahasia berada di environment server/secret store, bukan Git, log, JS, Folium atau notebook. Browser memakai Laravel; runtime DB non-owner dan schema privat. Akun teknis runtime/worker/publisher/migration terpisah mengikuti matriks akses. TLS untuk browser dan koneksi DB; debug produksi off; output/popup di-escape; SQL parameterized; sort/metric/radius allowlist. File impor memvalidasi ukuran, jenis dan header; limit kandidat 20 MiB per file, dapat ditinjau sebelum implementasi untuk sumber PDF lebih besar melalui jalur acquisition terpisah. File tidak dieksekusi dan tidak disimpan dalam public webroot.

Sesi/admin mengikuti WF-015 (CSRF, expiry, cookie, throttling). Audit append-only menyimpan actor nyata, operasi, target, before/after identifiers, request/job ID, waktu UTC, hasil dan alasan; tanpa credential/password. Publish dan audit sukses satu transaksi; efek cache setelah commit. Uji akses sebagai guest/admin dan role DB nyata, bukan hanya owner. Actor CLI palsu, perubahan published langsung dan balapan publish harus ditolak.

## Backup dan restore

Target kandidat RPO≤24 jam, RTO≤4 jam. RPO diukur dari waktu insiden sampai checkpoint backup terakhir yang lengkap/konsisten; RTO dari mulai pemulihan sampai smoke/fungsi penerimaan selesai. Target bukan klaim telah tercapai dan tidak bergantung pada paket berbayar yang belum dibeli.

| Objek | Kebijakan kandidat | Verifikasi |
|---|---|---|
| DB termasuk metadata/audit/pointer rilis | Backup harian terenkripsi serta sebelum migrasi/publish besar | Restore ke DB terisolasi; schema/FK/count/grants/pointer cocok |
| Raw yang boleh disimpan, processed data, GeoJSON/HTML, manifest | Snapshot berhash yang konsisten dengan release DB; jangan hanya backup metadata storage | File tersedia, hash cocok, notebook/peta dapat membaca artefak |
| Kode/lockfile/runbook | Git revision + arsip release | Instalasi dari revision yang sama |
| Rahasia/akses pemulihan | Secret store terpisah, akses operator dibatasi | Credential pemulihan dapat dipakai tanpa dicetak di bukti |

Retensi kandidat 7 backup harian + 4 mingguan; setidaknya satu salinan di lokasi terpisah dari layanan utama. Owner peran OP dan reviewer QA; nama dan storage anggaran masih perlu ditetapkan. Gagal backup memicu alert dan retry tercatat; lebih dari 24 jam tanpa backup lengkap memblokir publikasi baru sampai dipulihkan.

[Dokumentasi backup Supabase](https://supabase.com/docs/guides/platform/backups) membedakan database dan objek storage; backup DB tidak menggantikan salinan file. Jika paket tidak menyediakan backup yang dibutuhkan, gunakan job dump dan salinan artefak pada storage yang diizinkan atau ubah target melalui keputusan biaya. Tidak ada asumsi free tier memberi seluruh kemampuan recovery.

Restore drill sebelum rilis dan setelah perubahan besar prosedur: environment kosong terpisah, restore DB+file dari checkpoint sama, hitung recovery point/time, jalankan login, API published, marker/table, artefak dan hash; capture actual dan defect. Produksi tidak menjadi target eksperimen restore.

## Reproduksibilitas

Kunci dependency PHP/JS/Python, catat versi Postgres/PostGIS/PROJ/GEOS, seed bila ada proses acak, locale/timezone dan urutan langkah. Manifest run memuat input hash, release/boundary/code revision, parameter T/radius/kurva/kelas legenda, eligibility, output hash dan catatan nondeterministik. Dua run input/versi sama harus memiliki tabel identik dan geometri ekuivalen dalam toleransi yang ditetapkan sebelum eksekusi. Notebook gagal dengan alasan dependency/sumber tidak lengkap; tidak otomatis beralih ke live data terbaru. Bukti R01–R03 dan S06/S07 wajib sebelum rilis.
