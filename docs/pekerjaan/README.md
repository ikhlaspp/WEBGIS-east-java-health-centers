# Paket kerja folder 01 — Inisiasi

## Penyimpanan progres ke GitHub

Instruksi pengguna 23 Oktober 2026 meminta progres disimpan ke GitHub. Commit checkpoint boleh memuat kandidat yang belum diterima. Push checkpoint tidak mengubah status penerimaan tiket atau WF-G1. Field delivery pada checkpoint tiket merujuk pengiriman penutupan setelah penerimaan; bukti push progres dilaporkan terpisah dalam percakapan dengan SHA remote yang terverifikasi.

Versi kandidat 1, 23 Oktober 2026. Pelaksana persiapan: Codex. Semua keluaran lokal yang dapat dibuat telah disiapkan; penerimaan stakeholder dan delivery belum selesai. Tidak ada gerbang accepted atau tiket done yang diklaim.

Mulai review dari [charter](WF-004/project-charter.md), [estimasi](WF-008/estimasi-usaha-per-tiket.md), [jadwal](WF-008/jadwal-baseline.md), dan [checklist WF-G1](WF-012/penerimaan-WF-G1.md).

| Tiket | Status formal | Keluaran kandidat |
|---|---|---|
| WF-001 | in_review | [ringkasan-sumber.md](WF-001/ringkasan-sumber.md), [daftar-konflik.md](WF-001/daftar-konflik.md) |
| WF-002 | blocked | [register-stakeholder.md](WF-002/register-stakeholder.md), [matriks-penerima-gerbang.md](WF-002/matriks-penerima-gerbang.md) |
| WF-003 | blocked | [sasaran-dan-indikator-keberhasilan.md](WF-003/sasaran-dan-indikator-keberhasilan.md) |
| WF-004 | blocked | [project-charter.md](WF-004/project-charter.md), [catatan-review-charter.md](WF-004/catatan-review-charter.md) |
| WF-005 | blocked | [audit-cakupan-wbs.md](WF-005/audit-cakupan-wbs.md), [matriks-keluaran-wbs.md](WF-005/matriks-keluaran-wbs.md) |
| WF-006 | blocked | [penugasan-pic-reviewer.md](WF-006/penugasan-pic-reviewer.md), [kapasitas-tim.md](WF-006/kapasitas-tim.md) |
| WF-007 | blocked | [register-kebutuhan-sumber-daya.md](WF-007/register-kebutuhan-sumber-daya.md), [estimasi-biaya.md](WF-007/estimasi-biaya.md) |
| WF-008 | blocked | [estimasi-usaha-per-tiket.md](WF-008/estimasi-usaha-per-tiket.md), [jadwal-baseline.md](WF-008/jadwal-baseline.md), [catatan-jalur-kritis.md](WF-008/catatan-jalur-kritis.md) |
| WF-009 | blocked | [register-risiko.md](WF-009/register-risiko.md) |
| WF-010 | blocked | [prosedur-perubahan.md](WF-010/prosedur-perubahan.md), [template-change-request.md](WF-010/template-change-request.md), [register-keputusan.md](WF-010/register-keputusan.md) |
| WF-011 | blocked | [standar-definition-of-done.md](WF-011/standar-definition-of-done.md), [standar-bukti-dan-defect.md](WF-011/standar-bukti-dan-defect.md) |
| WF-012 | blocked | [rencana-komunikasi.md](WF-012/rencana-komunikasi.md), [penerimaan-WF-G1.md](WF-012/penerimaan-WF-G1.md) |

Keputusan yang dibutuhkan: tim/PIC/reviewer dan jam kerja, tenggat, budget/layanan yang tersedia, serta penerima bernama WF-G1. P1 dapat diputus pada WF-G2. Hasil validasi lokal: [JSON](verifikasi-inisiasi.json). Reproduksi: `python -B docs/pekerjaan/validasi-inisiasi.py`. Estimasi dapat dibentuk ulang dengan `susun-bukti-inisiasi.py`; jangan menjalankan ulang untuk menimpa baseline yang sudah direview tanpa meninjau diff.
