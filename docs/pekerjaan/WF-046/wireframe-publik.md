# Wireframe halaman publik

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Low-fidelity untuk perilaku/layout, bukan visual produk final. Label `[ ]` adalah kontrol; seluruh halaman membawa periode dan tautan sumber/rilis.

## Desktop 1366px

```text
BERANDA
┌ Logo / Judul ─ Beranda  Peta  Tabel  Metode ─ Login ┐
│ Snapshot fasilitas 2024-S1 | Penduduk2023 | release │
│ [F terdaftar] [Mapped] [Verified] [Missing]          │
│ Tujuan penelitian dan batas interpretasi            │
│ [Buka peta] [Cari di tabel] [Sumber dan metode]      │
│ Peringatan periode/coverage | sumber dan attribution│
└────────────────────────────────────────────────────┘

PETA (panel320px + area fleksibel, min-height560px)
┌ Header + release/period + label coverage parsial ───┐
│[Cari nama/kode/alamat]│ Layer [titik] [batas] [rasio]│
│[Kabupaten v]         │                             │
│[Kecamatan v]         │ MAP + zoom controls         │
│[Pelayanan v][Area v] │ Popup: nama/kode/status      │
│[Reset][Tampilkan]    │ [Detail]                     │
│Hasil filter / F admin│                             │
│Daftar + [Detail]     │ Legenda unit/kelas/no-data   │
│[Buka tabel]          │ radius [1][3][5km] attribution│
└──────────────────────┴─────────────────────────────┘

TABEL
┌ Header/period/release ─────────────────────────────┐
│ Search + filter + [Reset] | hasil N, F wilayah M   │
│ Kode | Nama | Wilayah | Layanan | Lokasi | Detail │
│ ... missing tetap baris dengan status jelas ...  │
│ [Prev] halaman n dari m [Next] | per_page50       │
│ Sumber, metadata dan label no-data               │
└───────────────────────────────────────────────────┘

DETAIL FASILITAS / DETAIL KECAMATAN
┌ Breadcrumb kembali menjaga filter dan rilis ───────┐
│ Nama + kode + parent + edisi                       │
│ Fasilitas: alamat/layanan/status/precision/sumber   │
│ [Fokus peta jika ada titik] [Detail kecamatan]      │
│ Kecamatan: P/tahun | A/tahun | F | rasio/defisit    │
│ eligible/excluded + [Ganti kecamatan]              │
│ Daftar fasilitas semua termasuk missing           │
│ [Sumber nilai] + release/run + keterbatasan         │
└────────────────────────────────────────────────────┘

METODE/SUMBER
┌ Header ─ sumber/period/release ─────────────────────┐
│ [Definisi] [Sumber] [Kualitas] [Artefak]            │
│ P/A/F/T, rumus, radius geometris, batas interpretasi│
│ Penerbit | Judul | Tahun observasi | Locator | URL │
│ [Notebook] [HTML penelitian] sesuai rilis/run      │
└────────────────────────────────────────────────────┘
```

## Mobile360px dan tablet768px

Header nav membungkus/menu accessible; satu kolom kartu beranda. Peta tinggi min360px/max70vh dengan tombol Filter dan Daftar di atas, bukan overlay yang menutup semua kontrol. Panel filter mobile width100%, max-height80vh, scroll internal; tombol Tutup sticky dan fokus terperangkap hanya selama dialog terbuka. Tablet≥768 memakai panel280px bila map tersisa≥400px, jika tidak pola mobile.

```text
┌ Judul       [Menu] ┐    ┌ FILTER dialog ─ [X] ┐
│ Periode / release  │    │ Cari / Kab / Kec    │
│ Partial x/y [Info] │    │ Layanan / Area      │
│ [Filter] [Daftar]  │    │ [Reset] [Terapkan]  │
│ MAP +zoom          │    └─────────────────────┘
│ [Layer] [Legenda] │
│ Attribution       │
└────────────────────┘
```

Tabel mobile horizontal scroll berlabel dengan kolom kode/nama/detail selalu dapat dicapai; tidak menghapus kolom sumber/status. Detail mobile menumpuk label/nilai, sumber tepat di bawah angka, tanpa mini-map wajib untuk missing. Metode accordion dengan heading semantik dan seluruh isi keyboard accessible. Popup max-width min(300px,viewport−32px), max-height50vh, scroll dan close accessible.

State slots: loading skeleton+aria-live (bukan0), empty filter+Reset, dataset belum terbit, API error+Retry, tile error+tabel tetap, null indicator+alasan. Posisi banner di bawah header berlaku semua viewport. Legend bukan tooltip hover-only; dapat dibuka tap/keyboard. Aksi perbandingan UC-02 memakai dua detail ber-release sama, bukan layar compare baru. Elemen CSV/ranking/admin dashboard tidak dirancang sebagai fitur aktif selama P1 belum dipilih.
