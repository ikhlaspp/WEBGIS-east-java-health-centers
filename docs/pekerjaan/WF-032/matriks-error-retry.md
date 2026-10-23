# Error, retry dan pesan

Versi 1 · 23 Oktober 2026 · Penyusun: Codex.

| Error | Retry desain | Dampak / operator |
|---|---|---|
| DNS/connect/timeout/502/503 | Maksimum3 attempts, backoff5/15s+jitter; connect10s/read60s | Raw partial tidak promoted; log URL sanitasi/correlation; operator cek sumber bila habis |
| HTTP429 | Hormati Retry-After; jadwalkan ulang maksimal3 attempts, tidak busy-loop | Bila jeda melebihi job deadline, pending sampai due_at atau failed dengan alasan; jangan tambah concurrency |
| 401/403/izin/CAPTCHA | Tidak retry otomatis | Periksa hak akses; tidak bypass; sumber blocked |
| 404 dokumen historis | Tidak beralih ke edisi terbaru | Operator memilih fallback setara dengan provenance baru |
| Header/format/expected IDs berubah | Tidak retry parser yang sama | quarantine, schema_changed; fixture baru dan review adapter |
| Angka/unit/mapping ambiguous | Tidak retry otomatis | Baris dan locator disimpan; koreksi berbukti |
| Constraint/FK/duplikat | Rollback transaksi chunk | Error report; perbaiki input, tidak disable constraints |
| Deadlock/serialization | Maksimum3 transaksi baru, jitter50–250ms | Revalidate expected pointer/input; jika konflik bisnis 409, jangan retry sebagai sukses |
| Storage unavailable/hash mismatch | Retry transient3; mismatch tidak retry buta | Run tidak succeeded/published; hapus hanya temp milik attempt setelah audit |
| Post-commit cache/outbox gagal | Outbox retry5, exponential hingga15min, kemudian alert | Commit tetap benar; visibility diperiksa sebelum cache read, pointer dibaca fresh |

Batas job chunk15min; download besar boleh konfigurasi timeout terukur sebelum akuisisi, tidak infinity. Batch OCR/manual panjang dipecah checkpoint, bukan proses15min yang kehilangan seluruh kerja. Public API timeout memberikan503 `{error:{code,message,request_id}}`; jangan bocorkan SQL/path/token. Internal log menyimpan source_id, stage, attempt, sanitized exception, counts dan elapsed_ms. Field secrets/headers auth selalu disensor.
