# Handoff peta publik

Tanggal 27 Oktober 2026. WF-087 selesai dan CI 40450699944 berhasil. Implementasi mengikuti API WF-084 dan aturan koordinat WF-042. Pelaksana: agen pengembangan atas instruksi pengguna; tidak mengklaim review eksternal.

Target aktual: `resources/js/map/markers.js`, `resources/views/map.blade.php`, `resources/css/map.css`. Tes berada di `tests/browser/markers.spec.js`, mengikuti direktori Playwright aktual. Rute `/puskesmas/{code}` dan view detail minimal disediakan agar tautan popup berfungsi; halaman ini memakai API detail yang sudah ada, bukan tabel database baru. Navigasi publik membawa release_id/analysis_run_id.

Lihat [bukti pengujian](bukti-peta-marker-cluster.md). Pengiriman dan CI dicatat dalam [checkpoint](checkpoint.json). Lanjut WF-089 setelah keduanya terverifikasi: pencarian dan filter bertingkat. Pertahankan satu pasangan rilis/run, hitungan missing, status gagal yang jujur, dan perlindungan respons terlambat saat menambah filter.

Data Archives, review koordinat dan Supabase tidak diubah. Penerimaan lokasi asli tetap mengikuti `docs/PEKERJAAN-LOKASI-DITUNDA.txt`.
