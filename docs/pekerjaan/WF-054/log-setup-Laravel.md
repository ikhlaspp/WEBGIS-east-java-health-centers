# Laravel setup log

Date: 23 October 2026
Executor: Codex on the project owner's instruction
Baseline revision: `0a2c3bab86e9d21e14ab2fa758d119bf8387106c`
Result: local Laravel base app installed and bootable; Supabase connectivity is not yet tested.

## Environment observed

| Tool | Actual version/state |
|---|---|
| PHP | 8.4.22 |
| Composer | 2.4.1; emits PHP 8.4 deprecation notices, but completed install and validation |
| Laravel framework | 13.38.0 from `composer.lock` |
| Node.js | 24.14.1 |
| npm | 11.11.0 |
| PostgreSQL PHP driver | `pdo_pgsql` is not loaded |
| Python | 3.10.6; Python 3.12 launcher is unavailable in this shell (tracked for WF-055) |

## Setup performed

- Created a clean Laravel skeleton in a temporary child directory, then overlaid it without replacing `Archives/`, `docs/`, `.git/`, or the WF-053 README and ignore rules. The temporary skeleton directory was removed after transfer.
- Retained the Laravel 13 dependency lock and added Laravel Boost as a development dependency because the generated Laravel project setup instructions required it. Boost installed its guidelines; it did not add application routes or database code.
- Configured `.env.example` for the selected Supabase PostgreSQL connection with SSL required and placeholder credentials. Session/cache use local files and the queue runs synchronously by default so setup and public health checks do not need a live database.
- Copied `.env.example` to the ignored `.env` and generated a local `APP_KEY`. The local file contains no real Supabase credentials and is not staged.
- Added the Laravel framework health route check and home-page smoke test in `tests/Feature/HealthTest.php`.

## Verification

| Command/action | Expected | Actual |
|---|---|---|
| `php artisan --version` | Laravel application boots | `Laravel Framework 13.38.0` |
| `composer.bat validate --no-check-publish` | Valid project and lock metadata | `./composer.json is valid`, exit 0 |
| `npm.cmd install` | Install from package manifest | 56 packages added; audit reported 0 vulnerabilities |
| `npm.cmd run build` | Vite production build succeeds | Vite 8.3.5 built successfully, exit 0; optional `fontaine` fallback optimization warning only |
| `php artisan test --compact tests/Feature/HealthTest.php` | Home and framework health routes return success | 2 tests, 2 assertions passed, exit 0 |
| `php artisan serve --host=127.0.0.1 --port=8877`, then GET `/up` | Local HTTP response 200 | HTTP 200; local server stopped after smoke test |
| `vendor/bin/pint --dirty --format agent` | PHP formatting passes | Passed |
| `git diff --check` | No whitespace errors | Passed, exit 0 |

## Limits and next action

No Supabase project credentials were provided or used, and the local PHP installation lacks `pdo_pgsql`; no database connection or migration was attempted. The current tests prove only the basic Laravel routes. Vercel deployment compatibility is not covered by this setup ticket. Next: verify Supabase/PostgreSQL driver setup and create the Python environment in their scheduled tickets.
