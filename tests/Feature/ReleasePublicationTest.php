<?php

namespace Tests\Feature;

use App\Services\LocationReviewService;
use App\Services\OperatorAnalysisService;
use App\Services\ReleaseContext;
use App\Services\ReleaseLifecycleService;
use App\Services\ReleaseValidationService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use PHPUnit\Framework\Attributes\DataProvider;
use RuntimeException;
use Symfony\Component\Process\Process;
use Tests\GisDatabaseTestCase;

class ReleasePublicationTest extends GisDatabaseTestCase
{
    private ?string $run = null;

    private function candidate(): void
    {
        DB::update('UPDATE app.users SET is_admin=true');
        DB::update("UPDATE gis.dataset_releases SET method_version='postgis-analysis-v1',code_revision=? WHERE id=?", [str_repeat('c', 40), $this->id(6)]);
        DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,'[\"review\",\"analyze\",\"validate\",\"publish\"]',now()+interval '1 hour')", [$this->id(70), $this->id(1), hash('sha256', str_repeat('A', 43))]);
        DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason) VALUES(?,?,'35010100001',?,extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),'fixture','synthetic','facility','pending','https://example.test/evidence','synthetic','')", [$this->id(7), $this->id(6), $this->id(2)]);
        app(LocationReviewService::class)->decide(str_repeat('A', 43), ['release_id' => $this->id(6), 'facility_code' => '35010100001', 'review_id' => $this->id(7), 'decision' => 'accepted', 'reason' => 'Synthetic facility evidence reviewed', 'expected_revision' => (int) DB::table('gis.dataset_releases')->value('input_revision'), 'operation_id' => (string) Str::uuid(), 'confirmed_facility_point' => true]);
        $this->run = (string) Str::uuid();
        app(OperatorAnalysisService::class)->run(str_repeat('A', 43), $this->id(6), $this->run, 30000, str_repeat('c', 40));
        $revision = (int) DB::table('gis.dataset_releases')->value('input_revision');
        app(ReleaseValidationService::class)->validate(str_repeat('A', 43), $this->id(6), $this->run, $revision, 'Synthetic partial scope for publication tests', true);
        DB::statement('RESET ROLE');
    }

    protected function tearDown(): void
    {
        if ($this->run !== null) {
            $directory = storage_path('app/private/analysis/'.$this->run);
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

    private function publish(?string $operation = null, int $version = 0): array
    {
        return app(ReleaseLifecycleService::class)->publish(str_repeat('A', 43), $this->id(6), $version, $operation ?? (string) Str::uuid(), 'Synthetic publication test');
    }

    public function test_publication_commits_pointer_status_audit_outbox_and_exact_retry_once(): void
    {
        $this->candidate();
        $operation = (string) Str::uuid();
        $result = $this->publish($operation);
        $this->assertSame(1, $result['active_version']);
        $this->assertFalse($result['replayed']);
        $this->assertTrue($this->publish($operation)['replayed']);
        DB::statement('RESET ROLE');
        $this->assertSame('published', DB::table('gis.dataset_releases')->value('status'));
        $this->assertSame($this->id(1), DB::table('gis.dataset_releases')->value('published_by'));
        $this->assertSame($this->run, DB::table('app.active_release')->value('analysis_run_id'));
        $this->assertSame(1, DB::table('app.outbox_events')->count());
        $audit = DB::table('app.audit_logs')->where('action', 'release.published')->sole();
        $this->assertSame($this->id(70), $audit->token_id);
        $this->assertStringNotContainsString(str_repeat('A', 43), json_encode($audit));
        DB::statement('SET LOCAL ROLE gis_runtime');
        $context = app(ReleaseContext::class)->resolve(null, null);
        $this->assertSame($this->id(6), $context['release']->id);
        $this->assertSame($this->run, $context['run']->id);
    }

    public static function rejectionCases(): array
    {
        return array_map(fn ($case) => [$case], ['tampered_file', 'wrong_ability', 'stale_pointer', 'outbox_failure', 'missing_acceptance', 'missing_backup', 'expired_backup']);
    }

    #[DataProvider('rejectionCases')]
    public function test_failures_do_not_partially_publish(string $case): void
    {
        $this->candidate();
        if (in_array($case, ['missing_backup', 'expired_backup'], true)) {
            DB::statement('TRUNCATE TABLE app.backup_checkpoints');
            if ($case === 'expired_backup') {
                DB::insert("INSERT INTO app.backup_checkpoints(id,database_name,instance_id,completed_at,manifest_sha256,inventory,verified_by) SELECT ?,current_database(),instance_id,clock_timestamp()-interval '25 hours',?,'[{},{}]',? FROM app.backup_environment WHERE singleton", [$this->id(90), str_repeat('b', 64), $this->id(1)]);
            }
        }
        if ($case === 'tampered_file') {
            file_put_contents(storage_path('app/private/analysis/'.$this->run.'/density.geojson'), '{}');
        } elseif ($case === 'wrong_ability') {
            DB::update("UPDATE app.operator_tokens SET abilities='[\"validate\"]'");
        } elseif ($case === 'missing_acceptance') {
            DB::update('UPDATE gis.dataset_releases SET quality_report_id=NULL');
        } elseif ($case === 'outbox_failure') {
            DB::unprepared("CREATE FUNCTION app.fail_publish_outbox() RETURNS trigger LANGUAGE plpgsql AS \$\$ BEGIN RAISE EXCEPTION 'Injected outbox failure'; END \$\$; CREATE TRIGGER fail_publish_outbox BEFORE INSERT ON app.outbox_events FOR EACH ROW EXECUTE FUNCTION app.fail_publish_outbox()");
        }
        try {
            $this->publish(version: $case === 'stale_pointer' ? 1 : 0);
            $this->fail('Invalid publication succeeded.');
        } catch (QueryException|RuntimeException) {
            $this->addToAssertionCount(1);
        }
        DB::statement('RESET ROLE');
        $this->assertSame('validated', DB::table('gis.dataset_releases')->value('status'));
        $this->assertSame(0, DB::table('app.active_release')->value('version'));
        $this->assertNull(DB::table('app.active_release')->value('release_id'));
        $this->assertSame(0, DB::table('app.audit_logs')->where('action', 'release.published')->count());
        $this->assertSame(0, DB::table('app.outbox_events')->count());
    }

    public function test_conflicting_retry_and_second_publication_are_rejected(): void
    {
        $this->candidate();
        $operation = (string) Str::uuid();
        $this->publish($operation);
        foreach ([[$operation, 1, '23505'], [(string) Str::uuid(), 1, '23514']] as [$id, $version, $state]) {
            try {
                $this->publish($id, $version);
                $this->fail('Conflicting publication accepted.');
            } catch (QueryException $exception) {
                $this->assertSame($state, (string) $exception->getCode());
            }
        }
        DB::statement('RESET ROLE');
        $this->assertSame(1, DB::table('app.active_release')->value('version'));
    }

    public function test_public_roles_cannot_bypass_file_attestation(): void
    {
        $this->candidate();
        foreach (['gis_runtime', 'gis_worker', 'gis_publisher'] as $role) {
            try {
                DB::transaction(function () use ($role): void {
                    DB::statement('SET LOCAL ROLE '.$role);
                    DB::selectOne("SELECT gis.publish_release(?,?::uuid,0,?::uuid,'Forged publication','{}')", [str_repeat('A', 43), $this->id(6), (string) Str::uuid()]);
                });
                $this->fail('Untrusted role published.');
            } catch (QueryException $exception) {
                $this->assertSame('42501', (string) $exception->getCode());
            }
        }
    }

    public function test_two_connections_compete_for_one_pointer_version(): void
    {
        $this->candidate();
        $this->assertSame('gis_schema_testing', DB::selectOne('SELECT current_database() AS name')->name);
        $manifest = file_get_contents(storage_path('app/private/analysis/'.$this->run.'/manifest.json'));
        DB::commit();
        $process = null;
        try {
            DB::beginTransaction();
            DB::statement('SET LOCAL ROLE gis_artifact_verifier');
            $first = DB::selectOne('SELECT gis.publish_release(?,?::uuid,0,?::uuid,?,?::jsonb) AS result', [str_repeat('A', 43), $this->id(6), (string) Str::uuid(), 'First competing publication', $manifest]);
            $config = config('database.connections.schema_testing');
            $process = new Process([PHP_BINARY, base_path('tests/ci/publication_contender.php')], base_path(), ['RACE_HOST' => $config['host'], 'RACE_PORT' => (string) $config['port'], 'RACE_USER' => $config['username'], 'RACE_PASSWORD' => $config['password']]);
            $process->setInput(json_encode(['release' => $this->id(6), 'operation' => (string) Str::uuid(), 'manifest' => json_decode($manifest, true)], JSON_THROW_ON_ERROR));
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
            $this->assertTrue($blocked, 'Second connection must wait on the uncommitted pointer lock.');
            DB::commit();
            $process->wait();
            $this->assertSame(0, $process->getExitCode(), $process->getErrorOutput());
            $this->assertStringContainsString('SQLSTATE:P4090', $process->getOutput());
            $this->assertSame(1, json_decode($first->result, true)['active_version']);
            $this->assertSame(1, DB::table('app.active_release')->value('version'));
            $this->assertSame(1, DB::table('app.audit_logs')->where('action', 'release.published')->count());
            $this->assertSame(1, DB::table('app.outbox_events')->count());
        } finally {
            if (DB::transactionLevel() > 0) {
                DB::rollBack();
            }
            if ($process?->isRunning()) {
                $process->stop();
            }
            DB::statement('RESET ROLE');
            // Only the dedicated disposable test database reaches this committed-fixture cleanup.
            $this->assertSame('gis_schema_testing', DB::selectOne('SELECT current_database() AS name')->name);
            $tables = DB::select("SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('app','gis','staging') AND NOT(schemaname='app' AND tablename='backup_environment')");
            $names = array_map(fn ($row) => '"'.str_replace('"', '""', $row->schemaname).'"."'.str_replace('"', '""', $row->tablename).'"', $tables);
            DB::statement('TRUNCATE TABLE '.implode(',', $names).' RESTART IDENTITY');
            DB::insert('INSERT INTO app.active_release(singleton) VALUES(1)');
        }
    }
}
