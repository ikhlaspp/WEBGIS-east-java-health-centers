# District indicator verification — 2026-10-25

Implemented in python/gis_pipeline/analysis/indicators.py and scripts/analysis/indicators.py. The Python package is shared by the CLI and later notebook integration; no formula is duplicated in presentation code.

The immutable WF-049 formula-fixtures.json examples, originally frozen before implementation, are the oracle. All nine normal reference cases and four invalid reference cases pass. Additional tests cover bool/float count rejection, nonfinite/invalid area, source precision/storage overflow, missingness, coordinate counts, HALF_UP display, fixed ratio scale, aggregate totals, sum of local deficits, partial population coverage, and provenance/duplicate district rejection. There are 38 Python tests. The PostgreSQL numeric reference compares the same nine cases with absolute tolerance 1e-9 in isolated CI.

P and F are administrative counts; missing coordinates do not subtract facilities. Values remain Decimal internally, with numeric(24,12) serialization only at the output boundary. A must fit numeric(16,6) without source precision loss. Overflow raises an error. T changes need/deficit, while facilities_per_30000 retains its fixed named scale. Null values carry per-metric reasons. Aggregates use explicit member sets, complete-scope totals, count-weighted quality percentages, and summed local deficits. The complete-population subset is separately labeled with its own F.

CLI: `python scripts/analysis/indicators.py --input snapshot.json --sha256 <digest> --output new-output.json --threshold 30000`. Input contains release_id, method_version, code_revision, boundary_hash and districts (district_id,P,F,A,optional coordinate_present/eligible). Output retains source fields, parameters, formula version and hashes. It is a candidate calculation, not an accepted/published analysis run. Existing output files are not overwritten. No real curated dataset or deployment database was processed.

Run: `.venv/Scripts/python.exe -m pytest tests/python/test_indicators.py -q` -> 38 passed. Full Python regression and real SQL CI results will be appended after execution.

CI 40178837833 succeeded at b12544a04de5c6179e09559701e30339bc8c64da: 259 Python regressions and the real PostgreSQL comparison of all nine frozen formula examples passed. Delivery is verified on origin/work/continued-implementation.
