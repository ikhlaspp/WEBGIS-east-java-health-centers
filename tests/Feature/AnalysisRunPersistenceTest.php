<?php

namespace Tests\Feature;

use App\Services\AnalysisRunService;
use App\Services\BufferService;
use App\Services\CoverageService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use RuntimeException;
use Symfony\Component\Process\Process;
use Tests\GisDatabaseTestCase;

class AnalysisRunPersistenceTest extends GisDatabaseTestCase
{
    private array $ownedFiles = [];

    private array $ownedDirectories = [];

    private string $runId;

    protected function setUp(): void
    {
        parent::setUp();
        $this->runId = (string) Str::uuid();
        DB::update('UPDATE app.users SET is_admin=true WHERE id=?', [$this->id(1)]);
    }

    protected function tearDown(): void
    {
        foreach ($this->ownedFiles as $path) {
            if (is_file($path)) {
                unlink($path);
            }
        }
        foreach ($this->ownedDirectories as $directory) {
            foreach (['results.json', 'density.geojson', 'facility_count.geojson', 'population_per_facility.geojson', 'indicative_deficit.geojson', 'manifest.json'] as $file) {
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

    public function test_real_python_export_persists_complete_results_and_replays_without_duplicates(): void
    {
        $service = $this->service();
        $bundle = $service->prepare($this->id(6), $this->runId, 30000, str_repeat('c', 40));
        $directory = $this->export($bundle);
        $result = $service->persist($bundle, $this->id(1), $directory);
        $this->assertSame('succeeded', $result['status']);
        $this->assertSame(1, DB::table('gis.indicator_results')->count());
        $this->assertSame(3, DB::table('gis.coverage_results')->count());
        $this->assertSame(5, DB::table('gis.artifacts')->count());
        $this->assertTrue($service->persist($bundle, $this->id(1), $directory)['replayed']);
        $this->assertSame(1, DB::table('gis.analysis_runs')->count());
        $this->assertSame('draft', DB::table('gis.dataset_releases')->value('status'));
        $this->assertNull(DB::table('gis.coverage_results')->value('coverage_pct'));
    }

    public function test_tampered_artifact_never_creates_a_successful_run(): void
    {
        $service = $this->service();
        $bundle = $service->prepare($this->id(6), $this->runId, 30000, str_repeat('c', 40));
        $directory = $this->export($bundle);
        file_put_contents(storage_path('app/private/'.$directory.'/density.geojson'), ' ', FILE_APPEND);
        try {
            $service->persist($bundle, $this->id(1), $directory);
            $this->fail('Tampered artifact was accepted.');
        } catch (RuntimeException $exception) {
            $this->assertStringContainsString('digest', $exception->getMessage());
        }
        $this->assertSame(0, DB::table('gis.analysis_runs')->count());
        $this->assertSame(0, DB::table('gis.indicator_results')->count());
    }

    public function test_stale_prepared_input_is_rejected_before_persistence(): void
    {
        $service = $this->service();
        $bundle = $service->prepare($this->id(6), $this->runId, 30000, str_repeat('c', 40));
        DB::update("UPDATE gis.facility_snapshots SET name='Changed source input'");
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('input changed');
        $service->persist($bundle, $this->id(1), 'analysis/'.$this->runId);
    }

    public function test_restricted_worker_cannot_invoke_trusted_persistence_directly(): void
    {
        $service = $this->service();
        $bundle = $service->prepare($this->id(6), $this->runId, 30000, str_repeat('c', 40));
        DB::statement('SET LOCAL ROLE gis_worker');
        try {
            $service->persist($bundle, $this->id(1), 'analysis/'.$this->runId);
            $this->fail('Worker was granted direct persistence.');
        } catch (QueryException $exception) {
            $this->assertSame('42501', (string) $exception->getCode());
        }
    }

    public function test_finished_results_cannot_be_rewritten(): void
    {
        $service = $this->service();
        $bundle = $service->prepare($this->id(6), $this->runId, 30000, str_repeat('c', 40));
        $directory = $this->export($bundle);
        $service->persist($bundle, $this->id(1), $directory);
        try {
            DB::update("UPDATE gis.indicator_results SET reason='rewrite'");
            $this->fail('Finished results were mutable.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', (string) $exception->getCode());
        }
    }

    public function test_database_failure_midway_rolls_back_every_result_and_run(): void
    {
        $service = $this->service();
        $bundle = $service->prepare($this->id(6), $this->runId, 30000, str_repeat('c', 40));
        $directory = $this->export($bundle);
        DB::unprepared("CREATE FUNCTION pg_temp.reject_fixture_radius() RETURNS trigger LANGUAGE plpgsql AS \$\$ BEGIN IF NEW.radius_m=3000 THEN RAISE EXCEPTION 'Synthetic middle failure' USING ERRCODE='23514'; END IF; RETURN NEW; END \$\$; CREATE TRIGGER fixture_middle_failure BEFORE INSERT ON gis.coverage_results FOR EACH ROW EXECUTE FUNCTION pg_temp.reject_fixture_radius()");
        try {
            $service->persist($bundle, $this->id(1), $directory);
            $this->fail('Synthetic database failure was ignored.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', (string) $exception->getCode());
        }
        $this->assertSame(0, DB::table('gis.analysis_runs')->count());
        $this->assertSame(0, DB::table('gis.indicator_results')->count());
        $this->assertSame(0, DB::table('gis.coverage_results')->count());
        $this->assertSame(0, DB::table('gis.artifacts')->count());
    }

    public function test_incomplete_run_cannot_be_marked_successful(): void
    {
        $revision = DB::table('gis.dataset_releases')->value('input_revision');
        DB::insert("INSERT INTO gis.analysis_runs(id,release_id,method_version,code_revision,input_hash,parameters_hash,input_revision,parameters,status,idempotency_key,started_by) VALUES(?,?,'fixture','fixture','fixture','fixture',?,'{}','running',?,?)", [$this->runId, $this->id(6), $revision, str_repeat('d', 64), $this->id(1)]);
        try {
            DB::update("UPDATE gis.analysis_runs SET status='succeeded',finished_at=now(),output_manifest=?::jsonb WHERE id=?", [json_encode(['validation_status' => 'passed', 'input_hash' => 'fixture', 'analysis_run_id' => $this->runId], JSON_THROW_ON_ERROR), $this->runId]);
            $this->fail('Incomplete run was accepted.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', (string) $exception->getCode());
        }
    }

    private function service(): AnalysisRunService
    {
        return new AnalysisRunService(new CoverageService(new BufferService));
    }

    private function export(array $bundle): string
    {
        $directory = 'analysis/'.$this->runId;
        $absolute = storage_path('app/private/'.$directory);
        $this->assertDirectoryDoesNotExist($absolute);
        $this->ownedDirectories[] = $absolute;
        $input = storage_path('app/private/analysis-input-'.$this->runId.'.json');
        if (! is_dir(dirname($input))) {
            mkdir(dirname($input), 0770, true);
        }
        $this->ownedFiles[] = $input;
        file_put_contents($input, json_encode($bundle, JSON_THROW_ON_ERROR));
        $python = PHP_OS_FAMILY === 'Windows' ? base_path('.venv/Scripts/python.exe') : 'python';
        $process = new Process([$python, base_path('scripts/analysis/export_layers.py'), '--input', $input, '--sha256', hash_file('sha256', $input), '--output-dir', $absolute], base_path());
        $process->setTimeout(120);
        $process->run();
        $this->assertTrue($process->isSuccessful(), $process->getErrorOutput());

        return $directory;
    }
}
