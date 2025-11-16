# 🚀 TwisterLab - Production Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2025-11-02  
**Status**: Production-Ready  
**Deployment Strategy**: Blue-Green with Rollback

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Deployment Strategies](#deployment-strategies)
5. [Manual Deployment](#manual-deployment)
6. [Automated Deployment (CI/CD)](#automated-deployment-cicd)
7. [Post-Deployment Validation](#post-deployment-validation)
8. [Rollback Procedures](#rollback-procedures)
9. [Monitoring & Alerting](#monitoring--alerting)
10. [Troubleshooting](#troubleshooting)

---

## Overview

TwisterLab v1.0.0 production deployment uses **Blue-Green deployment** strategy with:

- ✅ **Zero-downtime deployments**
- ✅ **Instant rollback capability**
- ✅ **Comprehensive health checks**
- ✅ **Automated smoke tests**
- ✅ **Traffic switching mechanism**
- ✅ **Full monitoring stack** (Prometheus + Grafana)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 Production Environment (HA)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────┐         ┌──────────────┐                       │
│  │   Nginx    │────────▶│ API (Blue)   │◀──┐                   │
│  │   :80/443  │         │  Replicas: 2 │   │                   │
│  │            │    ┌───▶│ API (Green)  │◀──┤                   │
│  └────────────┘    │    │  Replicas: 2 │   │                   │
│                    │    └──────────────┘   │                   │
│                    │                        │                   │
│  ┌──────────┐    ┌┴───────────┐   ┌────────┴────┐             │
│  │ Postgres │◀───│   Redis    │◀──│   Ollama    │             │
│  │  :5432   │    │   :6379    │   │   :11434    │             │
│  │  (HA)    │    │   (HA)     │   │   (GPU)     │             │
│  └──────────┘    └────────────┘   └─────────────┘             │
│                                                                 │
│  ┌────────────┐  ┌──────────┐  ┌──────────────┐               │
│  │ Prometheus │◀─│ Grafana  │  │ Alertmanager │               │
│  │   :9090    │  │  :3000   │  │    :9093     │               │
│  └────────────┘  └──────────┘  └──────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Infrastructure Requirements

- **CPU**: 16+ cores (24+ recommended)
- **RAM**: 32GB+ (64GB recommended)
- **Disk**: 500GB+ SSD (1TB+ recommended)
- **Network**: 1Gbps+ (10Gbps for high traffic)
- **GPU**: NVIDIA GPU (optional, for faster LLM inference)

### Software Requirements

- **OS**: Ubuntu 22.04 LTS / RHEL 8+ / Windows Server 2022
- **Docker**: 24.0+
- **Docker Compose**: v2.20+
- **Python**: 3.12+
- **Git**: 2.40+

### Network Requirements

- **Domain**: Registered domain with SSL certificate
- **DNS**: A/AAAA records configured
- **Firewall**: Ports 80, 443, 22 open
- **Load Balancer**: Optional (recommended for HA)

### Check Prerequisites

```bash
# System resources
free -h
df -h
lscpu
nvidia-smi  # If GPU available

# Software versions
docker --version
docker-compose --version
python --version
git --version

# Network connectivity
ping -c 3 google.com
curl -I https://github.com
```

---

## Pre-Deployment Checklist

### 1. Code & Tests

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Test coverage ≥80% (actual: 100%)
- [ ] Integration tests passing (4 scenarios)
- [ ] Code review complete
- [ ] No critical security vulnerabilities

### 2. Configuration

- [ ] `.env.production` created from `.env.production.example`
- [ ] All passwords changed from `_CHANGE_ME_` placeholders
- [ ] Database credentials configured
- [ ] Redis password configured
- [ ] API secret key generated (32+ chars)
- [ ] SSL certificates installed
- [ ] Domain configured in ALLOWED_ORIGINS

### 3. Infrastructure

- [ ] Production servers provisioned
- [ ] Docker installed and configured
- [ ] Persistent volumes mounted
- [ ] Network configured (firewall, DNS)
- [ ] SSL certificates valid
- [ ] Backup storage configured (S3)

### 4. Monitoring

- [ ] Prometheus configured
- [ ] Grafana dashboards imported
- [ ] Alertmanager rules configured
- [ ] Alert destinations configured (email, Slack, PagerDuty)
- [ ] Log aggregation configured

### 5. Security

- [ ] Secrets stored securely (GitHub Secrets, Vault)
- [ ] Firewall rules configured
- [ ] SSL/TLS enabled
- [ ] Rate limiting configured
- [ ] Security audit completed

### 6. Documentation

- [ ] Deployment runbook reviewed
- [ ] Rollback procedure documented
- [ ] Incident response plan ready
- [ ] On-call rotation configured

---

## Deployment Strategies

### Blue-Green Deployment (Recommended)

**How it works**:
1. Deploy new version to "Blue" environment (while "Green" is live)
2. Run health checks and smoke tests on Blue
3. Switch traffic from Green to Blue
4. Monitor Blue for stability (5 minutes)
5. If successful, decommission Green
6. If failed, instant rollback to Green

**Advantages**:
- ✅ Zero downtime
- ✅ Instant rollback
- ✅ Full testing before traffic switch
- ✅ Easy to verify new version

**Disadvantages**:
- ❌ Requires 2x resources during deployment
- ❌ Database migration complexity

**Use when**:
- Major version upgrades
- Critical production releases
- Database schema changes

### Rolling Deployment

**How it works**:
1. Update containers one at a time
2. Wait for each container to be healthy
3. Continue until all containers updated

**Advantages**:
- ✅ No extra resources required
- ✅ Gradual rollout
- ✅ Canary-like behavior

**Disadvantages**:
- ❌ Slower deployment
- ❌ More complex rollback
- ❌ Mixed versions during deployment

**Use when**:
- Minor version updates
- Configuration changes
- Low-risk deployments

### Canary Deployment

**How it works**:
1. Deploy new version to small subset (5-10%)
2. Monitor canary for issues
3. Gradually increase traffic to new version
4. Complete rollout if stable

**Advantages**:
- ✅ Minimal risk exposure
- ✅ Real-world testing
- ✅ Easy to abort

**Disadvantages**:
- ❌ Requires sophisticated routing
- ❌ Longer deployment time
- ❌ Complex monitoring

**Use when**:
- High-risk changes
- Large user base
- Gradual rollout needed

---

## Manual Deployment

### Step 1: Prepare Environment

```bash
# Clone repository (if not already)
git clone https://github.com/youneselfakir0/TwisterLab.git
cd TwisterLab

# Checkout production tag/branch
git checkout v1.0.0

# Create production environment file
cp .env.production.example .env.production

# Edit with production credentials
nano .env.production
```

**Update these critical values in `.env.production`**:
```bash
POSTGRES_PASSWORD=<strong_random_password>
REDIS_PASSWORD=<strong_random_password>
SECRET_KEY=<min_32_chars_random_key>
ALLOWED_ORIGINS=https://twisterlab.yourdomain.com
GRAFANA_PASSWORD=<grafana_admin_password>

# AWS S3 for backups
AWS_ACCESS_KEY_ID=<your_aws_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret>
BACKUP_S3_BUCKET=twisterlab-backups-production
```

### Step 2: Build Docker Images

```bash
# Build all services
docker-compose -f docker-compose.production.yml build --no-cache

# Verify images built
docker images | grep twisterlab

# Expected output:
# twisterlab  production  <image_id>  <size>
```

### Step 3: Deploy Blue Environment

```bash
# Stop any existing deployments (Green)
docker-compose -f docker-compose.production.yml -p twisterlab-green down

# Start Blue environment
docker-compose -f docker-compose.production.yml -p twisterlab-blue up -d

# Watch logs
docker-compose -f docker-compose.production.yml -p twisterlab-blue logs -f
```

### Step 4: Wait for Health Checks

```bash
# Check container status
docker-compose -f docker-compose.production.yml -p twisterlab-blue ps

# All services should show "healthy"
# Wait up to 5 minutes for all services to be ready

# Manual health check
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"1.0.0"}
```

### Step 5: Pull Ollama Models

```bash
# Pull primary model
docker exec twisterlab-ollama-prod ollama pull deepseek-r1

# Verify model loaded
docker exec twisterlab-ollama-prod ollama list

# Expected output showing deepseek-r1:latest
```

### Step 6: Run Smoke Tests

```bash
# Activate Python environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Run smoke tests against Blue
pytest tests/smoke_tests_staging.py -v -s --base-url=http://localhost:8000

# All tests should pass
```

### Step 7: Switch Traffic to Blue

```bash
# Update load balancer / Nginx to point to Blue
# This is environment-specific

# Example with Nginx:
sudo nano /etc/nginx/sites-available/twisterlab
# Update upstream servers to point to Blue containers

# Reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# Verify traffic switch
curl https://twisterlab.yourdomain.com/health
```

### Step 8: Monitor Blue Environment

```bash
# Monitor for 5-10 minutes
# Watch Grafana dashboards: https://grafana.yourdomain.com

# Check error rate
curl "http://localhost:9090/api/v1/query?query=rate(api_errors_total[5m])"

# Check response time (p95)
curl "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,api_response_time_seconds)"

# If error rate > 5% or p95 > 2s, ROLLBACK immediately
```

### Step 9: Cleanup Green Environment

```bash
# Only after Blue is confirmed stable
docker-compose -f docker-compose.production.yml -p twisterlab-green down

# Remove old images (optional)
docker image prune -f
```

---

## Automated Deployment (CI/CD)

### GitHub Actions Workflow

TwisterLab uses GitHub Actions for automated production deployment.

**Trigger**: Manual via GitHub Actions UI

**Workflow**: `.github/workflows/deploy-production.yml`

### Steps to Deploy via GitHub Actions

1. **Go to GitHub Repository**
   - Navigate to: https://github.com/youneselfakir0/TwisterLab

2. **Open Actions Tab**
   - Click "Actions" in repository navigation

3. **Select Production Deployment Workflow**
   - Find "Deploy to Production" workflow
   - Click on it

4. **Run Workflow**
   - Click "Run workflow" button
   - Select branch: `main` or `v1.0.0` tag
   - Choose deployment strategy:
     - **blue-green** (recommended)
     - **rolling**
     - **canary** (future)
   - Configure options:
     - Skip tests: `false` (recommended)
     - Rollback on failure: `true` (recommended)
   - Click "Run workflow"

5. **Monitor Deployment**
   - Watch workflow execution in real-time
   - Check logs for each job:
     - Pre-deployment validation
     - Build production image
     - Deploy Blue-Green
     - Post-deployment validation
   - Deployment takes ~15-20 minutes

6. **Verify Success**
   - Check for success comment on commit
   - Verify services at https://twisterlab.yourdomain.com
   - Review Grafana dashboards

### Required GitHub Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `PROD_DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://user:pass@host:5432/db` |
| `PROD_REDIS_URL` | Redis connection URL | `redis://:password@host:6379/0` |
| `PROD_SECRET_KEY` | API secret key (32+ chars) | `<generated_with_openssl_rand>` |
| `PROD_ALLOWED_ORIGINS` | CORS allowed origins | `https://twisterlab.yourdomain.com` |
| `PROD_GRAFANA_PASSWORD` | Grafana admin password | `<strong_password>` |

---

## Post-Deployment Validation

### Automated Validation (CI/CD)

The workflow automatically validates:
- ✅ Health checks (all services healthy)
- ✅ Smoke tests (6 services tested)
- ✅ Integration tests (4 scenarios)
- ✅ Metrics validation (Prometheus targets)

### Manual Validation

#### 1. Service Health

```bash
# API health
curl https://twisterlab.yourdomain.com/health
# Expected: {"status":"ok","version":"1.0.0"}

# Prometheus targets
curl https://prometheus.yourdomain.com/api/v1/targets
# All targets should be "up"

# Grafana
curl https://grafana.yourdomain.com/api/health
# Expected: {"database":"ok"}
```

#### 2. Functionality Tests

```bash
# Create test ticket
curl -X POST https://twisterlab.yourdomain.com/api/v1/tickets/ \
  -H "Content-Type: application/json" \
  -d '{"subject":"Test ticket","description":"Post-deployment test"}'

# List agents
curl https://twisterlab.yourdomain.com/api/v1/agents/

# Check metrics
curl https://twisterlab.yourdomain.com/metrics
```

#### 3. Performance Validation

```bash
# Run load test (optional)
pytest tests/test_integration_full_system.py::test_load_and_stress -v

# Check response times in Grafana
# API p95 should be < 2s
# API p99 should be < 5s
```

#### 4. Monitoring Validation

```bash
# Check Grafana dashboards
open https://grafana.yourdomain.com/dashboards

# Verify:
# - TwisterLab Overview dashboard loaded
# - All panels showing data
# - No red metrics (all green/yellow)
```

---

## Rollback Procedures

### Automatic Rollback (CI/CD)

If deployment fails, workflow automatically:
1. Stops Blue environment
2. Restarts Green environment
3. Restores traffic to Green
4. Notifies via GitHub comment

### Manual Rollback

#### Quick Rollback (< 1 minute)

```bash
# Stop Blue environment
docker-compose -f docker-compose.production.yml -p twisterlab-blue down

# Start Green environment (previous version)
docker-compose -f docker-compose.production.yml -p twisterlab-green up -d

# Switch traffic back to Green
# (Update load balancer / Nginx)

# Verify Green is healthy
curl http://localhost:8000/health
```

#### Full Rollback with Validation

```bash
# 1. Backup current logs
docker-compose -f docker-compose.production.yml -p twisterlab-blue logs > rollback-logs-$(date +%Y%m%d-%H%M%S).txt

# 2. Stop Blue
docker-compose -f docker-compose.production.yml -p twisterlab-blue down

# 3. Start Green
docker-compose -f docker-compose.production.yml -p twisterlab-green up -d

# 4. Wait for health checks
sleep 60

# 5. Run smoke tests
pytest tests/smoke_tests_staging.py -v --base-url=http://localhost:8000

# 6. Switch traffic
# Update load balancer / Nginx

# 7. Monitor for 5 minutes
# Check error rates, response times

# 8. Notify team
echo "Rollback completed at $(date)"
```

---

## Monitoring & Alerting

### Grafana Dashboards

Access: https://grafana.yourdomain.com  
Login: admin / <PROD_GRAFANA_PASSWORD>

**Available Dashboards**:
1. **TwisterLab Overview**
   - System metrics (CPU, memory, disk)
   - Agent performance (response time, success rate)
   - API metrics (request rate, latency)
   - Database metrics (connections, query time)

2. **Agent Performance** (custom)
   - Individual agent metrics
   - Success/error rates per agent
   - Response time percentiles

3. **Infrastructure Health** (custom)
   - Container status
   - Resource utilization
   - Network traffic

### Prometheus Alerts

Access: https://prometheus.yourdomain.com/alerts

**Configured Alerts**:
- CPU usage > 75% for 5 minutes
- Memory usage > 80% for 5 minutes
- Disk usage > 85%
- API response time p95 > 1.5s
- Error rate > 5%
- Agent response time > 3s

### Alert Destinations

Configure in `monitoring/alertmanager.yml`:
- **Email**: alerts@yourdomain.com
- **Slack**: #twisterlab-alerts channel
- **PagerDuty**: Production incidents

---

## Troubleshooting

### Deployment Fails at Health Checks

**Symptom**: Blue environment never becomes healthy

**Diagnosis**:
```bash
# Check container logs
docker-compose -f docker-compose.production.yml -p twisterlab-blue logs

# Check specific service
docker logs twisterlab-api-prod --tail=100

# Check resource usage
docker stats
```

**Common Causes**:
1. **Database connection failure**
   - Check DATABASE_URL in .env.production
   - Verify PostgreSQL is running: `docker ps | grep postgres`
   - Test connection: `psql $DATABASE_URL`

2. **Redis connection failure**
   - Check REDIS_URL and REDIS_PASSWORD
   - Test Redis: `docker exec twisterlab-redis-prod redis-cli -a <password> ping`

3. **Resource exhaustion**
   - Check available memory: `free -h`
   - Check disk space: `df -h`
   - Increase resource limits in docker-compose.production.yml

### High Error Rate After Deployment

**Symptom**: Error rate > 5% in Prometheus

**Diagnosis**:
```bash
# Check error logs
docker logs twisterlab-api-prod | grep ERROR

# Query error rate
curl "http://localhost:9090/api/v1/query?query=rate(api_errors_total[5m])"

# Check specific endpoints
curl https://twisterlab.yourdomain.com/api/v1/agents/
```

**Resolution**:
1. **Immediate**: Rollback to Green environment
2. **Investigation**: Review error logs, identify root cause
3. **Fix**: Apply fix, redeploy to staging first
4. **Retry**: Deploy to production again

### Traffic Not Switching to Blue

**Symptom**: Blue is healthy but still serving old version

**Diagnosis**:
```bash
# Check Nginx configuration
sudo nginx -t

# Check upstream servers
curl -I https://twisterlab.yourdomain.com
# Look for X-Served-By header

# Check load balancer
# (Depends on your infrastructure)
```

**Resolution**:
1. Verify Nginx/load balancer configuration
2. Reload Nginx: `sudo systemctl reload nginx`
3. Check firewall rules
4. Verify DNS propagation: `dig twisterlab.yourdomain.com`

---

## Best Practices

### Pre-Deployment

1. **Always deploy to staging first**
2. **Run full test suite before production**
3. **Review recent incidents/bugs**
4. **Notify team about deployment window**
5. **Have rollback plan ready**

### During Deployment

1. **Monitor closely during traffic switch**
2. **Keep communication channels open**
3. **Have multiple team members available**
4. **Document any issues encountered**
5. **Don't rush - verify each step**

### Post-Deployment

1. **Monitor for 24 hours after deployment**
2. **Review metrics daily for first week**
3. **Document lessons learned**
4. **Update runbook if needed**
5. **Celebrate success! 🎉**

---

## Appendix

### Useful Commands

```bash
# View all production containers
docker ps --filter name=twisterlab

# View resource usage
docker stats

# View logs for all services
docker-compose -f docker-compose.production.yml logs -f --tail=100

# Restart specific service
docker-compose -f docker-compose.production.yml restart api

# Execute command in container
docker exec -it twisterlab-api-prod bash

# Backup database
docker exec twisterlab-postgres-prod pg_dump -U twisterlab > backup-$(date +%Y%m%d).sql

# View Prometheus metrics
curl http://localhost:9090/metrics

# Test API endpoint
curl -X POST https://twisterlab.yourdomain.com/api/v1/tickets/ -d '{"subject":"test"}'
```

### Performance Tuning

```bash
# Increase API workers
# Edit .env.production:
API_WORKERS=8

# Increase database connections
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=20

# Increase concurrent tickets
MAX_CONCURRENT_TICKETS=200

# Restart services
docker-compose -f docker-compose.production.yml restart
```

---

**Last Updated**: 2025-11-02  
**Version**: 1.0.0  
**License**: Apache 2.0  
**Support**: support@twisterlab.yourdomain.com
