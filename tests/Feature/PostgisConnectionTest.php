<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\DB;
use Tests\TestCase;

class PostgisConnectionTest extends TestCase
{
    public function test_the_ci_database_supports_postgis_geometry(): void
    {
        if (getenv('RUN_POSTGIS_TESTS') !== '1') {
            $this->markTestSkipped('Set RUN_POSTGIS_TESTS=1 with an isolated PostgreSQL/PostGIS test database.');
        }

        $this->assertSame('pgsql', DB::connection()->getDriverName());
        $this->assertSame('gis_testing', DB::connection()->getDatabaseName());

        $result = DB::selectOne("SELECT PostGIS_Version() AS version, ST_Contains(ST_GeomFromText('POLYGON((0 0,0 2,2 2,2 0,0 0))', 4326), ST_SetSRID(ST_MakePoint(1,1), 4326)) AS inside");

        $this->assertNotEmpty($result->version);
        $this->assertTrue((bool) $result->inside);
    }
}
