<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;
GRANT SELECT,INSERT ON gis.analysis_runs,gis.indicator_results,gis.coverage_results,gis.artifacts TO gis_lifecycle_owner;
GRANT UPDATE(status,finished_at,output_manifest) ON gis.analysis_runs TO gis_lifecycle_owner;
GRANT EXECUTE ON FUNCTION gis.valid_geometry(extensions.geometry,text) TO gis_lifecycle_owner;

CREATE FUNCTION gis.analysis_indicator_rows(target uuid,threshold bigint) RETURNS SETOF jsonb LANGUAGE sql STABLE SET search_path=pg_catalog AS $fn$
SELECT to_jsonb(q) FROM (WITH counts AS (
 SELECT district_id,count(*) AS facility_count,jsonb_agg(DISTINCT source_id) AS facility_sources
 FROM gis.facility_snapshots WHERE release_id=target::uuid GROUP BY district_id
), inputs AS (
 SELECT d.id AS district_id,d.code,p.code AS parent_code,d.name,i.population,i.area_km2,
 i.population_year,i.area_year,i.population_source_id,i.area_source_id,
 coalesce(c.facility_count,0) AS facility_count,coalesce(c.facility_sources,'[]'::jsonb) AS facility_sources,
 extensions.ST_AsGeoJSON(d.geom,15) AS full_geometry
 FROM gis.districts d JOIN gis.regencies p ON p.id=d.regency_id
 JOIN gis.dataset_releases r ON r.boundary_set_id=d.boundary_set_id
 LEFT JOIN gis.district_indicators i ON i.release_id=r.id AND i.district_id=d.id
 LEFT JOIN counts c ON c.district_id=d.id WHERE r.id=target::uuid
), calculated AS (
 SELECT *,ceil(population::numeric/threshold::bigint)::bigint AS indicative_need FROM inputs
)
SELECT *, (population::numeric/area_km2)::numeric(24,12) AS density,
 (population::numeric/nullif(facility_count,0))::numeric(24,12) AS population_per_facility,
 (facility_count::numeric*30000/nullif(population,0))::numeric(24,12) AS facilities_per_30000,
 CASE WHEN indicative_need IS NULL THEN NULL ELSE greatest(0,indicative_need-facility_count) END AS indicative_deficit,
 facility_count=0 AS without_facility
FROM calculated ORDER BY code) q
$fn$;
CREATE FUNCTION gis.analysis_buffer_rows(target uuid) RETURNS SETOF jsonb LANGUAGE sql STABLE SET search_path=pg_catalog AS $fn$
SELECT to_jsonb(q) FROM (WITH assessed AS (
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
 WHERE f.release_id=target::uuid
)
SELECT a.facility_code,a.selected_review_id,a.coordinate_source_id,a.exclusion_reason,a.review_hash,
 extensions.ST_X(a.location) AS longitude,extensions.ST_Y(a.location) AS latitude,r.radius_m,
 CASE WHEN a.exclusion_reason IS NULL THEN extensions.ST_AsGeoJSON(
 extensions.ST_Buffer(a.location::extensions.geography,r.radius_m,'quad_segs=32')::extensions.geometry,15)::jsonb ELSE NULL END AS geometry
FROM assessed a CROSS JOIN (VALUES(1000),(3000),(5000)) r(radius_m)
ORDER BY a.facility_code,r.radius_m) q
$fn$;
CREATE FUNCTION gis.analysis_coverage_rows(features jsonb,target uuid) RETURNS SETOF jsonb LANGUAGE sql STABLE SET search_path=pg_catalog AS $fn$
SELECT to_jsonb(q) FROM (WITH buffers AS MATERIALIZED (
 SELECT feature->'properties'->>'facility_code' AS facility_code,
 (feature->'properties'->>'radius_m')::integer AS radius_m,
 extensions.ST_GeomFromGeoJSON((feature->'geometry')::text) AS geom
 FROM jsonb_array_elements(features::jsonb) AS feature
), regions AS (
 SELECT d.id,d.geom FROM gis.districts d
 JOIN gis.dataset_releases r ON r.boundary_set_id=d.boundary_set_id WHERE r.id=target::uuid
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
FROM clipped ORDER BY id,radius_m) q
$fn$;

CREATE FUNCTION gis.analysis_identity(bundle jsonb) RETURNS text LANGUAGE sql IMMUTABLE SET search_path=pg_catalog AS $fn$
SELECT encode(sha256(convert_to(jsonb_build_array(bundle->'release_id',bundle->'input_revision',bundle->'input_hash',bundle->'method_version',bundle->'code_revision',bundle->'parameters')::text,'UTF8')),'hex')
$fn$;

CREATE FUNCTION gis.persist_operator_analysis(raw_token text,bundle jsonb,manifest jsonb)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
DECLARE identity record; release_row record; old_run record; target uuid; run uuid; threshold bigint;
 key text; field text; item jsonb; row_data jsonb; buffer_rows jsonb; features jsonb; counts record;
 eligible bigint; excluded bigint; numerator double precision; denominator double precision; percentage double precision;
 previous_district uuid; previous_area double precision; district uuid; radius integer; reasons jsonb; expected bigint;
 artifact_kind text; artifact_path text; result jsonb; amount bigint;
BEGIN
 SELECT * INTO identity FROM gis.operator_identity(raw_token,'analyze');
 IF jsonb_typeof(bundle) IS DISTINCT FROM 'object' OR jsonb_typeof(manifest) IS DISTINCT FROM 'object' THEN
  RAISE EXCEPTION 'Invalid analysis envelope' USING ERRCODE='22023'; END IF;
 target:=(bundle->>'release_id')::uuid; run:=(bundle->>'analysis_run_id')::uuid; threshold:=(bundle->'parameters'->>'T')::bigint;
 IF target IS NULL OR run IS NULL OR threshold IS NULL OR threshold<1 OR bundle->>'input_revision' IS NULL
 OR bundle->>'input_hash' IS NULL OR bundle->>'input_hash' !~ '^[0-9a-f]{64}$'
 OR bundle->>'code_revision' IS NULL OR bundle->>'code_revision' !~ '^[0-9a-f]{40}$'
 OR bundle->>'method_version' IS DISTINCT FROM 'postgis-analysis-v1'
 OR bundle->'parameters' IS DISTINCT FROM jsonb_build_object('T',threshold,'radii_m',jsonb_build_array(1000,3000,5000),
 'quad_segs',32,'legend_version','fixed-v1','buffer_method','postgis-geography-buffer-v1','area_method','WGS84-spheroid')
 OR manifest->>'schema_version' IS DISTINCT FROM 'analysis-manifest-v1' OR manifest->>'validation_status' IS DISTINCT FROM 'passed'
 OR manifest->>'content_hash' IS NULL OR manifest->>'content_hash' !~ '^[0-9a-f]{64}$' THEN
  RAISE EXCEPTION 'Invalid analysis identity or parameters' USING ERRCODE='22023'; END IF;
 FOREACH field IN ARRAY ARRAY['release_id','analysis_run_id','boundary_set_id','input_revision','input_hash','boundary_hash','method_version','code_revision','parameters'] LOOP
  IF bundle->field IS NULL OR manifest->field IS DISTINCT FROM bundle->field THEN
   RAISE EXCEPTION 'Manifest does not match analysis identity' USING ERRCODE='23514'; END IF;
 END LOOP;
 SELECT id,status,boundary_set_id,input_revision INTO release_row FROM gis.dataset_releases WHERE id=target FOR UPDATE;
 IF NOT FOUND OR release_row.status<>'draft' THEN RAISE EXCEPTION 'Analysis requires a draft' USING ERRCODE='23514'; END IF;
 IF release_row.input_revision IS DISTINCT FROM (bundle->>'input_revision')::bigint
 OR release_row.boundary_set_id IS DISTINCT FROM (bundle->>'boundary_set_id')::uuid THEN
  RAISE EXCEPTION 'Stale analysis inputs' USING ERRCODE='P4090'; END IF;
 key:=gis.analysis_identity(bundle);
 SELECT id,status INTO old_run FROM gis.analysis_runs WHERE idempotency_key=key;
 IF FOUND THEN
  IF old_run.status<>'succeeded' THEN RAISE EXCEPTION 'Existing analysis is incomplete' USING ERRCODE='23514'; END IF;
  RETURN jsonb_build_object('analysis_run_id',old_run.id,'status','succeeded','replayed',true);
 END IF;
 SELECT count(*) INTO expected FROM gis.districts WHERE boundary_set_id=release_row.boundary_set_id;
 IF expected<1 OR jsonb_typeof(manifest->'artifacts') IS DISTINCT FROM 'array' OR jsonb_array_length(manifest->'artifacts')<>5
 OR (SELECT count(DISTINCT a->>'kind') FROM jsonb_array_elements(manifest->'artifacts') a)<>5 THEN
  RAISE EXCEPTION 'Complete analysis master and artifact registry required' USING ERRCODE='23514'; END IF;
 FOR item IN SELECT * FROM jsonb_array_elements(manifest->'artifacts') LOOP
  artifact_kind:=item->>'kind';
  artifact_path:=CASE artifact_kind WHEN 'analysis_results' THEN 'results.json' WHEN 'thematic_density' THEN 'density.geojson'
   WHEN 'thematic_facility_count' THEN 'facility_count.geojson' WHEN 'thematic_population_per_facility' THEN 'population_per_facility.geojson'
   WHEN 'thematic_indicative_deficit' THEN 'indicative_deficit.geojson' ELSE NULL END;
  IF artifact_path IS NULL OR item->>'path' IS DISTINCT FROM artifact_path OR item->>'sha256' IS NULL
   OR item->>'sha256' !~ '^[0-9a-f]{64}$' OR item->>'bytes' IS NULL OR (item->>'bytes')::bigint<1 THEN
    RAISE EXCEPTION 'Invalid artifact registry' USING ERRCODE='23514'; END IF;
 END LOOP;
 INSERT INTO gis.analysis_runs(id,release_id,method_version,code_revision,input_hash,parameters_hash,input_revision,parameters,status,idempotency_key,started_at,started_by)
 VALUES(run,target,bundle->>'method_version',bundle->>'code_revision',bundle->>'input_hash',
 encode(sha256(convert_to((bundle->'parameters')::text,'UTF8')),'hex'),release_row.input_revision,bundle->'parameters','running',key,clock_timestamp(),identity.actor_id);
 FOR row_data IN SELECT * FROM gis.analysis_indicator_rows(target,threshold) LOOP
  INSERT INTO gis.indicator_results(run_id,release_id,boundary_set_id,district_id,population,facility_count,density,population_per_facility,
  facilities_per_30000,indicative_need,indicative_deficit,without_facility,completeness,reason)
  VALUES(run,target,release_row.boundary_set_id,(row_data->>'district_id')::uuid,(row_data->>'population')::bigint,
  (row_data->>'facility_count')::bigint,(row_data->>'density')::numeric,(row_data->>'population_per_facility')::numeric,
  (row_data->>'facilities_per_30000')::numeric,(row_data->>'indicative_need')::bigint,(row_data->>'indicative_deficit')::bigint,
  (row_data->>'without_facility')::boolean,
  CASE WHEN row_data->>'population' IS NULL OR row_data->>'area_km2' IS NULL THEN 'partial' ELSE 'complete' END,
  CASE WHEN row_data->>'population' IS NULL THEN 'missing_population' WHEN row_data->>'area_km2' IS NULL THEN 'missing_area' ELSE '' END);
 END LOOP;
 SELECT coalesce(jsonb_agg(b),'[]'::jsonb) INTO buffer_rows FROM gis.analysis_buffer_rows(target) b;
 SELECT count(*) FILTER(WHERE b->>'exclusion_reason' IS NULL),count(*) FILTER(WHERE b->>'exclusion_reason' IS NOT NULL)
 INTO eligible,excluded FROM jsonb_array_elements(buffer_rows) b WHERE (b->>'radius_m')::integer=1000;
 SELECT coalesce(jsonb_agg(jsonb_build_object('properties',jsonb_build_object('facility_code',b->>'facility_code','radius_m',(b->>'radius_m')::integer),'geometry',b->'geometry')),'[]'::jsonb)
 INTO features FROM jsonb_array_elements(buffer_rows) b WHERE b->>'exclusion_reason' IS NULL;
 FOR row_data IN SELECT value FROM gis.analysis_coverage_rows(features,target) value ORDER BY value->>'district_id',(value->>'radius_m')::integer LOOP
  district:=(row_data->>'district_id')::uuid; radius:=(row_data->>'radius_m')::integer;
  numerator:=(row_data->>'covered_area_m2')::double precision; denominator:=(row_data->>'geometry_area_m2')::double precision;
  IF numerator IS NULL OR denominator IS NULL OR denominator<=0 OR numerator<0 OR numerator>denominator+1
   OR numerator='NaN'::double precision OR denominator='NaN'::double precision OR denominator='Infinity'::double precision THEN
   RAISE EXCEPTION 'Invalid recomputed coverage area' USING ERRCODE='23514'; END IF;
  percentage:=numerator/denominator*100;
  IF percentage>100+1e-8 OR (previous_district=district AND numerator+1<previous_area) THEN
   RAISE EXCEPTION 'Coverage tolerance or monotonicity failed' USING ERRCODE='23514'; END IF;
  previous_district:=district; previous_area:=numerator;
  SELECT count(*) AS registered,count(*) FILTER(WHERE b->>'exclusion_reason' IS NULL) AS eligible,
   count(*) FILTER(WHERE b->>'exclusion_reason' IS NOT NULL) AS excluded
  INTO counts FROM gis.facility_snapshots f JOIN jsonb_array_elements(buffer_rows) b ON b->>'facility_code'=f.facility_code
  WHERE f.release_id=target AND f.district_id=district AND (b->>'radius_m')::integer=1000;
  SELECT coalesce(jsonb_object_agg(reason,n),'{}'::jsonb) INTO reasons FROM (
   SELECT b->>'exclusion_reason' AS reason,count(*) AS n FROM gis.facility_snapshots f JOIN jsonb_array_elements(buffer_rows) b ON b->>'facility_code'=f.facility_code
   WHERE f.release_id=target AND f.district_id=district AND (b->>'radius_m')::integer=1000 AND b->>'exclusion_reason' IS NOT NULL
   GROUP BY b->>'exclusion_reason') reasons_by_kind;
  INSERT INTO gis.coverage_results(run_id,release_id,boundary_set_id,district_id,radius_m,covered_area_m2,geometry_area_m2,coverage_pct,geom,
  registered_count,eligible_count,excluded_count,contributing_count,exclusion_reasons,completeness,reason)
  VALUES(run,target,release_row.boundary_set_id,district,radius,
   CASE WHEN eligible>0 THEN least(numerator,denominator) ELSE NULL END,
   CASE WHEN eligible>0 THEN denominator ELSE NULL END,CASE WHEN eligible>0 THEN least(percentage,100) ELSE NULL END,
   CASE WHEN eligible>0 AND row_data->>'geometry' IS NOT NULL THEN extensions.ST_GeomFromGeoJSON(row_data->>'geometry') ELSE NULL END,
   counts.registered,counts.eligible,counts.excluded,(row_data->>'contributing_count')::integer,reasons,
   CASE WHEN eligible=0 THEN 'unavailable' WHEN excluded>0 THEN 'partial' ELSE 'complete' END,
   CASE WHEN eligible=0 THEN 'no_eligible_points' WHEN excluded>0 THEN 'excluded_locations_in_dataset' ELSE '' END);
 END LOOP;
 FOR item IN SELECT * FROM jsonb_array_elements(manifest->'artifacts') LOOP
  INSERT INTO gis.artifacts(id,release_id,analysis_run_id,kind,private_path,sha256,bytes,generated_at,sanitized)
  VALUES(gen_random_uuid(),target,run,item->>'kind','analysis/'||run::text||'/'||(item->>'path'),item->>'sha256',(item->>'bytes')::bigint,
   (manifest->>'generated_at')::timestamptz,false);
 END LOOP;
 UPDATE gis.analysis_runs SET status='succeeded',finished_at=clock_timestamp(),output_manifest=manifest WHERE id=run;
 result:=jsonb_build_object('analysis_run_id',run,'status','succeeded','replayed',false);
 INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id)
 VALUES(gen_random_uuid(),identity.actor_id,identity.token_id,'analysis.completed','analysis_run',run::text,'{}',
 result||jsonb_build_object('release_id',target,'input_revision',release_row.input_revision,'input_hash',bundle->>'input_hash'),key);
 RETURN result;
END $fn$;

ALTER FUNCTION gis.analysis_indicator_rows(uuid,bigint) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.analysis_buffer_rows(uuid) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.analysis_coverage_rows(jsonb,uuid) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.analysis_identity(jsonb) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.persist_operator_analysis(text,jsonb,jsonb) OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.analysis_indicator_rows(uuid,bigint),gis.analysis_buffer_rows(uuid),gis.analysis_coverage_rows(jsonb,uuid),
 gis.analysis_identity(jsonb),gis.persist_operator_analysis(text,jsonb,jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.analysis_identity(jsonb),gis.persist_operator_analysis(text,jsonb,jsonb) TO gis_worker;
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Authorized analysis rollback requires a reviewed deployment plan.');
    }
};
