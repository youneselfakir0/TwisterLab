# TwisterLab Security Guide — Secrets Management

This project follows a _secrets-first_ approach: avoid committing plaintext credentials, favor Docker secrets and file-backed environment variables.

Key practices:

- Use Docker secrets and the `_FILE`/`__FILE` pattern for all services (e.g. `POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password`).
- Avoid embedding passwords in `DATABASE_URL` — use `DATABASE_URL` without the password and `POSTGRES_PASSWORD_FILE` to pass the secret file at runtime.
- Read secrets at runtime in Python using `os.getenv("VAR__FILE")` or our `_read_env_file()` helper that reads `_FILE`/`__FILE` file secrets.
- Keep secrets out of code and repositories — archive/backups must be audited and sanitized by security team.
- Use the built-in CI policy and `scripts/ci_secret_scan.py` to block accidental inline secrets in PRs.

Developer guide:

1. Create secret files locally for community deployment using `deploy_community.py` or `infrastructure/scripts/create_secrets.ps1`.
2. Use `POSTGRES_PASSWORD_FILE` / `GF_SECURITY_ADMIN_PASSWORD__FILE` env variables or Docker secret references.
3. For local development, secrets can be placed under `secrets/` to keep parity with Docker secrets.
4. For deployment: deploy secrets to Docker Swarm using `security.ps1 -Action create-secrets`.
5. Rotate secrets using `security.ps1 -Action rotate-passwords` and update services as needed.

Audit and sanitize:

- Use `scripts/ci_secret_scan.py` in CI to block direct secrets. This is enforced in `ci.yml`.
- Use `scripts/sanitize_archives.py --dry-run` to discover hard-coded secrets in archives and logs. To create sanitized copies, run `scripts/sanitize_archives.py --apply --backup-dir sanitized_archive/` and review results.

If you find a hard-coded secret in a historical file (archive, backup, or log):

1. Do not change the file in-place. Create a sanitized copy, and move the original to an offline secure storage if needed.
2. Replace the hard-coded secret with a reference to a secret file or variable.
3. Rotate the leaked credential immediately using the `security.ps1` rotate function.

If you need help or have questions about secrets policy, open an issue or contact the security lead.
