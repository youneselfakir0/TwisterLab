<!-- PR template: ensure security checks are validated and rotated if needed -->

## PR: MonitoringAgent deterministic health checks & persisted failed_components

### Summary
This change improves the MonitoringAgent's determinism and resilience by:

- Persisting `failed_components` between runs to avoid clearing them during
  the same run and enabling deterministic rechecks.
- Adding `investigate_related` flag for configurable, deeper diagnostics
  (e.g., database -> cache/api/agents) — default True.
- Supporting the `investigate_related` per-run override in `execute(context)`
  so test and orchestration flows can be more efficient and deterministic.
- Introducing `initial_prev_failed` to `_monitor_system` to prevent
  accidental clearing of persisted failures mid-run.

### Files changed
- `agents/core/monitoring_agent.py` — core logic + new flag and safety checks
- `agents/metrics.py` — added monitoring-specific metrics
- `tests/test_monitoring_last_failed_persist.py` — new test adjustments
- `tests/test_monitoring_last_failed_components_more.py` — added tests and toggles
- `docs/OPERATIONS/MONITORING_README.md` — documentation on feature and usage

### Validation & QA
Unit/integration checks run locally:

1. Monitoring behavior (subset):
   - `pytest -q -k monitoring` -> 56 tests passed (local)
2. Specific tests added/updated:
   - `pytest -q tests/test_monitoring_last_failed_persist.py`
   - `pytest -q tests/test_monitoring_last_failed_components_more.py`
   - `pytest -q tests/test_mcp_call_counts.py`

All listed test subsets passed locally.

### Notes for reviewers
- The change intentionally keeps many `except Exception:` blocks to avoid
  brittle behavior and keep tests deterministic. We can tighten when we
  tackle a full lint/mypy sweep.

### Next steps (recommended)
1. Open a PR from this branch (feature/monitoring/deterministic-health-checks).
2. Validate the PR in CI on all monitoring and integration tests.
3. Follow up with a modest lint & mypy cleanup PR for changed files.

## PR Checklist
- [ ] Tests pass (`ci`)
- [ ] Secret scan (`secret-scan`) passed
- [ ] If any archived or sensitive files are modified, secrets are rotated and rotation logs added
- [ ] `pre-commit` hooks ran locally and no issues present
- [ ] One (1) reviewer approved (2 for infra changes)
- [ ] Confirm that `CHANGELOG.md` and `PR_DESCRIPTION.md` describe the changes.
- [ ] Run targeted tests:
  ```powershell
  pytest -q -k monitoring
  pytest -q tests/test_monitoring_last_failed_persist.py
  pytest -q tests/test_monitoring_last_failed_components_more.py
  pytest -q tests/test_mcp_call_counts.py
  ```
- [ ] Check `docs/OPERATIONS/MONITORING_README.md` updated with usage & flag details.
- [ ] Review the instrumentation log statements for clarity and security.
- [ ] Run `python -m py_compile agents/core/monitoring_agent.py` to ensure no syntax errors.

### Pre-merge staging verification (recommended)

- [ ] Run the 'Rotate & Test (Staging)' workflow in GitHub Actions (dry-run first): `Rotate & Test (Staging)` with `apply=false`.
- [ ] If the dry-run passes, run canary `Rotate & Test (Staging)` with `canary=true` and `canary_service=<service>` and verify logs.
- [ ] If canary passes, re-run with `apply=true` to perform the rotation on staging.

## Security Impact
Please check one:
- [ ] No secrets or sensitive data in this change
- [ ] Secrets rotated and proof committed
- [ ] Sanitized archived files with PR

If secrets were rotated, mention the rotation job output or logs and updated services.

If you used a Grafana service name override when testing, include `grafana_service_name: twisterlab_monitoring_grafana` as appropriate.
