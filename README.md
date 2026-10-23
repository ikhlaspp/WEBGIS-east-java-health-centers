# WebGIS Puskesmas Jawa Timur

Web application for exploring public-health facility locations and district-level indicators in East Java. The source material currently lives in `Archives/`; preserve those originals and do not edit them in place.

## Project status

The repository scaffold and Laravel 13 base application are in place. The project follows the accepted design baseline in `docs/pekerjaan/`. The stack is Laravel with Blade/Vite and Leaflet, Supabase PostgreSQL with PostGIS, and Vercel Hobby as the free hosting target. Vercel's PHP runtime is community-maintained, so Laravel deployment compatibility must be demonstrated before treating it as production-ready.

Some source data is incomplete: the archived facility-coordinate file has 565 of 973 facilities located and 408 without coordinates. No district-boundary GIS files were found in `Archives/`. Do not invent coordinates or polygons; keep outputs that require missing inputs blocked until a permitted source or revised scope is recorded.

## Development setup

1. Install PHP, Composer, and Node.js versions compatible with the committed lockfiles. WF-055 will add the Python environment lock.
2. Copy `.env.example` to `.env`, generate an application key, and add Supabase credentials only to the ignored `.env` file. Never commit service-role keys, database passwords, or production configuration.
3. Install PHP and JavaScript dependencies from the committed lockfiles. The application must use a PostgreSQL/PostGIS test database for database and spatial checks; SQLite is not a substitute for those checks.
4. Run the project checks listed in the active ticket handoff under `docs/pekerjaan/`.

The repository setup item introduces Laravel and frontend lockfiles. The local PHP currently lacks `pdo_pgsql`; routes that need the database cannot run until a suitable driver is enabled. No Supabase credential is stored in this repository.

## Data handling

- Treat files in `Archives/` as read-only source originals.
- Keep downloaded, staging, processed, and exported data outside Git under the ignored `data/` directories.
- Commit only synthetic fixtures and sanitized evidence. Record source name, period, retrieval facts that are actually known, and file hash; do not invent metadata for old archive files.
- Keep secrets in local environment variables or the hosting provider's secret manager.

## Repository layout

See [`docs/pekerjaan/WF-053/struktur-proyek.txt`](docs/pekerjaan/WF-053/struktur-proyek.txt) for the approved module map and which parts are not yet created.
