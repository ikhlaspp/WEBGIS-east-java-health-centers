<?php

namespace App\Console\Commands;

use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Throwable;

#[Signature('gis:check-database {--expected-database= : Explicit database identity to check} {--require-tls : Require TLS even on loopback}')]
#[Description('Read-only PostgreSQL/PostGIS connection check without exposing credentials')]
class CheckDatabaseConnection extends Command
{
    /**
     * Execute the console command.
     */
    public function handle(): int
    {
        $expected = $this->option('expected-database');
        if (! is_string($expected) || trim($expected) === '') {
            $this->error('Specify --expected-database before checking a connection.');

            return self::FAILURE;
        }

        try {
            $connection = DB::connection();
            if ($connection->getDriverName() !== 'pgsql' || $connection->getDatabaseName() !== $expected) {
                $this->error('Configured driver or database does not match the explicit target.');

                return self::FAILURE;
            }

            $loopback = in_array($connection->getConfig('host'), ['127.0.0.1', '::1', 'localhost'], true);
            $requireTls = ! $loopback || $this->option('require-tls');
            if ($requireTls && $connection->getConfig('sslmode') !== 'verify-full') {
                $this->error('Remote checks require DB_SSLMODE=verify-full and a trusted provider CA.');

                return self::FAILURE;
            }

            $identity = $connection->selectOne('SELECT current_database() AS database_name, current_setting(\'server_version\') AS server_version');
            if ($identity->database_name !== $expected) {
                $this->error('Connected database identity differs from the explicit target.');

                return self::FAILURE;
            }

            $tls = $connection->selectOne('SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()');
            $encrypted = in_array($tls?->ssl, [true, 1, '1', 't'], true);
            if ($requireTls && ! $encrypted) {
                $this->error('The connection is not encrypted.');

                return self::FAILURE;
            }

            $extension = $connection->selectOne("SELECT n.nspname AS schema_name, e.extversion AS version FROM pg_extension e JOIN pg_namespace n ON n.oid = e.extnamespace WHERE e.extname = 'postgis'");
            if ($extension === null || ! preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/D', $extension->schema_name)) {
                $this->error('PostGIS is missing or its schema cannot be checked.');

                return self::FAILURE;
            }

            $schema = '"'.$extension->schema_name.'"';
            $geometry = $connection->selectOne("SELECT {$schema}.ST_SRID({$schema}.ST_SetSRID({$schema}.ST_MakePoint(112.75, -7.25), 4326)) AS srid, {$schema}.ST_AsText({$schema}.ST_SetSRID({$schema}.ST_MakePoint(112.75, -7.25), 4326)) AS point_text");
            if ((int) $geometry->srid !== 4326 || $geometry->point_text !== 'POINT(112.75 -7.25)') {
                $this->error('PostGIS point construction failed the CRS84 coordinate check.');

                return self::FAILURE;
            }

            $this->line(json_encode([
                'database_matches_expected' => true,
                'postgresql_version' => $identity->server_version,
                'postgis_version' => $extension->version,
                'postgis_schema' => $extension->schema_name,
                'tls' => $encrypted,
                'point_srid' => (int) $geometry->srid,
                'read_only_probe' => true,
            ], JSON_THROW_ON_ERROR));

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Database check failed. Check private connection settings and server availability; credentials and exception details are omitted.');

            return self::FAILURE;
        }
    }
}
