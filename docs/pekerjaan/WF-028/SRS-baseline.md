> Current baseline: accepted under [WF-G2](penerimaan-WF-G2.md). [The accepted college supplement](revisi-tugas-kuliah-untuk-persetujuan.md) supersedes candidate-status and source-selection timing statements below. Core requirements remain; four optional features are deferred.

# Spesifikasi kebutuhan perangkat lunak

Versi kandidat 1.0 · 23 Oktober 2026 · Penyusun: Codex. Status: accepted with the linked college-project supplement.

## Tujuan dan konteks

WebGIS menyajikan persebaran puskesmas Jawa Timur historis 2024-S1, indikator penduduk/luas dan radius geometris. Dataset awal 973 fasilitas pada 38 kabupaten/kota; kandidat lokasi 565 terisi dan 408 kosong. Angka ini merupakan hasil audit raw, bukan lokasi tervalidasi. Keluaran adalah aplikasi Laravel/Leaflet, PostgreSQL/PostGIS melalui Supabase, pipeline Python, notebook Colab/Folium dan laporan yang bisa direproduksi. Tidak ada data pasien, akun masyarakat atau rekomendasi pembangunan otomatis.

Role aplikasi hanya admin dan guest. Guest tanpa akun membaca rilis terbit. Admin login dan command lifecycle P0; dashboard/review UI/CSV publik/ranking merupakan empat opsi P1. Scope P0-first is accepted; individual P1 deferrals are recorded in the scope register.

## Dokumen normatif kandidat

Dokumen tertaut adalah bagian SRS versi ini; manifest paket memuat SHA256 agar perubahan dapat dilacak. Salinan planning lokal merupakan sumber sejarah, bukan dependensi yang harus tersedia di clone GitHub untuk membaca kebutuhan ini.

| Bagian | Spesifikasi | Kriteria utama |
|---|---|---|
| Use cases | [Skenario](../WF-013/skenario-penggunaan.md) | UC-01–12 lengkap input/hasil/failure |
| Fungsi/scope | [Matriks FR](../WF-014/matriks-FR-dan-scope-rilis.md) | 17 FR, P0/P1/P2 dan build/test trace |
| Akses | [Matriks akses](../WF-015/matriks-hak-akses-aplikasi.md) | Guest published-only; admin/CLI authorized; tanpa pengelola terpisah |
| UI | [Halaman/konten](../WF-016/inventaris-halaman-dan-konten.md) | Missing tetap ada di tabel; state loading/error/empty/no-data |
| Dataset | [Ketersediaan](../WF-017/matriks-ketersediaan-dataset.md) | Raw/staging/verified dibedakan |
| Akuisisi | [Katalog](../WF-018/katalog-sumber-scraping.md), [kelayakan](../WF-018/catatan-kelayakan-sumber.md) | Sumber primer, format, sample, izin/edisi terbuka |
| Semantik data | [Periode/unit/identitas](../WF-019/kebijakan-periode-unit-identitas.md) | Snapshot dan tahun observasi terpisah; kode+parent+edisi |
| Kualitas | [Aturan kualitas](../WF-020/aturan-kualitas-dataset.md) | DQ-01–11; publish blockers, eligibility dan partial labels |
| Indikator | [Katalog indikator](../WF-021/katalog-indikator.md) | F administratif; formula/null/zero/agregasi/parameter |
| Visual | [Layer/legenda](../WF-022/kebutuhan-layer-dan-legenda.md) | Breakpoints tetap, no-data bukan nol |
| Spasial | [Radius](../WF-023/kebutuhan-analisis-radius.md) | Meter, verified, union/clip, geometri denominator |
| Penelitian | [Artefak](../WF-024/spesifikasi-keluaran-penelitian.md) | Notebook/HTML/tabel/manifest satu run |
| Performa/usability | [Target terukur](../WF-025/baseline-performa-dan-kegunaan.md) | Profil API/map/mobile/keyboard |
| Security/recovery/repro | [Baseline](../WF-026/baseline-keamanan-pemulihan-reproduksi.md) | Role/secret/audit; backup DB+file; lock/hash |
| Verifikasi | [Matriks FR/NFR-uji](../WF-027/matriks-kebutuhan-pengujian.md), [UAT](../WF-027/strategi-UAT.md) | Semua 17 FR dan 8 NFR terlacak; actual belum ada |
| Scope final | [Register keputusan](keputusan-scope-P1.md) | Accepted P1 deferrals and partial-demonstration conditions |

## Kontrak lintas bagian

1. Semua request satu tampilan memakai release_id sama; API publik tidak membuka draft. Run mengikat T/radius/boundary/input hash/code revision. Publikasi dan audit atomik; published immutable dan rollback pointer terkontrol.
2. Pencarian meliputi seluruh master, termasuk missing. Filter layanan mengubah daftar/marker, bukan F administratif atau rasio wilayah. Nol dan null mempunyai arti berbeda sampai ke JSON/tabel/legenda.
3. Analisis radius hanya verified facility. Eligible kosong dengan data master yang belum verified berarti unavailable. Union mencegah overlap ganda; denominator area geometri, bukan A statistik atau penduduk.
4. Tahun campuran harus terlihat. MFD 2023 target kode tidak mengesahkan polygon BIG 2026. Edisi/izin/crosswalk tetap memerlukan bukti sebelum penggunaan produksi.
5. P1 ditunda tidak menunda validasi file S05-IMPORT, A08-PARAM, login/command backend, audit, export artefak penelitian atau UAT P0.

## Penerimaan dan kendali perubahan

Penerimaan kebutuhan memerlukan keputusan scope dan sumber/periode/cakupan, review konsistensi, penerima nyata, tanggal dan versi paket. Penerimaan rilis nanti memerlukan uji P0 (serta P1 terpilih) aktual, nol critical/high, restore, reproduksi dan UAT. Angka performa/RPO/RTO adalah target, bukan hasil. Pemeriksaan paket dokumen tidak menggantikan pengujian aplikasi atau reviewer eksternal.

Perubahan setelah accepted menggunakan CR, mencatat kebutuhan dan tiket/test terdampak, versi/hash lama/baru, usaha/risiko dan keputusan pemilik. Kebutuhan yang berubah membuka kembali bukti lama bila tidak lagi berlaku. WF-G2 acceptance is now recorded; [checklist gerbang](penerimaan-WF-G2.md) mencatat status aktual.
