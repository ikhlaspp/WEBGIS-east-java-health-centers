<?php

namespace Tests\Feature;

use App\Services\AnalysisRunService;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Symfony\Component\Process\Process;
use Tests\GisDatabaseTestCase;

class MapStatisticsApiTest extends GisDatabaseTestCase
{
    private array $ownedDirectories = [];

    protected function tearDown(): void
    {
        foreach ($this->ownedDirectories as $directory) {
            foreach (['input.json', 'results.json', 'density.geojson', 'facility_count.geojson', 'population_per_facility.geojson', 'indicative_deficit.geojson', 'manifest.json'] as $file) {
                if (is_file($directory.'/'.$file)) {
                    unlink($directory.'/'.$file);
                }
            }
            if (is_dir($directory)) {
                rmdir($directory);
            }
        }
        parent::tearDown();
    }

    private function prepareFixture(bool $secondRun = false, bool $missingPopulation = false): array
    {
        Cache::flush();
        DB::update('UPDATE app.users SET is_admin=true');
        DB::insert("INSERT INTO gis.district_indicators(release_id,boundary_set_id,district_id,population,population_year,population_source_id,population_locator,population_raw,area_km2,area_year,area_source_id,area_locator,area_raw,quality_status,notes) VALUES(?,?,?,61000,2024,?,'fixture','61000',20,2024,?,'fixture','20','complete','synthetic')", [$this->id(6), $this->id(3), $this->id(5), $this->id(2), $this->id(2)]);
        if ($missingPopulation) {
            DB::update('UPDATE gis.district_indicators SET population=NULL');
        }
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level,location) SELECT ?,?,?,('3501010'||lpad(n::text,4,'0')),'Marker '||n,'Synthetic','Non Rawat Inap','Perkotaan',?,n,'unverified','street',extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326) FROM generate_series(2,61) n", [$this->id(6), $this->id(3), $this->id(5), $this->id(2)]);
        $runs = [$this->persistRun(30000)];
        if ($secondRun) {
            $runs[] = $this->persistRun(500);
        }
        DB::insert("INSERT INTO gis.quality_reports(id,release_id,input_revision,input_hash,report_hash,policy_version,checks,exclusions,passed,approved_by,approved_at) VALUES(?,?,1,'fixture','fixture','fixture','{}','{}',true,?,now())", [$this->id(9), $this->id(6), $this->id(1)]);
        DB::update("UPDATE gis.dataset_releases SET status='published',quality_report_id=?,default_analysis_run_id=?,published_at=now(),published_by=? WHERE id=?", [$this->id(9), $runs[0], $this->id(1), $this->id(6)]);
        DB::update('UPDATE app.active_release SET release_id=?,analysis_run_id=?,version=version+1 WHERE singleton=1', [$this->id(6), $runs[0]]);

        return $runs;
    }

    private function persistRun(int $threshold): string
    {
        $run = (string) Str::uuid();
        $service = app(AnalysisRunService::class);
        $bundle = $service->prepare($this->id(6), $run, $threshold, str_repeat('c', 40));
        $relative = 'analysis/'.$run;
        $directory = storage_path('app/private/'.$relative);
        $input = storage_path('app/private/input-'.$run.'.json');
        if (! is_dir(dirname($input))) {
            mkdir(dirname($input), 0770, true);
        }
        file_put_contents($input, json_encode($bundle, JSON_THROW_ON_ERROR));
        $this->ownedDirectories[] = $directory;
        try {
            $python = PHP_OS_FAMILY === 'Windows' ? base_path('.venv/Scripts/python.exe') : 'python';
            $process = new Process([$python, base_path('scripts/analysis/export_layers.py'), '--input', $input, '--sha256', hash_file('sha256', $input), '--output-dir', $directory], base_path());
            $process->setTimeout(120);
            $process->run();
            $this->assertTrue($process->isSuccessful(), $process->getErrorOutput());
            $service->persist($bundle, $this->id(1), $relative);
        } finally {
            unlink($input);
        }

        return $run;
    }

    public function test_points_are_unpaginated_and_bbox_preserves_full_filter_counts(): void
    {
        $this->prepareFixture();
        $this->getJson('/api/v1/map/points')->assertOk()->assertJsonCount(60, 'features')->assertJsonPath('meta.filtered_registered', 61)->assertJsonPath('meta.filtered_missing', 1);
        $this->getJson('/api/v1/map/points?bbox=112,-8,113,-7')->assertOk()->assertJsonCount(60, 'features');
        $this->getJson('/api/v1/map/points?bbox=110,-8,111,-7')->assertOk()->assertJsonCount(0, 'features')->assertJsonPath('meta.filtered_registered', 61)->assertJsonPath('meta.view_count', 0);
        $this->getJson('/api/v1/map/points?coordinate_status=missing')->assertOk()->assertJsonCount(0, 'features')->assertJsonPath('meta.filtered_registered', 1);
        $this->getJson('/api/v1/map/points?q=Marker%202')->assertOk()->assertJsonCount(11, 'features');
        $this->getJson('/api/v1/map/points?regency_code=3599')->assertUnprocessable();
    }

    public function test_statistics_and_layers_use_stored_run_and_fixed_administrative_counts(): void
    {
        [$run] = $this->prepareFixture();
        $statistics = $this->getJson('/api/v1/statistics')->assertOk()->assertJsonPath('data.facility_count', 61)->assertJsonPath('data.population', 61000)->assertJsonPath('data.population_per_facility', 1000)->assertJsonPath('data.density', 3050)->assertJsonPath('data.T', 30000)->assertJsonPath('meta.analysis_run_id', $run);
        $regions = $this->getJson('/api/v1/map/regions?level=district&parent_code=3501&metric=density')->assertOk()->assertJsonCount(1, 'features')->assertJsonPath('features.0.properties.value', 3050)->assertJsonPath('features.0.properties.geometry_detail_used', 'full');
        $this->getJson('/api/v1/map/regions?metric=count')->assertOk()->assertJsonPath('features.0.properties.value', 61);
        $this->getJson('/api/v1/map/points?coordinate_status=verified')->assertOk()->assertJsonCount(0, 'features');
        $this->getJson('/api/v1/statistics')->assertOk()->assertJsonPath('data.facility_count', 61);
        $buffers = $this->getJson('/api/v1/analysis/buffers?radius_m=1000')->assertOk()->assertJsonPath('features.0.geometry', null)->assertJsonPath('features.0.properties.registered_count', 61)->assertJsonPath('features.0.properties.eligible_count', 0)->assertJsonPath('features.0.properties.coverage_pct', null);
        foreach ([3000, 5000] as $radius) {
            $this->getJson('/api/v1/analysis/buffers?radius_m='.$radius)->assertOk()->assertJsonPath('meta.radius_m', $radius);
        }
        if (! is_dir(base_path('reports'))) {
            mkdir(base_path('reports'), 0770, true);
        }
        file_put_contents(base_path('reports/map-statistics-api.json'), json_encode(['synthetic' => true, 'statistics' => $statistics->json(), 'regions' => $regions->json(), 'buffers' => $buffers->json()], JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT));
    }

    public function test_cache_separates_runs_and_checks_visibility_before_a_hit(): void
    {
        [$first, $second] = $this->prepareFixture(true);
        $this->getJson('/api/v1/statistics?analysis_run_id='.$first)->assertOk()->assertJsonPath('data.indicative_deficit', 0);
        $this->getJson('/api/v1/statistics?analysis_run_id='.$second)->assertOk()->assertJsonPath('data.indicative_deficit', 61)->assertJsonPath('data.T', 500);
        $this->getJson('/api/v1/statistics?analysis_run_id='.$first)->assertOk()->assertJsonPath('data.indicative_deficit', 0);
        $this->getJson('/api/v1/statistics?analysis_run_id='.$this->id(999))->assertNotFound();
        DB::statement('RESET ROLE');
        DB::update("UPDATE gis.dataset_releases SET status='withdrawn'");
        $this->getJson('/api/v1/statistics?analysis_run_id='.$first)->assertNotFound();
    }

    public function test_missing_population_stays_null_without_erasing_facility_counts(): void
    {
        $this->prepareFixture(missingPopulation: true);
        $this->getJson('/api/v1/statistics')->assertOk()->assertJsonPath('data.population', null)->assertJsonPath('data.population_per_facility', null)->assertJsonPath('data.facility_count', 61)->assertJsonPath('data.completeness', 'partial');
        $this->getJson('/api/v1/map/regions?metric=density')->assertOk()->assertJsonPath('features.0.properties.value', null)->assertJsonPath('features.0.properties.class', 'no_data');
        $this->getJson('/api/v1/map/regions?metric=count')->assertOk()->assertJsonPath('features.0.properties.value', 61);
    }

    public function test_unpublished_data_is_unavailable(): void
    {
        $this->getJson('/api/v1/statistics')->assertStatus(503)->assertJsonPath('error.code', 'NO_PUBLISHED_RELEASE');
        $this->getJson('/api/v1/map/points?release_id='.$this->id(6))->assertNotFound();
    }
}
