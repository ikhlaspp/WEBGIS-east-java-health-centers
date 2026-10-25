WITH counts AS (
 SELECT district_id,count(*) AS facility_count,jsonb_agg(DISTINCT source_id) AS facility_sources
 FROM gis.facility_snapshots WHERE release_id=?::uuid GROUP BY district_id
), inputs AS (
 SELECT d.id AS district_id,d.code,p.code AS parent_code,d.name,i.population,i.area_km2,
 i.population_year,i.area_year,i.population_source_id,i.area_source_id,
 coalesce(c.facility_count,0) AS facility_count,coalesce(c.facility_sources,'[]'::jsonb) AS facility_sources,
 extensions.ST_AsGeoJSON(d.geom,15) AS full_geometry
 FROM gis.districts d JOIN gis.regencies p ON p.id=d.regency_id
 JOIN gis.dataset_releases r ON r.boundary_set_id=d.boundary_set_id
 LEFT JOIN gis.district_indicators i ON i.release_id=r.id AND i.district_id=d.id
 LEFT JOIN counts c ON c.district_id=d.id WHERE r.id=?::uuid
), calculated AS (
 SELECT *,ceil(population::numeric/?::bigint)::bigint AS indicative_need FROM inputs
)
SELECT *, (population::numeric/area_km2)::numeric(24,12) AS density,
 (population::numeric/nullif(facility_count,0))::numeric(24,12) AS population_per_facility,
 (facility_count::numeric*30000/nullif(population,0))::numeric(24,12) AS facilities_per_30000,
 CASE WHEN indicative_need IS NULL THEN NULL ELSE greatest(0,indicative_need-facility_count) END AS indicative_deficit,
 facility_count=0 AS without_facility
FROM calculated ORDER BY code
