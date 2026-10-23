# Python and Colab setup log

Date: 23 October 2026
Executor: Codex on the project owner's instruction
Baseline revision: `1ee8e1c6d7afe9284902a6aa5c58fe137dfe5818`
Result: local Python/GIS environment and synthetic notebook preflight pass. Colab execution remains blocked because no browser is available in this session.

## Environment installed

- System Python is 3.10.6; no Python 3.12 command or `uv` was initially available.
- Installed `uv` 0.13.5 into the ignored workspace `.tools/` directory and provisioned CPython 3.12.15 under `.tools/python/`. Installation could not create a global PATH shim or registry entry due Windows access restrictions; the local interpreter works by explicit path.
- Created the ignored `.venv/` using Python 3.12.15.
- Added `requirements.in` and generated universal, hash-checked `requirements.lock` for Python 3.12. The resolved environment includes GeoPandas 1.2.0, Shapely 2.2.0, PyProj 3.8.0, Pandas 3.1.0, Folium 0.20.0, ipykernel 7.4.0, and pytest 9.1.1.
- The `.tools/` and `.venv/` directories are ignored; only dependency inputs and the lockfile are committed.

## Synthetic fixtures and notebook

`tests/data/wf-055/` contains one synthetic facility `Point` and one synthetic district `MultiPolygon` with two components. Neither fixture is derived from the user's archived facilities or real administrative boundaries. The test uses a GeoPandas GeoDataFrame in EPSG:4326 and checks an inside point plus an outside point. `notebooks/gis_puskesmas.ipynb` installs from the lock, prints dependency versions, validates the geometries, performs the spatial predicate, and displays a Folium marker explicitly labeled synthetic.

## Verification

| Command/action | Expected | Actual |
|---|---|---|
| `uv python install 3.12` | Provision local CPython 3.12 | CPython 3.12.15 installed under ignored `.tools/python/`; global PATH/registry shim unavailable but not needed |
| `uv venv --python <workspace Python 3.12> --seed .venv` | Isolated 3.12 environment | Created; seed pip 26.2.2 |
| `uv pip compile --python-version 3.12 --universal --generate-hashes requirements.in -o requirements.lock` | Cross-platform, pinned, hash-checked lock | Resolved 53 packages |
| `uv pip sync --python .venv/Scripts/python.exe requirements.lock` | Install locked environment | 48 packages installed for Windows/Python 3.12 |
| `.venv/Scripts/python.exe -m pytest tests/python/test_environment.py -q` | Validate imports and synthetic point/polygon behavior | 2 passed |
| Execute notebook code cells locally after skipping its `%pip` install cell | Notebook imports, checks geometry, and renders Folium map | Passed; printed GeoPandas 1.2.0 and Folium 0.20.0 and `Synthetic spatial preflight passed.` |
| Inspect available Colab browser session | Run notebook in user Colab environment | Not run: no browser surfaces were available; `iab` browser could not be created |

## Remaining work

The local environment and fixture checks pass, but the ticket requires a real Colab run. Do not mark WF-055 done until the notebook is run in Colab and the output is recorded. This local preflight does not validate Colab's current interpreter, Google account state, or runtime package installation.
