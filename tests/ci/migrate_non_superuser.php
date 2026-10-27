<?php

use Illuminate\Contracts\Console\Kernel;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;

require __DIR__.'/../../vendor/autoload.php';
$app = require __DIR__.'/../../bootstrap/app.php';
$app->make(Kernel::class)->bootstrap();
$connection = config('database.connections.pgsql');
if (getenv('RUN_POSTGIS_TESTS') !== '1' || ! in_array($connection['host'], ['127.0.0.1', 'localhost', '::1'], true)
    || $connection['database'] !== 'gis_testing' || ! empty($connection['url'])) {
    throw new RuntimeException('This regression requires the disposable loopback CI database.');
}

DB::statement('CREATE ROLE gis_migration_admin NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB CREATEROLE NOINHERIT');
DB::statement('CREATE DATABASE gis_migration_testing OWNER gis_migration_admin TEMPLATE template0');
$connection['database'] = 'gis_migration_testing';
config(['database.connections.migration_regression' => $connection, 'database.default' => 'migration_regression']);
DB::purge('migration_regression');
DB::statement('CREATE SCHEMA extensions');
DB::statement('CREATE EXTENSION postgis WITH SCHEMA extensions');
DB::statement('GRANT USAGE ON SCHEMA extensions TO gis_migration_admin');
DB::statement('SET SESSION AUTHORIZATION gis_migration_admin');
$identity = DB::selectOne('SELECT current_user AS name,rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user');
if ($identity->name !== 'gis_migration_admin' || $identity->rolsuper || $identity->rolbypassrls) {
    throw new RuntimeException('Migration must execute without superuser or bypass RLS privileges.');
}
if (Artisan::call('migrate', ['--database' => 'migration_regression', '--force' => true]) !== 0) {
    throw new RuntimeException(Artisan::output());
}
foreach (['gis_runtime', 'gis_worker', 'gis_publisher', 'gis_artifact_verifier'] as $role) {
    DB::beginTransaction();
    DB::statement('SET LOCAL ROLE '.$role);
    $identity = DB::selectOne('SELECT current_user AS name');
    if ($identity->name !== $role) {
        throw new RuntimeException('Administrator cannot select the required application role.');
    }
    $membership = DB::selectOne("SELECT pg_has_role(current_user,'gis_lifecycle_owner','MEMBER') AS owns_lifecycle");
    if ($membership->owns_lifecycle) {
        throw new RuntimeException('Application role must not inherit lifecycle ownership.');
    }
    DB::rollBack();
}
echo "All migrations passed as a non-superuser; application roles remain separate from lifecycle ownership.\n";
