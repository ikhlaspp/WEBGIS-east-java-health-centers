<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
DO $$
DECLARE name text;
BEGIN
 FOREACH name IN ARRAY ARRAY['gis_runtime','gis_worker','gis_publisher','gis_lifecycle_owner'] LOOP
  IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=name) THEN
   IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=name AND (rolsuper OR rolbypassrls OR rolcreaterole OR rolcreatedb OR rolcanlogin OR rolreplication OR rolinherit)) THEN
    RAISE EXCEPTION 'Existing GIS role has unsafe attributes: %',name;
   END IF;
  ELSE
   EXECUTE format('CREATE ROLE %I NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS',name);
  END IF;
  -- Managed PostgreSQL administrators can create roles without being able to use them.
  -- Only the migration administrator receives membership, never an application group.
  IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
   EXECUTE format('GRANT %I TO %I WITH INHERIT %s, SET TRUE',name,current_user,
    CASE WHEN name='gis_lifecycle_owner' THEN 'TRUE' ELSE 'FALSE' END);
  END IF;
 END LOOP;
END $$;
REVOKE ALL ON SCHEMA app,gis,staging FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA app,gis,staging FROM PUBLIC,gis_runtime,gis_worker,gis_publisher;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA app,gis,staging FROM PUBLIC,gis_runtime,gis_worker,gis_publisher;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA app,gis,staging FROM PUBLIC,gis_runtime,gis_worker,gis_publisher;
ALTER DEFAULT PRIVILEGES IN SCHEMA app,gis,staging REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA app,gis,staging REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
GRANT USAGE ON SCHEMA gis,extensions TO gis_runtime,gis_worker,gis_publisher,gis_lifecycle_owner;
GRANT USAGE ON SCHEMA app TO gis_runtime,gis_lifecycle_owner;
GRANT USAGE ON SCHEMA staging TO gis_worker;

DO $$
DECLARE relation record;
BEGIN
 FOR relation IN SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('gis','staging') LOOP
  EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY',relation.schemaname,relation.tablename);
  EXECUTE format('ALTER TABLE %I.%I FORCE ROW LEVEL SECURITY',relation.schemaname,relation.tablename);
  EXECUTE format('CREATE POLICY lifecycle_access ON %I.%I TO gis_lifecycle_owner USING (true) WITH CHECK (true)',relation.schemaname,relation.tablename);
  EXECUTE format('CREATE POLICY worker_read ON %I.%I FOR SELECT TO gis_worker USING (true)',relation.schemaname,relation.tablename);
  IF relation.schemaname='gis' THEN
   EXECUTE format('CREATE POLICY publisher_read ON %I.%I FOR SELECT TO gis_publisher USING (true)',relation.schemaname,relation.tablename);
  END IF;
 END LOOP;
END $$;
GRANT SELECT ON ALL TABLES IN SCHEMA gis TO gis_worker,gis_publisher;
GRANT SELECT ON staging.rows TO gis_worker;
GRANT SELECT ON gis.dataset_releases,gis.release_sources,gis.boundary_sets,gis.analysis_runs TO gis_lifecycle_owner;
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;

CREATE FUNCTION gis.is_public_release(target uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT EXISTS(SELECT 1 FROM gis.dataset_releases WHERE id=target AND status='published')
$$;
CREATE FUNCTION gis.is_public_boundary(target uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT EXISTS(SELECT 1 FROM gis.dataset_releases WHERE boundary_set_id=target AND status='published')
$$;
CREATE FUNCTION gis.is_public_source(target uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT EXISTS(SELECT 1 FROM gis.release_sources s JOIN gis.dataset_releases r ON r.id=s.release_id WHERE s.source_id=target AND r.status='published')
 OR EXISTS(SELECT 1 FROM gis.boundary_sets b JOIN gis.dataset_releases r ON r.boundary_set_id=b.id WHERE b.source_id=target AND r.status='published')
$$;
CREATE FUNCTION gis.is_public_run(target uuid, target_release uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT EXISTS(SELECT 1 FROM gis.analysis_runs a JOIN gis.dataset_releases r ON r.id=a.release_id WHERE a.id=target AND a.release_id=target_release AND a.status='succeeded' AND r.status='published')
$$;
ALTER FUNCTION gis.is_public_run(uuid,uuid) OWNER TO gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.is_public_run(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.is_public_run(uuid,uuid) TO gis_runtime;
ALTER FUNCTION gis.is_public_release(uuid) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.is_public_boundary(uuid) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.is_public_source(uuid) OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.is_public_release(uuid),gis.is_public_boundary(uuid),gis.is_public_source(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.is_public_release(uuid),gis.is_public_boundary(uuid),gis.is_public_source(uuid) TO gis_runtime;

CREATE POLICY public_releases ON gis.dataset_releases FOR SELECT TO gis_runtime USING(status='published');
CREATE POLICY public_sources ON gis.data_sources FOR SELECT TO gis_runtime USING(gis.is_public_source(id));
CREATE POLICY public_boundaries ON gis.boundary_sets FOR SELECT TO gis_runtime USING(gis.is_public_boundary(id));
CREATE POLICY public_regencies ON gis.regencies FOR SELECT TO gis_runtime USING(gis.is_public_boundary(boundary_set_id));
CREATE POLICY public_districts ON gis.districts FOR SELECT TO gis_runtime USING(gis.is_public_boundary(boundary_set_id));
CREATE POLICY public_release_sources ON gis.release_sources FOR SELECT TO gis_runtime USING(gis.is_public_release(release_id));
CREATE POLICY public_indicators ON gis.district_indicators FOR SELECT TO gis_runtime USING(gis.is_public_release(release_id));
CREATE POLICY public_facilities ON gis.facility_snapshots FOR SELECT TO gis_runtime USING(gis.is_public_release(release_id));
CREATE POLICY public_runs ON gis.analysis_runs FOR SELECT TO gis_runtime USING(gis.is_public_release(release_id) AND status='succeeded');
CREATE POLICY public_indicator_results ON gis.indicator_results FOR SELECT TO gis_runtime USING(gis.is_public_run(run_id,release_id));
CREATE POLICY public_coverage_results ON gis.coverage_results FOR SELECT TO gis_runtime USING(gis.is_public_run(run_id,release_id));
CREATE POLICY public_artifacts ON gis.artifacts FOR SELECT TO gis_runtime USING(gis.is_public_release(release_id) AND sanitized AND (analysis_run_id IS NULL OR gis.is_public_run(analysis_run_id,release_id)));

GRANT SELECT(id,label,boundary_set_id,facility_period,population_policy,area_policy,status,method_version,code_revision,default_analysis_run_id,published_at) ON gis.dataset_releases TO gis_runtime;
GRANT SELECT(id,publisher,title,source_url,publication_year,observation_period,license_note,limitations,status) ON gis.data_sources TO gis_runtime;
GRANT SELECT(id,source_id,name,version,code_system,reference_year,source_crs) ON gis.boundary_sets TO gis_runtime;
GRANT SELECT ON gis.regencies,gis.districts,gis.release_sources TO gis_runtime;
GRANT SELECT(release_id,boundary_set_id,district_id,population,population_year,population_source_id,area_km2,area_year,area_source_id,quality_status,notes) ON gis.district_indicators TO gis_runtime;
GRANT SELECT(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,location,coordinate_status,precision_level) ON gis.facility_snapshots TO gis_runtime;
GRANT SELECT(id,release_id,method_version,code_revision,input_revision,parameters,status,started_at,finished_at) ON gis.analysis_runs TO gis_runtime;
GRANT SELECT ON gis.indicator_results,gis.coverage_results TO gis_runtime;
GRANT SELECT(id,release_id,analysis_run_id,kind,sha256,bytes,generated_at,sanitized) ON gis.artifacts TO gis_runtime;
ALTER TABLE app.active_release ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.active_release FORCE ROW LEVEL SECURITY;
CREATE POLICY active_public ON app.active_release FOR SELECT TO gis_runtime USING(release_id IS NULL OR gis.is_public_release(release_id));
CREATE POLICY active_lifecycle ON app.active_release TO gis_lifecycle_owner USING(true) WITH CHECK(true);
GRANT SELECT ON app.active_release TO gis_runtime;
GRANT SELECT(id,name,email,password_hash,is_admin,is_active) ON app.users TO gis_runtime;
GRANT SELECT,INSERT,UPDATE,DELETE ON app.sessions,app.jobs,app.failed_jobs,app.job_batches TO gis_runtime;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA app TO gis_runtime;

CREATE POLICY worker_release_insert ON gis.dataset_releases FOR INSERT TO gis_worker WITH CHECK(status='draft' AND input_revision=0 AND quality_report_id IS NULL AND default_analysis_run_id IS NULL AND published_at IS NULL AND published_by IS NULL);
CREATE POLICY worker_release_update ON gis.dataset_releases FOR UPDATE TO gis_worker USING(status='draft') WITH CHECK(status='draft');
GRANT INSERT(id,label,boundary_set_id,facility_period,population_policy,area_policy,source_manifest,method_version,code_revision), UPDATE(label,facility_period,population_policy,area_policy,source_manifest,method_version,code_revision) ON gis.dataset_releases TO gis_worker;

CREATE POLICY worker_indicators ON gis.district_indicators FOR ALL TO gis_worker USING(EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft')) WITH CHECK(EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft'));
CREATE POLICY worker_facilities ON gis.facility_snapshots FOR ALL TO gis_worker USING(EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft')) WITH CHECK(coordinate_status IN ('missing','unverified') AND selected_review_id IS NULL AND EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft'));
CREATE POLICY worker_release_sources ON gis.release_sources FOR ALL TO gis_worker USING(EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft')) WITH CHECK(EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft'));
CREATE POLICY worker_reviews ON gis.geocode_reviews FOR ALL TO gis_worker USING(EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft')) WITH CHECK(result_status='pending' AND reviewed_by IS NULL AND reviewed_at IS NULL AND EXISTS(SELECT 1 FROM gis.dataset_releases r WHERE r.id=release_id AND r.status='draft'));
GRANT INSERT,UPDATE,DELETE ON gis.district_indicators,gis.release_sources TO gis_worker;
GRANT INSERT(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,location,coordinate_status,precision_level,coordinate_source_id), UPDATE(district_id,name,address,service_type,area_type,source_id,source_row,location,coordinate_status,precision_level,coordinate_source_id), DELETE ON gis.facility_snapshots TO gis_worker;
ALTER TABLE gis.geocode_reviews ALTER COLUMN result_status SET DEFAULT 'pending';
ALTER TABLE gis.geocode_reviews ALTER COLUMN decision_reason SET DEFAULT '';
GRANT INSERT(id,release_id,facility_code,source_id,candidate_location,provider,query,provider_object_id,precision_level,raw_response_private_path,evidence_url,evidence_note,evidence_sha256), UPDATE(candidate_location,provider,query,provider_object_id,precision_level,raw_response_private_path,evidence_url,evidence_note,evidence_sha256) ON gis.geocode_reviews TO gis_worker;

ALTER TABLE gis.data_sources ALTER COLUMN status SET DEFAULT 'pending';
CREATE POLICY worker_source_insert ON gis.data_sources FOR INSERT TO gis_worker WITH CHECK(status='pending');
GRANT INSERT(id,publisher,title,source_url,private_path,publication_year,observation_period,retrieved_at,sha256,license_note,limitations) ON gis.data_sources TO gis_worker;
CREATE POLICY worker_boundary_insert ON gis.boundary_sets FOR INSERT TO gis_worker WITH CHECK(frozen_at IS NULL);
GRANT INSERT(id,source_id,name,version,code_system,reference_year,source_crs,metadata) ON gis.boundary_sets TO gis_worker;
CREATE POLICY worker_regencies ON gis.regencies FOR ALL TO gis_worker USING(true) WITH CHECK(true);
CREATE POLICY worker_districts ON gis.districts FOR ALL TO gis_worker USING(true) WITH CHECK(true);
GRANT INSERT,UPDATE,DELETE ON gis.regencies,gis.districts TO gis_worker;
ALTER TABLE gis.region_aliases ALTER COLUMN status SET DEFAULT 'pending';
CREATE POLICY worker_alias_insert ON gis.region_aliases FOR INSERT TO gis_worker WITH CHECK(status='pending' AND reviewed_by IS NULL AND reviewed_at IS NULL);
GRANT INSERT(id,source_id,boundary_set_id,district_id,raw_regency,raw_district,source_code_system,source_edition,source_code,mapping_kind,evidence) ON gis.region_aliases TO gis_worker;
CREATE POLICY worker_staging_insert ON staging.rows FOR INSERT TO gis_worker WITH CHECK(EXISTS(SELECT 1 FROM gis.import_batches b JOIN gis.dataset_releases r ON r.id=b.target_release_id WHERE b.id=batch_id AND r.status='draft'));
GRANT INSERT ON staging.rows TO gis_worker;

CREATE FUNCTION gis.track_release_metadata() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF (to_jsonb(NEW)-ARRAY['status','input_revision','quality_report_id','default_analysis_run_id','published_at','published_by'])
 IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['status','input_revision','quality_report_id','default_analysis_run_id','published_at','published_by']) THEN
  IF OLD.status<>'draft' THEN RAISE EXCEPTION 'Frozen release metadata cannot change' USING ERRCODE='23514'; END IF;
  NEW.input_revision:=OLD.input_revision+1; NEW.quality_report_id:=NULL; NEW.default_analysis_run_id:=NULL;
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION gis.track_release_metadata() FROM PUBLIC;
CREATE TRIGGER release_metadata_revision BEFORE UPDATE ON gis.dataset_releases FOR EACH ROW EXECUTE FUNCTION gis.track_release_metadata();

GRANT EXECUTE ON FUNCTION gis.valid_geometry(extensions.geometry,text) TO gis_worker;
GRANT SELECT,UPDATE(input_revision,quality_report_id,default_analysis_run_id) ON gis.dataset_releases TO gis_lifecycle_owner;
ALTER FUNCTION gis.lock_release_input() SECURITY DEFINER;
ALTER FUNCTION gis.protect_shared_input() SECURITY DEFINER;
GRANT SELECT ON gis.facility_snapshots,gis.district_indicators,gis.geocode_reviews TO gis_lifecycle_owner;
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;
ALTER FUNCTION gis.lock_release_input() OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.protect_shared_input() OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.lock_release_input(),gis.protect_shared_input() FROM PUBLIC;

DO $$
DECLARE api_role text;
BEGIN
 FOREACH api_role IN ARRAY ARRAY['anon','authenticated'] LOOP
  IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=api_role) THEN
   EXECUTE format('REVOKE ALL ON SCHEMA app,gis,staging FROM %I',api_role);
   EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA app,gis,staging FROM %I',api_role);
   EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA app,gis,staging FROM %I',api_role);
  END IF;
 END LOOP;
END $$;
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Access-policy rollback requires a reviewed deployment plan.');
    }
};
