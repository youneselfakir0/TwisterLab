# Rotate & Test Runbook (Staging)

This runbook shows how to safely run the rotate-and-test workflow on a staging host. It covers the GitHub Action inputs, the verification steps, and expected outputs.

Prerequisites

- Ensure the following secrets are present in the GitHub repository: `STAGING_SSH_PRIVATE_KEY`, `STAGING_SSH_HOST`, `STAGING_SSH_USER`, `STAGING_SSH_PORT` (optional), and `STAGING_SSH_DEPLOY_DIR`.
- The staging host must have Docker, Docker Swarm, and PowerShell Core (pwsh) installed and accessible to the SSH user.
- The staging host should be configured with the same service/stack names used by production where possible.

How to run (dry-run recommended first)

1. Open the repository actions UI and find `Rotate & Test (Staging)`.

2. Choose `Run workflow` and set the inputs (recommended dry-run for first run):
   - environment: `staging`
   - apply: `false` (dry-run)
   - rotate_postgres: `true` / `false` (as needed)
   - rotate_redis: `true` / `false` (as needed)
   - rotate_grafana: `true` / `false` (as needed)
   - restart_grafana: `true` / `false` (only if a restart is desired)
   - grafana_service_name: `twisterlab_monitoring_grafana` (optional; if empty, the script will attempt to auto-detect a grafana service name)

3. Start the run and wait for the job to complete.

What happens during the run
 - The full repository is `scp`'d to the staging host under `STAGING_SSH_DEPLOY_DIR`.
 - The remote host ensures PowerShell Core (`pwsh`) is available then runs `rotate_and_test.ps1` with the chosen flags.
 - If `apply` is false — a dry-run is performed. The script generates new secure passwords (printed in logs), but does not update Docker secrets.
 - The verification checks run (smoke checks, DB/Redis connect, monitoring, Grafana datasources, and pytest). These may fail on local environments if the staging host lacks services, in which case investigate the environment first.
 - Logs are copied back to GitHub Actions artifacts under `rotation-logs` and a rotation issue is created summarizing the artifacts found.

Interpreting results
 - The action will upload `logs/rotate_*` files. Each file contains timestamps and the result of each step.
 - If verification fails, open the logs and the rotation issue for details and followable steps. Depending on the failure, consider re-running the job after addressing the issue.

Rollback & Post-rotation
 - If the rotation resulted in an applied change and the stack or services cannot pick the new secret, rotate back using a saved previous secret or follow your organization's rollback process.
 - Always inform stakeholders when production rotation is scheduled, and ensure a valid rollback plan exists.

Notes
- The `grafana_service_name` input lets you explicitly specify which Docker Swarm service to restart after a Grafana secret rotation; if omitted, the script attempts to detect a candidate service automatically.
- For true production rotations, run a canary first via `canary=true` and `canary_service=<service>`.

----

Generated: $(Get-Date -Format o)
