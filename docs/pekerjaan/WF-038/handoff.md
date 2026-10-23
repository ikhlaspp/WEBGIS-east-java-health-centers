# Handoff WF-038

Versi1 · 23 Oktober2026 · Pelaksana Codex · Status in_review.

## Dasar dan keluaran

Input: [SRS kandidat](../WF-028/SRS-baseline.md), dokumen kebutuhan terkait dan instruksi pengguna melanjutkan folder03. Otorisasi lanjut dipakai tanpa mengarang persetujuan akademik atau keputusan data. Sumber versi/hash dicatat pada [manifest input](../WF-052/manifest-input.json).

- [spesifikasi-normalisasi-crosswalk.md](spesifikasi-normalisasi-crosswalk.md)

## Pemeriksaan mandiri

Expected: Aturan tidak menebak kode wilayah dari nama atau potongan kode fasilitas dan tidak menghapus baris hanya demi jumlah target.

Actual: Raw/typed split, locale/unit/null, code+parent+edition, approved aliases dan Sempol–Ijen tanpa double-count didesain.

[Verifikasi paket](../WF-052/verifikasi-desain.json) menguji struktur/hash/traceability/JSON/arithmetic. Tidak membuktikan migration, PostGIS, browser aplikasi atau UAT sudah lulus. Jam aktual tidak diukur dan tidak diganti estimasi.

## Tindak lanjut dan pengiriman

- Review/penerimaan stakeholder belum tercatat; status in_review bukan done/accepted.
- Edisi/izin polygon historis, provider lokasi dan keputusan full/partial belum final.

Satu progress commit memuat keluaran item ini; judul tanpa ID tiket sesuai pengguna. SHA/remote diverifikasi setelah push. Planning tetap ignored, tidak force-add. Setelah keputusan reviewer tersedia, perbarui versi/desain terdampak dan catat acceptance nyata.
