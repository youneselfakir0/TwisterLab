<!-- PR template: ensure security checks are validated and rotated if needed -->

## PR Checklist
- [ ] Tests pass (`ci`)
- [ ] Secret scan (`secret-scan`) passed
- [ ] If any archived or sensitive files are modified, secrets are rotated and rotation logs added
- [ ] `pre-commit` hooks ran locally and no issues present
 - [ ] One (1) reviewer approved (2 for infra changes)

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
