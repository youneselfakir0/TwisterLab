# Changelog

## Unreleased

### Monitoring
- Persist `failed_components` across runs to avoid clearing during same run and to enable deterministic rechecks.
- Add `investigate_related` flag to control whether related services should be checked when a primary service detects an issue.
- Add per-run override `investigate_related` to `execute` context for testing and per-request control.
- Add tests for failed components persistence, partial recovery, multi-failures, and `investigate_related` toggles.
- Refactor `_check_health_all` and `_monitor_system` to support the above behaviors with minimal disruption.

## 2025-11-20
- Initial checkpoint for MonitoringAgent rework.


