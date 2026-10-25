WITH assessed AS (
 SELECT f.facility_code,f.location,f.selected_review_id,f.coordinate_source_id,
 encode(sha256(convert_to(to_jsonb(r)::text,'UTF8')),'hex') AS review_hash,
 CASE
 WHEN f.coordinate_status<>'verified' THEN 'not_verified'
 WHEN f.precision_level<>'facility' THEN 'not_facility_precision'
 WHEN f.location IS NULL THEN 'missing_coordinates'
 WHEN r.id IS NULL THEN 'missing_review'
 WHEN r.result_status<>'accepted' THEN 'review_not_accepted'
 WHEN r.release_id<>f.release_id OR r.facility_code<>f.facility_code OR r.source_id IS DISTINCT FROM f.coordinate_source_id THEN 'review_identity_mismatch'
 WHEN r.candidate_location IS NULL OR NOT extensions.ST_Equals(r.candidate_location,f.location) THEN 'review_point_mismatch'
 WHEN r.precision_level<>'facility' OR r.reviewed_by IS NULL OR r.reviewed_at IS NULL OR btrim(r.decision_reason)=''
 OR NOT (coalesce(r.evidence_url ~ '^https://[^/[:space:]]+',false) OR (btrim(r.evidence_note)<>'' AND r.evidence_sha256 IS NOT NULL)) THEN 'invalid_review_evidence'
 ELSE NULL END AS exclusion_reason
 FROM gis.facility_snapshots f LEFT JOIN gis.geocode_reviews r ON r.id=f.selected_review_id
 WHERE f.release_id=?::uuid
)
SELECT a.facility_code,a.selected_review_id,a.coordinate_source_id,a.exclusion_reason,a.review_hash,
 extensions.ST_X(a.location) AS longitude,extensions.ST_Y(a.location) AS latitude,r.radius_m,
 CASE WHEN a.exclusion_reason IS NULL THEN extensions.ST_AsGeoJSON(
 extensions.ST_Buffer(a.location::extensions.geography,r.radius_m,'quad_segs=32')::extensions.geometry,15)::jsonb ELSE NULL END AS geometry
FROM assessed a CROSS JOIN (VALUES(1000),(3000),(5000)) r(radius_m)
ORDER BY a.facility_code,r.radius_m
