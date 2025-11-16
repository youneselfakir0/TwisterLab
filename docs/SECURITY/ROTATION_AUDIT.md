# Secrets Rotation & Archive Sanitization Audit

This document summarizes the automated sanitization and rotation activities performed by the security automation tools.

Sanitized branch
----------------
- Branch created: `sanitized/archives-20251116`
- PR URL: https://github.com/youneselfakir0/TwisterLab/pull/new/sanitized/archives-20251116

Sanitization
------------
- Script used: `scripts/sanitize_archives.py --apply --backup-dir sanitized_archives`
- Sanitized files written to: `sanitized_archives/`
- A sanitized copy of the file(s) that exceeded our patterns were added and committed in the branch above. Files were sanitized by replacing passwords with `<REDACTED>` values.

Rotation
--------
- The following per-secret rotation scripts were added to the repository under `scripts/`:
	- `scripts/rotate_postgres_secret.ps1` — rotate `postgres_password` Docker secret
	- `scripts/rotate_redis_secret.ps1` — rotate `redis_password` Docker secret
	- `scripts/rotate_grafana_secret.ps1` — rotate `grafana_admin_password` Docker secret (optionally restart Grafana service)
	- `scripts/rotate_and_test.ps1` — orchestrator that calls per-secret rotation scripts and runs verification checks; supports `-GrafanaServiceName` to pass an explicit Grafana service name to the rotate script.
 - `scripts/rotate_and_test.ps1` — orchestrator that calls per-secret rotation scripts and runs verification checks; supports `-GrafanaServiceName` to pass an explicit Grafana service name to the rotate script.
	 - Supports `-ServiceName` to explicitly specify the service to restart; if omitted the script will attempt to auto-detect a Grafana service name (swarm service or running container) and restart it automatically.

Rotation logs
-------------
- Rotations write logs in `logs/rotate_*.log` mentioning timestamp and success.

Checklist (post rotation)
-------------------------
1. After rotation, update external systems that use the old credential (3rd-party services, backup systems, DSNs that still embed passwords).
2. Restart relevant services (grafana/monitoring/exporters/ingress) so new secrets are loaded.
3. Verify dry-run succeeded before running real rotation.

Next steps
----------
1. If the rotation was performed on a production system: notify stakeholders, update runbooks, and rotate secrets in dependent services.
2. Configure branch protection in GitHub (see `scripts/create_branch_protection.ps1`) and require PR checks in Branch Protect Rules.
