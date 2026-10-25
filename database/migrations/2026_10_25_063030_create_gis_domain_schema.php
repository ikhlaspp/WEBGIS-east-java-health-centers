<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        if (DB::connection()->getDriverName() !== 'pgsql') {
            throw new RuntimeException('The GIS schema requires PostgreSQL/PostGIS.');
        }

        $extension = DB::selectOne("SELECT n.nspname AS schema_name FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace WHERE e.extname='postgis'");
        if ($extension !== null && $extension->schema_name !== 'extensions') {
            throw new RuntimeException('PostGIS must be provisioned in schema extensions before GIS migrations.');
        }

        DB::unprepared(<<<'SQL'
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA extensions;
CREATE SCHEMA app;
CREATE SCHEMA gis;
CREATE SCHEMA staging;
REVOKE ALL ON SCHEMA app, gis, staging FROM PUBLIC;

CREATE FUNCTION gis.valid_geometry(g extensions.geometry, expected_type text) RETURNS boolean
LANGUAGE sql IMMUTABLE STRICT SET search_path = pg_catalog, extensions AS $$
 SELECT extensions.ST_SRID(g)=4326 AND extensions.ST_GeometryType(g)='ST_' || expected_type
 AND NOT extensions.ST_IsEmpty(g) AND extensions.ST_IsValid(g)
 AND extensions.ST_XMin(extensions.Box3D(g)) >= -180 AND extensions.ST_XMax(extensions.Box3D(g)) <= 180
 AND extensions.ST_YMin(extensions.Box3D(g)) >= -90 AND extensions.ST_YMax(extensions.Box3D(g)) <= 90
$$;
REVOKE ALL ON FUNCTION gis.valid_geometry(extensions.geometry,text) FROM PUBLIC;

ALTER TABLE public.jobs SET SCHEMA app;
ALTER TABLE public.job_batches SET SCHEMA app;
ALTER TABLE public.failed_jobs SET SCHEMA app;
CREATE TABLE app.users (
 id uuid PRIMARY KEY, name text NOT NULL, email text NOT NULL CHECK (email=lower(email)), password_hash text NOT NULL,
 is_admin boolean NOT NULL DEFAULT false, is_active boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(email)
);
CREATE TABLE app.sessions (
 id text PRIMARY KEY, user_id uuid REFERENCES app.users ON DELETE RESTRICT, ip_address inet, user_agent text,
 payload text NOT NULL, last_activity bigint NOT NULL, absolute_expires_at timestamptz NOT NULL
);
CREATE INDEX sessions_user ON app.sessions(user_id);
CREATE TABLE app.operator_tokens (
 id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES app.users ON DELETE RESTRICT,
 token_hash char(64) NOT NULL UNIQUE CHECK (token_hash ~ '^[0-9a-f]{64}$'), abilities jsonb NOT NULL DEFAULT '[]',
 expires_at timestamptz NOT NULL, revoked_at timestamptz, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX tokens_user ON app.operator_tokens(user_id);
CREATE TABLE gis.data_sources (
 id uuid PRIMARY KEY, publisher text NOT NULL, title text NOT NULL, source_url text, private_path text,
 publication_year smallint, observation_period text NOT NULL, retrieved_at timestamptz,
 sha256 char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'), license_note text NOT NULL, limitations text NOT NULL,
 status text NOT NULL CHECK (status IN ('pending','verified','rejected')), created_at timestamptz NOT NULL DEFAULT now(),
 CHECK (nullif(btrim(source_url),'') IS NOT NULL OR nullif(btrim(private_path),'') IS NOT NULL)
);
CREATE TABLE gis.boundary_sets (
 id uuid PRIMARY KEY, source_id uuid NOT NULL REFERENCES gis.data_sources ON DELETE RESTRICT,
 name text NOT NULL, version text NOT NULL, code_system text NOT NULL, reference_year smallint,
 source_crs text NOT NULL, metadata jsonb NOT NULL DEFAULT '{}', frozen_at timestamptz, UNIQUE(source_id,version)
);
CREATE TABLE gis.regencies (
 id uuid PRIMARY KEY, boundary_set_id uuid NOT NULL REFERENCES gis.boundary_sets ON DELETE RESTRICT,
 code text NOT NULL, name text NOT NULL, kind text NOT NULL CHECK(kind IN ('kabupaten','kota')),
 geom extensions.geometry(MultiPolygon,4326) NOT NULL CHECK (gis.valid_geometry(geom,'MultiPolygon')),
 geom_display extensions.geometry(MultiPolygon,4326) CHECK (gis.valid_geometry(geom_display,'MultiPolygon')),
 UNIQUE(boundary_set_id,code), UNIQUE(id,boundary_set_id)
);
CREATE TABLE gis.districts (
 id uuid PRIMARY KEY, boundary_set_id uuid NOT NULL REFERENCES gis.boundary_sets ON DELETE RESTRICT,
 regency_id uuid NOT NULL, code text NOT NULL, name text NOT NULL,
 geom extensions.geometry(MultiPolygon,4326) NOT NULL CHECK (gis.valid_geometry(geom,'MultiPolygon')),
 geom_display extensions.geometry(MultiPolygon,4326) CHECK (gis.valid_geometry(geom_display,'MultiPolygon')),
 UNIQUE(boundary_set_id,code), UNIQUE(id,boundary_set_id),
 FOREIGN KEY(regency_id,boundary_set_id) REFERENCES gis.regencies(id,boundary_set_id) ON DELETE RESTRICT
);
CREATE TABLE gis.region_aliases (
 id uuid PRIMARY KEY, source_id uuid NOT NULL REFERENCES gis.data_sources ON DELETE RESTRICT,
 boundary_set_id uuid NOT NULL, district_id uuid NOT NULL, raw_regency text NOT NULL, raw_district text NOT NULL,
 source_code_system text NOT NULL, source_edition text NOT NULL, source_code text,
 mapping_kind text NOT NULL, status text NOT NULL CHECK(status IN ('pending','approved','rejected')),
 evidence text NOT NULL, reviewed_by uuid REFERENCES app.users ON DELETE RESTRICT, reviewed_at timestamptz,
 UNIQUE(source_id,boundary_set_id,raw_regency,raw_district),
 FOREIGN KEY(district_id,boundary_set_id) REFERENCES gis.districts(id,boundary_set_id) ON DELETE RESTRICT,
 CHECK(status<>'approved' OR (btrim(evidence)<>'' AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL))
);
CREATE TABLE gis.dataset_releases (
 id uuid PRIMARY KEY, label text NOT NULL UNIQUE, boundary_set_id uuid NOT NULL REFERENCES gis.boundary_sets ON DELETE RESTRICT,
 facility_period text NOT NULL, population_policy text NOT NULL, area_policy text NOT NULL,
 status text NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','validated','published','withdrawn')),
 input_revision bigint NOT NULL DEFAULT 0 CHECK(input_revision>=0), source_manifest jsonb NOT NULL DEFAULT '{}',
 method_version text NOT NULL, code_revision text NOT NULL, quality_report_id uuid, default_analysis_run_id uuid,
 published_at timestamptz, published_by uuid REFERENCES app.users ON DELETE RESTRICT,
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(id,boundary_set_id),
 CHECK(status NOT IN ('published','withdrawn') OR (published_at IS NOT NULL AND published_by IS NOT NULL
 AND quality_report_id IS NOT NULL AND default_analysis_run_id IS NOT NULL))
);
CREATE TABLE gis.release_sources (
 release_id uuid NOT NULL REFERENCES gis.dataset_releases ON DELETE RESTRICT,
 source_id uuid NOT NULL REFERENCES gis.data_sources ON DELETE RESTRICT, purpose text NOT NULL,
 PRIMARY KEY(release_id,source_id,purpose)
);
CREATE TABLE gis.district_indicators (
 release_id uuid NOT NULL, boundary_set_id uuid NOT NULL, district_id uuid NOT NULL,
 population bigint CHECK(population>=0), population_year smallint,
 population_source_id uuid REFERENCES gis.data_sources ON DELETE RESTRICT, population_locator text, population_raw text,
 area_km2 numeric(16,6) CHECK(area_km2>0 AND area_km2<>'NaN'::numeric), area_year smallint,
 area_source_id uuid REFERENCES gis.data_sources ON DELETE RESTRICT, area_locator text, area_raw text,
 quality_status text NOT NULL, notes text NOT NULL,
 PRIMARY KEY(release_id,district_id),
 FOREIGN KEY(release_id,boundary_set_id) REFERENCES gis.dataset_releases(id,boundary_set_id) ON DELETE RESTRICT,
 FOREIGN KEY(district_id,boundary_set_id) REFERENCES gis.districts(id,boundary_set_id) ON DELETE RESTRICT,
 CHECK(population IS NULL OR (population_year IS NOT NULL AND population_source_id IS NOT NULL AND nullif(btrim(population_locator),'') IS NOT NULL AND population_raw IS NOT NULL)),
 CHECK(area_km2 IS NULL OR (area_year IS NOT NULL AND area_source_id IS NOT NULL AND nullif(btrim(area_locator),'') IS NOT NULL AND area_raw IS NOT NULL))
);
CREATE TABLE gis.facility_snapshots (
 release_id uuid NOT NULL, boundary_set_id uuid NOT NULL, district_id uuid NOT NULL,
 facility_code text NOT NULL CHECK(facility_code ~ '^[0-9]{11}$'), name text NOT NULL, address text NOT NULL,
 service_type text NOT NULL, area_type text NOT NULL, source_id uuid NOT NULL REFERENCES gis.data_sources ON DELETE RESTRICT,
 source_row integer NOT NULL CHECK(source_row>0), location extensions.geometry(Point,4326) CHECK(gis.valid_geometry(location,'Point')),
 coordinate_status text NOT NULL CHECK(coordinate_status IN ('missing','unverified','verified','rejected')),
 precision_level text NOT NULL CHECK(precision_level IN ('facility','street','village','district','regency','unknown')),
 coordinate_source_id uuid REFERENCES gis.data_sources ON DELETE RESTRICT, selected_review_id uuid,
 PRIMARY KEY(release_id,facility_code),
 FOREIGN KEY(release_id,boundary_set_id) REFERENCES gis.dataset_releases(id,boundary_set_id) ON DELETE RESTRICT,
 FOREIGN KEY(district_id,boundary_set_id) REFERENCES gis.districts(id,boundary_set_id) ON DELETE RESTRICT,
 CHECK(coordinate_status<>'missing' OR (location IS NULL AND selected_review_id IS NULL)),
 CHECK(coordinate_status<>'verified' OR (location IS NOT NULL AND precision_level='facility' AND coordinate_source_id IS NOT NULL AND selected_review_id IS NOT NULL)),
 CHECK(coordinate_status<>'unverified' OR location IS NOT NULL)
);
CREATE TABLE gis.geocode_reviews (
 id uuid PRIMARY KEY, release_id uuid NOT NULL, facility_code text NOT NULL,
 source_id uuid NOT NULL REFERENCES gis.data_sources ON DELETE RESTRICT,
 candidate_location extensions.geometry(Point,4326) CHECK(gis.valid_geometry(candidate_location,'Point')),
 provider text NOT NULL, query text NOT NULL, provider_object_id text,
 precision_level text NOT NULL CHECK(precision_level IN ('facility','street','village','district','regency','unknown')),
 result_status text NOT NULL CHECK(result_status IN ('pending','accepted','rejected','missing')),
 raw_response_private_path text, evidence_url text, evidence_note text NOT NULL, decision_reason text NOT NULL,
 evidence_sha256 char(64) CHECK(evidence_sha256 ~ '^[0-9a-f]{64}$'),
 reviewed_by uuid REFERENCES app.users ON DELETE RESTRICT, reviewed_at timestamptz, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(id,release_id,facility_code),
 FOREIGN KEY(release_id,facility_code) REFERENCES gis.facility_snapshots(release_id,facility_code) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
 CHECK(result_status<>'missing' OR candidate_location IS NULL),
 CHECK(result_status<>'accepted' OR (candidate_location IS NOT NULL AND precision_level='facility'
 AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND btrim(decision_reason)<>''
 AND (nullif(btrim(evidence_url),'') IS NOT NULL OR (btrim(evidence_note)<>'' AND evidence_sha256 IS NOT NULL))))
);
ALTER TABLE gis.facility_snapshots ADD CONSTRAINT selected_review_owner
 FOREIGN KEY(selected_review_id,release_id,facility_code) REFERENCES gis.geocode_reviews(id,release_id,facility_code)
 ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE gis.analysis_runs (
 id uuid PRIMARY KEY, release_id uuid NOT NULL REFERENCES gis.dataset_releases ON DELETE RESTRICT,
 method_version text NOT NULL, code_revision text NOT NULL, input_hash text NOT NULL, parameters_hash text NOT NULL,
 input_revision bigint NOT NULL CHECK(input_revision>=0), parameters jsonb NOT NULL,
 status text NOT NULL CHECK(status IN ('pending','running','succeeded','failed')),
 idempotency_key char(64) NOT NULL UNIQUE CHECK(idempotency_key ~ '^[0-9a-f]{64}$'),
 started_at timestamptz, finished_at timestamptz, output_manifest jsonb NOT NULL DEFAULT '{}',
 started_by uuid NOT NULL REFERENCES app.users ON DELETE RESTRICT, UNIQUE(id,release_id)
);
CREATE TABLE gis.indicator_results (
 run_id uuid NOT NULL, release_id uuid NOT NULL, boundary_set_id uuid NOT NULL, district_id uuid NOT NULL,
 population bigint CHECK(population>=0), facility_count bigint NOT NULL CHECK(facility_count>=0),
 density numeric(24,12) CHECK(density>=0 AND density<>'NaN'::numeric),
 population_per_facility numeric(24,12) CHECK(population_per_facility>=0 AND population_per_facility<>'NaN'::numeric),
 facilities_per_30000 numeric(24,12) CHECK(facilities_per_30000>=0 AND facilities_per_30000<>'NaN'::numeric),
 indicative_need bigint CHECK(indicative_need>=0), indicative_deficit bigint CHECK(indicative_deficit>=0),
 without_facility boolean NOT NULL, completeness text NOT NULL, reason text NOT NULL,
 PRIMARY KEY(run_id,district_id), CHECK(without_facility=(facility_count=0)),
 FOREIGN KEY(run_id,release_id) REFERENCES gis.analysis_runs(id,release_id) ON DELETE RESTRICT,
 FOREIGN KEY(release_id,boundary_set_id) REFERENCES gis.dataset_releases(id,boundary_set_id) ON DELETE RESTRICT,
 FOREIGN KEY(district_id,boundary_set_id) REFERENCES gis.districts(id,boundary_set_id) ON DELETE RESTRICT
);
CREATE TABLE gis.coverage_results (
 run_id uuid NOT NULL, release_id uuid NOT NULL, boundary_set_id uuid NOT NULL, district_id uuid NOT NULL,
 radius_m integer NOT NULL CHECK(radius_m IN (1000,3000,5000)),
 covered_area_m2 numeric(24,8), geometry_area_m2 numeric(24,8), coverage_pct numeric(24,8),
 geom extensions.geometry(MultiPolygon,4326) CHECK(gis.valid_geometry(geom,'MultiPolygon')),
 registered_count integer NOT NULL CHECK(registered_count>=0), eligible_count integer NOT NULL CHECK(eligible_count>=0),
 excluded_count integer NOT NULL CHECK(excluded_count>=0), contributing_count integer NOT NULL CHECK(contributing_count>=0),
 exclusion_reasons jsonb NOT NULL DEFAULT '{}', completeness text NOT NULL, reason text NOT NULL,
 PRIMARY KEY(run_id,district_id,radius_m), CHECK(eligible_count+excluded_count=registered_count),
 CHECK((covered_area_m2 IS NULL AND geometry_area_m2 IS NULL AND coverage_pct IS NULL)
 OR (covered_area_m2 IS NOT NULL AND geometry_area_m2 IS NOT NULL AND coverage_pct IS NOT NULL
 AND geometry_area_m2>0 AND covered_area_m2>=0 AND covered_area_m2<=geometry_area_m2
 AND coverage_pct>=0 AND coverage_pct<=100 AND covered_area_m2<>'NaN'::numeric AND geometry_area_m2<>'NaN'::numeric)),
 FOREIGN KEY(run_id,release_id) REFERENCES gis.analysis_runs(id,release_id) ON DELETE RESTRICT,
 FOREIGN KEY(release_id,boundary_set_id) REFERENCES gis.dataset_releases(id,boundary_set_id) ON DELETE RESTRICT,
 FOREIGN KEY(district_id,boundary_set_id) REFERENCES gis.districts(id,boundary_set_id) ON DELETE RESTRICT
);
CREATE TABLE gis.artifacts (
 id uuid PRIMARY KEY, release_id uuid NOT NULL REFERENCES gis.dataset_releases ON DELETE RESTRICT, analysis_run_id uuid,
 kind text NOT NULL, private_path text NOT NULL, sha256 char(64) NOT NULL CHECK(sha256 ~ '^[0-9a-f]{64}$'),
 bytes bigint NOT NULL CHECK(bytes>=0), generated_at timestamptz NOT NULL, sanitized boolean NOT NULL DEFAULT false,
 UNIQUE(release_id,kind,sha256),
 FOREIGN KEY(analysis_run_id,release_id) REFERENCES gis.analysis_runs(id,release_id) ON DELETE RESTRICT
);
CREATE TABLE gis.import_batches (
 id uuid PRIMARY KEY, source_id uuid NOT NULL REFERENCES gis.data_sources ON DELETE RESTRICT,
 target_release_id uuid NOT NULL REFERENCES gis.dataset_releases ON DELETE RESTRICT,
 started_by uuid NOT NULL REFERENCES app.users ON DELETE RESTRICT,
 operation text NOT NULL, file_hash text NOT NULL, pipeline_version text NOT NULL, parameters_hash text NOT NULL,
 idempotency_key text NOT NULL UNIQUE, status text NOT NULL CHECK(status IN ('pending','running','succeeded','failed')),
 attempt integer NOT NULL DEFAULT 0 CHECK(attempt>=0), lease_token uuid, lease_until timestamptz, heartbeat_at timestamptz,
 started_at timestamptz, finished_at timestamptz, due_at timestamptz,
 expected_rows bigint CHECK(expected_rows>=0), raw_rows bigint CHECK(raw_rows>=0), accepted_rows bigint CHECK(accepted_rows>=0),
 quarantined_rows bigint CHECK(quarantined_rows>=0), aggregate_rows bigint CHECK(aggregate_rows>=0),
 checkpoint jsonb NOT NULL DEFAULT '{}', report_path text,
 CHECK(status<>'succeeded' OR (raw_rows IS NOT NULL AND accepted_rows IS NOT NULL AND quarantined_rows IS NOT NULL
 AND aggregate_rows IS NOT NULL AND raw_rows=accepted_rows+quarantined_rows+aggregate_rows))
);
CREATE TABLE staging.rows (
 batch_id uuid NOT NULL REFERENCES gis.import_batches ON DELETE RESTRICT, row_no bigint NOT NULL CHECK(row_no>0),
 source_locator text NOT NULL, raw jsonb NOT NULL, normalized jsonb,
 disposition text NOT NULL CHECK(disposition IN ('accepted','quarantined','aggregate')),
 errors jsonb NOT NULL DEFAULT '[]', row_hash char(64) NOT NULL CHECK(row_hash ~ '^[0-9a-f]{64}$'), PRIMARY KEY(batch_id,row_no)
);
CREATE TABLE gis.quality_reports (
 id uuid PRIMARY KEY, release_id uuid NOT NULL REFERENCES gis.dataset_releases ON DELETE RESTRICT,
 input_revision bigint NOT NULL CHECK(input_revision>=0), input_hash text NOT NULL, report_hash text NOT NULL,
 policy_version text NOT NULL, checks jsonb NOT NULL, exclusions jsonb NOT NULL, passed boolean NOT NULL,
 approved_by uuid REFERENCES app.users ON DELETE RESTRICT, approved_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(id,release_id),
 CHECK((approved_by IS NULL)=(approved_at IS NULL))
);
ALTER TABLE gis.dataset_releases ADD CONSTRAINT release_quality_owner FOREIGN KEY(quality_report_id,id)
 REFERENCES gis.quality_reports(id,release_id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE gis.dataset_releases ADD CONSTRAINT release_analysis_owner FOREIGN KEY(default_analysis_run_id,id)
 REFERENCES gis.analysis_runs(id,release_id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE app.active_release (
 singleton smallint PRIMARY KEY CHECK(singleton=1), release_id uuid REFERENCES gis.dataset_releases ON DELETE RESTRICT,
 analysis_run_id uuid, version bigint NOT NULL DEFAULT 0 CHECK(version>=0), changed_at timestamptz NOT NULL DEFAULT now(),
 CHECK((release_id IS NULL)=(analysis_run_id IS NULL)),
 FOREIGN KEY(analysis_run_id,release_id) REFERENCES gis.analysis_runs(id,release_id) ON DELETE RESTRICT
);
INSERT INTO app.active_release(singleton) VALUES(1);
CREATE TABLE app.audit_logs (
 id uuid PRIMARY KEY, actor_id uuid NOT NULL REFERENCES app.users ON DELETE RESTRICT,
 token_id uuid REFERENCES app.operator_tokens ON DELETE RESTRICT,
 action text NOT NULL, entity_type text NOT NULL, entity_key text NOT NULL,
 before_json jsonb NOT NULL, after_json jsonb NOT NULL, request_id text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.outbox_events (
 id uuid PRIMARY KEY, audit_id uuid NOT NULL REFERENCES app.audit_logs ON DELETE RESTRICT,
 event_type text NOT NULL, payload jsonb NOT NULL, attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
 available_at timestamptz NOT NULL, delivered_at timestamptz, last_error text, UNIQUE(audit_id,event_type)
);
CREATE INDEX regencies_geom ON gis.regencies USING gist(geom);
CREATE INDEX districts_geom ON gis.districts USING gist(geom);
CREATE INDEX districts_parent ON gis.districts(boundary_set_id,regency_id);
CREATE INDEX facilities_district ON gis.facility_snapshots(release_id,district_id);
CREATE INDEX facilities_filters ON gis.facility_snapshots(release_id,service_type,area_type);
CREATE INDEX facilities_location ON gis.facility_snapshots USING gist(location);
CREATE INDEX facilities_geography ON gis.facility_snapshots USING gist((location::extensions.geography));
CREATE INDEX reviews_facility ON gis.geocode_reviews(release_id,facility_code);
CREATE INDEX runs_status ON gis.analysis_runs(release_id,status);
CREATE INDEX artifacts_run ON gis.artifacts(release_id,analysis_run_id);
CREATE INDEX batches_status ON gis.import_batches(status,due_at);
CREATE INDEX audit_actor ON app.audit_logs(created_at,actor_id);
CREATE INDEX sources_release ON gis.release_sources(source_id);

CREATE FUNCTION gis.lock_release_input() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE parent record;
BEGIN
 FOR parent IN SELECT id,status FROM gis.dataset_releases WHERE id IN (NEW.release_id,OLD.release_id) ORDER BY id FOR UPDATE LOOP
  IF parent.status<>'draft' THEN RAISE EXCEPTION 'Only draft release inputs may change' USING ERRCODE='23514'; END IF;
  UPDATE gis.dataset_releases SET input_revision=input_revision+1,quality_report_id=NULL,default_analysis_run_id=NULL WHERE id=parent.id;
 END LOOP;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION gis.lock_release_input() FROM PUBLIC;
CREATE TRIGGER indicators_revision BEFORE INSERT OR UPDATE OR DELETE ON gis.district_indicators FOR EACH ROW EXECUTE FUNCTION gis.lock_release_input();
CREATE TRIGGER facilities_revision BEFORE INSERT OR UPDATE OR DELETE ON gis.facility_snapshots FOR EACH ROW EXECUTE FUNCTION gis.lock_release_input();
CREATE TRIGGER reviews_revision BEFORE INSERT OR UPDATE OR DELETE ON gis.geocode_reviews FOR EACH ROW EXECUTE FUNCTION gis.lock_release_input();
CREATE TRIGGER sources_revision BEFORE INSERT OR UPDATE OR DELETE ON gis.release_sources FOR EACH ROW EXECUTE FUNCTION gis.lock_release_input();

CREATE FUNCTION gis.protect_published_release() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF OLD.published_at IS NOT NULL OR OLD.status IN ('published','withdrawn') THEN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Published history cannot be deleted' USING ERRCODE='23514'; END IF;
  IF NOT (OLD.status='published' AND NEW.status='withdrawn' AND (to_jsonb(OLD)-'status')=(to_jsonb(NEW)-'status')) THEN
   RAISE EXCEPTION 'Published history is immutable' USING ERRCODE='23514';
  END IF;
 END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION gis.protect_published_release() FROM PUBLIC;
CREATE TRIGGER published_history BEFORE UPDATE OR DELETE ON gis.dataset_releases FOR EACH ROW EXECUTE FUNCTION gis.protect_published_release();

CREATE FUNCTION gis.protect_shared_input() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE parent record; old_value jsonb := to_jsonb(OLD); new_value jsonb := to_jsonb(NEW);
BEGIN
 FOR parent IN
  SELECT DISTINCT r.id,r.status FROM gis.dataset_releases r
  WHERE (TG_TABLE_NAME='data_sources' AND (
   EXISTS(SELECT 1 FROM gis.release_sources rs WHERE rs.release_id=r.id AND rs.source_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid))
   OR EXISTS(SELECT 1 FROM gis.boundary_sets b WHERE b.id=r.boundary_set_id AND b.source_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid))
   OR EXISTS(SELECT 1 FROM gis.facility_snapshots f WHERE f.release_id=r.id AND (f.source_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid) OR f.coordinate_source_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid)))
   OR EXISTS(SELECT 1 FROM gis.district_indicators d WHERE d.release_id=r.id AND (d.population_source_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid) OR d.area_source_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid)))
   OR EXISTS(SELECT 1 FROM gis.geocode_reviews g WHERE g.release_id=r.id AND g.source_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid))
  )) OR (TG_TABLE_NAME='boundary_sets' AND r.boundary_set_id IN ((old_value->>'id')::uuid,(new_value->>'id')::uuid))
  OR (TG_TABLE_NAME IN ('regencies','districts','region_aliases') AND r.boundary_set_id IN ((old_value->>'boundary_set_id')::uuid,(new_value->>'boundary_set_id')::uuid))
  ORDER BY r.id
 LOOP
  SELECT status INTO parent.status FROM gis.dataset_releases WHERE id=parent.id FOR UPDATE;
  IF parent.status<>'draft' THEN RAISE EXCEPTION 'Shared input belongs to a frozen release' USING ERRCODE='23514'; END IF;
  UPDATE gis.dataset_releases SET input_revision=input_revision+1,quality_report_id=NULL,default_analysis_run_id=NULL WHERE id=parent.id;
 END LOOP;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION gis.protect_shared_input() FROM PUBLIC;
CREATE TRIGGER freeze_sources BEFORE UPDATE OR DELETE ON gis.data_sources FOR EACH ROW EXECUTE FUNCTION gis.protect_shared_input();
CREATE TRIGGER freeze_boundary_sets BEFORE UPDATE OR DELETE ON gis.boundary_sets FOR EACH ROW EXECUTE FUNCTION gis.protect_shared_input();
CREATE TRIGGER freeze_regencies BEFORE INSERT OR UPDATE OR DELETE ON gis.regencies FOR EACH ROW EXECUTE FUNCTION gis.protect_shared_input();
CREATE TRIGGER freeze_districts BEFORE INSERT OR UPDATE OR DELETE ON gis.districts FOR EACH ROW EXECUTE FUNCTION gis.protect_shared_input();
CREATE TRIGGER freeze_aliases BEFORE INSERT OR UPDATE OR DELETE ON gis.region_aliases FOR EACH ROW EXECUTE FUNCTION gis.protect_shared_input();

CREATE FUNCTION gis.reject_mutation() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN RAISE EXCEPTION 'Immutable evidence cannot be changed or deleted' USING ERRCODE='23514'; END $$;
REVOKE ALL ON FUNCTION gis.reject_mutation() FROM PUBLIC;
CREATE TRIGGER immutable_raw BEFORE UPDATE OR DELETE ON staging.rows FOR EACH ROW EXECUTE FUNCTION gis.reject_mutation();
CREATE TRIGGER immutable_quality BEFORE UPDATE OR DELETE ON gis.quality_reports FOR EACH ROW EXECUTE FUNCTION gis.reject_mutation();
CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON app.audit_logs FOR EACH ROW EXECUTE FUNCTION gis.reject_mutation();

CREATE FUNCTION gis.check_selected_review() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF EXISTS (
  SELECT 1 FROM gis.facility_snapshots f LEFT JOIN gis.geocode_reviews r ON r.id=f.selected_review_id
  WHERE f.release_id IN (NEW.release_id,OLD.release_id) AND f.coordinate_status='verified'
  AND (r.id IS NULL OR r.result_status<>'accepted' OR r.release_id<>f.release_id OR r.facility_code<>f.facility_code
   OR r.source_id<>f.coordinate_source_id OR r.candidate_location IS NULL
   OR NOT extensions.ST_Equals(r.candidate_location,f.location))
 ) THEN RAISE EXCEPTION 'Selected review must be accepted and match facility, release, source and point' USING ERRCODE='23514'; END IF;
 RETURN NULL;
END $$;
REVOKE ALL ON FUNCTION gis.check_selected_review() FROM PUBLIC;
CREATE CONSTRAINT TRIGGER selected_review_snapshot AFTER INSERT OR UPDATE ON gis.facility_snapshots
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gis.check_selected_review();
CREATE CONSTRAINT TRIGGER selected_review_evidence AFTER INSERT OR UPDATE OR DELETE ON gis.geocode_reviews
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gis.check_selected_review();
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('GIS domain rollback requires an explicit reviewed backup/restore plan. Use a fresh disposable test database for reconstruction.');
    }
};
