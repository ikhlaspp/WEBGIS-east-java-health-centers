<?php

namespace Tests\Feature;

use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\GisDatabaseTestCase;

class DatabaseAccessTest extends GisDatabaseTestCase
{
    private function asRole(string $role): void
    {
        $this->assertContains($role, ['gis_runtime', 'gis_worker', 'gis_publisher', 'anon', 'authenticated']);
        DB::statement('SET LOCAL ROLE '.$role);
        $this->assertSame($role, DB::selectOne('SELECT current_user AS name')->name);
        $attributes = DB::selectOne('SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user');
        $this->assertFalse((bool) $attributes->rolsuper);
        $this->assertFalse((bool) $attributes->rolbypassrls);
    }

    private function publishedFixture(): void
    {
        DB::insert("INSERT INTO gis.analysis_runs(id,release_id,method_version,code_revision,input_hash,parameters_hash,input_revision,parameters,status,idempotency_key,started_by) VALUES(?,?,'fixture','fixture','fixture','fixture',1,'{}','succeeded',?,?)", [$this->id(8), $this->id(6), str_repeat('b', 64), $this->id(1)]);
        DB::insert("INSERT INTO gis.quality_reports(id,release_id,input_revision,input_hash,report_hash,policy_version,checks,exclusions,passed,approved_by,approved_at) VALUES(?,?,1,'fixture','fixture','fixture','{}','{}',true,?,now())", [$this->id(9), $this->id(6), $this->id(1)]);
        DB::update("UPDATE gis.dataset_releases SET status='published',quality_report_id=?,default_analysis_run_id=?,published_at=now(),published_by=?", [$this->id(9), $this->id(8), $this->id(1)]);
    }

    public function test_runtime_cannot_see_drafts_or_their_shared_boundaries(): void
    {
        $this->asRole('gis_runtime');
        $this->assertSame(0, DB::table('gis.dataset_releases')->count());
        $this->assertSame(0, DB::table('gis.facility_snapshots')->count());
        $this->assertSame(0, DB::table('gis.districts')->count());
        $this->assertSame(0, DB::table('gis.data_sources')->count());
    }

    public function test_runtime_reads_published_data_without_policy_recursion(): void
    {
        $this->publishedFixture();
        $this->asRole('gis_runtime');
        $this->assertSame('Fixture', DB::table('gis.dataset_releases')->value('label'));
        $this->assertSame(1, DB::table('gis.facility_snapshots')->count());
        $this->assertSame(1, DB::table('gis.districts')->count());
        $this->assertSame(1, DB::table('gis.data_sources')->count());
    }

    public function test_withdrawal_hides_previously_visible_data(): void
    {
        $this->publishedFixture();
        $this->asRole('gis_runtime');
        $this->assertSame(1, DB::table('gis.facility_snapshots')->count());
        DB::statement('RESET ROLE');
        DB::update("UPDATE gis.dataset_releases SET status='withdrawn'");
        $this->asRole('gis_runtime');
        $this->assertSame(0, DB::table('gis.facility_snapshots')->count());
        $this->assertSame(0, DB::table('gis.districts')->count());
    }

    public function test_worker_can_edit_draft_input_with_system_revision_increment(): void
    {
        $before = DB::table('gis.dataset_releases')->value('input_revision');
        $this->asRole('gis_worker');
        $this->assertSame(1, DB::table('gis.facility_snapshots')->update(['name' => 'Worker draft edit']));
        $this->assertSame((int) $before + 1, (int) DB::table('gis.dataset_releases')->value('input_revision'));
    }

    public function test_worker_cannot_edit_published_input(): void
    {
        $this->publishedFixture();
        $this->asRole('gis_worker');
        $this->assertSame(0, DB::table('gis.facility_snapshots')->update(['name' => 'Forbidden edit']));
        $this->assertSame('Fixture', DB::table('gis.facility_snapshots')->value('name'));
    }

    public function test_worker_metadata_edit_invalidates_the_input_revision(): void
    {
        $before = DB::table('gis.dataset_releases')->value('input_revision');
        $this->asRole('gis_worker');
        DB::table('gis.dataset_releases')->update(['population_policy' => 'new draft policy']);
        $this->assertSame((int) $before + 1, (int) DB::table('gis.dataset_releases')->value('input_revision'));
    }

    public function test_publisher_can_read_candidate_but_not_modify_it(): void
    {
        $this->asRole('gis_publisher');
        $this->assertSame(1, DB::table('gis.dataset_releases')->count());
        $this->assertSame(0, DB::table('gis.quality_reports')->count());
    }

    public static function deniedQueries(): array
    {
        return [
            ['gis_runtime', 'SELECT * FROM staging.rows'],
            ['gis_runtime', 'SELECT * FROM app.operator_tokens'],
            ['gis_runtime', 'SELECT private_path FROM gis.data_sources'],
            ['gis_runtime', 'SELECT * FROM gis.geocode_reviews'],
            ['gis_runtime', 'SELECT private_path FROM gis.artifacts'],
            ['gis_runtime', "UPDATE gis.facility_snapshots SET name='Forbidden'"],
            ['gis_runtime', 'TRUNCATE gis.facility_snapshots'],
            ['gis_worker', "UPDATE gis.dataset_releases SET status='published'"],
            ['gis_worker', 'UPDATE gis.dataset_releases SET input_revision=0'],
            ['gis_worker', 'UPDATE gis.quality_reports SET passed=true'],
            ['gis_worker', "UPDATE gis.geocode_reviews SET result_status='accepted'"],
            ['gis_worker', 'UPDATE gis.facility_snapshots SET selected_review_id=NULL'],
            ['gis_publisher', "UPDATE gis.dataset_releases SET status='published'"],
            ['gis_publisher', 'UPDATE app.active_release SET version=10'],
            ['gis_publisher', 'DELETE FROM app.audit_logs'],
            ['anon', 'SELECT * FROM gis.dataset_releases'],
            ['authenticated', 'SELECT * FROM app.users'],
        ];
    }

    #[DataProvider('deniedQueries')]
    public function test_untrusted_access_is_denied(string $role, string $query): void
    {
        $this->asRole($role);
        try {
            DB::statement($query);
            $this->fail('Disallowed SQL unexpectedly succeeded.');
        } catch (QueryException $exception) {
            $this->assertSame('42501', $exception->errorInfo[0]);
        }
    }

    public function test_runtime_cannot_assume_the_definer_role(): void
    {
        $this->asRole('gis_runtime');
        $this->assertFalse((bool) DB::selectOne("SELECT pg_has_role(current_user,'gis_lifecycle_owner','MEMBER') AS member")->member);
    }
}
