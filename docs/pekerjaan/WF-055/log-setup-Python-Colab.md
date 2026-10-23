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
| `uv pip compile --python-version 3.12 --universal --generate-hashes requirements.in -o requirements.lock` | Cross-platform, pinned, hash-checked lock | Resolved 106 packages after adding Jupyter Notebook |
| `uv pip sync --python .venv/Scripts/python.exe requirements.lock` | Install locked environment | 103 applicable packages installed for Windows/Python 3.12 |
| `.venv/Scripts/python.exe -m pytest tests/python/test_environment.py -q` | Validate imports and synthetic point/polygon behavior | 2 passed |
| Execute notebook code cells locally after skipping its `%pip` install cell | Notebook imports, checks geometry, and renders Folium map | Passed; printed GeoPandas 1.2.0 and Folium 0.20.0 and `Synthetic spatial preflight passed.` |
| Inspect available Colab browser session | Run notebook in user Colab environment | Not run: no browser surfaces were available; `iab` browser could not be created |

## Remaining work

The local environment and fixture checks pass, but the ticket requires a real Colab run. Do not mark WF-055 done until the notebook is run in Colab and the output is recorded. This local preflight does not validate Colab's current interpreter, Google account state, or runtime package installation.

## Local runtime follow-up ? 23 October 2026

The user authorized the local runtime startup. Jupyter Notebook 7.6.3 is installed in `.venv`; `scripts/analysis/start-colab-local-runtime.ps1` starts it on `127.0.0.1:8888`, enables only the Colab origin, retains token authentication, and avoids automatically opening a browser. Runtime/config/profile files stay in ignored `.tools/`; the runtime directory is separated by Windows username to avoid cookie-file ownership conflicts between the sandbox and owner account.

Run from the repository root in PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\analysis\start-colab-local-runtime.ps1
```

The execution-policy override applies only to that child process. Copy the authenticated URL shown by Jupyter into Colab's **Connect to local runtime** dialog. The current background server's URL is in the local ignored `.tools/colab/stderr.log`; do not commit that log or paste its token into evidence. Follow Google's setup guide: https://research.google.com/colaboratory/local-runtimes.html .

Actual verification: all notebook cells executed through `nbclient` in a real local Jupyter kernel, from the `notebooks/` directory. The hashed installer ran against the already installed environment with `PIP_NO_INDEX=1`; GeoPandas/Folium imports and the synthetic spatial check passed; pytest reported 2 passed and 1 warning. The notebook includes the test runner cell so the same checks can run from Colab. The complete locally executed notebook is ignored at `.tools/colab/executed-preflight.ipynb`; concise results are in `hasil-fixture-awal.txt`.

Startup troubleshooting: the initial PowerShell policy blocked the script; the child-process bypass resolved it. Windows profile permissions required keeping Jupyter/IPython directories in the workspace and separating runtime directories by account. An attempted duplicate startup correctly failed because port 8888 was already in use; the existing runtime was retained. Final authenticated API verification on the running server returned HTTP 200 for status, 201 for creating a temporary python3 kernel, and 204 for deleting that kernel. Token authentication was enabled and the allowed origin was `https://colab.research.google.com`.

The available browser inventory was empty. This verifies the local Jupyter runtime, not an actual Colab frontend connection or a hosted Google runtime. WF-055 stays blocked pending the required Colab run; no external review or Colab result is claimed.
