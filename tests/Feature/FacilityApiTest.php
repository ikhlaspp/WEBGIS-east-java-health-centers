<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\DB;
use Tests\GisDatabaseTestCase;

class FacilityApiTest extends GisDatabaseTestCase
{
    private function publish(int $release = 6, int $run = 8, int $quality = 9): void
    {
        DB::insert("INSERT INTO gis.analysis_runs(id,release_id,method_version,code_revision,input_hash,parameters_hash,input_revision,parameters,status,idempotency_key,started_by) VALUES(?,?,'fixture','fixture','fixture','fixture',1,'{}','succeeded',?,?)", [$this->id($run), $this->id($release), hash('sha256', (string) $run), $this->id(1)]);
        DB::insert("INSERT INTO gis.quality_reports(id,release_id,input_revision,input_hash,report_hash,policy_version,checks,exclusions,passed,approved_by,approved_at) VALUES(?,?,1,'fixture','fixture','fixture','{}','{}',true,?,now())", [$this->id($quality), $this->id($release), $this->id(1)]);
        DB::update("UPDATE gis.dataset_releases SET status='published',quality_report_id=?,default_analysis_run_id=?,published_at=now(),published_by=? WHERE id=?", [$this->id($quality), $this->id($run), $this->id(1), $this->id($release)]);
        DB::update('UPDATE app.active_release SET release_id=?,analysis_run_id=?,version=version+1 WHERE singleton=1', [$this->id($release), $this->id($run)]);
    }

    private function extraFacility(): void
    {
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level,location) VALUES(?,?,?,'35010100002','Fixture','100%_! Road','Non Rawat Inap','Perkotaan',?,2,'unverified','street',extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326))", [$this->id(6), $this->id(3), $this->id(5), $this->id(2)]);
    }

    public function test_missing_facilities_remain_in_list_and_detail_with_public_provenance(): void
    {
        $this->extraFacility();
        $this->publish();
        $list = $this->getJson('/api/v1/facilities?per_page=1')->assertOk()->assertJsonPath('meta.total', 2)->assertJsonPath('data.0.code', '35010100001')->assertJsonPath('data.0.location', null);
        $detail = $this->getJson('/api/v1/facilities/35010100001')->assertOk()->assertJsonPath('data.coordinate_status', 'missing')->assertJsonPath('data.source.source_id', $this->id(2))->assertJsonPath('data.coordinate_source', null);
        $this->assertArrayNotHasKey('source_row', $detail->json('data'));
        $this->assertArrayNotHasKey('private_path', $detail->json('data.source'));
        $this->assertSame('gis_runtime', DB::selectOne('SELECT current_user AS role')->role);
        $this->assertFalse(DB::selectOne("SELECT has_column_privilege(current_user,'gis.facility_snapshots','selected_review_id','SELECT') AS allowed")->allowed);
        if (! is_dir(base_path('reports'))) {
            mkdir(base_path('reports'), 0770, true);
        }
        file_put_contents(base_path('reports/facility-api.json'), json_encode(['synthetic' => true, 'list' => $list->json(), 'detail' => $detail->json()], JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR));
    }

    public function test_filters_pagination_and_stable_sort_preserve_the_filtered_total(): void
    {
        $this->extraFacility();
        $this->publish();
        $this->getJson('/api/v1/facilities?sort=-name&per_page=1&page=2')->assertOk()->assertJsonPath('data.0.code', '35010100002')->assertJsonPath('meta.total', 2);
        $this->getJson('/api/v1/facilities?sort=-code&per_page=1')->assertOk()->assertJsonPath('data.0.code', '35010100002');
        $this->getJson('/api/v1/facilities?page=3&per_page=1')->assertOk()->assertJsonCount(0, 'data')->assertJsonPath('meta.total', 2);
        $this->getJson('/api/v1/facilities?'.http_build_query(['regency_code' => '3501', 'district_code' => '3501010', 'service_type' => 'Non Rawat Inap', 'area_type' => 'Perkotaan', 'coordinate_status' => 'unverified']))->assertOk()->assertJsonPath('meta.total', 1)->assertJsonPath('data.0.location.coordinates', [112.5, -7.5]);
        $this->getJson('/api/v1/facilities?coordinate_status=verified')->assertOk()->assertJsonPath('meta.total', 0);
        $this->getJson('/api/v1/facilities?coordinate_status=missing')->assertOk()->assertJsonPath('data.0.code', '35010100001');
    }

    public function test_search_is_literal_and_parameterized_across_name_code_and_address(): void
    {
        $this->extraFacility();
        $this->publish();
        foreach (['%', '_', '!', '100%_!'] as $search) {
            $this->getJson('/api/v1/facilities?'.http_build_query(['q' => $search]))->assertOk()->assertJsonPath('meta.total', 1)->assertJsonPath('data.0.code', '35010100002');
        }
        $this->getJson('/api/v1/facilities?q=fixture')->assertOk()->assertJsonPath('meta.total', 2);
        $this->getJson('/api/v1/facilities?q=35010100001')->assertOk()->assertJsonPath('meta.total', 1);
        $this->getJson('/api/v1/facilities?q=%20%20')->assertOk()->assertJsonPath('meta.total', 2);
        $this->getJson('/api/v1/facilities?'.http_build_query(['q' => "' OR 1=1 --"]))->assertOk()->assertJsonPath('meta.total', 0);
    }

    public function test_parent_mismatch_and_unknown_region_are_rejected(): void
    {
        DB::insert("INSERT INTO gis.regencies(id,boundary_set_id,code,name,kind,geom) SELECT ?,boundary_set_id,'3502','Other','kabupaten',geom FROM gis.regencies WHERE id=?", [$this->id(40), $this->id(4)]);
        $this->publish();
        foreach (['regency_code=3502&district_code=3501010', 'regency_code=3599', 'district_code=3599999'] as $query) {
            $this->getJson('/api/v1/facilities?'.$query)->assertUnprocessable()->assertJsonPath('error.code', 'VALIDATION_FAILED');
        }
    }

    public function test_drafts_and_wrong_runs_cannot_be_read_and_unknown_facility_is_not_found(): void
    {
        $this->getJson('/api/v1/facilities')->assertStatus(503);
        $this->getJson('/api/v1/facilities/35010100001?release_id='.$this->id(6))->assertNotFound();
        DB::statement('RESET ROLE');
        $this->publish();
        $this->getJson('/api/v1/facilities?analysis_run_id='.$this->id(999))->assertNotFound();
        $this->getJson('/api/v1/facilities/35010109999')->assertNotFound();
    }

    public function test_the_same_facility_code_is_resolved_only_within_the_requested_release(): void
    {
        DB::insert("INSERT INTO gis.dataset_releases(id,label,boundary_set_id,facility_period,population_policy,area_policy,method_version,code_revision) VALUES(?,'Historical',?,'2023','fixture','fixture','test','test')", [$this->id(16), $this->id(3)]);
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level) SELECT ?,boundary_set_id,district_id,facility_code,'Historical name',address,service_type,area_type,source_id,source_row,coordinate_status,precision_level FROM gis.facility_snapshots WHERE release_id=?", [$this->id(16), $this->id(6)]);
        $this->publish(16, 18, 19);
        $this->publish();
        $this->getJson('/api/v1/facilities/35010100001')->assertOk()->assertJsonPath('data.name', 'Fixture')->assertJsonPath('meta.release_id', $this->id(6));
        $this->getJson('/api/v1/facilities/35010100001?release_id='.$this->id(16))->assertOk()->assertJsonPath('data.name', 'Historical name')->assertJsonPath('meta.analysis_run_id', $this->id(18));
    }
}
