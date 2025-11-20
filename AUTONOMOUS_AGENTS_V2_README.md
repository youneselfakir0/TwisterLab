## Monitoring Agent Improvements (2025-11-20)

- `MonitoringAgent` persists summary-detected `failed_components` across runs, improving recheck determinism and correctness.
- `investigate_related` boolean toggle (default True) allows enabling/disabling related-service checks for deeper diagnostics (useful for prod and integration tests).
- `execute(context)` supports per-run override of `investigate_related` with context param `investigate_related` True/False.

Use these features to reduce test flakiness and to tune the depth of diagnostics for production vs test environments.
