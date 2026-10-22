# Standar bukti dan defect

Versi 1 — 23 Oktober 2026.

Simpan bukti di `docs/pekerjaan/WF-NNN/`. Dokumen berisi judul, versi, tanggal, pelaksana, sumber/commit, hasil dan batas pemeriksaan. `handoff.md` menjelaskan input, perubahan, keputusan, penghalang dan langkah berikutnya; `checkpoint.json` memuat status aktual yang dapat dilanjutkan. Simpan input asli secara immutable dengan manifest SHA-256, nama sumber, tanggal akses, izin, periode dan unit. Koreksi menghasilkan versi baru, bukan menimpa provenance.

Format pemeriksaan: ID kebutuhan/uji; versi kode dan data; prasyarat; command/langkah; expected; actual; status pass/fail/not_run; lokasi log; pelaksana; waktu; reviewer. Screenshot mendukung bukti, bukan pengganti data atau log yang diperlukan. Waktu kerja aktual diukur bila tersedia; jangan menyamakan estimasi dengan realisasi.

Format defect: ID; tiket/uji; judul; severity; environment; input/fixture; langkah reproduksi; expected; actual; bukti; owner; status; perubahan perbaikan; retest; regresi; keputusan penutupan. Critical: kebocoran rahasia, korupsi data/publikasi tak sah; high: fungsi P0 gagal atau hasil analisis salah; medium: fungsi terbatas dengan workaround aman; low: kosmetik. Critical/high terbuka menghalangi rilis; pengecualian lain harus diputus penerima dan tidak boleh melanggar acceptance P0.

Alur defect: open → triaged → fixing → ready_for_retest → closed; kegagalan retest kembali open. Pelaksana perbaikan tidak mengarang penerimaan reviewer.

Jangan simpan password, token, service-role key, connection string, cookie, atau data pribadi yang tidak diperlukan. Gunakan nama variabel konfigurasi dan log tersanitasi. Periksa staged diff sebelum commit. Input berlisensi terbatas dicatat lokasi/hash dan disimpan sesuai izin; jangan otomatis mempublikasikannya. Backup terenkripsi/akses terbatas ditetapkan pada desain operasi.

Git: stage keluaran tiket secara eksplisit setelah diterima; gunakan identitas pengguna yang terkonfigurasi; tanpa trailer AI; periksa diff/check; push ke target terverifikasi; cocokkan SHA remote atau buktikan ancestor. Kegagalan push tetap pending/blocked. Jangan menulis hash commit di dalam commit itu sendiri; laporkan setelah push atau pada catatan berikutnya.
