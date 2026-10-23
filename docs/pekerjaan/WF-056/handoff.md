Status update: done. Hosted normal run 39968079070 passed; diagnostic run 39967313521 failed at the intentional assertion. The clean-checkout storage defect is fixed. Earlier preparation notes below are historical.

# WF-056 handoff

Status: in_review until the hosted normal and intentional failure runs are observed. The implementation and local checks are ready. Scope: workflow, runner configurations, PostGIS service smoke test, browser smoke test, opt-in failure probe and evidence.

Inputs: completed WF-054/WF-055 and the accepted WF-031 CI design. Local checks passed with an explicit spatial skip. No production database credentials or actual source data enter CI. Use the authenticated project owner Git identity; plain descriptive commit title.

Next: push the implementation, observe GitHub Actions and record exact results. Failure diagnostics must not be misreported as normal pipeline failures or suppressed. Fix genuine errors before advancing to WF-057.
