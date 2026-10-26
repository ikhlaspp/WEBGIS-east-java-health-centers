<?php

namespace Tests\Feature;

use App\Services\OperatorAnalysisService;
use App\Services\ReleaseValidationService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use PHPUnit\Framework\Attributes\DataProvider;
use RuntimeException;
use Tests\GisDatabaseTestCase;

class ReleaseValidationTest extends GisDatabaseTestCase
{
    private ?string $run = null;

    private function fixture(bool $point = true): int
    {
        DB::update('UPDATE app.users SET is_admin=true');
        DB::update("UPDATE gis.dataset_releases SET method_version='postgis-analysis-v1',code_revision=? WHERE id=?", [str_repeat('c', 40), $this->id(6)]);
        DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,'[\"analyze\",\"validate\"]',now()+interval '1 hour')", [$this->id(70), $this->id(1), hash('sha256', str_repeat('A', 43))]);
        if ($point) {
            DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason,reviewed_by,reviewed_at) VALUES(?,?,'35010100001',?,extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),'fixture','synthetic','facility','accepted','https://example.test/evidence','synthetic','fixture evidence',?,now())", [$this->id(7), $this->id(6), $this->id(2), $this->id(1)]);
            DB::update("UPDATE gis.facility_snapshots SET coordinate_status='verified',precision_level='facility',location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),coordinate_source_id=?,selected_review_id=?", [$this->id(2), $this->id(7)]);
        }
        $this->run = (string) Str::uuid();
        app(OperatorAnalysisService::class)->run(str_repeat('A', 43), $this->id(6), $this->run, 30000, str_repeat('c', 40));

        return (int) DB::table('gis.dataset_releases')->where('id', $this->id(6))->value('input_revision');
    }

    private function validate(int $revision, bool $partial = true): array
    {
        return app(ReleaseValidationService::class)->validate(str_repeat('A', 43), $this->id(6), $this->run, $revision, 'Synthetic partial scope accepted for this test only', $partial);
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

    public function test_verified_files_and_explicit_scope_freeze_candidate_with_atomic_report_and_audit(): void
    {
        $revision = $this->fixture();
        $result = $this->validate($revision);
        $this->assertSame('validated', $result['status']);
        DB::statement('RESET ROLE');
        $report = DB::table('gis.quality_reports')->sole();
        $this->assertTrue($report->passed);
        $this->assertSame($this->id(1), $report->approved_by);
        $this->assertSame(1, json_decode($report->exclusions, true)['districts_with_missing_indicators']);
        $this->assertSame($this->run, DB::table('gis.dataset_releases')->value('default_analysis_run_id'));
        $audit = DB::table('app.audit_logs')->where('action', 'release.validated')->sole();
        $this->assertSame($this->id(70), $audit->token_id);
        $this->assertStringNotContainsString(str_repeat('A', 43), json_encode($audit));
        $this->assertNull(DB::table('app.active_release')->value('release_id'));
        $this->assertSame(0, DB::table('gis.artifacts')->where('sanitized', true)->count());
        try {
            DB::transaction(fn () => DB::update("UPDATE gis.facility_snapshots SET address='Changed after validation'"));
            $this->fail('Frozen candidate changed.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', (string) $exception->getCode());
        }
    }

    public static function rejectionCases(): array
    {
        return array_map(fn ($case) => [$case], ['tampered_file', 'stale_revision', 'wrong_ability', 'no_eligible_points', 'partial_not_accepted', 'wrong_run', 'audit_failure']);
    }

    #[DataProvider('rejectionCases')]
    public function test_failures_leave_draft_without_quality_acceptance(string $case): void
    {
        $revision = $this->fixture($case !== 'no_eligible_points');
        DB::statement('RESET ROLE');
        if ($case === 'tampered_file') {
            file_put_contents(storage_path('app/private/analysis/'.$this->run.'/density.geojson'), '{}');
        } elseif ($case === 'stale_revision') {
            DB::update("UPDATE gis.facility_snapshots SET address='Changed input'");
        } elseif ($case === 'wrong_ability') {
            DB::update("UPDATE app.operator_tokens SET abilities='[\"analyze\"]'");
        } elseif ($case === 'audit_failure') {
            DB::unprepared("CREATE FUNCTION app.fail_validation_audit() RETURNS trigger LANGUAGE plpgsql AS \$\$ BEGIN IF NEW.action='release.validated' THEN RAISE EXCEPTION 'Injected audit failure'; END IF; RETURN NEW; END \$\$; CREATE TRIGGER fail_validation_audit BEFORE INSERT ON app.audit_logs FOR EACH ROW EXECUTE FUNCTION app.fail_validation_audit()");
        }
        try {
            app(ReleaseValidationService::class)->validate(str_repeat('A', 43), $this->id(6), $case === 'wrong_run' ? $this->id(99) : $this->run, $revision, 'Synthetic validation rejection test', $case !== 'partial_not_accepted');
            $this->fail('Invalid candidate accepted.');
        } catch (QueryException|RuntimeException) {
            $this->addToAssertionCount(1);
        }
        DB::statement('RESET ROLE');
        $this->assertSame('draft', DB::table('gis.dataset_releases')->value('status'));
        $this->assertSame(0, DB::table('gis.quality_reports')->count());
        $this->assertSame(0, DB::table('app.audit_logs')->where('action', 'release.validated')->count());
    }

    public function test_application_roles_cannot_attest_files_or_write_quality_acceptance(): void
    {
        $this->fixture();
        foreach (['gis_runtime', 'gis_worker', 'gis_publisher'] as $role) {
            try {
                DB::transaction(function () use ($role): void {
                    DB::statement('SET LOCAL ROLE '.$role);
                    DB::selectOne("SELECT gis.validate_release(?,?::uuid,?::uuid,0,'{}',true,'Forged acceptance attempt')", [str_repeat('A', 43), $this->id(6), $this->run]);
                });
                $this->fail('Untrusted role attested files.');
            } catch (QueryException $exception) {
                $this->assertSame('42501', (string) $exception->getCode());
            }
        }
    }
}
