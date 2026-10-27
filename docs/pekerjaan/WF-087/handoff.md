# Handoff dashboard publik

Input: WF-086 selesai pada commit `253480d964d53e05ed34fcf83fd70daa787da9fd`, wireframe WF-046 dan kontrak API statistik/wilayah/sumber yang sudah tersedia.

Implementasi dan pengujian lokal selesai. Lihat [bukti dashboard](bukti-dashboard-responsif.md) dan [checkpoint](checkpoint.json). Pengiriman GitHub dan full CI harus diverifikasi sebelum melanjutkan antrean serial.

Lanjut WF-088: peta dasar, marker, cluster dan popup aman. Gunakan layout publik dan pertahankan release_id/analysis_run_id saat menambahkan navigasi peta. Fasilitas tanpa koordinat tetap dihitung, tidak diberi marker pengganti. Jangan menyamakan koordinat tersedia dengan lokasi terverifikasi atau layak analisis.

Data Archives dan konfigurasi Supabase asli tidak diubah. Prasyarat penerimaan lokasi dan deployment tetap mengikuti `docs/PEKERJAAN-LOKASI-DITUNDA.txt`.
