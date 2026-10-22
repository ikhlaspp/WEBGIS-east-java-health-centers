-- READ ONLY. Jalankan SETELAH impor 3 CSV ke planning_staging.
-- Belum dieksekusi terhadap PostgreSQL pada tahap perencanaan.
-- Expected berikut hanya berlaku untuk hash input dalam inventaris_sumber.csv.

-- Expected: 973 rows, 973 codes, 38 regencies.
SELECT count(*) AS rows, count(DISTINCT kode_puskesmas) AS unique_codes,
       count(DISTINCT kabupaten) AS regencies
FROM planning_staging.puskesmas_2024_s1;

-- Expected: 565 pairs, 408 missing, 0 eligible.
SELECT
  count(*) FILTER (WHERE nullif(latitude, '') IS NOT NULL AND nullif(longitude, '') IS NOT NULL) AS coordinate_pairs,
  count(*) FILTER (WHERE nullif(latitude, '') IS NULL OR nullif(longitude, '') IS NULL) AS missing_coordinates,
  count(*) FILTER (WHERE eligible_for_buffer = 'true') AS eligible_for_buffer
FROM planning_staging.puskesmas_2024_s1;

-- Expected: empty result. Detect missing/duplicate identities before promotion.
SELECT kode_puskesmas, count(*)
FROM planning_staging.puskesmas_2024_s1
GROUP BY kode_puskesmas
HAVING count(*) > 1 OR nullif(trim(kode_puskesmas), '') IS NULL;

-- Expected: 5 groups with 2 facilities each. Review, do not DELETE duplicates.
SELECT latitude, longitude, count(*) AS facilities,
       string_agg(kode_puskesmas || ' ' || nama_puskesmas, '; ' ORDER BY kode_puskesmas) AS identities
FROM planning_staging.puskesmas_2024_s1
WHERE nullif(latitude, '') IS NOT NULL AND nullif(longitude, '') IS NOT NULL
GROUP BY latitude, longitude
HAVING count(*) > 1;

-- Expected: Rawat Inap 616, Non Rawat Inap 357.
SELECT kemampuan_pelayanan, count(*) FROM planning_staging.puskesmas_2024_s1
GROUP BY kemampuan_pelayanan;

-- Expected: 658 Perdesaan, 294 Perkotaan, 16 Terpencil, 5 Sangat Terpencil.
SELECT karakteristik_wilayah, count(*) FROM planning_staging.puskesmas_2024_s1
GROUP BY karakteristik_wilayah;

-- Check invalid raw integer fields FIRST; expected empty.
SELECT 'kecamatan_gabungan' AS source, source_row::text AS source_key, jumlah_puskesmas
FROM planning_staging.kecamatan_gabungan
WHERE jumlah_puskesmas IS NULL OR jumlah_puskesmas !~ '^[0-9]+$'
UNION ALL
SELECT 'jumlah_puskesmas_kecamatan', kabupaten || '/' || kecamatan, jumlah_puskesmas
FROM planning_staging.jumlah_puskesmas_kecamatan
WHERE jumlah_puskesmas IS NULL OR jumlah_puskesmas !~ '^[0-9]+$';

-- Expected: 667 rows, 973 total; null counted independently. CASE avoids unsafe cast.
SELECT count(*) AS rows,
       sum(CASE WHEN jumlah_puskesmas ~ '^[0-9]+$' THEN jumlah_puskesmas::bigint END) AS total_facilities,
       count(*) FILTER (WHERE nullif(jumlah_penduduk, '') IS NULL) AS missing_population,
       count(*) FILTER (WHERE nullif(luas_km2, '') IS NULL) AS missing_area
FROM planning_staging.kecamatan_gabungan;

-- Expected: Bondowoso / Sempol only. Do not fill with zero.
SELECT source_row, kabupaten, kecamatan, jumlah_penduduk, luas_km2
FROM planning_staging.kecamatan_gabungan
WHERE nullif(jumlah_penduduk, '') IS NULL OR nullif(luas_km2, '') IS NULL;

-- Expected: 665 rows, 973 facilities, 0 aggregate rows.
SELECT count(*) AS rows,
       sum(CASE WHEN jumlah_puskesmas ~ '^[0-9]+$' THEN jumlah_puskesmas::bigint END) AS facilities,
       count(*) FILTER (WHERE upper(kabupaten) = 'TOTAL' OR upper(kecamatan) = 'TOTAL') AS aggregate_rows
FROM planning_staging.jumlah_puskesmas_kecamatan;

-- Expected empty: exact raw-name counts match facility master.
WITH actual AS (
  SELECT kabupaten, kecamatan, count(*) AS n
  FROM planning_staging.puskesmas_2024_s1 GROUP BY kabupaten, kecamatan
), reported AS (
  SELECT kabupaten, kecamatan,
         CASE WHEN jumlah_puskesmas ~ '^[0-9]+$' THEN jumlah_puskesmas::bigint END AS n
  FROM planning_staging.jumlah_puskesmas_kecamatan
)
SELECT coalesce(a.kabupaten, r.kabupaten) AS kabupaten,
       coalesce(a.kecamatan, r.kecamatan) AS kecamatan, a.n AS actual, r.n AS reported
FROM actual a FULL OUTER JOIN reported r USING (kabupaten, kecamatan)
WHERE a.n IS DISTINCT FROM r.n;
