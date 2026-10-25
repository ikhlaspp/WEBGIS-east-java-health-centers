# Variasi perencanaan waterfall — WebGIS Puskesmas Jawa Timur

Dokumen ini memisahkan pendekatan waterfall dari [planning awal](../README.md). WBS sudah diuraikan menjadi 160 tiket pelaksanaan. Jadwal, estimasi biaya, dan pembagian nama anggota belum ditetapkan; penetapannya termasuk pekerjaan pada tiket inisiasi.

- [WBS detail tiga level](01-WBS-waterfall.md): fase, kelompok pekerjaan, tugas rinci, PIC, bukti selesai, dependensi fase, serta gerbang penerimaan.
- [Indeks dan urutan 160 tiket](Tiket/README.md): satu tiket per tugas level 3, dengan langkah spesifik, input/dependensi, target keluaran, acceptance checklist, penanganan kegagalan, serta log kerja.
- [Mulai dari WF-001](Tiket/01-inisiasi/WF-001-WBS-1.1.1.md): menelaah proposal, planning awal, dan revisi pengguna.
- [Katalog tiket terstruktur](Tiket/daftar-tiket.json): metadata awal dan pemetaan WBS–tiket untuk alat bantu; status kerja aktual disimpan pada file tiket.
- [Hasil pemeriksaan paket tiket](Tiket/verifikasi-tiket.json): cakupan, urutan, dependensi, isi wajib, dan tautan; bukan laporan kelulusan aplikasi.

Nomor WF menunjukkan urutan eksekusi, sedangkan kode WBS tetap mengikuti dokumen sumber. Kebutuhan sumber daya dijalankan sebelum estimasi, akun admin produksi dibuat setelah migration, dan pemeliharaan mengikuti siklus monitoring–triase–perbaikan–verifikasi. Aturan lengkap tersedia di indeks tiket.

Setiap tiket kini memiliki **task tambahan commit dan push ke GitHub** setelah hasil direview. Checklist meliputi identitas author/committer pengguna, pemilihan perubahan, commit per tiket, push, dan verifikasi remote. Ini tidak menambah jumlah tugas WBS. Penutupan pengiriman menunggu push terverifikasi; repository/akses yang belum siap dicatat sebagai penghalang pengiriman. Tidak ada commit/push yang dilakukan hanya dengan menyusun dokumen ini.

Untuk memeriksa ulang paket setelah perubahan, jalankan dari workspace:

```powershell
python Planning/Waterfall/bahan-tiket/validasi_tiket.py
```

WBS mengikuti cakupan proyek pada planning awal dan revisi peran/pengumpulan data di [revisi.txt](../revisi.txt): admin dan user/guest, dengan pengumpulan data melalui scraping. Aktivitas validasi data tetap diperlukan dan menjadi tanggung jawab admin/tim, tanpa menambah peran aplikasi pengelola data.

**Status:** usulan WBS v1, disusun 22 Oktober 2026. Ini merupakan rencana pekerjaan, bukan laporan bahwa aplikasi, scraping, Supabase, pengujian, atau deployment telah dilaksanakan.
