<?php

namespace Tests;

use Illuminate\Support\Facades\DB;

abstract class GisDatabaseTestCase extends TestCase
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

    protected function id(int $number): string
    {
        return sprintf('00000000-0000-4000-8000-%012d', $number);
    }

    protected function seedFixture(): void
    {
        DB::insert("INSERT INTO app.users(id,name,email,password_hash) VALUES(?,'Fixture','fixture@example.test','fixture-only')", [$this->id(1)]);
        // Synthetic prerequisite only; this never represents an actual database backup or restore drill.
        DB::insert("INSERT INTO app.backup_checkpoints(id,database_name,instance_id,completed_at,manifest_sha256,inventory,verified_by) SELECT ?,current_database(),instance_id,clock_timestamp(),?,'[{},{}]',? FROM app.backup_environment WHERE singleton", [$this->id(90), str_repeat('b', 64), $this->id(1)]);
        DB::insert("INSERT INTO gis.data_sources(id,publisher,title,source_url,observation_period,sha256,license_note,limitations,status) VALUES(?,'Fixture','Synthetic','https://example.test/source','synthetic',?,'fixture','not real data','verified')", [$this->id(2), str_repeat('a', 64)]);
        DB::insert("INSERT INTO gis.boundary_sets(id,source_id,name,version,code_system,source_crs) VALUES(?,?,'Fixture','one','fixture','CRS84')", [$this->id(3), $this->id(2)]);
        DB::insert("INSERT INTO gis.boundary_sets(id,source_id,name,version,code_system,source_crs) VALUES(?,?,'Other','two','fixture','CRS84')", [$this->id(30), $this->id(2)]);
        DB::insert("INSERT INTO gis.regencies(id,boundary_set_id,code,name,kind,geom) VALUES(?,?,'3501','Fixture','kabupaten',extensions.ST_GeomFromText('MULTIPOLYGON(((112 -7,113 -7,113 -8,112 -8,112 -7)))',4326))", [$this->id(4), $this->id(3)]);
        DB::insert("INSERT INTO gis.districts(id,boundary_set_id,regency_id,code,name,geom) SELECT ?,boundary_set_id,id,'3501010','Fixture',geom FROM gis.regencies WHERE id=?", [$this->id(5), $this->id(4)]);
        DB::insert("INSERT INTO gis.dataset_releases(id,label,boundary_set_id,facility_period,population_policy,area_policy,method_version,code_revision) VALUES(?,'Fixture',?,'2024','fixture','fixture','test','test')", [$this->id(6), $this->id(3)]);
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level) VALUES(?,?,?,'35010100001','Fixture','Synthetic address','Rawat Inap','Perdesaan',?,1,'missing','unknown')", [$this->id(6), $this->id(3), $this->id(5), $this->id(2)]);
    }
}
