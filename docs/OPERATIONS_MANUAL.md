# 🛠️ TwisterLab Operations Manual

**Version**: 1.0.0  
**Last Updated**: 2025-11-02  
**Audience**: Operations Team, SRE, DevOps  
**Classification**: INTERNAL

---

## 📋 Table of Contents

1. [Daily Operations](#daily-operations)
2. [Weekly Maintenance](#weekly-maintenance)
3. [Monthly Tasks](#monthly-tasks)
4. [Incident Response](#incident-response)
5. [Backup & Recovery](#backup--recovery)
6. [Performance Tuning](#performance-tuning)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting Playbooks](#troubleshooting-playbooks)

---

## 🌅 Daily Operations

### Morning Health Checks (15 minutes)

#### 1. Service Status Verification

```powershell
# Check all containers
docker-compose -f docker-compose.production.yml ps

# Expected output: All services "Up" and "healthy"
```

**Checklist**:
- [ ] PostgreSQL: healthy
- [ ] Redis: healthy
- [ ] API (x2 replicas): healthy
- [ ] Ollama: healthy
- [ ] Prometheus: Up
- [ ] Grafana: Up
- [ ] Nginx: Up

#### 2. Grafana Dashboard Review

**URL**: https://monitoring.twisterlab.com (production) or http://localhost:3003 (staging)

**Dashboards to check**:
1. **TwisterLab Overview**
   - System CPU < 75%
   - System Memory < 80%
   - API response time < 1.5s
   - Error rate < 5%

2. **Agent Performance** (when created)
   - All 7 agents reporting
   - Success rate > 95%
   - No agent stuck/frozen

3. **Infrastructure Health** (when created)
   - All containers running
   - No disk space issues (< 85%)
   - Network traffic normal

#### 3. Log Review (Critical Errors)

```powershell
# Check API logs for errors
docker logs twisterlab-api-1 --since 24h | Select-String "ERROR|CRITICAL"

# Check database logs
docker logs twisterlab-postgres --since 24h | Select-String "ERROR|FATAL"

# Check Ollama logs (GPU issues)
docker logs twisterlab-ollama --since 24h | Select-String "error|fail"
```

**Action**: If > 10 errors in 24h, investigate immediately.

#### 4. Metrics Snapshot

```powershell
# Quick metrics check
curl http://localhost:9090/metrics | Select-String "response_time|error_rate|cpu_usage"
```

**Baseline values** (production):
- `api_response_time_avg_ms`: < 500ms
- `api_error_rate`: < 5%
- `system_cpu_usage_percent`: < 75%
- `system_memory_usage_percent`: < 80%

---

## 📅 Weekly Maintenance

### Monday Morning (30 minutes)

#### 1. System Updates Check

```powershell
# Check for Docker image updates
docker-compose -f docker-compose.production.yml pull

# Check for security updates (if updates available)
docker images | Select-String "twisterlab|postgres|redis|ollama"
```

**Action**: Schedule update during low-traffic window if critical security patches.

#### 2. Database Maintenance

```powershell
# Connect to PostgreSQL
docker exec -it twisterlab-postgres psql -U twisterlab_prod -d twisterlab_prod

# Run maintenance commands
VACUUM ANALYZE;
REINDEX DATABASE twisterlab_prod;

# Check database size
SELECT pg_size_pretty(pg_database_size('twisterlab_prod'));

# Check largest tables
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

**Thresholds**:
- Database size > 50GB → Consider archiving old data
- Single table > 10GB → Review indexes and partitioning

#### 3. Backup Verification

```powershell
# List recent backups
aws s3 ls s3://twisterlab-backups-prod/ --recursive | Sort-Object -Property LastWriteTime -Descending | Select-Object -First 10

# Test restore (on staging)
# See Backup & Recovery section
```

**Requirements**:
- Daily backups for last 7 days: present
- Weekly backups for last 4 weeks: present
- Monthly backups: present

#### 4. Performance Review

**Review Grafana**:
1. Check p95/p99 latency trends (week over week)
2. Identify any degradation (> 10% increase)
3. Check slow query logs in PostgreSQL

```sql
-- Top 10 slowest queries (last 7 days)
SELECT
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Action**: If query > 1s, optimize with indexes or query rewrite.

---

## 📆 Monthly Tasks

### First Monday of Month (2 hours)

#### 1. Security Audit

```powershell
# Run security scan on all images
docker scan twisterlab-api:production
docker scan postgres:16-alpine
docker scan redis:7-alpine

# Check for CVEs
bandit -r agents/ -f json -o security_scan_$(Get-Date -Format "yyyyMMdd").json
safety check --json > dependency_scan_$(Get-Date -Format "yyyyMMdd").json
```

**Action**: Patch any HIGH or CRITICAL vulnerabilities within 7 days.

#### 2. Capacity Planning

**Collect metrics**:
- Average tickets/day (last 30 days)
- Peak concurrent users
- Database growth rate (GB/month)
- API response time trends

**Forecast next 3 months**:
- Will we exceed 80% CPU/Memory?
- Will database exceed 80% disk?
- Do we need horizontal scaling?

**Document in**: `reports/capacity_planning_YYYYMM.md`

#### 3. Disaster Recovery Test

**Simulate**:
1. Database failure → Restore from backup
2. API container crash → Automatic restart (health check)
3. Full system failure → Blue-green rollback

**Document results**: `reports/dr_test_YYYYMM.md`

**Success criteria**:
- RTO (Recovery Time Objective): < 15 minutes
- RPO (Recovery Point Objective): < 1 hour (last backup)

#### 4. Password Rotation

**Rotate** (every 90 days):
- Database passwords
- Redis password
- API secret keys
- Grafana admin password
- AWS S3 access keys

**Process**:
1. Generate new passwords (use `generate_production_passwords.ps1`)
2. Update `.env.production` on production server
3. Restart affected services (blue-green deployment)
4. Update encrypted credentials file
5. Test all services after rotation
6. Document rotation date

---

## 🚨 Incident Response

### Severity Levels

| Severity | Description | Response Time | Escalation |
|----------|-------------|---------------|------------|
| **P0 - Critical** | Complete outage, data loss | 5 minutes | Immediate |
| **P1 - High** | Major feature broken, >50% users affected | 15 minutes | Within 30 min |
| **P2 - Medium** | Minor feature broken, <50% users affected | 1 hour | Within 2 hours |
| **P3 - Low** | Cosmetic issue, no user impact | 1 day | Next business day |

### Incident Response Workflow

#### 1. Detection (0-5 minutes)

**Automated alerts** (Prometheus):
- API error rate > 10%
- API response time > 3s
- Database connection failures
- Disk space > 90%
- Container unhealthy for > 2 minutes

**Manual detection**:
- User reports
- Health check failures
- Log monitoring

#### 2. Triage (5-15 minutes)

**Questions to answer**:
1. What is the user-facing impact?
2. How many users are affected?
3. Is data at risk?
4. What is the estimated downtime?

**Assign severity** (P0-P3) and **notify** stakeholders.

#### 3. Diagnosis (15-60 minutes)

**Check in order**:
1. **Service status**: `docker-compose ps`
2. **Recent changes**: Check last deployment time
3. **Resource usage**: CPU, memory, disk, network
4. **Logs**: API, database, application logs
5. **External dependencies**: Ollama, Redis, network

**Common causes**:
- Deployment gone wrong → Rollback
- Resource exhaustion → Scale up or restart
- Database deadlock → Kill long-running queries
- Network issue → Check DNS, firewall, connectivity

#### 4. Resolution (varies)

**Quick fixes**:
- Restart unhealthy container: `docker-compose restart <service>`
- Rollback deployment: See [Rollback Procedures](#rollback-procedures)
- Kill long query: `SELECT pg_terminate_backend(pid);`
- Clear Redis cache: `docker exec twisterlab-redis redis-cli FLUSHDB`

**Longer fixes**:
- Code hotfix → Deploy via CI/CD
- Database migration → Run Alembic migration
- Configuration change → Update `.env`, restart services

#### 5. Communication

**Stakeholders to notify**:
- Operations team (Slack #incidents)
- Development team (if code issue)
- Management (if P0/P1)
- Users (if > 30 min outage)

**Status updates**:
- Every 30 minutes for P0/P1
- Hourly for P2
- When resolved for P3

#### 6. Post-Mortem (within 48 hours)

**Document**:
- Timeline of events
- Root cause analysis
- What went well / What went wrong
- Action items to prevent recurrence

**Template**: `reports/postmortem_YYYY-MM-DD.md`

---

## 💾 Backup & Recovery

### Backup Strategy

#### Daily Backups (Automated)

**Schedule**: 2:00 AM UTC (low traffic)

**Components backed up**:
1. **PostgreSQL database** (full dump)
2. **Redis snapshot** (RDB file)
3. **Ollama models** (weekly, large files)
4. **Application config** (.env, docker-compose.yml)

**Destination**: AWS S3 bucket `twisterlab-backups-prod`

**Retention**:
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months

**Script**: See `scripts/backup.sh` (runs in BackupAgent)

#### Manual Backup (Ad-hoc)

```powershell
# Database backup
docker exec twisterlab-postgres pg_dump -U twisterlab_prod -Fc twisterlab_prod > backup_manual_$(Get-Date -Format "yyyyMMddHHmmss").dump

# Redis backup
docker exec twisterlab-redis redis-cli BGSAVE

# Full system backup
docker-compose -f docker-compose.production.yml stop
tar -czf twisterlab_full_backup_$(Get-Date -Format "yyyyMMdd").tar.gz \
    .env.production \
    docker-compose.production.yml \
    data/

docker-compose -f docker-compose.production.yml start
```

### Recovery Procedures

#### Database Restore

```powershell
# 1. Stop API (to prevent writes)
docker-compose -f docker-compose.production.yml stop api

# 2. Download backup from S3
aws s3 cp s3://twisterlab-backups-prod/postgres_backup_YYYYMMDD.dump .

# 3. Restore database
docker exec -i twisterlab-postgres pg_restore -U twisterlab_prod -d twisterlab_prod -c < postgres_backup_YYYYMMDD.dump

# 4. Verify restore
docker exec twisterlab-postgres psql -U twisterlab_prod -d twisterlab_prod -c "SELECT COUNT(*) FROM tickets;"

# 5. Restart API
docker-compose -f docker-compose.production.yml start api
```

**Expected RTO**: 10-15 minutes  
**Expected RPO**: < 1 hour (last daily backup)

#### Full System Restore (Disaster Recovery)

**Scenario**: Complete infrastructure loss

**Steps**:
1. Provision new servers (AWS EC2, Azure VMs, etc.)
2. Install Docker + Docker Compose
3. Clone TwisterLab repository
4. Restore `.env.production` from encrypted backup
5. Pull Docker images: `docker-compose pull`
6. Restore database from S3
7. Start services: `docker-compose up -d`
8. Verify health checks
9. Update DNS to point to new servers
10. Monitor for 24 hours

**Expected RTO**: 2-4 hours  
**Expected RPO**: < 1 hour

---

## ⚡ Performance Tuning

### Database Optimization

#### Index Analysis

```sql
-- Find missing indexes (queries doing sequential scans)
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_tup_read DESC
LIMIT 10;

-- Find unused indexes (candidates for removal)
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

#### Connection Pooling Tuning

**Current settings** (`.env.production`):
```
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

**Adjust if**:
- High connection errors → Increase `DB_POOL_SIZE`
- Slow queries under load → Increase `DB_MAX_OVERFLOW`
- Connection timeouts → Increase `DB_POOL_TIMEOUT`

#### Query Performance

```sql
-- Enable query timing
\timing on

-- Analyze slow queries
EXPLAIN ANALYZE <your_query>;

-- Check query plan cache
SELECT * FROM pg_prepared_statements;
```

### API Performance

#### Worker Tuning

**Current** (`docker-compose.production.yml`):
```yaml
command: uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Formula**: `workers = (2 x CPU_cores) + 1`

**Adjust if**:
- High CPU usage (>80%) → Reduce workers
- Low CPU, high latency → Increase workers
- Memory issues → Reduce workers

#### Caching Strategy

**Redis cache** (already configured):
- Session data: 24h TTL
- API responses: 5min TTL
- Agent results: 1h TTL

**Optimize**:
```python
# Example: Cache expensive DB queries
@cache(ttl=300)  # 5 minutes
async def get_active_sops(db: AsyncSession):
    ...
```

### Ollama Performance

**GPU Optimization** (RTX 3060):
- Model: deepseek-r1:latest (fits in 12GB VRAM)
- Batch size: 8 (adjust based on VRAM usage)
- Context length: 4096 (increase if needed, up to 8192)

**Monitor GPU**:
```powershell
# Check GPU usage
docker exec twisterlab-ollama nvidia-smi

# Expected: <80% utilization, <11GB VRAM used
```

---

## 🔧 Common Tasks

### Add New User (OpenWebUI)

1. Access OpenWebUI: https://chat.twisterlab.com
2. Login as admin
3. Settings → Users → Add User
4. Fill: Email, Password, Role
5. Send welcome email with credentials

### Rotate SSL Certificates

```bash
# Using Let's Encrypt (certbot)
certbot renew --nginx

# Test renewal (dry-run)
certbot renew --dry-run

# Restart Nginx
docker-compose restart nginx
```

**Automation**: Add to cron:
```
0 0 * * 0 certbot renew --quiet && docker-compose restart nginx
```

### Scale API Replicas

```yaml
# Edit docker-compose.production.yml
services:
  api:
    deploy:
      replicas: 4  # Increase from 2 to 4
```

```powershell
# Apply changes
docker-compose -f docker-compose.production.yml up -d --scale api=4
```

### Update Ollama Model

```powershell
# Pull new model
docker exec twisterlab-ollama ollama pull deepseek-r1:latest

# List models
docker exec twisterlab-ollama ollama list

# Remove old model
docker exec twisterlab-ollama ollama rm <old_model>
```

---

## 🔍 Troubleshooting Playbooks

### Playbook 1: API Not Responding

**Symptoms**:
- `curl http://localhost:8000/health` fails
- Grafana shows API down
- Users can't create tickets

**Diagnosis**:
```powershell
# 1. Check container status
docker ps | Select-String "api"

# 2. Check logs
docker logs twisterlab-api-1 --tail 100

# 3. Check resource usage
docker stats twisterlab-api-1 --no-stream
```

**Common causes & fixes**:

| Cause | Symptom | Fix |
|-------|---------|-----|
| Container crashed | Exited status | `docker-compose restart api` |
| Out of memory | OOMKilled | Increase memory limit in docker-compose.yml |
| Database unreachable | Connection errors in logs | Check PostgreSQL health |
| Ollama timeout | LLM request timeout | Restart Ollama or increase timeout |

### Playbook 2: High Error Rate

**Symptoms**:
- Prometheus alert: error_rate > 10%
- Grafana shows red error spike
- User complaints

**Diagnosis**:
```powershell
# 1. Check error logs
docker logs twisterlab-api-1 --since 1h | Select-String "ERROR|CRITICAL"

# 2. Check specific error types
docker logs twisterlab-api-1 --since 1h | Select-String "500|502|503|504"

# 3. Check database errors
docker exec twisterlab-postgres psql -U twisterlab_prod -d twisterlab_prod -c "SELECT * FROM pg_stat_database WHERE datname='twisterlab_prod';"
```

**Common causes & fixes**:

| Error Type | Fix |
|------------|-----|
| 500 Internal Server | Check application logs, recent deployment |
| 502 Bad Gateway | Restart Nginx, check upstream health |
| 503 Service Unavailable | Scale up replicas, check resource limits |
| Database deadlock | Kill long queries, optimize indexes |

### Playbook 3: Slow Performance

**Symptoms**:
- API response time > 2s (normal < 500ms)
- Users complaining of slowness
- Grafana shows latency spike

**Diagnosis**:
```powershell
# 1. Check resource usage
docker stats --no-stream

# 2. Check slow queries
docker exec twisterlab-postgres psql -U twisterlab_prod -d twisterlab_prod -c "SELECT pid, query, state, query_start FROM pg_stat_activity WHERE state != 'idle' AND query_start < now() - interval '5 seconds';"

# 3. Check Redis latency
docker exec twisterlab-redis redis-cli --latency-history
```

**Common causes & fixes**:

| Cause | Symptom | Fix |
|-------|---------|-----|
| CPU saturated | >90% CPU | Scale up replicas or CPU cores |
| Memory pressure | High swap usage | Increase memory limit |
| Slow database | Queries >1s | Add indexes, optimize queries |
| Network congestion | High latency, packet loss | Check network config, firewall |
| Ollama overloaded | LLM timeouts | Reduce concurrent requests or add GPU |

### Playbook 4: Disk Space Critical

**Symptoms**:
- Prometheus alert: disk_usage > 90%
- Logs show "No space left on device"
- Services crashing randomly

**Diagnosis**:
```powershell
# 1. Check disk usage
docker system df

# 2. Find largest directories
Get-ChildItem -Path "C:\TwisterLab\data" -Recurse | Sort-Object Length -Descending | Select-Object -First 10 FullName, Length

# 3. Check Docker volumes
docker volume ls
docker system df -v
```

**Immediate actions**:
```powershell
# 1. Clean up Docker
docker system prune -a --volumes -f

# 2. Rotate logs
docker logs twisterlab-api-1 > /dev/null 2>&1

# 3. Archive old backups
aws s3 mv s3://twisterlab-backups-prod/old/ s3://twisterlab-backups-archive/
```

**Long-term fix**:
- Implement log rotation (max-size: 50MB, max-file: 10)
- Archive old database records (> 90 days)
- Move backups to cheaper S3 storage class (Glacier)

### Playbook 5: Ollama GPU Issues

**Symptoms**:
- LLM requests timing out
- Ollama logs show CUDA errors
- GPU not detected

**Diagnosis**:
```powershell
# 1. Check GPU visibility
docker exec twisterlab-ollama nvidia-smi

# 2. Check Ollama status
docker exec twisterlab-ollama ollama list

# 3. Check logs
docker logs twisterlab-ollama --tail 100
```

**Common causes & fixes**:

| Cause | Fix |
|-------|-----|
| GPU not exposed to container | Verify `runtime: nvidia` in docker-compose.yml |
| CUDA driver mismatch | Update NVIDIA drivers on host |
| VRAM exhausted | Reduce model size or batch size |
| Model not loaded | `docker exec twisterlab-ollama ollama pull deepseek-r1:latest` |

---

## 📞 Escalation Contacts

| Role | Name | Contact | Availability |
|------|------|---------|--------------|
| **On-Call Engineer** | TBD | TBD | 24/7 |
| **DevOps Lead** | TBD | TBD | Business hours |
| **Database Admin** | TBD | TBD | Business hours |
| **Security Team** | TBD | TBD | Business hours |
| **Management** | youneselfakir0 | youneselfakir0@gmail.com | As needed |

---

## 📚 Additional Resources

- **System Architecture**: See `docs/ARCHITECTURE_DEEP_DIVE.md`
- **Deployment Guide**: See `docs/PRODUCTION_DEPLOYMENT_GUIDE.md`
- **API Documentation**: https://api.twisterlab.com/docs
- **Grafana Dashboards**: https://monitoring.twisterlab.com
- **Prometheus Metrics**: https://metrics.twisterlab.com

---

**Last Updated**: 2025-11-02  
**Version**: 1.0.0  
**Maintainer**: Operations Team
