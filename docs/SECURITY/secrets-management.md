# Secrets Management - TwisterLab

**Version**: 1.0  
**Last Updated**: 2025-11-13

---

## Overview

TwisterLab uses **Docker Secrets** for secure secrets management in production.

**Benefits**:
- ✅ No passwords in code or Git
- ✅ Encrypted at rest and in transit
- ✅ Fine-grained access control
- ✅ Easy rotation without rebuild
- ✅ Audit trail

---

## Required Secrets

### 1. postgres_password (32 bytes)
**Used by**: PostgreSQL database  
**File**: `secrets/postgres_password.txt`  
**Access**: postgres service only

### 2. redis_password (32 bytes)
**Used by**: Redis cache  
**File**: `secrets/redis_password.txt`  
**Access**: redis service + api

### 3. admin_password (24 bytes)
**Used by**: Admin user authentication  
**File**: `secrets/admin_password.txt`  
**Access**: api service

### 4. jwt_secret (64 bytes)
**Used by**: JWT token signing  
**File**: `secrets/jwt_secret.txt`  
**Access**: api service

### 5. webui_secret_key (48 bytes)
**Used by**: OpenWebUI session management  
**File**: `secrets/webui_secret_key.txt`  
**Access**: webui service

### 6. grafana_admin_password (24 bytes)
**Used by**: Grafana admin login  
**File**: `secrets/grafana_admin_password.txt`  
**Access**: grafana service

---

## Setup Instructions

### Initial Setup

1. **Generate secrets**:
   ```powershell
   cd C:\twisterlab
   powershell -ExecutionPolicy Bypass -File scripts\generate-secrets.ps1 -Force
   ```

2. **Verify generation**:
   ```powershell
   ls secrets\*.txt
   # Should show 6 files
   ```

3. **Verify .gitignore**:
   ```bash
   # Ensure secrets/ is excluded
   cat .gitignore | grep secrets
   ```

4. **Deploy with secrets**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Verify secrets in containers**:
   ```bash
   # Check secrets are mounted
   docker exec twisterlab-postgres-prod ls /run/secrets/
   ```

---

## Secrets Rotation

**When to rotate**:
- Every 90 days (recommended)
- After security incident
- When employee leaves
- Before major releases

**How to rotate**:

1. **Generate new secrets** (backs up old):
   ```powershell
   powershell -File scripts\generate-secrets.ps1 -Rotate
   ```

2. **Redeploy services**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --force-recreate
   ```

3. **Verify services healthy**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

4. **Archive old secrets backup**:
   ```bash
   # Old secrets in secrets/backup/ with timestamp
   ls secrets/backup/
   ```

---

## Accessing Secrets

### In Docker Services

Secrets are mounted at `/run/secrets/<secret_name>`:

**Python example**:
```python
def get_secret(secret_name):
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path) as f:
            return f.read().strip()
    return os.getenv(secret_name.upper())  # Fallback to env
```

**Environment variables**:
```bash
# .env.prod uses _FILE suffix
POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
ADMIN_PASSWORD_FILE=/run/secrets/admin_password
SECRET_KEY_FILE=/run/secrets/jwt_secret
```

---

## Security Best Practices

### DO ✅
- Use Docker Secrets in production
- Rotate secrets every 90 days
- Backup secrets encrypted
- Use strong passwords (>24 chars)
- Audit secret access logs
- Separate secrets per environment

### DON'T ❌
- Commit secrets/ to Git
- Hardcode passwords in code
- Share secrets via email/chat
- Reuse passwords across services
- Store secrets in plain text logs
- Use weak passwords

---

## Troubleshooting

### Secret not found in container

**Symptoms**: Service can't read secret  
**Check**:
```bash
docker exec <container> ls /run/secrets/
docker logs <container>
```

**Fix**: Ensure secret defined in docker-compose secrets: section

### Permission denied

**Symptoms**: Can't read secret file  
**Check**:
```bash
ls -l secrets/
```

**Fix**: Secrets should be 600 (owner read/write only)

### Service won't start

**Symptoms**: Container crashes at startup  
**Check**:
```bash
docker logs <container>
```

**Fix**: Verify secret files exist and contain valid data

---

## Emergency Procedures

### Secret Compromised

1. **Immediate**:
   - Generate new secret: `generate-secrets.ps1 -Rotate`
   - Redeploy all services: `docker-compose up -d --force-recreate`

2. **Investigation**:
   - Check audit logs
   - Review access history
   - Identify breach vector

3. **Prevention**:
   - Update security procedures
   - Rotate all secrets
   - Review access controls

### Secret Lost

1. **Recovery**:
   - Check backups: `secrets/backup/`
   - If no backup: Generate new + reconfigure

2. **Impact**:
   - PostgreSQL: Database inaccessible
   - Redis: Cache unavailable
   - JWT: All sessions invalid
   - Admin: Can't login

---

## Compliance

### Audit Requirements

**What to log**:
- Secret generation timestamp
- Secret rotation events
- Access attempts (success/failure)
- Secret exposure incidents

**Where**:
- `logs/audit.db` (SQLite)
- Prometheus metrics
- System logs

### Retention Policy

- Active secrets: Current + 1 rotation backup
- Archived secrets: Encrypted, 1 year retention
- Audit logs: 7 years retention

---

## References

- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)

---

**Maintained by**: TwisterLab Security Team  
**Contact**: security@twisterlab.local  
**Last Review**: 2025-11-13
