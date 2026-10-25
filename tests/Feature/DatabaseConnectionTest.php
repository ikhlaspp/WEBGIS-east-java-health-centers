<?php

namespace Tests\Feature;

use Illuminate\Database\Connection;
use Illuminate\Support\Facades\DB;
use Mockery;
use RuntimeException;
use Tests\TestCase;

class DatabaseConnectionTest extends TestCase
{
    public function test_an_explicit_target_is_required_without_connecting(): void
    {
        DB::shouldReceive('connection')->never();
        $this->artisan('gis:check-database')->assertFailed();
    }

    public function test_a_different_database_is_rejected_before_queries(): void
    {
        $connection = $this->connection();
        $connection->shouldReceive('selectOne')->never();
        $this->artisan('gis:check-database --expected-database=other')->assertFailed();
    }

    public function test_remote_connections_cannot_downgrade_tls(): void
    {
        $connection = $this->connection('remote.example', 'require');
        $connection->shouldReceive('selectOne')->never();
        $this->artisan('gis:check-database --expected-database=gis_testing')->assertFailed();
    }

    public function test_connection_errors_do_not_print_credentials(): void
    {
        $connection = $this->connection();
        $connection->shouldReceive('selectOne')->once()->andThrow(new RuntimeException('password=synthetic-secret'));
        $this->artisan('gis:check-database --expected-database=gis_testing')
            ->doesntExpectOutputToContain('synthetic-secret')
            ->assertFailed();
    }

    public function test_the_probe_uses_the_actual_extension_schema(): void
    {
        $connection = $this->connection();
        $connection->shouldReceive('selectOne')->once()->with(Mockery::pattern('/current_database/'))
            ->andReturn((object) ['database_name' => 'gis_testing', 'server_version' => '16.fixture']);
        $connection->shouldReceive('selectOne')->once()->with(Mockery::pattern('/pg_stat_ssl/'))
            ->andReturn((object) ['ssl' => false]);
        $connection->shouldReceive('selectOne')->once()->with(Mockery::pattern('/pg_extension/'))
            ->andReturn((object) ['schema_name' => 'extensions', 'version' => '3.4.fixture']);
        $connection->shouldReceive('selectOne')->once()->with(Mockery::pattern('/"extensions"\.ST_MakePoint/'))
            ->andReturn((object) ['srid' => 4326, 'point_text' => 'POINT(112.75 -7.25)']);
        $this->artisan('gis:check-database --expected-database=gis_testing')->assertSuccessful();
    }

    public function test_the_real_isolated_postgis_database_passes_the_probe(): void
    {
        if (getenv('RUN_POSTGIS_TESTS') !== '1') {
            $this->markTestSkipped('Requires the isolated PostgreSQL/PostGIS test service.');
        }

        $this->artisan('gis:check-database --expected-database=gis_testing')->assertSuccessful();
    }

    private function connection(string $host = '127.0.0.1', string $sslmode = 'prefer'): Connection
    {
        $connection = Mockery::mock(Connection::class);
        $connection->shouldReceive('getDriverName')->andReturn('pgsql');
        $connection->shouldReceive('getDatabaseName')->andReturn('gis_testing');
        $connection->shouldReceive('getConfig')->with('host')->andReturn($host);
        $connection->shouldReceive('getConfig')->with('sslmode')->andReturn($sslmode);
        DB::shouldReceive('connection')->andReturn($connection);

        return $connection;
    }
}
