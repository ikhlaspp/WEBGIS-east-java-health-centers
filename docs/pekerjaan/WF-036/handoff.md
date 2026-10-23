# Handoff WF-036

Versi1 · 23 Oktober2026 · Pelaksana Codex · Status in_review.

## Dasar dan keluaran

Input: [SRS kandidat](../WF-028/SRS-baseline.md), dokumen kebutuhan terkait dan instruksi pengguna melanjutkan folder03. Otorisasi lanjut dipakai tanpa mengarang persetujuan akademik atau keputusan data. Sumber versi/hash dicatat pada [manifest input](../WF-052/manifest-input.json).

- [desain-lifecycle-rilis.md](desain-lifecycle-rilis.md)
- [desain-backup-rollback.md](desain-backup-rollback.md)

## Pemeriksaan mandiri

Expected: Rollback memilih versi valid sebelumnya tanpa menghapus sejarah; koreksi data membentuk rilis baru.

Actual: Lifecycle/version CAS/audit/outbox/visibility-before-cache dan backupDB+file/restore/rollback dijelaskan dengan race failure cases.

[Verifikasi paket](../WF-052/verifikasi-desain.json) menguji struktur/hash/traceability/JSON/arithmetic. Tidak membuktikan migration, PostGIS, browser aplikasi atau UAT sudah lulus. Jam aktual tidak diukur dan tidak diganti estimasi.

## Tindak lanjut dan pengiriman

- Review/penerimaan stakeholder belum tercatat; status in_review bukan done/accepted.
- Hosting/akun/budget/versiDB aktual dan operator bernama perlu dikonfirmasi sebelum provisioning/operasi.

Satu progress commit memuat keluaran item ini; judul tanpa ID tiket sesuai pengguna. SHA/remote diverifikasi setelah push. Planning tetap ignored, tidak force-add. Setelah keputusan reviewer tersedia, perbarui versi/desain terdampak dan catat acceptance nyata.
