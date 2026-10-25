# Database development/test preparation

2026-10-25. User explicitly postponed location-evidence review and asked to continue implementation. This authorizes independent database preparation ahead of the serial location-review gate; it does not accept that gate or complete WF-068 through WF-071.

Implemented gis:check-database --expected-database=<explicit-target> as a read-only PDO/PostgreSQL/PostGIS probe. It checks configured and connected database identity, server version, actual TLS state, extension version/schema, and a CRS84 point. Remote hosts require verify-full; loopback CI may use its explicit local SSL mode. Exception messages and credentials are not emitted. No schema creation, migrations, data imports, or production mutations occur in this command.

config/database.php now passes DB_SSLROOTCERT to Laravel's PostgreSQL connector and supports DB_SEARCH_PATH. .env.example defaults to verify-full and documents the provider CA path. Existing CI explicitly configures its isolated loopback service; Supabase direct/session endpoints must use their actual provider hostname and trusted CA. Installed Laravel PostgresConnector source was checked for sslrootcert support. No application dependencies were changed; Laravel Boost was already installed and its generated guidelines were followed.

Local verification: php vendor/bin/pint --dirty --format agent passed. php artisan test --compact tests/Feature/DatabaseConnectionTest.php: five passed, fourteen assertions, one live PostGIS test skipped because no isolated local PostgreSQL service is configured. The existing GitHub workflow enables RUN_POSTGIS_TESTS=1 against its dedicated gis_testing database; the new live test runs there after push.

Provisioning remains incomplete: local .env has a placeholder DB host, no database password/URL, no .env.testing, and no available Supabase connector. No account, project, or credential was invented. Test CI coverage is not proof of a separate development database or Supabase TLS. Actual dev/test provisioning and both connection checks remain pending. Current source code/test preparation can proceed without location acceptance.
