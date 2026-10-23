# Paket kerja folder 01 â€” Inisiasi

## Penyimpanan progres ke GitHub

Instruksi pengguna 23 Oktober 2026 meminta progres disimpan ke GitHub. Commit checkpoint boleh memuat kandidat yang belum diterima. Push checkpoint tidak mengubah status penerimaan tiket atau WF-G1. Field delivery pada checkpoint tiket merujuk pengiriman penutupan setelah penerimaan; bukti push progres dilaporkan terpisah dalam percakapan dengan SHA remote yang terverifikasi.

WF-G1 accepted by the project owner under the revised college-assignment plan. WF-001 through WF-012 are done as an accepted document package; Git acceptance-delivery evidence is reported in the conversation. This does not claim application completion or lecturer approval.

Mulai review dari [charter](WF-004/project-charter.md), [estimasi](WF-008/estimasi-usaha-per-tiket.md), [jadwal](WF-008/jadwal-baseline.md), dan [checklist WF-G1](WF-012/penerimaan-WF-G1.md).

| Tiket | Status formal | Keluaran kandidat |
|---|---|---|
| WF-001 | done | [ringkasan-sumber.md](WF-001/ringkasan-sumber.md), [daftar-konflik.md](WF-001/daftar-konflik.md) |
| WF-002 | done | [register-stakeholder.md](WF-002/register-stakeholder.md), [matriks-penerima-gerbang.md](WF-002/matriks-penerima-gerbang.md) |
| WF-003 | done | [sasaran-dan-indikator-keberhasilan.md](WF-003/sasaran-dan-indikator-keberhasilan.md) |
| WF-004 | done | [project-charter.md](WF-004/project-charter.md), [catatan-review-charter.md](WF-004/catatan-review-charter.md) |
| WF-005 | done | [audit-cakupan-wbs.md](WF-005/audit-cakupan-wbs.md), [matriks-keluaran-wbs.md](WF-005/matriks-keluaran-wbs.md) |
| WF-006 | done | [penugasan-pic-reviewer.md](WF-006/penugasan-pic-reviewer.md), [kapasitas-tim.md](WF-006/kapasitas-tim.md) |
| WF-007 | done | [register-kebutuhan-sumber-daya.md](WF-007/register-kebutuhan-sumber-daya.md), [estimasi-biaya.md](WF-007/estimasi-biaya.md) |
| WF-008 | done | [estimasi-usaha-per-tiket.md](WF-008/estimasi-usaha-per-tiket.md), [jadwal-baseline.md](WF-008/jadwal-baseline.md), [catatan-jalur-kritis.md](WF-008/catatan-jalur-kritis.md) |
| WF-009 | done | [register-risiko.md](WF-009/register-risiko.md) |
| WF-010 | done | [prosedur-perubahan.md](WF-010/prosedur-perubahan.md), [template-change-request.md](WF-010/template-change-request.md), [register-keputusan.md](WF-010/register-keputusan.md) |
| WF-011 | done | [standar-definition-of-done.md](WF-011/standar-definition-of-done.md), [standar-bukti-dan-defect.md](WF-011/standar-bukti-dan-defect.md) |
| WF-012 | done | [rencana-komunikasi.md](WF-012/rencana-komunikasi.md), [penerimaan-WF-G1.md](WF-012/penerimaan-WF-G1.md) |

Current decisions: owner-directed college assignment, free services, milestone-only plan; no invented hours/deadline. See [accepted G1 revision](WF-012/revisi-tugas-kuliah-untuk-persetujuan.md). Release scope is governed by WF-G2. Hasil validasi lokal: [JSON](verifikasi-inisiasi.json). Reproduksi: `python -B docs/pekerjaan/validasi-inisiasi.py`. Estimasi dapat dibentuk ulang dengan `susun-bukti-inisiasi.py`; jangan menjalankan ulang untuk menimpa baseline yang sudah direview tanpa meninjau diff.
