# 🚀 TwisterLab - Staging Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2025-02-11  
**Status**: Production-Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Validation](#validation)
8. [Troubleshooting](#troubleshooting)
9. [Rollback](#rollback)
10. [Maintenance](#maintenance)

---

## Overview

Staging environment provides a production-like testing environment with:

- **Full monitoring stack** (Prometheus + Grafana)
- **Separate ports** (no conflicts with local development)
- **Health checks** for all services
- **Persistent volumes** for data preservation
- **Automated deployment** and rollback scripts

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Staging Environment                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌───────┐  ┌────────┐  ┌────────────┐          │
│  │ API:8001 │  │ Redis │  │ Ollama │  │ Prometheus │          │
│  │          │─▶│ :6380 │  │ :11435 │  │   :9092    │          │
│  └────┬─────┘  └───────┘  └────────┘  └────────────┘          │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐                │
│  │ Postgres │  │ Grafana  │  │  OpenWebUI   │                │
│  │  :5433   │  │  :3001   │  │    :8081     │                │
│  └──────────┘  └──────────┘  └──────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Services

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| API | 8001 | FastAPI application | `/health` |
| PostgreSQL | 5433 | Database | `pg_isready` |
| Redis | 6380 | Cache & queues | `redis-cli ping` |
| Ollama | 11435 | LLM inference | `/api/tags` |
| Prometheus | 9092 | Metrics collection | `/-/healthy` |
| Grafana | 3001 | Dashboards | `/api/health` |
| OpenWebUI | 8081 | Frontend (optional) | `/health` |

---

## Prerequisites

### Required

- **Docker** 24.0+ with Compose v2
- **Python** 3.12+
- **Git** for cloning repository
- **8GB RAM** minimum (16GB recommended)
- **50GB disk space** (for models and data)

### Optional

- **NVIDIA GPU** (for faster LLM inference)
- **NVIDIA Docker runtime** (for GPU support)

### Check Prerequisites

```powershell
# Check Docker
docker --version
docker-compose --version

# Check Python
python --version

# Check available disk space
Get-PSDrive C | Select-Object Used,Free

# Check Docker daemon
docker ps
```

---

## Quick Start

### 1. Clone Repository

```powershell
git clone https://github.com/twisterlab/twisterlab.git
cd twisterlab
```

### 2. Run Automated Deployment

```powershell
# Full deployment with tests
python deploy_staging.py

# Skip tests (faster, not recommended)
python deploy_staging.py --skip-tests

# Pull latest images
python deploy_staging.py --pull-images
```

### 3. Access Services

- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Prometheus**: http://localhost:9092
- **Grafana**: http://localhost:3001 (admin/staging_grafana_password)

---

## Detailed Setup

### Step 1: Environment Configuration

```powershell
# Copy example file
Copy-Item .env.staging.example .env.staging

# Edit configuration
notepad .env.staging
```

**Required Changes** in `.env.staging`:

```bash
# Update ALL _CHANGE_ME placeholders
POSTGRES_PASSWORD=your_secure_postgres_password
REDIS_PASSWORD=your_secure_redis_password
SECRET_KEY=your_secret_key_min_32_chars
GRAFANA_PASSWORD=your_grafana_password
```

### Step 2: Pre-Deployment Validation

```powershell
# Run test suite
pytest tests/ -v --cov=agents --cov-report=html

# Check test coverage (should be ≥80%)
open htmlcov/index.html

# Run linting
pylint agents/ --rcfile=.pylintrc
mypy agents/ --strict
```

### Step 3: Build Docker Images

```powershell
# Build all services
docker-compose -f docker-compose.staging.yml build --no-cache

# Verify images
docker images | Select-String "twisterlab"
```

### Step 4: Deploy Services

```powershell
# Start all services
docker-compose -f docker-compose.staging.yml up -d

# Watch logs (Ctrl+C to exit)
docker-compose -f docker-compose.staging.yml logs -f
```

### Step 5: Wait for Health Checks

```powershell
# Check service status
docker-compose -f docker-compose.staging.yml ps

# Wait for all services to be "healthy"
# This takes ~2 minutes for initial startup
```

### Step 6: Pull Ollama Models

```powershell
# Pull primary model
docker exec twisterlab-ollama-staging ollama pull deepseek-r1

# Verify model
docker exec twisterlab-ollama-staging ollama list
```

---

## Configuration

### Environment Variables

Complete reference: `.env.staging.example`

#### Critical Settings

```bash
# Environment
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Security (MUST change!)
POSTGRES_PASSWORD=<strong_password>
REDIS_PASSWORD=<strong_password>
SECRET_KEY=<min_32_chars>

# Performance
MAX_CONCURRENT_TICKETS=50
TICKET_TIMEOUT_SECONDS=300
API_WORKERS=2

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Alert Thresholds
ALERT_CPU_THRESHOLD=80.0
ALERT_MEMORY_THRESHOLD=85.0
ALERT_DISK_THRESHOLD=90.0
ALERT_API_RESPONSE_TIME=2.0
ALERT_ERROR_RATE=10.0
```

### Docker Compose Configuration

File: `docker-compose.staging.yml`

**Key Features**:
- Health checks every 10-30s
- Automatic restart policies
- Named volumes for persistence
- Isolated network (twisterlab-staging-network)
- Environment variable injection

---

## Deployment

### Automated Deployment

```powershell
# Full deployment (recommended)
python deploy_staging.py

# Options
python deploy_staging.py --skip-tests       # Skip test suite
python deploy_staging.py --pull-images      # Pull latest images
python deploy_staging.py --clean            # Clean build
```

### Manual Deployment

```powershell
# 1. Stop existing containers
docker-compose -f docker-compose.staging.yml down

# 2. Build images
docker-compose -f docker-compose.staging.yml build

# 3. Start services
docker-compose -f docker-compose.staging.yml up -d

# 4. Wait for health checks
Start-Sleep -Seconds 60

# 5. Run smoke tests
pytest tests/smoke_tests_staging.py -v
```

### Deployment Checklist

- [ ] Environment variables configured (`.env.staging`)
- [ ] All tests passing (`pytest tests/`)
- [ ] Docker images built successfully
- [ ] All services started (`docker-compose ps`)
- [ ] Health checks passing (all services "healthy")
- [ ] Smoke tests passing (`smoke_tests_staging.py`)
- [ ] Ollama models pulled (`deepseek-r1`)
- [ ] Grafana accessible (http://localhost:3001)
- [ ] Prometheus scraping targets (http://localhost:9092/targets)
- [ ] API responding (http://localhost:8001/health)

---

## Validation

### Smoke Tests

```powershell
# Run all smoke tests
python tests/smoke_tests_staging.py

# Or with pytest
pytest tests/smoke_tests_staging.py -v -s

# Expected output:
# ✅ PostgreSQL: Connected successfully
# ✅ Redis: Connected successfully
# ✅ API: Health check passed
# ✅ Ollama: Service running
# ✅ Prometheus: Service running
# ✅ Grafana: UI accessible
```

### Integration Tests

```powershell
# Run full integration test suite
pytest tests/test_integration_full_system.py -v -s

# Expected: 4 tests passing
# - Full ticket lifecycle (8 stages)
# - Error handling & failover (5 scenarios)
# - Load & stress testing (100 concurrent tickets)
# - Monitoring & alerting (4 alerts)
```

### Manual Validation

#### Check API Health

```powershell
curl http://localhost:8001/health
# Expected: {"status":"ok","version":"1.0.0"}
```

#### Check API Documentation

```powershell
Start-Process http://localhost:8001/docs
# Should open Swagger UI in browser
```

#### Check Prometheus Targets

```powershell
Start-Process http://localhost:9092/targets
# All targets should be "UP"
```

#### Check Grafana

```powershell
Start-Process http://localhost:3001
# Login: admin / staging_grafana_password
# Verify dashboards are loaded
```

#### Check Container Logs

```powershell
# API logs
docker logs twisterlab-api-staging --tail=50

# All service logs
docker-compose -f docker-compose.staging.yml logs --tail=50
```

---

## Troubleshooting

### Common Issues

#### Services Not Starting

```powershell
# Check container status
docker-compose -f docker-compose.staging.yml ps

# Check logs for errors
docker-compose -f docker-compose.staging.yml logs

# Restart specific service
docker-compose -f docker-compose.staging.yml restart api
```

#### Port Conflicts

```powershell
# Check if ports are already in use
netstat -ano | Select-String "8001|5433|6380|11435|9092|3001"

# Kill process using port (replace PID)
Stop-Process -Id <PID> -Force
```

#### Health Checks Failing

```powershell
# PostgreSQL
docker exec twisterlab-postgres-staging pg_isready -U twisterlab

# Redis
docker exec twisterlab-redis-staging redis-cli -a <password> ping

# API
curl http://localhost:8001/health

# Check service logs
docker logs <container_name>
```

#### Database Connection Errors

```powershell
# Verify PostgreSQL is running
docker exec twisterlab-postgres-staging psql -U twisterlab -c "SELECT version();"

# Check connection string in .env.staging
# DATABASE_URL=postgresql+asyncpg://twisterlab:<password>@postgres:5432/twisterlab
```

#### Ollama Model Not Found

```powershell
# Pull model manually
docker exec twisterlab-ollama-staging ollama pull deepseek-r1

# List available models
docker exec twisterlab-ollama-staging ollama list

# Check Ollama logs
docker logs twisterlab-ollama-staging
```

#### Prometheus Not Scraping

```powershell
# Check Prometheus configuration
docker exec prometheus-staging cat /etc/prometheus/prometheus.yml

# Verify targets
Start-Process http://localhost:9092/targets

# Restart Prometheus
docker-compose -f docker-compose.staging.yml restart prometheus
```

#### Grafana Dashboards Not Loading

```powershell
# Check Grafana datasource
Start-Process http://localhost:3001/datasources

# Verify Prometheus datasource configured
# URL should be: http://prometheus:9090

# Re-provision dashboards
docker-compose -f docker-compose.staging.yml restart grafana
```

---

## Rollback

### Automated Rollback

```powershell
# Rollback with data preservation
python rollback_staging.py --keep-volumes

# Full rollback (deletes data)
python rollback_staging.py
```

### Manual Rollback

```powershell
# Stop all services
docker-compose -f docker-compose.staging.yml down

# Remove volumes (optional - deletes data)
docker-compose -f docker-compose.staging.yml down -v

# Remove network
docker network rm twisterlab-staging-network
```

### Rollback Checklist

- [ ] Backup logs (`logs/rollback_<timestamp>/`)
- [ ] Stop all containers
- [ ] Remove containers
- [ ] Decide: Keep volumes or delete
- [ ] Remove network
- [ ] Verify cleanup (`docker ps -a | Select-String staging`)

---

## Maintenance

### Routine Tasks

#### Daily Checks

```powershell
# Check service health
docker-compose -f docker-compose.staging.yml ps

# Review logs for errors
docker-compose -f docker-compose.staging.yml logs --tail=100 | Select-String "ERROR"

# Check disk usage
docker system df
```

#### Weekly Maintenance

```powershell
# Update images
docker-compose -f docker-compose.staging.yml pull

# Restart services
docker-compose -f docker-compose.staging.yml restart

# Clean up unused resources
docker system prune -f
```

#### Monthly Tasks

```powershell
# Backup database
docker exec twisterlab-postgres-staging pg_dump -U twisterlab > backup_$(Get-Date -Format "yyyyMMdd").sql

# Review metrics in Grafana
Start-Process http://localhost:3001

# Update Ollama models
docker exec twisterlab-ollama-staging ollama pull deepseek-r1
```

### Performance Monitoring

#### Key Metrics to Watch

- **API Response Time**: Should be <2s (p95)
- **Error Rate**: Should be <10%
- **CPU Usage**: Should be <80%
- **Memory Usage**: Should be <85%
- **Disk Usage**: Should be <90%

#### Prometheus Queries

```promql
# API request rate
rate(api_requests_total[5m])

# API error rate
rate(api_errors_total[5m]) / rate(api_requests_total[5m])

# Agent response time (p95)
histogram_quantile(0.95, agent_response_time_seconds)

# System CPU usage
system_cpu_usage_percent

# Database connections
db_connections_active
```

### Backup and Recovery

#### Database Backup

```powershell
# Manual backup
docker exec twisterlab-postgres-staging pg_dump -U twisterlab -F c -f /tmp/backup.dump
docker cp twisterlab-postgres-staging:/tmp/backup.dump ./backups/

# Automated backup (via BackupAgent)
# Runs every 6 hours by default
# Check logs: docker logs twisterlab-api-staging | Select-String "BackupAgent"
```

#### Database Restore

```powershell
# Copy backup to container
docker cp ./backups/backup.dump twisterlab-postgres-staging:/tmp/

# Restore
docker exec twisterlab-postgres-staging pg_restore -U twisterlab -d twisterlab -c /tmp/backup.dump
```

#### Volume Backup

```powershell
# Backup all volumes
docker run --rm -v twisterlab-staging-postgres-data:/data -v ${PWD}/backups:/backup alpine tar czf /backup/postgres-data.tar.gz -C /data .

# Restore volume
docker run --rm -v twisterlab-staging-postgres-data:/data -v ${PWD}/backups:/backup alpine tar xzf /backup/postgres-data.tar.gz -C /data
```

---

## Advanced Configuration

### GPU Support (Optional)

To enable GPU acceleration for Ollama:

1. Install NVIDIA Docker runtime
2. Verify GPU available: `docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi`
3. GPU automatically configured in `docker-compose.staging.yml`

### Custom Monitoring Alerts

Edit `monitoring/prometheus.staging.yml` to add alert rules:

```yaml
# Example: High API latency alert
- alert: HighAPILatency
  expr: histogram_quantile(0.95, api_response_time_seconds) > 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High API latency detected"
```

### Custom Grafana Dashboards

1. Access Grafana: http://localhost:3001
2. Create dashboard: **+** → **Dashboard**
3. Add panels with Prometheus queries
4. Export JSON: **Dashboard settings** → **JSON Model**
5. Save to `monitoring/grafana/dashboards/`

---

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [System Prompt - Technical Excellence](./SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md)
- [Technical Validation Checklist](./TECHNICAL_VALIDATION_CHECKLIST.md)

---

**Last Updated**: 2025-02-11  
**Version**: 1.0.0  
**Status**: Production-Ready  
**License**: Apache 2.0
