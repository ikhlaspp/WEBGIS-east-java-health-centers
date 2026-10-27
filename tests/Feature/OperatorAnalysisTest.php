<?php

namespace Tests\Feature;

use App\Services\AnalysisRunService;
use App\Services\OperatorAnalysisService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use RuntimeException;
use Tests\GisDatabaseTestCase;

class OperatorAnalysisTest extends GisDatabaseTestCase
{
    private array $runs = [];

    public function test_exact_numeric_batches_preserve_decimal_precision_and_bound_query_count(): void
    {
        $verify = new \ReflectionMethod(AnalysisRunService::class, 'verifyNumericValues');
        $service = app(AnalysisRunService::class);
        $values = array_fill(0, 2001, ['actual' => '9007199254740993.000', 'expected' => '9007199254740993']);
        $values[] = ['actual' => null, 'expected' => null];
        DB::enableQueryLog();
        DB::flushQueryLog();
        try {
            $verify->invoke($service, $values);
            $this->assertCount(3, DB::getQueryLog());
        } finally {
            DB::disableQueryLog();
            DB::flushQueryLog();
        }

        $values[2000]['actual'] = '9007199254740992.999999999999999999';
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('Thematic value differs from the recomputed database result.');
        $verify->invoke($service, $values);
    }

    public function test_exact_numeric_batches_reject_null_in_place_of_zero(): void
    {
        $verify = new \ReflectionMethod(AnalysisRunService::class, 'verifyNumericValues');
        $this->expectException(RuntimeException::class);
        $verify->invoke(app(AnalysisRunService::class), [['actual' => null, 'expected' => '0']]);
    }

    private function fixture(): string
    {
        DB::update('UPDATE app.users SET is_admin=true');
        DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,'[\"analyze\"]',now()+interval '1 hour')", [$this->id(70), $this->id(1), hash('sha256', str_repeat('A', 43))]);

        return $this->newRun();
    }

    private function newRun(): string
    {
        $run = (string) Str::uuid();
        $this->runs[] = $run;

        return $run;
    }

    protected function tearDown(): void
    {
        foreach ($this->runs as $run) {
            $directory = storage_path('app/private/analysis/'.$run);
            foreach (['results.json', 'density.geojson', 'facility_count.geojson', 'population_per_facility.geojson', 'indicative_deficit.geojson', 'manifest.json'] as $file) {
                if (is_file($directory.'/'.$file)) {
                    unlink($directory.'/'.$file);
                }
            }
            if (is_dir($directory)) {
                rmdir($directory);
            }
            $input = storage_path('app/private/analysis-input-'.$run.'.json');
            if (is_file($input)) {
                unlink($input);
            }
        }
        parent::tearDown();
    }

    private function runAnalysis(string $run): array
    {
        return app(OperatorAnalysisService::class)->run(str_repeat('A', 43), $this->id(6), $run, 30000, str_repeat('c', 40));
    }

    public function test_operator_runs_real_python_and_persists_recomputed_results_with_audit_and_retry(): void
    {
        $run = $this->fixture();
        $result = $this->runAnalysis($run);
        $this->assertSame($run, $result['analysis_run_id']);
        $this->assertFalse($result['replayed']);
        $this->assertTrue($this->runAnalysis($run)['replayed']);
        $other = $this->runAnalysis($this->newRun());
        $this->assertTrue($other['replayed']);
        $this->assertSame($run, $other['analysis_run_id']);
        DB::statement('RESET ROLE');
        $this->assertSame(1, DB::table('gis.analysis_runs')->count());
        $this->assertSame(1, DB::table('gis.indicator_results')->value('facility_count'));
        $this->assertSame(3, DB::table('gis.coverage_results')->count());
        $this->assertNull(DB::table('gis.coverage_results')->value('coverage_pct'));
        $this->assertSame(5, DB::table('gis.artifacts')->count());
        $this->assertSame(0, DB::table('gis.artifacts')->where('sanitized', true)->count());
        $audit = DB::table('app.audit_logs')->where('action', 'analysis.completed')->sole();
        $this->assertSame($this->id(1), $audit->actor_id);
        $this->assertSame($this->id(70), $audit->token_id);
        $this->assertStringNotContainsString(str_repeat('A', 43), json_encode($audit));
        $this->assertSame('draft', DB::table('gis.dataset_releases')->value('status'));
    }

    public function test_invalid_or_wrong_ability_tokens_cannot_start_an_export(): void
    {
        $run = $this->fixture();
        DB::update("UPDATE app.operator_tokens SET abilities='[\"review\"]'");
        try {
            $this->runAnalysis($run);
            $this->fail('Wrong capability accepted.');
        } catch (QueryException $exception) {
            $this->assertSame('28000', (string) $exception->getCode());
        }
        $this->assertDirectoryDoesNotExist(storage_path('app/private/analysis/'.$run));
        $this->assertSame(0, DB::table('gis.analysis_runs')->count());
    }

    public function test_evidenced_point_produces_monotonic_stored_coverage(): void
    {
        $run = $this->fixture();
        DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason,reviewed_by,reviewed_at) VALUES(?,?,'35010100001',?,extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),'fixture','synthetic','facility','accepted','https://example.test/evidence','synthetic','fixture evidence',?,now())", [$this->id(7), $this->id(6), $this->id(2), $this->id(1)]);
        DB::update("UPDATE gis.facility_snapshots SET coordinate_status='verified',precision_level='facility',location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),coordinate_source_id=?,selected_review_id=?", [$this->id(2), $this->id(7)]);
        $this->runAnalysis($run);
        $rows = DB::table('gis.coverage_results')->orderBy('radius_m')->get();
        $previous = 0;
        foreach ($rows as $row) {
            $this->assertSame(1, $row->eligible_count);
            $this->assertGreaterThan($previous, (float) $row->covered_area_m2);
            $this->assertGreaterThan(0, (float) $row->coverage_pct);
            $this->assertLessThanOrEqual(100, (float) $row->coverage_pct);
            $this->assertNotNull($row->geom);
            $previous = (float) $row->covered_area_m2;
        }
    }

    public function test_export_failure_leaves_no_successful_run_or_audit(): void
    {
        $run = $this->fixture();
        config(['gis.python_binary' => '/missing/python-executable']);
        try {
            $this->runAnalysis($run);
            $this->fail('Missing Python executable accepted.');
        } catch (RuntimeException) {
            $this->addToAssertionCount(1);
        }
        DB::statement('RESET ROLE');
        $this->assertSame(0, DB::table('gis.analysis_runs')->count());
        $this->assertSame(0, DB::table('app.audit_logs')->count());
        $this->assertFileDoesNotExist(storage_path('app/private/analysis-input-'.$run.'.json'));
    }

    public function test_tampered_files_are_rejected_on_retry(): void
    {
        $run = $this->fixture();
        $this->runAnalysis($run);
        file_put_contents(storage_path('app/private/analysis/'.$run.'/density.geojson'), '{}');
        $this->expectException(RuntimeException::class);
        $this->runAnalysis($run);
    }

    public function test_database_recomputes_values_instead_of_trusting_submitted_results(): void
    {
        $run = $this->fixture();
        $this->runAnalysis($run);
        $original = json_decode(file_get_contents(storage_path('app/private/analysis/'.$run.'/manifest.json')), true, 512, JSON_THROW_ON_ERROR);
        $next = $this->newRun();
        $bundle = app(AnalysisRunService::class)->prepare($this->id(6), $next, 1, str_repeat('d', 40));
        $bundle['indicators'][0]['facility_count'] = 999999;
        $bundle['coverage'][0]['covered_area_m2'] = 999999;
        $manifest = $original;
        foreach (['release_id', 'analysis_run_id', 'boundary_set_id', 'input_revision', 'input_hash', 'boundary_hash', 'method_version', 'code_revision', 'parameters'] as $field) {
            $manifest[$field] = $bundle[$field];
        }
        foreach ($manifest['artifacts'] as $index => $artifact) {
            $manifest['artifacts'][$index]['sha256'] = hash('sha256', 'unverified-submitted-artifact:'.$next.':'.$artifact['kind']);
        }
        $result = DB::selectOne('SELECT gis.persist_operator_analysis(?,?::jsonb,?::jsonb) AS result', [str_repeat('A', 43), json_encode($bundle, JSON_THROW_ON_ERROR), json_encode($manifest, JSON_THROW_ON_ERROR)]);
        $this->assertSame('succeeded', json_decode($result->result, true)['status']);
        DB::statement('RESET ROLE');
        $this->assertSame(1, DB::table('gis.indicator_results')->where('run_id', $next)->value('facility_count'));
        $this->assertNull(DB::table('gis.coverage_results')->where('run_id', $next)->value('covered_area_m2'));
        $this->assertSame(0, DB::table('gis.artifacts')->where('analysis_run_id', $next)->where('sanitized', true)->count());
    }

    public function test_runtime_and_publisher_cannot_execute_persistence(): void
    {
        $this->fixture();
        foreach (['gis_runtime', 'gis_publisher'] as $role) {
            try {
                DB::transaction(function () use ($role): void {
                    DB::statement('SET LOCAL ROLE '.$role);
                    DB::selectOne("SELECT gis.persist_operator_analysis(?,'{}','{}')", [str_repeat('A', 43)]);
                });
                $this->fail('Forbidden role executed persistence.');
            } catch (QueryException $exception) {
                $this->assertSame('42501', (string) $exception->getCode());
            }
        }
    }

    public function test_stale_revision_is_rejected_by_the_database_function(): void
    {
        $run = $this->fixture();
        $this->runAnalysis($run);
        $bundle = app(AnalysisRunService::class)->prepare($this->id(6), $run, 30000, str_repeat('c', 40));
        $manifest = json_decode(file_get_contents(storage_path('app/private/analysis/'.$run.'/manifest.json')), true, 512, JSON_THROW_ON_ERROR);
        DB::statement('RESET ROLE');
        DB::update("UPDATE gis.facility_snapshots SET address='Changed after export'");
        DB::statement('SET LOCAL ROLE gis_worker');
        try {
            DB::transaction(fn () => DB::selectOne('SELECT gis.persist_operator_analysis(?,?::jsonb,?::jsonb)', [str_repeat('A', 43), json_encode($bundle), json_encode($manifest)]));
            $this->fail('Stale analysis accepted.');
        } catch (QueryException $exception) {
            $this->assertSame('P4090', (string) $exception->getCode());
        }
    }

    public function test_failure_during_persistence_rolls_back_all_results_and_audit(): void
    {
        $run = $this->fixture();
        DB::unprepared("CREATE FUNCTION gis.fail_operator_coverage() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.radius_m=3000 THEN RAISE EXCEPTION 'synthetic failure'; END IF; RETURN NEW; END $$; CREATE TRIGGER fail_operator_coverage BEFORE INSERT ON gis.coverage_results FOR EACH ROW EXECUTE FUNCTION gis.fail_operator_coverage()");
        try {
            $this->runAnalysis($run);
            $this->fail('Injected failure did not abort analysis.');
        } catch (QueryException) {
            DB::statement('RESET ROLE');
            $this->assertSame(0, DB::table('gis.analysis_runs')->count());
            $this->assertSame(0, DB::table('gis.indicator_results')->count());
            $this->assertSame(0, DB::table('gis.coverage_results')->count());
            $this->assertSame(0, DB::table('app.audit_logs')->count());
        }
    }
}
