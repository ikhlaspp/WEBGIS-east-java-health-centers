# Handoff WF-054

Status kesiapan: ready for basic local framework work; database-dependent routes remain unconfigured.
Revision awal: `0a2c3bab86e9d21e14ab2fa758d119bf8387106c`; WF-053 is on `origin/main`.
Input: accepted WF-G3; repository scaffold in WF-053; environment and dependency design in WF-030; Supabase and Vercel Hobby selected by the project owner.
Prasyarat: PHP 8.4.22 and Node 24.14.1 available. Local PHP lacks `pdo_pgsql`; no Supabase credentials were provided.
Scope: install the Laravel 13 skeleton, frontend manifests, sample environment, and basic home/health checks; no production connection or data feature.
File aktual: `composer.json`, `composer.lock`, `package.json`, `package-lock.json`, `routes/web.php`, `.env.example`, Laravel framework directories, and `tests/Feature/HealthTest.php`.
Kontrak: database uses PostgreSQL (`DB_CONNECTION=pgsql`, `DB_SSLMODE=require`); local session/cache use file and queue uses sync by default; real credentials stay outside Git.
Fixture: none; route checks require no database and do not validate spatial behavior.
Verifikasi: from root, `php artisan test --compact tests/Feature/HealthTest.php`, `npm.cmd run build`, `composer.bat validate --no-check-publish`, `vendor/bin/pint --dirty --format agent`, and local HTTP GET `/up`.
Checkpoint: both routes pass, assets build, and manifests validate.
Review: Codex technical self-review; no independent QA reviewer named.
Penghalang: live database checks require `pdo_pgsql`, a provisioned Supabase project, and credentials. Vercel Hobby Laravel runtime remains a later deployment proof.
