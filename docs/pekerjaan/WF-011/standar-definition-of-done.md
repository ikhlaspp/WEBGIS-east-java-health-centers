# Standar definition of done

Versi 1 — 23 Oktober 2026. Kandidat untuk WF-G1.

| Status | Makna dan syarat |
|---|---|
| not_started | Belum dimulai secara formal; persiapan artefak dapat dicatat terpisah |
| in_progress | Syarat mulai terpenuhi dan PIC sedang bekerja |
| blocked | Pekerjaan tidak dapat diteruskan karena penghalang bernama dan tindakan lanjut tercatat |
| in_review | Keluaran lokal siap ditinjau; belum diterima |
| done | Semua acceptance terpenuhi, reviewer menerima bukti, dependensi terpenuhi, dan commit/push terverifikasi |
| deferred | Hanya P1 dengan keputusan scope tertaut; bukan implementasi selesai |

Untuk done: seluruh keluaran tersedia dengan asal input/versi, expected/actual dapat direproduksi, tidak ada defect penghalang, hasil review nyata tersedia, serta delivery Git terverifikasi. Gerbang hanya accepted oleh penerima yang ditetapkan. Antrean finish-to-start tetap berlaku. Persiapan paket review secara bersamaan tidak membuat tiket berikutnya otomatis dimulai atau selesai.

P1 yang ditunda tidak menghapus A08-PARAM/S05 backend P0. Koreksi baseline mengikuti WF-010. Bukti reviewer berbeda dari pemeriksaan mandiri pelaksana; jangan memberi identitas manusia pada hasil Codex.

Contoh dokumentasi nyata: WF-001 memiliki ringkasan, konflik, dan hash sumber; pemeriksaan struktur dapat lulus, tetapi penerimaan reviewer dan pengiriman belum tersedia sehingga belum done.

Contoh tiket uji (template, belum dijalankan): WF-109 menggunakan fixture penduduk 60.000 dan dua fasilitas, expected 30.000 penduduk/fasilitas; actual, versi run, log dan reviewer harus diisi setelah eksekusi. Status tetap not_started, bukan pass. Jika actual berbeda, buat defect, perbaiki, retest fixture dan regresi yang relevan; setelah bukti dan delivery lengkap barulah done. Kedua contoh menggunakan syarat penutupan yang sama tanpa hasil uji fiktif.
