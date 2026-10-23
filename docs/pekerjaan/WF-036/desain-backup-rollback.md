# Backup, restore dan rollback

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Target SRS RPO24h/RTO4h, bukan hasil drill.

Backup checkpoint mengikat DB dump/snapshot, artifact inventory/hash, raw yang boleh disimpan, code revision dan locks. Jadwal harian + sebelum migrasi/publish berisiko; retensi7harian+4mingguan dengan satu salinan lokasi terpisah dan akses terenkripsi. Secret recovery terpisah dari repo/log. OP owner peran, nama/layanan/budget masih menunggu pemilik.

Prosedur restore: catat incident/time → pilih checkpoint utuh → provision DB/storage terisolasi dengan engine kompatibel → restore schema/data/grants tanpa memakai produksi sebagai eksperimen → restore file inventory → cocokkan hashes/FK/count/pointer/run → pasang code/lock yang sesuai → buat credential environment baru → smoke login/API/map/HTML → catat waktu selesai dan recovery point. RTO mencakup smoke, RPO selisih insiden terhadap checkpoint konsisten. Jangan menganggap dump DB mencakup object storage; lihat [backup Supabase](https://supabase.com/docs/guides/platform/backups).

Rollback data normal hanya pointer ke rilis published lama yang valid. Restore disaster tidak sama dengan rollback rilis dan memerlukan jendela operasi, diagnosis, backup bukti kondisi rusak dan owner nyata. Schema rollback menggunakan code backward-compatible atau checkpoint restore; tidak menjalankan drop cascade spontan. Rilis withdrawn tidak boleh menjadi target rollback. Backup lebih tua24h memblokir publish baru sesuai target; alert/retry tercatat.

Drill WF-122: hilangkan satu file pada restore test untuk memastikan deteksi; uji backup mismatch release, grant runtime salah, dan checkpoint valid. Expected gagal tertahan pada mismatch, sukses hanya setelah count/hash/permissions/artefak/smoke semua pulih. Laporan menyertakan ukuran, durasi, lokasi backup tersanitasi, timestamp, operator dan defect; jangan mengisi nilai RPO/RTO sebelum dijalankan.
