# Security Readiness — DevOps, Devs & CI

Overview
--------
This document organizes the 'Security Ready' procedures for developers, operations, and CI/CD systems. It explains how to sanitize archives, rotate secrets after a leak, and enforce policies in CI.

Goals
-----
- Keep secrets out of source code and repository history.
- Sanitize historical artifacts (archives & backups) and handle leaks responsibly.
- Make the CI fail if inline secrets are introduced.
- Ensure secret rotation process is clear and repeatable.

Roles & Responsibilities
------------------------
- Developers: Use `_FILE`/`__FILE` patterns, do not commit secrets, follow pre-commit hooks and security docs.
- DevOps/Operations: Manage Docker Swarm secrets, run `security.ps1` to create/rotate secrets, and coordinate vaulted secret delivery.
- CI: Enforce pre-commit checks, run `ci_secret_scan.py` & `detect-secrets`, and block PRs with inline secrets.

Sanitizing archives & backups
-----------------------------
1. Run local scan and dry-run to list leaked entries:

```powershell
# Dry-run (no writes)
python scripts/sanitize_archives.py --root . --patterns "archive/**" "backups/**" --quiet
```

2. Create sanitized copies:

```powershell
python scripts/sanitize_archives.py --apply --backup-dir sanitized_archives
```

3. Create PR with sanitized changes using branch helper (PowerShell):

```powershell
.\scripts\create_sanitized_branch.ps1 -BranchName sanitized/archives-$(Get-Date -Format yyyyMMdd) -BackupDir sanitized_archives
```

4. Review the sanitized PR in code review. Ensure that any recovered secrets are rotated prior to merge.

Secret rotation (if leaks found)
-------------------------------
If leaks are confirmed, rotate the affected secrets using the provided scripts.

1. Rotate in Docker Swarm:

```powershell
.\scripts\rotate_leaked_secrets.ps1 -Force
```

2. Update any external systems (DNS, 3rd-party services) with the new credentials.
3. Apply new secrets locally / in CI: Ensure they are added to GitHub secrets and to infrastructure.

CI & PR enforcement
--------------------
1. The CI pipeline runs `scripts/ci_secret_scan.py` as part of the lint step and `zricethezav/gitleaks-action` on PRs and pushes.
2. Pre-commit contains `detect-secrets` and `ruff` hooks to prevent accidental commits.
3. Branch protection: enforce the `ci` and `secret-scan.yml` workflows to be successful before allowing PR merges (set up on GitHub UI).

Developer workflow (do's & don'ts)
--------------------------------
- DO use `docker secret create` or `secrets/` files (local) and `_FILE`/`__FILE` in env.
- DO run `pre-commit` and `ci_secret_scan.py` locally before pushing.
- DO rotate secrets immediately if you suspect a leak.
- DO open a PR for any sanitized changes — don't push replacements directly to `main`.
- DON'T commit secrets, passwords, tokens, or private keys.

Appendix: Tools & Scripts
-------------------------
- `scripts/sanitize_archives.py` — list and optionally redact sensitive occurrences in logs/archives.
- `scripts/create_sanitized_branch.ps1` — create a branch and commit sanitized files for PR review.
- `scripts/rotate_leaked_secrets.ps1` — wrapper to rotate Docker secrets using `infrastructure/scripts/security.ps1`.
- `scripts/ci_secret_scan.py` — CI/PR scanner to detect inline secret patterns.
- `infrastructure/scripts/security.ps1` — manage Docker Swarm secrets, rotation, auditing.

-- END --
