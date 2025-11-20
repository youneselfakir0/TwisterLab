PR: MonitoringAgent deterministic health checks & persisted failed_components

Summary
-------
This change improves the MonitoringAgent's determinism and resilience by:

- Persisting `failed_components` between runs to avoid clearing them during
  the same run and enabling deterministic rechecks.
- Adding `investigate_related` flag for configurable, deeper diagnostics
  (e.g., database -> cache/api/agents) — default True.
- Supporting the `investigate_related` per-run override in `execute(context)`
  so test and orchestration flows can be more efficient and deterministic.
- Introducing `initial_prev_failed` to `_monitor_system` to prevent
  accidental clearing of persisted failures mid-run.

Files changed
-------------
- `agents/core/monitoring_agent.py` — core logic + new flag and safety checks
- `tests/test_monitoring_last_failed_persist.py` — new test adjustments
- `tests/test_monitoring_last_failed_components_more.py` — added tests and toggles
- `docs/OPERATIONS/MONITORING_README.md` — documentation on feature and usage

Validation & QA
-------------
Unit/integration checks run locally:

1. Monitoring behavior (subset):
   - `pytest -q -k monitoring` -> 56 tests passed (local)
2. Specific tests added/updated:
   - `pytest -q tests/test_monitoring_last_failed_persist.py`
   - `pytest -q tests/test_monitoring_last_failed_components_more.py`
   - `pytest -q tests/test_mcp_call_counts.py`

All listed test subsets passed locally.

Notes for reviewers
-------------------
- The change intentionally keeps many `except Exception:` blocks to avoid
  brittle behavior and keep tests deterministic. We can tighten when we
  tackle a full lint/mypy sweep.

Next steps (recommended)
-----------------------
1. Open a PR from this branch (feature/monitoring/deterministic-health-checks).
2. Validate the PR in CI on all monitoring and integration tests.
3. Follow up with a modest lint & mypy cleanup PR for changed files.

PR checklist (local)
--------------------
1. Run the monitoring test subset:
   ```powershell
   pytest -q -k monitoring
   ```
2. Run the dedicated tests:
   ```powershell
   pytest -q tests/test_monitoring_last_failed_persist.py
   pytest -q tests/test_monitoring_last_failed_components_more.py
   pytest -q tests/test_mcp_call_counts.py
   ```
3. Validate that `CHANGELOG.md` and `docs/OPERATIONS/MONITORING_README.md` are updated.

If you'd like, I can also create a PR branch and draft the PR summary and CI checks.
