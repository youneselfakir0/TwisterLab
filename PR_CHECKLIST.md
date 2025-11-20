PR: MonitoringAgent deterministic health checks

Checklist for reviewers
----------------------
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

Suggested CI checks to enable for the PR:
- Focused test run: `pytest -q -k monitoring`.
- Linting: `ruff check` for the modified files.
- Type checking: `mypy agents/core/monitoring_agent.py`.

If approved, include notes in the PR about any additional follow-up tasks (lint/mypy sweep, instrumentation metrics, Grafana dashboard updates).
