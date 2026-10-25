<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
ALTER TABLE app.operator_tokens ADD CONSTRAINT token_abilities_array CHECK(jsonb_typeof(abilities)='array');
ALTER TABLE app.operator_tokens ADD CONSTRAINT token_lifetime CHECK(expires_at>created_at AND expires_at<=created_at+interval '8 hours');
GRANT SELECT ON app.operator_tokens,app.users TO gis_lifecycle_owner;
GRANT USAGE ON SCHEMA staging TO gis_lifecycle_owner;
GRANT SELECT ON staging.rows,gis.import_batches TO gis_lifecycle_owner;
GRANT INSERT,UPDATE ON gis.import_batches TO gis_lifecycle_owner;
GRANT INSERT ON app.audit_logs TO gis_lifecycle_owner;
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;

CREATE FUNCTION gis.import_actor(raw_token text) RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE actor uuid;
BEGIN
 IF octet_length(raw_token)<43 THEN RAISE EXCEPTION 'Invalid import capability' USING ERRCODE='28000'; END IF;
 SELECT t.user_id INTO actor FROM app.operator_tokens t JOIN app.users u ON u.id=t.user_id
 WHERE t.token_hash=encode(sha256(convert_to(raw_token,'UTF8')),'hex') AND t.revoked_at IS NULL
 AND t.expires_at>clock_timestamp() AND t.abilities ? 'import' AND u.is_active AND u.is_admin;
 IF actor IS NULL THEN RAISE EXCEPTION 'Invalid import capability' USING ERRCODE='28000'; END IF;
 RETURN actor;
END $$;
CREATE FUNCTION gis.import_key(source uuid,target uuid,file_hash text,pipeline text,parameters text) RETURNS text
LANGUAGE sql IMMUTABLE SET search_path=pg_catalog AS $$
 SELECT encode(sha256(convert_to(jsonb_build_array(source,target,file_hash,pipeline,'import_draft_v1',parameters)::text,'UTF8')),'hex')
$$;
CREATE FUNCTION gis.begin_import(raw_token text,source uuid,target uuid,file_hash text,pipeline text,parameters text,expected bigint)
RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE actor uuid; key text; existing uuid; batch uuid; release_status text; token_id uuid;
BEGIN
 actor:=gis.import_actor(raw_token);
 IF file_hash !~ '^[0-9a-f]{64}$' OR parameters !~ '^[0-9a-f]{64}$' OR btrim(pipeline)='' OR expected<1 OR expected>50000 THEN
  RAISE EXCEPTION 'Invalid import identity' USING ERRCODE='22023'; END IF;
 key:=gis.import_key(source,target,file_hash,pipeline,parameters);
 PERFORM pg_advisory_xact_lock(hashtextextended(key,0));
 SELECT id INTO existing FROM gis.import_batches WHERE idempotency_key=key;
 IF existing IS NOT NULL THEN RETURN existing; END IF;
 SELECT status INTO release_status FROM gis.dataset_releases WHERE id=target FOR UPDATE;
 IF release_status IS DISTINCT FROM 'draft' THEN RAISE EXCEPTION 'Import target must be an existing draft' USING ERRCODE='23514'; END IF;
 batch:=gen_random_uuid();
 INSERT INTO gis.import_batches(id,source_id,target_release_id,started_by,operation,file_hash,pipeline_version,parameters_hash,idempotency_key,status,attempt,started_at,expected_rows)
 VALUES(batch,source,target,actor,'import_draft_v1',file_hash,pipeline,parameters,key,'running',1,clock_timestamp(),expected);
 SELECT id INTO token_id FROM app.operator_tokens WHERE token_hash=encode(sha256(convert_to(raw_token,'UTF8')),'hex');
 INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id)
 VALUES(gen_random_uuid(),actor,token_id,'dataset.import.started','import_batch',batch::text,'{}',jsonb_build_object('file_hash',file_hash,'release_id',target),key);
 RETURN batch;
END $$;
CREATE FUNCTION gis.finish_import(raw_token text,batch uuid,promotion_succeeded boolean,report jsonb)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE actor uuid; owner_id uuid; expected bigint; current_status text; raw_count bigint; accepted bigint; quarantined bigint; aggregate_count bigint; outcome text; key text; token_id uuid;
BEGIN
 actor:=gis.import_actor(raw_token);
 SELECT started_by,expected_rows,status,idempotency_key INTO owner_id,expected,current_status,key FROM gis.import_batches WHERE id=batch FOR UPDATE;
 IF owner_id IS DISTINCT FROM actor OR current_status IS DISTINCT FROM 'running' THEN RAISE EXCEPTION 'Import batch is not owned/running' USING ERRCODE='42501'; END IF;
 SELECT count(*),count(*) FILTER(WHERE disposition='accepted'),count(*) FILTER(WHERE disposition='quarantined'),count(*) FILTER(WHERE disposition='aggregate')
 INTO raw_count,accepted,quarantined,aggregate_count FROM staging.rows WHERE batch_id=batch;
 IF raw_count<>expected THEN RAISE EXCEPTION 'Import row partition incomplete' USING ERRCODE='23514'; END IF;
 outcome:=CASE WHEN promotion_succeeded AND quarantined=0 THEN 'succeeded' ELSE 'failed' END;
 UPDATE gis.import_batches SET status=outcome,finished_at=clock_timestamp(),raw_rows=raw_count,accepted_rows=accepted,quarantined_rows=quarantined,aggregate_rows=aggregate_count,checkpoint=report WHERE id=batch;
 SELECT id INTO token_id FROM app.operator_tokens WHERE token_hash=encode(sha256(convert_to(raw_token,'UTF8')),'hex');
 INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id)
 VALUES(gen_random_uuid(),actor,token_id,'dataset.import.finished','import_batch',batch::text,'{}',jsonb_build_object('status',outcome,'raw_rows',raw_count),key);
 RETURN outcome;
END $$;
ALTER FUNCTION gis.import_actor(text) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.begin_import(text,uuid,uuid,text,text,text,bigint) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.finish_import(text,uuid,boolean,jsonb) OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.import_actor(text),gis.import_key(uuid,uuid,text,text,text),gis.begin_import(text,uuid,uuid,text,text,text,bigint),gis.finish_import(text,uuid,boolean,jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.import_key(uuid,uuid,text,text,text) TO gis_worker,gis_lifecycle_owner;
GRANT EXECUTE ON FUNCTION gis.import_actor(text),gis.begin_import(text,uuid,uuid,text,text,text,bigint),gis.finish_import(text,uuid,boolean,jsonb) TO gis_worker;
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Import capability rollback requires a reviewed deployment plan.');
    }
};
