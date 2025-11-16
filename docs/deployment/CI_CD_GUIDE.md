# 🔄 TwisterLab CI/CD Pipelines

**Version**: 1.0.0  
**Last Updated**: 2025-02-11  
**Status**: Production-Ready

---

## 📋 Overview

TwisterLab uses GitHub Actions for continuous integration and deployment with:

- ✅ **Automated testing** (unit, integration, smoke tests)
- ✅ **Quality gates** (linting, type checking, coverage ≥80%)
- ✅ **Security scans** (Ruff, Bandit, dependency checks)
- ✅ **Docker builds** with multi-stage caching
- ✅ **Automated staging deployment** with health checks
- ✅ **Automatic rollback** on deployment failures

---

## 🔧 Workflows

### 1. CI - Tests & Quality Gates (`.github/workflows/ci.yml`)

**Triggers**:
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main` or `master`

**Jobs**:

#### **Lint** (Code Quality)
- Ruff (fast linting)
- Black (code formatting)
- isort (import sorting)
- Pylint (comprehensive linting)
- MyPy (type checking)

#### **Test** (Unit Tests)
- Runs with PostgreSQL 15 and Redis 7 services
- Coverage threshold: ≥80%
- Generates coverage reports (XML, HTML)
- Uploads test results as artifacts

#### **Integration Tests**
- Full stack tests (8-stage ticket lifecycle)
- Error handling & failover scenarios
- Load testing (100 concurrent tickets)
- Monitoring & alerting validation

#### **Quality Gate**
- Validates all previous jobs passed
- Posts summary comment on PRs
- Blocks merge if quality gate fails

**Required Checks**:
- ✅ All lint checks pass (Ruff, Pylint, MyPy)
- ✅ Unit tests pass with ≥80% coverage
- ✅ Integration tests pass (4 scenarios)

---

### 2. Deploy to Staging (`.github/workflows/deploy-staging.yml`)

**Triggers**:
- Automatic: Push to `main` branch (after CI passes)
- Manual: `workflow_dispatch` (Actions tab)

**Jobs**:

#### **Build & Push Docker Image**
- Builds multi-arch Docker image
- Pushes to GitHub Container Registry (ghcr.io)
- Tags: `staging-latest`, `staging-<sha>`
- Uses layer caching for fast builds

#### **Deploy to Staging**
- Creates `.env.staging` from secrets
- Pulls latest images
- Deploys with Docker Compose
- Waits for health checks (max 120s)
- Pulls Ollama models
- Runs smoke tests
- Creates deployment summary

#### **Rollback on Failure**
- Automatically triggers if deployment fails
- Runs `rollback_staging.py --keep-volumes`
- Preserves data but stops services
- Notifies via GitHub commit comment

---

## 🔐 Required Secrets

Configure in **Settings → Secrets and variables → Actions**:

### Staging Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `STAGING_DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://user:pass@host:5433/db` |
| `STAGING_POSTGRES_PASSWORD` | PostgreSQL password | `strong_random_password_here` |
| `STAGING_REDIS_URL` | Redis connection URL | `redis://:password@host:6380/0` |
| `STAGING_REDIS_PASSWORD` | Redis password | `strong_random_password_here` |
| `STAGING_SECRET_KEY` | API secret key (32+ chars) | `your_secret_key_min_32_characters` |

### How to Generate Secrets

```powershell
# Generate random password (32 chars)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Or using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

---

## 🚀 Usage

### Running CI Locally

```powershell
# Full test suite
pytest tests/ -v --cov=agents --cov-report=html

# Linting
ruff check agents/ tests/ cli/
pylint agents/ --rcfile=.pylintrc
mypy agents/ --strict --ignore-missing-imports

# Integration tests
pytest tests/test_integration_full_system.py -v -s

# Smoke tests (requires staging environment)
python tests/smoke_tests_staging.py
```

### Manual Staging Deployment

```powershell
# Via GitHub Actions
# 1. Go to Actions tab
# 2. Select "Deploy to Staging"
# 3. Click "Run workflow"
# 4. Select branch: main
# 5. Optional: Check "Skip tests" (not recommended)
# 6. Click "Run workflow"

# Via CLI
gh workflow run deploy-staging.yml

# With input
gh workflow run deploy-staging.yml -f skip_tests=false
```

### Manual Rollback

```powershell
# Local rollback
python rollback_staging.py --keep-volumes

# Or via GitHub Actions
# The rollback job runs automatically on deployment failure
```

---

## 📊 Monitoring Deployments

### GitHub Actions UI

- **Actions tab**: View all workflow runs
- **Commit page**: See deployment comments
- **Pull request**: See quality gate status

### Deployment Summary

Each successful deployment creates a summary with:
- Environment details (staging)
- Commit SHA and author
- Deployment timestamp
- Docker image tag and digest
- Access URLs (API, Prometheus, Grafana)
- Next steps checklist

### Logs and Artifacts

Workflows upload artifacts for debugging:
- `test-results`: pytest reports, coverage HTML
- `integration-test-logs`: full stack test logs
- `security-reports`: Bandit scan results

---

## 🛠 Workflow Maintenance

### Updating Workflows

```powershell
# Edit workflow files
notepad .github/workflows/ci.yml
notepad .github/workflows/deploy-staging.yml

# Test locally with act (optional)
act -j lint
act -j test

# Commit and push
git add .github/workflows/
git commit -m "ci: Update workflow configuration"
git push
```

### Debugging Workflow Failures

#### Lint Failures

```powershell
# Fix formatting
black agents/ tests/ cli/
isort agents/ tests/ cli/

# Check Pylint issues
pylint agents/ --rcfile=.pylintrc

# Fix type errors
mypy agents/ --strict --ignore-missing-imports
```

#### Test Failures

```powershell
# Run specific test
pytest tests/test_specific.py::test_function -v

# Run with verbose output
pytest tests/ -v -s

# Check test coverage
pytest tests/ --cov=agents --cov-report=html
open htmlcov/index.html
```

#### Integration Test Failures

```powershell
# Run with full logging
pytest tests/test_integration_full_system.py -v -s --log-cli-level=DEBUG

# Check for service availability
docker-compose -f docker-compose.staging.yml ps
docker-compose -f docker-compose.staging.yml logs
```

#### Deployment Failures

```powershell
# Check service health
docker-compose -f docker-compose.staging.yml ps

# View service logs
docker-compose -f docker-compose.staging.yml logs --tail=100

# Check specific service
docker logs twisterlab-api-staging --tail=50

# Manual rollback
python rollback_staging.py --keep-volumes
```

---

## 🔒 Security Best Practices

### Secrets Management

- ✅ **Never commit secrets** to repository
- ✅ **Use GitHub Secrets** for sensitive data
- ✅ **Rotate secrets regularly** (every 90 days)
- ✅ **Use environment-specific secrets** (staging vs production)
- ✅ **Limit secret access** to required workflows only

### Code Security

- ✅ **Ruff linting** catches common issues
- ✅ **MyPy type checking** prevents type errors
- ✅ **Dependency scanning** checks for vulnerabilities
- ✅ **Docker image scanning** with Trivy (optional)

### Access Control

- ✅ **Branch protection** on main branch
- ✅ **Required reviews** for pull requests
- ✅ **Status checks** must pass before merge
- ✅ **Manual approval** for production deployments

---

## 📈 Performance Optimization

### Workflow Speed

Current average times:
- **Lint**: ~2 minutes
- **Test**: ~5 minutes (with services)
- **Integration**: ~8 seconds
- **Docker Build**: ~3 minutes (cached)
- **Deploy**: ~5 minutes (with health checks)
- **Total CI**: ~10-12 minutes

### Optimization Tips

```yaml
# Use pip caching
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('pyproject.toml') }}

# Use Docker layer caching
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max

# Parallel job execution
jobs:
  lint:
  test:
  integration-tests:
  # All run in parallel where possible
```

---

## 🔄 Continuous Improvement

### Metrics to Track

- CI duration (target: <15 minutes)
- Test coverage (target: ≥80%, actual: 100%)
- Deployment frequency (target: >1/day)
- Deployment success rate (target: >95%)
- Rollback frequency (target: <5%)

### Suggested Enhancements

1. **Production Deployment Workflow**
   - Blue-green deployment strategy
   - Canary releases
   - Manual approval gates

2. **Performance Testing**
   - Load test workflow
   - Benchmark comparisons
   - Performance regression detection

3. **Security Scanning**
   - SAST (Static Application Security Testing)
   - DAST (Dynamic Application Security Testing)
   - Dependency vulnerability scanning

4. **Notification Integrations**
   - Slack notifications
   - Email alerts
   - PagerDuty integration

---

## 📚 References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [pytest Documentation](https://docs.pytest.org/)
- [System Prompt - Technical Excellence](../docs/SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md)
- [Staging Deployment Guide](../docs/STAGING_DEPLOYMENT_GUIDE.md)

---

**Last Updated**: 2025-02-11  
**Version**: 1.0.0  
**License**: Apache 2.0
