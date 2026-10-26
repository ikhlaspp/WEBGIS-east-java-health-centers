<?php

namespace Tests\Feature;

use App\Services\OperatorAnalysisService;
use App\Services\ReleaseContext;
use App\Services\ReleaseLifecycleService;
use App\Services\ReleaseValidationService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use InvalidArgumentException;
use PHPUnit\Framework\Attributes\DataProvider;
use RuntimeException;
use Symfony\Component\Process\Process;
use Tests\GisDatabaseTestCase;

class ReleaseRollbackTest extends GisDatabaseTestCase
{
    private array $runs = [];

    private function candidate(int $number): void
    {
        DB::statement('RESET ROLE');
        if ($number === 6) {
            DB::update('UPDATE app.users SET is_admin=true');
            DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,'[\"analyze\",\"validate\",\"publish\",\"rollback\"]',now()+interval '1 hour')", [$this->id(70), $this->id(1), hash('sha256', str_repeat('A', 43))]);
            DB::update("UPDATE gis.dataset_releases SET method_version='postgis-analysis-v1',code_revision=? WHERE id=?", [str_repeat('c', 40), $this->id(6)]);
        } else {
            DB::insert('INSERT INTO gis.dataset_releases(id,label,boundary_set_id,facility_period,population_policy,area_policy,method_version,code_revision) SELECT ?,?,boundary_set_id,facility_period,population_policy,area_policy,method_version,code_revision FROM gis.dataset_releases WHERE id=?', [$this->id($number), 'Fixture '.$number, $this->id(6)]);
            DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level) SELECT ?,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,'missing','unknown' FROM gis.facility_snapshots WHERE release_id=?", [$this->id($number), $this->id(6)]);
        }
        DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason,reviewed_by,reviewed_at) VALUES(?,?,'35010100001',?,extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),'fixture','synthetic','facility','accepted','https://example.test/evidence','synthetic','fixture evidence',?,now())", [$this->id(100 + $number), $this->id($number), $this->id(2), $this->id(1)]);
        DB::update("UPDATE gis.facility_snapshots SET coordinate_status='verified',precision_level='facility',location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),coordinate_source_id=?,selected_review_id=? WHERE release_id=?", [$this->id(2), $this->id(100 + $number), $this->id($number)]);
        $this->runs[$number] = (string) Str::uuid();
        app(OperatorAnalysisService::class)->run(str_repeat('A', 43), $this->id($number), $this->runs[$number], 30000, str_repeat('c', 40));
        $revision = (int) DB::table('gis.dataset_releases')->where('id', $this->id($number))->value('input_revision');
        app(ReleaseValidationService::class)->validate(str_repeat('A', 43), $this->id($number), $this->runs[$number], $revision, 'Synthetic rollback fixture scope acceptance', true);
        DB::statement('RESET ROLE');
    }

    private function versions(): void
    {
        $this->candidate(6);
        app(ReleaseLifecycleService::class)->publish(str_repeat('A', 43), $this->id(6), 0, (string) Str::uuid(), 'First synthetic version');
        $this->candidate(8);
        app(ReleaseLifecycleService::class)->publish(str_repeat('A', 43), $this->id(8), 1, (string) Str::uuid(), 'Second synthetic version');
        DB::statement('RESET ROLE');
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
        }
        parent::tearDown();
    }

    public function test_rollback_switches_pointer_once_and_preserves_both_release_histories(): void
    {
        $this->versions();
        $history = DB::select('SELECT to_jsonb(r)::text AS row FROM gis.dataset_releases r ORDER BY id');
        $operation = (string) Str::uuid();
        $service = app(ReleaseLifecycleService::class);
        $result = $service->rollback(str_repeat('A', 43), $this->id(6), 2, $operation, 'Restore first synthetic version');
        $this->assertSame(3, $result['active_version']);
        $this->assertTrue($service->rollback(str_repeat('A', 43), $this->id(6), 2, $operation, 'Restore first synthetic version')['replayed']);
        DB::statement('RESET ROLE');
        $this->assertEquals($history, DB::select('SELECT to_jsonb(r)::text AS row FROM gis.dataset_releases r ORDER BY id'));
        $this->assertSame(1, DB::table('app.audit_logs')->where('action', 'release.rolled_back')->count());
        $this->assertSame(1, DB::table('app.outbox_events')->where('event_type', 'release.rolled_back')->count());
        $audit = DB::table('app.audit_logs')->where('action', 'release.rolled_back')->sole();
        $this->assertSame($this->id(8), json_decode($audit->before_json, true)['release_id']);
        $this->assertStringNotContainsString(str_repeat('A', 43), json_encode($audit));
        DB::statement('SET LOCAL ROLE gis_runtime');
        $this->assertSame($this->id(6), app(ReleaseContext::class)->resolve(null, null)['release']->id);
        $this->assertSame($this->runs[8], app(ReleaseContext::class)->resolve($this->id(8), null)['run']->id);
    }

    public static function failures(): array
    {
        return array_map(fn ($case) => [$case], ['withdrawn', 'tampered', 'wrong_ability', 'stale_version', 'outbox_failure', 'already_active']);
    }

    #[DataProvider('failures')]
    public function test_invalid_rollback_preserves_current_pointer(string $case): void
    {
        $this->versions();
        if ($case === 'withdrawn') {
            DB::update("UPDATE gis.dataset_releases SET status='withdrawn' WHERE id=?", [$this->id(6)]);
        } elseif ($case === 'tampered') {
            file_put_contents(storage_path('app/private/analysis/'.$this->runs[6].'/density.geojson'), '{}');
        } elseif ($case === 'wrong_ability') {
            DB::update("UPDATE app.operator_tokens SET abilities='[\"publish\"]'");
        } elseif ($case === 'outbox_failure') {
            DB::unprepared("CREATE FUNCTION app.fail_rollback_outbox() RETURNS trigger LANGUAGE plpgsql AS \$\$ BEGIN RAISE EXCEPTION 'Injected rollback outbox failure'; END \$\$; CREATE TRIGGER fail_rollback_outbox BEFORE INSERT ON app.outbox_events FOR EACH ROW EXECUTE FUNCTION app.fail_rollback_outbox()");
        }
        try {
            app(ReleaseLifecycleService::class)->rollback(str_repeat('A', 43), $this->id($case === 'already_active' ? 8 : 6), $case === 'stale_version' ? 1 : 2, (string) Str::uuid(), 'Synthetic rejected rollback');
            $this->fail('Invalid rollback succeeded.');
        } catch (QueryException|RuntimeException|InvalidArgumentException) {
            $this->addToAssertionCount(1);
        }
        DB::statement('RESET ROLE');
        $this->assertSame($this->id(8), DB::table('app.active_release')->value('release_id'));
        $this->assertSame(2, DB::table('app.active_release')->value('version'));
        $this->assertSame(0, DB::table('app.audit_logs')->where('action', 'release.rolled_back')->count());
        $this->assertSame(0, DB::table('app.outbox_events')->where('event_type', 'release.rolled_back')->count());
    }

    public function test_roles_cannot_directly_rollback_without_file_verification(): void
    {
        $this->versions();
        foreach (['gis_runtime', 'gis_worker', 'gis_publisher'] as $role) {
            try {
                DB::transaction(function () use ($role): void {
                    DB::statement('SET LOCAL ROLE '.$role);
                    DB::selectOne("SELECT gis.rollback_release(?,?::uuid,2,?::uuid,'Forged rollback','{}')", [str_repeat('A', 43), $this->id(6), (string) Str::uuid()]);
                });
                $this->fail('Untrusted role rolled back.');
            } catch (QueryException $exception) {
                $this->assertSame('42501', (string) $exception->getCode());
            }
        }
    }

    public static function raceWinners(): array
    {
        return [['publish'], ['rollback']];
    }

    #[DataProvider('raceWinners')]
    public function test_publish_and_rollback_compete_for_the_same_pointer_version(string $winner): void
    {
        $this->versions();
        $this->candidate(9);
        $this->assertSame('gis_schema_testing', DB::selectOne('SELECT current_database() AS name')->name);
        DB::commit();
        $process = null;
        try {
            $firstNumber = $winner === 'publish' ? 9 : 6;
            $secondNumber = $winner === 'publish' ? 6 : 9;
            $manifest = fn ($number) => json_decode(file_get_contents(storage_path('app/private/analysis/'.$this->runs[$number].'/manifest.json')), true, 512, JSON_THROW_ON_ERROR);
            DB::beginTransaction();
            DB::statement('SET LOCAL ROLE gis_artifact_verifier');
            $function = $winner === 'publish' ? 'gis.publish_release' : 'gis.rollback_release';
            DB::selectOne('SELECT '.$function.'(?,?::uuid,2,?::uuid,?,?::jsonb)', [str_repeat('A', 43), $this->id($firstNumber), (string) Str::uuid(), 'First mixed lifecycle operation', json_encode($manifest($firstNumber), JSON_THROW_ON_ERROR)]);
            $config = config('database.connections.schema_testing');
            $process = new Process([PHP_BINARY, base_path('tests/ci/publication_contender.php')], base_path(), ['RACE_HOST' => $config['host'], 'RACE_PORT' => (string) $config['port'], 'RACE_USER' => $config['username'], 'RACE_PASSWORD' => $config['password']]);
            $process->setInput(json_encode(['release' => $this->id($secondNumber), 'operation' => (string) Str::uuid(), 'manifest' => $manifest($secondNumber), 'action' => $winner === 'publish' ? 'rollback' : 'publish', 'version' => 2], JSON_THROW_ON_ERROR));
            $process->setTimeout(20);
            $process->start();
            DB::statement('RESET ROLE');
            $blocked = false;
            for ($attempt = 0; $attempt < 100 && $process->isRunning(); $attempt++) {
                if (preg_match('/PID:(\d+)/', $process->getOutput(), $match)) {
                    DB::selectOne('SELECT pg_stat_clear_snapshot()');
                    $blocked = DB::selectOne("SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE pid=? AND wait_event_type='Lock') AS blocked", [(int) $match[1]])->blocked;
                    if ($blocked) {
                        break;
                    }
                }
                usleep(50000);
            }
            $this->assertTrue($blocked);
            DB::commit();
            $process->wait();
            $this->assertSame(0, $process->getExitCode(), $process->getErrorOutput());
            $this->assertStringContainsString('SQLSTATE:P4090', $process->getOutput());
            $this->assertSame($this->id($firstNumber), DB::table('app.active_release')->value('release_id'));
            $this->assertSame(3, DB::table('app.active_release')->value('version'));
            $this->assertSame(3, DB::table('app.outbox_events')->count());
            $this->assertSame('published', DB::table('gis.dataset_releases')->where('id', $this->id(8))->value('status'));
        } finally {
            if (DB::transactionLevel() > 0) {
                DB::rollBack();
            }
            if ($process?->isRunning()) {
                $process->stop();
            }
            DB::statement('RESET ROLE');
            $this->assertSame('gis_schema_testing', DB::selectOne('SELECT current_database() AS name')->name);
            $tables = DB::select("SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('app','gis','staging')");
            $names = array_map(fn ($row) => '"'.str_replace('"', '""', $row->schemaname).'"."'.str_replace('"', '""', $row->tablename).'"', $tables);
            DB::statement('TRUNCATE TABLE '.implode(',', $names).' RESTART IDENTITY');
            DB::insert('INSERT INTO app.active_release(singleton) VALUES(1)');
        }
    }
}
