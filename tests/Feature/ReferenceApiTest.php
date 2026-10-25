<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\DB;
use Tests\GisDatabaseTestCase;

class ReferenceApiTest extends GisDatabaseTestCase
{
    private function publishFixture(): void
    {
        DB::insert("INSERT INTO gis.analysis_runs(id,release_id,method_version,code_revision,input_hash,parameters_hash,input_revision,parameters,status,idempotency_key,started_by) VALUES(?,?,'fixture','fixture','fixture','fixture',1,'{}','succeeded',?,?)", [$this->id(8), $this->id(6), str_repeat('b', 64), $this->id(1)]);
        DB::insert("INSERT INTO gis.quality_reports(id,release_id,input_revision,input_hash,report_hash,policy_version,checks,exclusions,passed,approved_by,approved_at) VALUES(?,?,1,'fixture','fixture','fixture','{}','{}',true,?,now())", [$this->id(9), $this->id(6), $this->id(1)]);
        DB::update("UPDATE gis.dataset_releases SET status='published',quality_report_id=?,default_analysis_run_id=?,published_at=now(),published_by=?", [$this->id(9), $this->id(8), $this->id(1)]);
        DB::update('UPDATE app.active_release SET release_id=?,analysis_run_id=?,version=version+1 WHERE singleton=1', [$this->id(6), $this->id(8)]);
    }

    public function test_empty_public_catalog_and_no_active_dataset_have_distinct_responses(): void
    {
        $this->getJson('/api/v1/releases')->assertOk()->assertJsonCount(0, 'data')->assertJsonPath('meta.active_release_id', null)->assertJsonPath('meta.total', 0);
        $this->getJson('/api/v1/regions')->assertStatus(503)->assertJsonPath('error.code', 'NO_PUBLISHED_RELEASE')->assertJsonStructure(['error' => ['request_id']]);
    }

    public function test_draft_identity_is_not_readable_by_guessing_its_uuid(): void
    {
        $this->getJson('/api/v1/regions?release_id='.$this->id(6))->assertNotFound()->assertJsonPath('error.code', 'NOT_FOUND');
        $this->getJson('/api/v1/sources?release_id='.$this->id(6))->assertNotFound();
    }

    public function test_catalog_is_published_only_paginated_and_safe(): void
    {
        $this->publishFixture();
        $response = $this->getJson('/api/v1/releases?per_page=1');
        $response->assertOk()->assertJsonCount(1, 'data')->assertJsonPath('data.0.release_id', $this->id(6))->assertJsonPath('data.0.active', true)->assertJsonPath('meta.total', 1);
        $this->assertArrayNotHasKey('published_by', $response->json('data.0'));
        $this->assertArrayNotHasKey('source_manifest', $response->json('data.0'));
        $this->assertSame('gis_runtime', DB::selectOne('SELECT current_user AS role')->role);
        if (! is_dir(base_path('reports'))) {
            mkdir(base_path('reports'), 0770, true);
        }
        file_put_contents(base_path('reports/reference-api.json'), json_encode([
            'synthetic' => true, 'releases' => $response->json(),
            'regions' => $this->getJson('/api/v1/regions')->assertOk()->json(),
            'sources' => $this->getJson('/api/v1/sources')->assertOk()->json(),
        ], JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT));
        $this->getJson('/api/v1/releases?page=2&per_page=1')->assertOk()->assertJsonCount(0, 'data')->assertJsonPath('meta.total', 1);
    }

    public function test_region_choices_keep_the_correct_parent_and_boundary_edition(): void
    {
        DB::insert("INSERT INTO gis.regencies(id,boundary_set_id,code,name,kind,geom) SELECT ?,?,'3599','Hidden other edition','kabupaten',geom FROM gis.regencies WHERE id=?", [$this->id(40), $this->id(30), $this->id(4)]);
        $this->publishFixture();
        $this->getJson('/api/v1/regions')->assertOk()->assertJsonCount(1, 'data')->assertJsonPath('data.0.code', '3501')->assertJsonPath('data.0.edition', 'one')->assertJsonPath('meta.release_id', $this->id(6))->assertJsonPath('meta.analysis_run_id', $this->id(8));
        $this->getJson('/api/v1/regions?level=district&parent_code=3501')->assertOk()->assertJsonCount(1, 'data')->assertJsonPath('data.0.code', '3501010')->assertJsonPath('data.0.parent_code', '3501');
        $this->getJson('/api/v1/regions?level=district&parent_code=3599')->assertUnprocessable()->assertJsonPath('error.code', 'VALIDATION_FAILED');
    }

    public function test_sources_are_release_scoped_without_private_locations_or_hashes(): void
    {
        DB::update("UPDATE gis.data_sources SET private_path='private/secret-source.json'");
        DB::insert("INSERT INTO gis.data_sources(id,publisher,title,source_url,observation_period,sha256,license_note,limitations,status) VALUES(?,'Other','Not referenced','https://example.test/other','fixture',?,'fixture','private draft','pending')", [$this->id(60), str_repeat('e', 64)]);
        $this->publishFixture();
        $response = $this->getJson('/api/v1/sources')->assertOk()->assertJsonCount(1, 'data')->assertJsonPath('data.0.source_id', $this->id(2))->assertJsonPath('meta.coordinate_coverage.registered', 1)->assertJsonPath('meta.coordinate_coverage.missing', 1);
        $this->assertStringNotContainsString('private/secret', $response->getContent());
        $this->assertArrayNotHasKey('sha256', $response->json('data.0'));
        $this->assertArrayNotHasKey('private_path', $response->json('data.0'));
    }

    public function test_wrong_run_is_not_found_and_withdrawal_takes_effect_on_the_next_request(): void
    {
        $this->publishFixture();
        $this->getJson('/api/v1/regions?analysis_run_id='.$this->id(999))->assertNotFound();
        $this->getJson('/api/v1/regions')->assertOk()->assertHeader('X-Request-ID');
        DB::statement('RESET ROLE');
        DB::update("UPDATE gis.dataset_releases SET status='withdrawn'");
        $this->getJson('/api/v1/regions?release_id='.$this->id(6))->assertNotFound();
        $this->getJson('/api/v1/releases')->assertOk()->assertJsonCount(0, 'data');
    }

    public function test_public_requests_are_rate_limited_with_retry_header(): void
    {
        config(['gis.public_api_rate_limit' => 2]);
        $this->getJson('/api/v1/releases')->assertOk();
        $this->getJson('/api/v1/releases')->assertOk();
        $this->getJson('/api/v1/releases')->assertStatus(429)->assertHeader('Retry-After')->assertJsonPath('error.code', 'RATE_LIMITED');
    }
}
