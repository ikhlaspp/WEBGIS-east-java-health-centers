<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
CREATE TABLE app.backup_environment(singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),instance_id uuid NOT NULL UNIQUE);
INSERT INTO app.backup_environment(instance_id) VALUES(gen_random_uuid());
REVOKE ALL ON app.backup_environment FROM PUBLIC,gis_runtime,gis_worker,gis_publisher,gis_artifact_verifier;
GRANT SELECT ON app.backup_environment TO gis_lifecycle_owner;
CREATE TRIGGER immutable_backup_environment BEFORE UPDATE OR DELETE ON app.backup_environment FOR EACH ROW EXECUTE FUNCTION gis.reject_mutation();
CREATE TABLE app.backup_checkpoints (
 id uuid PRIMARY KEY, database_name text NOT NULL, instance_id uuid NOT NULL REFERENCES app.backup_environment(instance_id), completed_at timestamptz NOT NULL,
 manifest_sha256 text NOT NULL CHECK(manifest_sha256 ~ '^[0-9a-f]{64}$'), inventory jsonb NOT NULL,
 verified_by uuid NOT NULL REFERENCES app.users ON DELETE RESTRICT, verified_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK(jsonb_typeof(inventory)='array' AND jsonb_array_length(inventory)=2)
);
REVOKE ALL ON app.backup_checkpoints FROM PUBLIC,gis_runtime,gis_worker,gis_publisher,gis_artifact_verifier;
GRANT SELECT,INSERT ON app.backup_checkpoints TO gis_lifecycle_owner;
CREATE TRIGGER immutable_backup_checkpoint BEFORE UPDATE OR DELETE ON app.backup_checkpoints FOR EACH ROW EXECUTE FUNCTION gis.reject_mutation();
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;
CREATE FUNCTION gis.backup_context(raw_token text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
BEGIN
 PERFORM gis.operator_identity(raw_token,'publish');
 RETURN (SELECT jsonb_build_object('database_name',current_database(),'instance_id',instance_id) FROM app.backup_environment WHERE singleton);
END $fn$;
CREATE FUNCTION gis.register_backup_checkpoint(raw_token text,manifest jsonb,digest text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
DECLARE identity record; checkpoint uuid; completed timestamptz; prior record; result jsonb;
BEGIN
 SELECT * INTO identity FROM gis.operator_identity(raw_token,'publish');
 checkpoint:=(manifest->>'checkpoint_id')::uuid; completed:=(manifest->>'completed_at')::timestamptz;
 IF checkpoint IS NULL OR completed IS NULL OR completed>clock_timestamp() OR completed<=clock_timestamp()-interval '24 hours'
 OR manifest->>'schema_version' IS DISTINCT FROM 'backup-checkpoint-v1' OR manifest->>'database_name' IS DISTINCT FROM current_database()
 OR manifest->>'instance_id' IS DISTINCT FROM (SELECT instance_id::text FROM app.backup_environment WHERE singleton)
 OR digest IS NULL OR digest !~ '^[0-9a-f]{64}$' OR jsonb_typeof(manifest->'files') IS DISTINCT FROM 'array'
 OR jsonb_array_length(manifest->'files')<>2 THEN
  RAISE EXCEPTION 'Fresh database-bound backup evidence required' USING ERRCODE='23514'; END IF;
 IF (SELECT count(DISTINCT f->>'kind') FROM jsonb_array_elements(manifest->'files') f WHERE
 (f->>'kind',f->>'path') IN (('database_snapshot','database.snapshot'),('artifact_bundle','artifacts.bundle'))
 AND (f->>'bytes')::bigint>0 AND f->>'sha256' ~ '^[0-9a-f]{64}$')<>2 THEN
  RAISE EXCEPTION 'Complete verified backup inventory required' USING ERRCODE='23514'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended('backup/'||checkpoint::text,0));
 SELECT * INTO prior FROM app.backup_checkpoints WHERE id=checkpoint;
 IF FOUND THEN
  IF prior.manifest_sha256<>digest OR prior.verified_by<>identity.actor_id THEN
   RAISE EXCEPTION 'Backup checkpoint identity conflict' USING ERRCODE='23505'; END IF;
  RETURN jsonb_build_object('checkpoint_id',checkpoint,'replayed',true);
 END IF;
 INSERT INTO app.backup_checkpoints(id,database_name,instance_id,completed_at,manifest_sha256,inventory,verified_by)
 VALUES(checkpoint,current_database(),(manifest->>'instance_id')::uuid,completed,digest,manifest->'files',identity.actor_id);
 result:=jsonb_build_object('checkpoint_id',checkpoint,'completed_at',completed,'replayed',false);
 INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id)
 VALUES(gen_random_uuid(),identity.actor_id,identity.token_id,'backup.verified','backup_checkpoint',checkpoint::text,'{}',result,checkpoint::text);
 RETURN result;
END $fn$;
CREATE FUNCTION gis.require_fresh_publication_backup() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM app.backup_checkpoints WHERE database_name=current_database()
 AND completed_at<=clock_timestamp() AND completed_at>clock_timestamp()-interval '24 hours') THEN
  RAISE EXCEPTION 'New publication requires a verified backup within 24 hours' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $fn$;
ALTER FUNCTION gis.register_backup_checkpoint(text,jsonb,text) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.backup_context(text) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.require_fresh_publication_backup() OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.register_backup_checkpoint(text,jsonb,text),gis.require_fresh_publication_backup(),gis.backup_context(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.backup_context(text) TO gis_worker,gis_publisher;
GRANT EXECUTE ON FUNCTION gis.register_backup_checkpoint(text,jsonb,text) TO gis_artifact_verifier;
CREATE TRIGGER publication_backup_guard BEFORE UPDATE OF status ON gis.dataset_releases FOR EACH ROW
WHEN(NEW.status='published' AND OLD.status IS DISTINCT FROM NEW.status) EXECUTE FUNCTION gis.require_fresh_publication_backup();
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Backup gate rollback requires a reviewed deployment plan.');
    }
};
