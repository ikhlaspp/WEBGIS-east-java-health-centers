WITH buffers AS MATERIALIZED (
 SELECT feature->'properties'->>'facility_code' AS facility_code,
 (feature->'properties'->>'radius_m')::integer AS radius_m,
 extensions.ST_GeomFromGeoJSON((feature->'geometry')::text) AS geom
 FROM jsonb_array_elements(?::jsonb) AS feature
), regions AS (
 SELECT d.id,d.geom FROM gis.districts d
 JOIN gis.dataset_releases r ON r.boundary_set_id=d.boundary_set_id WHERE r.id=?::uuid
), clipped AS (
 SELECT d.id,rad.radius_m,d.geom AS region,
 extensions.ST_Multi(extensions.ST_CollectionExtract(extensions.ST_Intersection(
 extensions.ST_UnaryUnion(extensions.ST_Collect(b.geom)),d.geom),3)) AS covered,
 count(DISTINCT b.facility_code) AS contributing_count
 FROM regions d CROSS JOIN (VALUES(1000),(3000),(5000)) rad(radius_m)
 LEFT JOIN buffers b ON b.radius_m=rad.radius_m AND b.geom && d.geom
 AND extensions.ST_Intersects(b.geom,d.geom) AND NOT extensions.ST_Touches(b.geom,d.geom)
 GROUP BY d.id,d.geom,rad.radius_m
)
SELECT id AS district_id,radius_m,extensions.ST_Area(region::extensions.geography,true) AS geometry_area_m2,
 coalesce(extensions.ST_Area(covered::extensions.geography,true),0) AS covered_area_m2,
 CASE WHEN covered IS NULL OR extensions.ST_IsEmpty(covered) THEN NULL ELSE extensions.ST_AsGeoJSON(covered,15) END AS geometry,
 contributing_count,encode(sha256(extensions.ST_AsEWKB(region)),'hex') AS geometry_hash
FROM clipped ORDER BY id,radius_m
