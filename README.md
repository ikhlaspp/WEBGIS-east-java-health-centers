# WebGIS Puskesmas Jawa Timur

Web application for exploring public-health facility locations and district-level indicators in East Java. The source material currently lives in `Archives/`; preserve those originals and do not edit them in place.

## Project status

The repository scaffold and Laravel 13 base application are in place. The project follows the accepted design baseline in `docs/pekerjaan/`. The stack is Laravel with Blade/Vite and Leaflet, Supabase PostgreSQL with PostGIS, and Vercel Hobby as the free hosting target. Vercel's PHP runtime is community-maintained, so Laravel deployment compatibility must be demonstrated before treating it as production-ready.

The backend now includes published-release APIs, Python/PostGIS analysis, admin authentication and authorized CLI review, validation, publication and rollback. See the [operator command guide](docs/pekerjaan/WF-086/panduan-command-admin.md) for private capability files, backup verification and retryable release-event delivery. Actual dataset acceptance and deployment remain separate from synthetic CI verification; the public dashboard is the next implementation task.

Some source data is incomplete: the archived facility-coordinate file has 565 of 973 facilities located and 408 without coordinates. No district-boundary GIS files were found in `Archives/`. Do not invent coordinates or polygons; keep outputs that require missing inputs blocked until a permitted source or revised scope is recorded.

## Development setup

1. Install PHP, Composer, and Node.js versions compatible with the committed lockfiles, plus Python 3.12 for the hash-locked analysis environment described below.
2. Copy `.env.example` to `.env`, generate an application key, and add Supabase credentials only to the ignored `.env` file. Never commit service-role keys, database passwords, or production configuration.
3. Install PHP and JavaScript dependencies from the committed lockfiles. The application must use a PostgreSQL/PostGIS test database for database and spatial checks; SQLite is not a substitute for those checks.
4. Run the project checks listed in the active ticket handoff under `docs/pekerjaan/`.

The repository setup item introduces Laravel and frontend lockfiles. The local PHP currently lacks `pdo_pgsql`; routes that need the database cannot run until a suitable driver is enabled. No Supabase credential is stored in this repository.

## Python/GIS environment

Use Python 3.12. On Windows, create `.venv` with `python -m venv .venv`; on other systems use `python3.12 -m venv .venv`. Install the pinned, hash-checked packages with `.venv/Scripts/python -m pip install --require-hashes -r requirements.lock` on Windows or `.venv/bin/python -m pip install --require-hashes -r requirements.lock` on Linux/macOS. Run fixture tests with `.venv/Scripts/python -m pytest tests/python -q` (Windows) or `.venv/bin/python -m pytest tests/python -q` (Linux/macOS). The notebook's sample geometry is synthetic; it does not process `Archives/`.

To use Google's Colab website with this computer's local Python runtime, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\analysis\start-colab-local-runtime.ps1` from the repository root, then in Colab choose **Connect → Connect to local runtime** and enter the authenticated URL printed in the terminal. The server binds to `127.0.0.1:8888`, restricts browser origin to `https://colab.research.google.com`, and keeps Jupyter token authentication enabled. Stop it with Ctrl+C when finished. A Colab notebook connected this way executes code on this computer and can access files available to the Jupyter process.

## Data handling

- Treat files in `Archives/` as read-only source originals.
- Keep downloaded, staging, processed, and exported data outside Git under the ignored `data/` directories.
- Commit only synthetic fixtures and sanitized evidence. Record source name, period, retrieval facts that are actually known, and file hash; do not invent metadata for old archive files.
- Keep secrets in local environment variables or the hosting provider's secret manager.

## Repository layout

See [`docs/pekerjaan/WF-053/struktur-proyek.txt`](docs/pekerjaan/WF-053/struktur-proyek.txt) for the approved module map and which parts are not yet created.
