# Handoff WF-035

Versi1 · 23 Oktober2026 · Pelaksana Codex · Status in_review.

## Dasar dan keluaran

Input: [SRS kandidat](../WF-028/SRS-baseline.md), dokumen kebutuhan terkait dan instruksi pengguna melanjutkan folder03. Otorisasi lanjut dipakai tanpa mengarang persetujuan akademik atau keputusan data. Sumber versi/hash dicatat pada [manifest input](../WF-052/manifest-input.json).

- [desain-otorisasi-dan-grants.md](desain-otorisasi-dan-grants.md)

## Pemeriksaan mandiri

Expected: Runtime harian tidak memakai owner/BYPASSRLS; policy tidak mengasumsikan auth.uid Supabase jika identitas memakai session Laravel.

Actual: Grants/RLS roles non-owner, session dan operator token/abilities dirancang; tidak percaya --actor/auth.uid tanpa identitas.

[Verifikasi paket](../WF-052/verifikasi-desain.json) menguji struktur/hash/traceability/JSON/arithmetic. Tidak membuktikan migration, PostGIS, browser aplikasi atau UAT sudah lulus. Jam aktual tidak diukur dan tidak diganti estimasi.

## Tindak lanjut dan pengiriman

- Review/penerimaan stakeholder belum tercatat; status in_review bukan done/accepted.
- Hosting/akun/budget/versiDB aktual dan operator bernama perlu dikonfirmasi sebelum provisioning/operasi.

Satu progress commit memuat keluaran item ini; judul tanpa ID tiket sesuai pengguna. SHA/remote diverifikasi setelah push. Planning tetap ignored, tidak force-add. Setelah keputusan reviewer tersedia, perbarui versi/desain terdampak dan catat acceptance nyata.
