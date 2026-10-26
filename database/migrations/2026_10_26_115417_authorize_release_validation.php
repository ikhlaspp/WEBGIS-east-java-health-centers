<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
DO $$ BEGIN
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='gis_artifact_verifier') THEN
  CREATE ROLE gis_artifact_verifier NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
 END IF;
 IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='gis_artifact_verifier' AND (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit OR rolbypassrls)) THEN
  RAISE EXCEPTION 'Unsafe existing artifact verifier role';
 END IF;
END $$;
GRANT USAGE ON SCHEMA gis TO gis_artifact_verifier;
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;
GRANT SELECT,INSERT ON gis.quality_reports TO gis_lifecycle_owner;
GRANT UPDATE(status) ON gis.dataset_releases TO gis_lifecycle_owner;
CREATE FUNCTION gis.validate_release(raw_token text,target uuid,run uuid,revision bigint,verified_manifest jsonb,allow_partial boolean,reason text)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
DECLARE identity record; candidate record; analysis record; expected bigint; eligible bigint; excluded bigint;
 report uuid; checks jsonb; exclusions jsonb; result jsonb; missing bigint;
BEGIN
 SELECT * INTO identity FROM gis.operator_identity(raw_token,'validate');
 IF reason IS NULL OR length(btrim(reason))<10 OR length(reason)>2000 OR allow_partial IS NULL THEN
  RAISE EXCEPTION 'Explicit validation reason and scope required' USING ERRCODE='22023'; END IF;
 SELECT * INTO candidate FROM gis.dataset_releases WHERE id=target FOR UPDATE;
 IF NOT FOUND OR candidate.status<>'draft' THEN RAISE EXCEPTION 'Validation requires draft' USING ERRCODE='23514'; END IF;
 IF candidate.input_revision IS DISTINCT FROM revision THEN RAISE EXCEPTION 'Stale validation' USING ERRCODE='P4090'; END IF;
 SELECT * INTO analysis FROM gis.analysis_runs WHERE id=run AND release_id=target;
 IF NOT FOUND OR analysis.status<>'succeeded' OR analysis.input_revision<>revision
 OR analysis.method_version IS DISTINCT FROM candidate.method_version OR analysis.code_revision IS DISTINCT FROM candidate.code_revision
 OR analysis.output_manifest IS DISTINCT FROM verified_manifest
 OR verified_manifest->>'input_hash' IS DISTINCT FROM analysis.input_hash
 OR verified_manifest->>'boundary_set_id' IS DISTINCT FROM candidate.boundary_set_id::text THEN
  RAISE EXCEPTION 'Current verified analysis required' USING ERRCODE='23514'; END IF;
 SELECT count(*) INTO expected FROM gis.districts WHERE boundary_set_id=candidate.boundary_set_id;
 IF expected=0 OR (SELECT count(*) FROM gis.indicator_results WHERE run_id=run)<>expected
 OR (SELECT count(*) FROM gis.coverage_results WHERE run_id=run)<>expected*3
 OR (SELECT count(*) FROM gis.artifacts WHERE analysis_run_id=run)<>5 THEN
  RAISE EXCEPTION 'Incomplete analysis' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM gis.artifacts a WHERE a.analysis_run_id=run AND NOT EXISTS(
  SELECT 1 FROM jsonb_array_elements(verified_manifest->'artifacts') m WHERE m->>'kind'=a.kind
  AND m->>'sha256'=a.sha256 AND (m->>'bytes')::bigint=a.bytes
  AND a.private_path='analysis/'||run::text||'/'||(m->>'path'))) THEN
  RAISE EXCEPTION 'Artifact registry differs from verified files' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM gis.districts d LEFT JOIN gis.district_indicators i ON i.district_id=d.id AND i.release_id=target
  LEFT JOIN gis.data_sources p ON p.id=i.population_source_id LEFT JOIN gis.data_sources a ON a.id=i.area_source_id
  WHERE d.boundary_set_id=candidate.boundary_set_id AND ((i.population IS NOT NULL AND p.status IS DISTINCT FROM 'verified')
  OR (i.area_km2 IS NOT NULL AND a.status IS DISTINCT FROM 'verified')))
 OR EXISTS(SELECT 1 FROM gis.facility_snapshots f JOIN gis.data_sources s ON s.id=f.source_id WHERE f.release_id=target AND s.status<>'verified')
 OR EXISTS(SELECT 1 FROM gis.boundary_sets b JOIN gis.data_sources s ON s.id=b.source_id WHERE b.id=candidate.boundary_set_id AND s.status<>'verified') THEN
  RAISE EXCEPTION 'Complete sourced indicators and verified sources required' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM gis.geocode_reviews WHERE release_id=target AND result_status='pending') THEN
  RAISE EXCEPTION 'Pending location decisions require review' USING ERRCODE='23514'; END IF;
 SELECT count(*) FILTER(WHERE b->>'exclusion_reason' IS NULL),count(*) FILTER(WHERE b->>'exclusion_reason' IS NOT NULL)
 INTO eligible,excluded FROM gis.analysis_buffer_rows(target) b WHERE (b->>'radius_m')::integer=1000;
 IF eligible=0 THEN RAISE EXCEPTION 'No eligible facility points for coverage release' USING ERRCODE='23514'; END IF;
 SELECT count(*) INTO missing FROM gis.districts d LEFT JOIN gis.district_indicators i ON i.district_id=d.id AND i.release_id=target
 WHERE d.boundary_set_id=candidate.boundary_set_id AND (i.population IS NULL OR i.area_km2 IS NULL);
 IF (excluded>0 OR missing>0) AND NOT allow_partial THEN
  RAISE EXCEPTION 'Partial data requires explicit scope acceptance' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM gis.facility_snapshots f JOIN gis.districts d ON d.id=f.district_id
  JOIN gis.data_sources s ON s.id=f.coordinate_source_id WHERE f.release_id=target AND f.coordinate_status='verified'
  AND (s.status<>'verified' OR NOT extensions.ST_Covers(d.geom,f.location))) THEN
  RAISE EXCEPTION 'Verified coordinates violate source or district checks' USING ERRCODE='23514'; END IF;
 checks:=jsonb_build_object('analysis_run_id',run,'input_revision',revision,'input_hash',analysis.input_hash,
  'manifest_content_hash',verified_manifest->>'content_hash','artifact_registry',verified_manifest->'artifacts',
  'district_count',expected,'source_checks',true,'artifact_files_verified',true,'foreign_keys_enforced',true);
 exclusions:=jsonb_build_object('eligible',eligible,'excluded',excluded,'districts_with_missing_indicators',missing,'partial_accepted',allow_partial,
 'reason',reason,'policy','excluded points omitted from coverage; partial coverage and missing indicators remain labelled');
 report:=gen_random_uuid();
 INSERT INTO gis.quality_reports(id,release_id,input_revision,input_hash,report_hash,policy_version,checks,exclusions,passed,approved_by,approved_at)
 VALUES(report,target,revision,analysis.input_hash,encode(sha256(convert_to(jsonb_build_array(checks,exclusions)::text,'UTF8')),'hex'),
 'release-quality-v1',checks,exclusions,true,identity.actor_id,clock_timestamp());
 UPDATE gis.dataset_releases SET status='validated',quality_report_id=report,default_analysis_run_id=run WHERE id=target;
 result:=jsonb_build_object('release_id',target,'analysis_run_id',run,'quality_report_id',report,'status','validated','input_revision',revision);
 INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id)
 VALUES(gen_random_uuid(),identity.actor_id,identity.token_id,'release.validated','dataset_release',target::text,
 jsonb_build_object('status','draft','input_revision',revision),result,report::text);
 RETURN result;
END $fn$;
ALTER FUNCTION gis.validate_release(text,uuid,uuid,bigint,jsonb,boolean,text) OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.validate_release(text,uuid,uuid,bigint,jsonb,boolean,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.validate_release(text,uuid,uuid,bigint,jsonb,boolean,text) TO gis_artifact_verifier;
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Release validation rollback requires a reviewed deployment plan.');
    }
};
