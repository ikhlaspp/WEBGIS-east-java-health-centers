<?php

namespace Tests\Feature;

use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class DatabaseConstraintsTest extends TestCase
{
    private static bool $migrated = false;

    protected function setUp(): void
    {
        parent::setUp();
        if (getenv('RUN_POSTGIS_TESTS') !== '1') {
            $this->markTestSkipped('Requires the dedicated disposable gis_schema_testing PostGIS database.');
        }

        $config = config('database.connections.pgsql');
        if (! in_array($config['host'], ['127.0.0.1', 'localhost', '::1'], true)) {
            $this->fail('Schema tests must use the isolated loopback CI database.');
        }

        $config['database'] = 'gis_schema_testing';
        $config['url'] = null;
        config(['database.connections.schema_testing' => $config, 'database.default' => 'schema_testing']);
        DB::purge('schema_testing');
        $this->assertSame('gis_schema_testing', DB::selectOne('SELECT current_database() AS name')->name);
        if (! self::$migrated) {
            $this->artisan('migrate', ['--database' => 'schema_testing', '--force' => true])->assertSuccessful();
            self::$migrated = true;
        }

        DB::beginTransaction();
        $this->seedFixture();
    }

    protected function tearDown(): void
    {
        if (self::$migrated && DB::connection()->transactionLevel() > 0) {
            DB::rollBack();
        }
        parent::tearDown();
    }

    private function id(int $number): string
    {
        return sprintf('00000000-0000-4000-8000-%012d', $number);
    }

    private function seedFixture(): void
    {
        DB::insert("INSERT INTO app.users(id,name,email,password_hash) VALUES(?,'Fixture','fixture@example.test','fixture-only')", [$this->id(1)]);
        DB::insert("INSERT INTO gis.data_sources(id,publisher,title,source_url,observation_period,sha256,license_note,limitations,status) VALUES(?,'Fixture','Synthetic','https://example.test/source','synthetic',?,'fixture','not real data','verified')", [$this->id(2), str_repeat('a', 64)]);
        DB::insert("INSERT INTO gis.boundary_sets(id,source_id,name,version,code_system,source_crs) VALUES(?,?,'Fixture','one','fixture','CRS84')", [$this->id(3), $this->id(2)]);
        DB::insert("INSERT INTO gis.boundary_sets(id,source_id,name,version,code_system,source_crs) VALUES(?,?,'Other','two','fixture','CRS84')", [$this->id(30), $this->id(2)]);
        DB::insert("INSERT INTO gis.regencies(id,boundary_set_id,code,name,kind,geom) VALUES(?,?,'3501','Fixture','kabupaten',extensions.ST_GeomFromText('MULTIPOLYGON(((112 -7,113 -7,113 -8,112 -8,112 -7)))',4326))", [$this->id(4), $this->id(3)]);
        DB::insert("INSERT INTO gis.districts(id,boundary_set_id,regency_id,code,name,geom) SELECT ?,boundary_set_id,id,'3501010','Fixture',geom FROM gis.regencies WHERE id=?", [$this->id(5), $this->id(4)]);
        DB::insert("INSERT INTO gis.dataset_releases(id,label,boundary_set_id,facility_period,population_policy,area_policy,method_version,code_revision) VALUES(?,'Fixture',?,'2024','fixture','fixture','test','test')", [$this->id(6), $this->id(3)]);
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level) VALUES(?,?,?,'35010100001','Fixture','Synthetic address','Rawat Inap','Perdesaan',?,1,'missing','unknown')", [$this->id(6), $this->id(3), $this->id(5), $this->id(2)]);
    }

    public function test_fresh_migration_creates_domain_tables_indexes_and_empty_pointer(): void
    {
        $this->assertSame('extensions', DB::selectOne("SELECT n.nspname AS name FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace WHERE e.extname='postgis'")->name);
        $this->assertNull(DB::selectOne('SELECT release_id FROM app.active_release WHERE singleton=1')->release_id);
        $this->assertSame(0, DB::table('gis.analysis_runs')->count());
        $this->assertNotNull(DB::selectOne("SELECT indexname FROM pg_indexes WHERE schemaname='gis' AND indexname='facilities_geography'"));
        $this->assertNotNull(DB::selectOne("SELECT tablename FROM pg_tables WHERE schemaname='app' AND tablename='jobs'"));
    }

    public static function invalidUpdates(): array
    {
        return [
            'negative population' => ["INSERT INTO gis.district_indicators(release_id,boundary_set_id,district_id,population,quality_status,notes) SELECT release_id,boundary_set_id,district_id,-1,'pending','fixture' FROM gis.facility_snapshots", '23514'],
            'missing population provenance' => ["INSERT INTO gis.district_indicators(release_id,boundary_set_id,district_id,population,quality_status,notes) SELECT release_id,boundary_set_id,district_id,100,'pending','fixture' FROM gis.facility_snapshots", '23514'],
            'zero area' => ["INSERT INTO gis.district_indicators(release_id,boundary_set_id,district_id,area_km2,quality_status,notes) SELECT release_id,boundary_set_id,district_id,0,'pending','fixture' FROM gis.facility_snapshots", '23514'],
            'verified without evidence' => ["UPDATE gis.facility_snapshots SET coordinate_status='verified'", '23514'],
            'missing with a point' => ['UPDATE gis.facility_snapshots SET location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326)', '23514'],
            'point outside longitude range' => ["UPDATE gis.facility_snapshots SET coordinate_status='unverified',location=extensions.ST_SetSRID(extensions.ST_MakePoint(200,-7.5),4326)", '23514'],
            'empty polygon' => ["UPDATE gis.districts SET geom=extensions.ST_GeomFromText('MULTIPOLYGON EMPTY',4326)", '23514'],
            'wrong SRID' => ["UPDATE gis.districts SET geom=extensions.ST_GeomFromText('MULTIPOLYGON(((112 -7,113 -7,113 -8,112 -8,112 -7)))',3857)", '22023'],
            'invalid polygon' => ["UPDATE gis.districts SET geom=extensions.ST_GeomFromText('MULTIPOLYGON(((112 -7,113 -8,112 -8,113 -7,112 -7)))',4326)", '23514'],
            'duplicate facility' => ['INSERT INTO gis.facility_snapshots SELECT * FROM gis.facility_snapshots', '23505'],
            'cross boundary parent' => ["UPDATE gis.districts SET boundary_set_id='00000000-0000-4000-8000-000000000030'", '23503'],
            'cross boundary fact' => ["UPDATE gis.facility_snapshots SET boundary_set_id='00000000-0000-4000-8000-000000000030'", '23503'],
        ];
    }

    #[DataProvider('invalidUpdates')]
    public function test_invalid_domain_data_is_rejected(string $sql, string $sqlState): void
    {
        try {
            DB::statement($sql);
            DB::statement('SET CONSTRAINTS ALL IMMEDIATE');
            $this->fail('Invalid domain data was accepted.');
        } catch (QueryException $exception) {
            $this->assertSame($sqlState, $exception->errorInfo[0]);
        }
    }

    private function acceptReview(): void
    {
        DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason,reviewed_by,reviewed_at) VALUES(?,?,'35010100001',?,extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),'fixture','synthetic query','facility','accepted','https://example.test/evidence','synthetic','fixture evidence',?,now())", [$this->id(7), $this->id(6), $this->id(2), $this->id(1)]);
        DB::update("UPDATE gis.facility_snapshots SET coordinate_status='verified',precision_level='facility',location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),coordinate_source_id=?,selected_review_id=?", [$this->id(2), $this->id(7)]);
        DB::statement('SET CONSTRAINTS ALL IMMEDIATE');
    }

    public function test_a_same_facility_accepted_review_can_verify_the_exact_candidate(): void
    {
        $this->acceptReview();
        $this->assertSame('verified', DB::table('gis.facility_snapshots')->value('coordinate_status'));
    }

    public function test_changing_selected_review_point_invalidates_verified_snapshot(): void
    {
        $this->acceptReview();
        try {
            DB::update('UPDATE gis.geocode_reviews SET candidate_location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.6,-7.5),4326)');
            $this->fail('Mismatched review point was accepted.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', $exception->errorInfo[0]);
        }
    }

    public function test_a_review_from_another_facility_cannot_be_selected(): void
    {
        $this->acceptReview();
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level) SELECT release_id,boundary_set_id,district_id,'35010100002',name,address,service_type,area_type,source_id,2,'missing','unknown' FROM gis.facility_snapshots WHERE facility_code='35010100001'");
        try {
            DB::update("UPDATE gis.facility_snapshots SET selected_review_id=?,coordinate_status='verified',precision_level='facility',coordinate_source_id=?,location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326) WHERE facility_code='35010100002'", [$this->id(7), $this->id(2)]);
            $this->fail('Another facility review was accepted.');
        } catch (QueryException $exception) {
            $this->assertContains($exception->errorInfo[0], ['23503', '23514']);
        }
    }

    public function test_frozen_release_rejects_input_edits(): void
    {
        DB::update("UPDATE gis.dataset_releases SET status='validated'");
        try {
            DB::update("UPDATE gis.facility_snapshots SET name='Changed'");
            $this->fail('Frozen input was changed.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', $exception->errorInfo[0]);
        }
    }

    public function test_shared_boundary_of_a_frozen_release_is_protected(): void
    {
        DB::update("UPDATE gis.dataset_releases SET status='validated'");
        try {
            DB::update("UPDATE gis.districts SET name='Changed'");
            $this->fail('Frozen shared boundary was changed.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', $exception->errorInfo[0]);
        }
    }

    public function test_draft_input_edit_increments_revision(): void
    {
        $before = DB::table('gis.dataset_releases')->value('input_revision');
        DB::update("UPDATE gis.facility_snapshots SET name='New draft name'");
        $this->assertSame((int) $before + 1, (int) DB::table('gis.dataset_releases')->value('input_revision'));
    }
}
