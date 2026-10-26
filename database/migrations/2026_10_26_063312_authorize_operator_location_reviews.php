<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;
GRANT EXECUTE ON FUNCTION gis.valid_geometry(extensions.geometry,text) TO gis_lifecycle_owner;
GRANT SELECT ON app.audit_logs,gis.districts,gis.data_sources TO gis_lifecycle_owner;
GRANT UPDATE(result_status,decision_reason,reviewed_by,reviewed_at) ON gis.geocode_reviews TO gis_lifecycle_owner;
GRANT UPDATE(location,coordinate_status,precision_level,coordinate_source_id,selected_review_id) ON gis.facility_snapshots TO gis_lifecycle_owner;
CREATE UNIQUE INDEX review_operation_identity ON app.audit_logs(request_id) WHERE action='location.reviewed';

CREATE FUNCTION gis.operator_identity(raw_token text,required_ability text)
RETURNS TABLE(actor_id uuid,token_id uuid) LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
BEGIN
 IF raw_token IS NULL OR octet_length(raw_token)<43 OR octet_length(raw_token)>4096
 OR required_ability IS NULL OR required_ability NOT IN ('import','review','analyze','validate','publish','rollback','withdraw') THEN
  RAISE EXCEPTION 'Invalid operator capability' USING ERRCODE='28000'; END IF;
 RETURN QUERY SELECT t.user_id,t.id FROM app.operator_tokens t JOIN app.users u ON u.id=t.user_id
 WHERE t.token_hash=encode(sha256(convert_to(raw_token,'UTF8')),'hex') AND t.revoked_at IS NULL
 AND t.expires_at>clock_timestamp() AND t.created_at<=clock_timestamp()
 AND t.abilities ? required_ability AND u.is_active AND u.is_admin;
 IF NOT FOUND THEN RAISE EXCEPTION 'Invalid operator capability' USING ERRCODE='28000'; END IF;
END $$;

CREATE FUNCTION gis.review_location(raw_token text,target_release uuid,target_facility text,target_review uuid,
 decision text,reason text,expected_revision bigint,operation_id uuid,confirmed_facility_point boolean)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE identity record; release_row record; review_row record; facility_row record; prior record;
 request_hash text; outcome jsonb; final_revision bigint;
BEGIN
 SELECT * INTO identity FROM gis.operator_identity(raw_token,'review');
 IF target_release IS NULL OR target_review IS NULL OR operation_id IS NULL OR expected_revision IS NULL
 OR expected_revision<0 OR target_facility IS NULL OR target_facility !~ '^[0-9]{11}$'
 OR decision IS NULL OR decision NOT IN ('accepted','rejected') OR reason IS NULL
 OR length(btrim(reason))<10 OR length(reason)>2000 THEN
  RAISE EXCEPTION 'Invalid review request' USING ERRCODE='22023'; END IF;
 request_hash:=encode(sha256(convert_to(jsonb_build_array(target_release,target_facility,target_review,decision,reason,expected_revision,confirmed_facility_point)::text,'UTF8')),'hex');
 PERFORM pg_advisory_xact_lock(hashtextextended(operation_id::text,0));
 SELECT actor_id,after_json INTO prior FROM app.audit_logs WHERE action='location.reviewed' AND request_id=operation_id::text;
 IF FOUND THEN
  IF prior.actor_id<>identity.actor_id OR prior.after_json->>'request_hash' IS DISTINCT FROM request_hash THEN
   RAISE EXCEPTION 'Operation identity conflict' USING ERRCODE='23505'; END IF;
  RETURN prior.after_json || jsonb_build_object('replayed',true);
 END IF;
 SELECT id,status,input_revision INTO release_row FROM gis.dataset_releases WHERE id=target_release FOR UPDATE;
 IF NOT FOUND OR release_row.status<>'draft' THEN RAISE EXCEPTION 'Review requires a draft' USING ERRCODE='23514'; END IF;
 IF release_row.input_revision<>expected_revision THEN RAISE EXCEPTION 'Stale release revision' USING ERRCODE='40001'; END IF;
 SELECT * INTO facility_row FROM gis.facility_snapshots WHERE release_id=target_release AND facility_code=target_facility FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Facility not found' USING ERRCODE='23514'; END IF;
 SELECT * INTO review_row FROM gis.geocode_reviews WHERE id=target_review AND release_id=target_release AND facility_code=target_facility FOR UPDATE;
 IF NOT FOUND OR review_row.result_status<>'pending' THEN RAISE EXCEPTION 'Review does not belong to this pending candidate' USING ERRCODE='23514'; END IF;
 IF decision='accepted' THEN
  IF confirmed_facility_point IS DISTINCT FROM true OR review_row.candidate_location IS NULL OR review_row.precision_level<>'facility'
   OR NOT (coalesce(review_row.evidence_url ~ '^https://[^/[:space:]]+',false)
      OR (btrim(review_row.evidence_note)<>'' AND review_row.evidence_sha256 IS NOT NULL))
   OR NOT EXISTS(SELECT 1 FROM gis.data_sources WHERE id=review_row.source_id AND status='verified')
   OR NOT EXISTS(SELECT 1 FROM gis.districts WHERE id=facility_row.district_id AND extensions.ST_Covers(geom,review_row.candidate_location)) THEN
    RAISE EXCEPTION 'Facility-level evidence and matching boundary required' USING ERRCODE='23514'; END IF;
 END IF;
 UPDATE gis.geocode_reviews SET result_status=decision,decision_reason=reason,reviewed_by=identity.actor_id,reviewed_at=clock_timestamp() WHERE id=target_review;
 IF decision='accepted' THEN
  UPDATE gis.facility_snapshots SET location=review_row.candidate_location,coordinate_status='verified',precision_level='facility',
   coordinate_source_id=review_row.source_id,selected_review_id=target_review WHERE release_id=target_release AND facility_code=target_facility;
 ELSIF facility_row.selected_review_id IS NULL AND facility_row.coordinate_status='unverified'
 AND extensions.ST_Equals(facility_row.location,review_row.candidate_location) THEN
  UPDATE gis.facility_snapshots SET coordinate_status='rejected' WHERE release_id=target_release AND facility_code=target_facility;
 END IF;
 SELECT input_revision INTO final_revision FROM gis.dataset_releases WHERE id=target_release;
 outcome:=jsonb_build_object('release_id',target_release,'facility_code',target_facility,'review_id',target_review,'decision',decision,
  'input_revision',final_revision,'request_hash',request_hash,'replayed',false);
 INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id)
 VALUES(gen_random_uuid(),identity.actor_id,identity.token_id,'location.reviewed','geocode_review',target_review::text,
  jsonb_build_object('status',review_row.result_status,'input_revision',expected_revision),outcome,operation_id::text);
 RETURN outcome;
END $$;

CREATE FUNCTION gis.freeze_review_decision() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF OLD.result_status<>'pending' THEN RAISE EXCEPTION 'Reviewed evidence is immutable; submit a new candidate' USING ERRCODE='23514'; END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER reviewed_evidence_immutable BEFORE UPDATE OR DELETE ON gis.geocode_reviews FOR EACH ROW EXECUTE FUNCTION gis.freeze_review_decision();
ALTER FUNCTION gis.operator_identity(text,text) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.review_location(text,uuid,text,uuid,text,text,bigint,uuid,boolean) OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.operator_identity(text,text),gis.review_location(text,uuid,text,uuid,text,text,bigint,uuid,boolean),gis.freeze_review_decision() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.operator_identity(text,text) TO gis_worker,gis_publisher;
GRANT EXECUTE ON FUNCTION gis.review_location(text,uuid,text,uuid,text,text,bigint,uuid,boolean) TO gis_worker;
SQL);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        throw new RuntimeException('Operator authorization rollback requires a reviewed deployment plan.');
    }
};
