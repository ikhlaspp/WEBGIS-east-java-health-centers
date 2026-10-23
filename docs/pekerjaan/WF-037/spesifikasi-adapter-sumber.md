# Adapter akuisisi sumber

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Kontrak implementasi Python, bukan batch sudah dijalankan. Bukti discovery/sampel ada pada [kelayakan sumber](../WF-018/catatan-kelayakan-sumber.md).

Interface: `discover(source_spec) -> document_refs`; `fetch(ref, cache) -> raw_manifest`; `parse(raw_manifest) -> rows, diagnostics`; `validate_completeness(rows, expected) -> report`. Setiap row membawa source_id, file_hash, locator, parser_version, raw_fields; tidak langsung menulis domain. SourceSpec mengunci dataset/edisi/URL allowlist dan license decision. URL user arbitrary tidak boleh menjadi SSRF; reject private/link-local destinations, non-HTTPS dan redirect keluar allowlist pada semua hops.

| Adapter | Endpoint/discovery dan input | Parser/output | Kelengkapan / gagal |
|---|---|---|---|
| KemenkesFacilityPdf | `https://kemkes.go.id/id/data-puskesmas-teregistrasi-semester-i-tahun-2024`; tautan PDF spesifik1690/2024 dari katalog | Header kode/nama/alamat/kecamatan/kab/provinsi/layanan/karakter; multiline diikat kode11digit; output identity_raw | Filter provinsi Jatim setelah parse; reconcile973/38/kategori, pages manifest239 pada sampel; jangan hardcode jumlah halaman semua edisi |
| BpsPublication | Daftar38 URL publikasi terpilih; sampel Bangkalan dari katalog, bukan semua hasil search | Table identity/year/unit dikenali; rows district_raw/population_raw/area_raw dengan PDF page dan printed page | expected document list lengkap; tabel tidak ditemukan/scan → requires_ocr, bukan rows=[] sukses |
| BpsTableDownload | URL unduhan tabel resmi yang didapat dari halaman dataset berperiode eksplisit | CSV header/locale/unit/schema contract per tabel; total dipisahkan | Cocokkan code/period/definition dengan publikasi; fallback tidak otomatis memakai2025 |
| BpsMasterFile | MFD Jatim2023 landing URL dari katalog → PDF | Kode/parent/nama string per tingkat, perubahan wilayah sebagai metadata | Reconcile edisi dan set parent; jumlah666 hanya pembanding, bukan filter |
| BigBoundary | MapServer/0 pada URL katalog; metadata format/fields diperiksa dulu | Query scoped province field KDPBPS setelah verifikasi nilai, returnIdsOnly lalu chunks IDs atau pagination1000; outSR4326 | Count IDs total/unique/exceededTransferLimit; edisi2026/izin belum accepted sehingga download produksi disabled |
| LocationEvidence | Koordinat resmi dan bukti per facility_code; provider batch optional configured | Candidate point/provider object/precision/raw response hash | Public Nominatim default disabled; provider/license/rate budget harus dipilih sebelum query |

Fetch connect10s/read60s, max3 attempts untuk transient sesuai WF-032, User-Agent identitas proyek nyata, cache by canonical URL+edition+hash/ETag; conditional GET hanya untuk cek perubahan, tidak overwrite snapshot. Rate default serial≤1request/s untuk discovery/download metadata; aturan provider yang lebih ketat menang. Retry-After dihormati. Tidak scraping CAPTCHA/login atau menjalankan autocomplete geocoder.

Parser contoh sintetis: `{kode:'035001',penduduk:'30.001',unit:'jiwa',year:2023,locator:'table3.1.1/page89/row4'}` → `{code:'035001',population:30001,...,raw_value:'30.001'}` jika locale id_ID eksplisit. Input header tanpa unit/year → quarantined metadata_missing. HTTP200 berisi login page/PDF rusak → content_type_or_magic_mismatch, bukan parsed. Hilang satu page/ID → incomplete_source dan release promotion blocked. OCR perlu per-row visual review dan independent total; raw text dump tidak menjadi bukti akurasi.

Provider source formats diubah lewat schema version dan fixture regression; tidak fuzzy menggeser kolom tanpa flag. Penyimpanan raw lokal/private; hanya source metadata yang izin publikasikannya jelas diekspos. Edisi polygon/provider yang masih terbuka tercatat pada gerbang, tidak diputuskan melalui keberhasilan parsing.
