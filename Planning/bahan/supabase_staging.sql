-- DRAFT PERENCANAAN 2026-10-22. Belum dijalankan di Supabase/PostgreSQL.
-- Hanya untuk schema baru pada environment test Supabase.
-- Kolom mentah TEXT disengaja: validasi dan casting dilakukan pada kurasi.
-- Tidak membuat database produksi, role aplikasi, PostGIS, atau policy publik.
-- Jika schema sudah ada, CREATE SCHEMA gagal dan transaksi harus dibatalkan.
BEGIN;

CREATE SCHEMA planning_staging;
REVOKE ALL ON SCHEMA planning_staging FROM PUBLIC, anon, authenticated, service_role;

CREATE TABLE planning_staging.puskesmas_2024_s1 (
    source_row integer PRIMARY KEY,
    no text,
    kode_puskesmas text,
    nama_puskesmas text,
    alamat text,
    kecamatan text,
    kabupaten text,
    provinsi text,
    kemampuan_pelayanan text,
    karakteristik_wilayah text,
    query_alamat text,
    latitude text,
    longitude text,
    status_geocoding text,
    periode_fasilitas text,
    coordinate_review_status text,
    precision_level text,
    eligible_for_buffer text
);

CREATE TABLE planning_staging.kecamatan_gabungan (
    source_row integer PRIMARY KEY,
    kabupaten text,
    kecamatan text,
    jumlah_penduduk text,
    luas_km2 text,
    jumlah_puskesmas text
);

CREATE TABLE planning_staging.jumlah_puskesmas_kecamatan (
    kabupaten text,
    kecamatan text,
    jumlah_puskesmas text
);

ALTER TABLE planning_staging.puskesmas_2024_s1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE planning_staging.kecamatan_gabungan ENABLE ROW LEVEL SECURITY;
ALTER TABLE planning_staging.jumlah_puskesmas_kecamatan ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON ALL TABLES IN SCHEMA planning_staging FROM PUBLIC, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA planning_staging
    REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated, service_role;

COMMENT ON SCHEMA planning_staging IS
    'Bahan mentah perencanaan; tidak diekspos Data API, belum layak untuk analisis publik';

COMMIT;
