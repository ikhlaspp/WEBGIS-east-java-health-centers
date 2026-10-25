<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
CREATE FUNCTION gis.protect_analysis_result() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE run_id uuid; run_status text; release uuid; release_status text;
BEGIN
 IF TG_TABLE_NAME='artifacts' THEN
  run_id:=CASE WHEN TG_OP='DELETE' THEN OLD.analysis_run_id ELSE NEW.analysis_run_id END;
 ELSE
  run_id:=CASE WHEN TG_OP='DELETE' THEN OLD.run_id ELSE NEW.run_id END;
 END IF;
 release:=CASE WHEN TG_OP='DELETE' THEN OLD.release_id ELSE NEW.release_id END;
 IF TG_OP='UPDATE' AND (to_jsonb(OLD)->'run_id' IS DISTINCT FROM to_jsonb(NEW)->'run_id'
 OR to_jsonb(OLD)->'analysis_run_id' IS DISTINCT FROM to_jsonb(NEW)->'analysis_run_id'
 OR OLD.release_id<>NEW.release_id) THEN RAISE EXCEPTION 'Result identity is immutable' USING ERRCODE='23514'; END IF;
 SELECT status INTO release_status FROM gis.dataset_releases WHERE id=release FOR SHARE;
 IF release_status IS DISTINCT FROM 'draft' THEN RAISE EXCEPTION 'Analysis output requires a draft' USING ERRCODE='23514'; END IF;
 IF run_id IS NOT NULL THEN
  SELECT status INTO run_status FROM gis.analysis_runs WHERE id=run_id FOR UPDATE;
  IF run_status IS DISTINCT FROM 'running' THEN RAISE EXCEPTION 'Finished analysis output is immutable' USING ERRCODE='23514'; END IF;
 END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER analysis_result_guard BEFORE INSERT OR UPDATE OR DELETE ON gis.indicator_results FOR EACH ROW EXECUTE FUNCTION gis.protect_analysis_result();
CREATE TRIGGER coverage_result_guard BEFORE INSERT OR UPDATE OR DELETE ON gis.coverage_results FOR EACH ROW EXECUTE FUNCTION gis.protect_analysis_result();
CREATE TRIGGER analysis_artifact_guard BEFORE INSERT OR UPDATE OR DELETE ON gis.artifacts FOR EACH ROW EXECUTE FUNCTION gis.protect_analysis_result();

CREATE FUNCTION gis.protect_finished_analysis() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE revision bigint; boundary uuid; release_status text; expected bigint;
BEGIN
 IF OLD.status IN ('succeeded','failed') THEN RAISE EXCEPTION 'Finished analysis run is immutable' USING ERRCODE='23514'; END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 IF (to_jsonb(OLD)-ARRAY['status','finished_at','output_manifest']) IS DISTINCT FROM (to_jsonb(NEW)-ARRAY['status','finished_at','output_manifest']) THEN
  RAISE EXCEPTION 'Analysis identity is immutable' USING ERRCODE='23514'; END IF;
 IF NEW.status='succeeded' THEN
  SELECT input_revision,boundary_set_id,status INTO revision,boundary,release_status FROM gis.dataset_releases WHERE id=NEW.release_id FOR SHARE;
  SELECT count(*) INTO expected FROM gis.districts WHERE boundary_set_id=boundary;
  IF release_status IS DISTINCT FROM 'draft' OR revision IS DISTINCT FROM NEW.input_revision OR expected=0
   OR (SELECT count(*) FROM gis.indicator_results WHERE run_id=NEW.id)<>expected
   OR (SELECT count(*) FROM gis.coverage_results WHERE run_id=NEW.id)<>expected*3
   OR (SELECT count(DISTINCT kind) FROM gis.artifacts WHERE analysis_run_id=NEW.id AND kind IN ('analysis_results','thematic_density','thematic_facility_count','thematic_population_per_facility','thematic_indicative_deficit'))<>5
   OR NEW.output_manifest->>'validation_status' IS DISTINCT FROM 'passed'
   OR NEW.output_manifest->>'input_hash' IS DISTINCT FROM NEW.input_hash
   OR NEW.output_manifest->>'analysis_run_id' IS DISTINCT FROM NEW.id::text
   OR NEW.finished_at IS NULL THEN
   RAISE EXCEPTION 'Incomplete or stale analysis cannot succeed' USING ERRCODE='23514'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER finished_analysis_guard BEFORE UPDATE OR DELETE ON gis.analysis_runs FOR EACH ROW EXECUTE FUNCTION gis.protect_finished_analysis();
REVOKE ALL ON FUNCTION gis.protect_analysis_result(),gis.protect_finished_analysis() FROM PUBLIC;
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Analysis immutability rollback requires a reviewed deployment plan.');
    }
};
