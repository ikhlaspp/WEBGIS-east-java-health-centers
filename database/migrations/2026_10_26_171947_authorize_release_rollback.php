<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;
CREATE FUNCTION gis.rollback_release(raw_token text,target uuid,expected_version bigint,operation uuid,reason text,verified_manifest jsonb)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
DECLARE identity record; pointer record; candidate record; analysis record; quality record; prior record;
 request_hash text; result jsonb; audit uuid;
BEGIN
 SELECT * INTO identity FROM gis.operator_identity(raw_token,'rollback');
 IF target IS NULL OR operation IS NULL OR expected_version IS NULL OR expected_version<0
 OR reason IS NULL OR length(btrim(reason))<10 OR length(reason)>2000 THEN
  RAISE EXCEPTION 'Explicit rollback identity, version and reason required' USING ERRCODE='22023'; END IF;
 request_hash:=encode(sha256(convert_to(jsonb_build_array(target,expected_version,reason,verified_manifest)::text,'UTF8')),'hex');
 PERFORM pg_advisory_xact_lock(hashtextextended('rollback/'||operation::text,0));
 SELECT actor_id,after_json INTO prior FROM app.audit_logs WHERE action='release.rolled_back' AND request_id=operation::text;
 IF FOUND THEN
  IF prior.actor_id<>identity.actor_id OR prior.after_json->>'request_hash' IS DISTINCT FROM request_hash THEN
   RAISE EXCEPTION 'Conflicting rollback retry' USING ERRCODE='23505'; END IF;
  RETURN (prior.after_json-'request_hash')||jsonb_build_object('replayed',true);
 END IF;
 SELECT * INTO pointer FROM app.active_release WHERE singleton=1 FOR UPDATE;
 IF NOT FOUND OR pointer.version<>expected_version THEN RAISE EXCEPTION 'Stale active pointer version' USING ERRCODE='P4090'; END IF;
 IF pointer.release_id IS NULL OR pointer.release_id=target THEN RAISE EXCEPTION 'Rollback requires a different historical release' USING ERRCODE='23514'; END IF;
 SELECT * INTO candidate FROM gis.dataset_releases WHERE id=target FOR UPDATE;
 IF NOT FOUND OR candidate.status<>'published' OR candidate.published_at IS NULL THEN
  RAISE EXCEPTION 'Rollback requires previously published, non-withdrawn release' USING ERRCODE='23514'; END IF;
 SELECT * INTO analysis FROM gis.analysis_runs WHERE id=candidate.default_analysis_run_id AND release_id=target;
 IF NOT FOUND OR analysis.status<>'succeeded' OR analysis.input_revision<>candidate.input_revision
 OR analysis.method_version<>candidate.method_version OR analysis.code_revision<>candidate.code_revision
 OR analysis.output_manifest IS DISTINCT FROM verified_manifest THEN
  RAISE EXCEPTION 'Current verified historical run required' USING ERRCODE='23514'; END IF;
 SELECT * INTO quality FROM gis.quality_reports WHERE id=candidate.quality_report_id AND release_id=target;
 IF NOT FOUND OR NOT quality.passed OR quality.approved_by IS NULL OR quality.approved_at IS NULL
 OR quality.input_revision<>candidate.input_revision OR quality.input_hash<>analysis.input_hash
 OR quality.policy_version<>'release-quality-v1' OR quality.checks->>'analysis_run_id' IS DISTINCT FROM analysis.id::text
 OR quality.checks->>'manifest_content_hash' IS DISTINCT FROM verified_manifest->>'content_hash'
 OR quality.checks->'artifact_registry' IS DISTINCT FROM verified_manifest->'artifacts'
 OR quality.report_hash<>encode(sha256(convert_to(jsonb_build_array(quality.checks,quality.exclusions)::text,'UTF8')),'hex') THEN
  RAISE EXCEPTION 'Historical quality acceptance required' USING ERRCODE='23514'; END IF;
 IF (SELECT count(*) FROM gis.artifacts WHERE analysis_run_id=analysis.id)<>5
 OR EXISTS(SELECT 1 FROM gis.artifacts a WHERE a.analysis_run_id=analysis.id AND NOT EXISTS(
  SELECT 1 FROM jsonb_array_elements(verified_manifest->'artifacts') m WHERE m->>'kind'=a.kind
  AND m->>'sha256'=a.sha256 AND (m->>'bytes')::bigint=a.bytes
  AND a.private_path='analysis/'||analysis.id::text||'/'||(m->>'path'))) THEN
  RAISE EXCEPTION 'Historical artifact registry mismatch' USING ERRCODE='23514'; END IF;
 UPDATE app.active_release SET release_id=target,analysis_run_id=analysis.id,version=version+1,changed_at=clock_timestamp() WHERE singleton=1;
 result:=jsonb_build_object('release_id',target,'analysis_run_id',analysis.id,'quality_report_id',quality.id,
  'status','published','active_version',pointer.version+1,'operation_id',operation,'replayed',false);
 audit:=gen_random_uuid();
 INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id)
 VALUES(audit,identity.actor_id,identity.token_id,'release.rolled_back','dataset_release',target::text,
  jsonb_build_object('release_id',pointer.release_id,'analysis_run_id',pointer.analysis_run_id,'active_version',pointer.version,'reason',reason),
  result||jsonb_build_object('request_hash',request_hash),operation::text);
 INSERT INTO app.outbox_events(id,audit_id,event_type,payload,available_at)
 VALUES(gen_random_uuid(),audit,'release.rolled_back',result,clock_timestamp());
 RETURN result;
END $fn$;
ALTER FUNCTION gis.rollback_release(text,uuid,bigint,uuid,text,jsonb) OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.rollback_release(text,uuid,bigint,uuid,text,jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.rollback_release(text,uuid,bigint,uuid,text,jsonb) TO gis_artifact_verifier;
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Lifecycle rollback schema changes require a reviewed deployment plan.');
    }
};
