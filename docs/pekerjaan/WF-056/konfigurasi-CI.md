# Automated project checks

Prepared 23 October 2026 for WF-056. `.github/workflows/checks.yml` runs on pushes, pull requests, and manual dispatch. Actions are pinned to the resolved commit of their major release. Token permissions are read-only; production secrets are not used. Timeouts and per-ref cancellation bound work.

Python 3.12 installs `requirements.lock` with hashes, checks syntax and runs synthetic pytest fixtures. PHP 8.4 runs Composer platform validation, Pint and PHPUnit. Node 24 installs the npm lock, checks JavaScript syntax, builds Vite, and runs Playwright Chromium against an isolated local server. Reports and failure traces are retained for seven days. Raw data, environments and runtime authentication files are excluded from artifacts.

The PostgreSQL/PostGIS service uses an ephemeral `gis_testing` database with CI-only credentials declared in the workflow. No Supabase credentials are needed. `PostgisConnectionTest` requires PostgreSQL, the expected test DB name, and a successful PostGIS point-in-polygon query. CI enables it with RUN_POSTGIS_TESTS=1. Local execution without a test DB reports an explicit skip, not a spatial pass. Separate runtime/worker/publisher authorization tests arrive with their implementation tickets; this check establishes the test engine only.

The main suite excludes `tests/ci/assertion_failure.py`. Manually dispatch with `prove_failure=true`, or push the candidate commit to the dedicated `ci/assertion-proof` branch, to execute that deliberately failing assertion. The Python job must fail; application work is skipped for this diagnostic branch. Ordinary runs must pass. The fixture has a known expected failure and is never silently enabled for main.

`pytest.ini` disables the optional persistent cache, avoiding the Windows ownership warning seen in Colab. `pint.json` excludes generated tools/caches and raw archives from PHP scans. The Playwright fixture currently checks the health endpoint and landing page; later UI tickets add real feature coverage.

Local evidence is in log-pemeriksaan-awal.txt. Remote run IDs/results are recorded after push in the conversation and next checkpoint update. The initial commit does not claim an unobserved hosted run passed.

References: https://docs.github.com/en/actions/tutorials/build-and-test-code/python ; https://github.com/shivammathur/setup-php ; https://github.com/actions/setup-node .
