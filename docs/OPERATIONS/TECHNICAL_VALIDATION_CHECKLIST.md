# TwisterLab - Technical Validation Checklist

Quick reference for validating code changes against TwisterLab quality standards.

**Reference**: See [SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md](./SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md) for complete standards.

---

## Pre-Commit Validation (MANDATORY)

Run these commands before committing:

```bash
# 1. Run tests with coverage
pytest tests/ -v --cov=agents --cov-report=term-missing --cov-report=html
# ✅ PASS: ≥80% coverage, all tests passing

# 2. Check linting
pylint agents/ --rcfile=.pylintrc
# ✅ PASS: Score ≥8.0, no errors

# 3. Type checking
mypy agents/ --strict
# ✅ PASS: No type errors

# 4. Format code
black agents/ tests/
isort agents/ tests/
# ✅ PASS: Code formatted

# 5. Security scan
bandit -r agents/ -f json -o security_report.json
# ✅ PASS: No high/critical vulnerabilities
```

---

## Code Quality Checklist

### ✅ Type Hints & Documentation
- [ ] All functions have type hints (PEP 484)
- [ ] All public methods have docstrings (Google style)
- [ ] Complex logic has inline comments
- [ ] Module has README.md

### ✅ Error Handling
- [ ] Try/except on all I/O operations
- [ ] Structured error responses with context
- [ ] Logging with diagnostic data (error type, stack trace)
- [ ] Metrics updated on error (error counter, error type tag)

### ✅ Testing
- [ ] Unit tests written (isolated logic)
- [ ] Integration tests written (end-to-end workflow)
- [ ] Edge cases covered (timeout, null input, concurrent access)
- [ ] Test coverage ≥80%
- [ ] All tests passing

### ✅ Observability
- [ ] Metrics exposed (response_time_ms, success_rate, error_rate)
- [ ] Health check implemented (`async def health_check()`)
- [ ] Structured logging (JSON format, timestamp, context)
- [ ] Alert thresholds defined

### ✅ Agent Pattern Compliance
- [ ] Inherits from `TwisterAgent`
- [ ] Implements `async def execute(task, context)`
- [ ] Implements `async def health_check()`
- [ ] Returns structured responses (`{"status": "success", "data": ...}`)

---

## Testing Standards

### Unit Test Template
```python
import pytest
from agents.your_agent import YourAgent

@pytest.fixture
def agent():
    """Create agent instance for testing"""
    return YourAgent()

@pytest.mark.asyncio
async def test_agent_operation(agent):
    """Test agent operation with full context"""
    result = await agent.execute(
        "Operation description",
        {"key": "value"}
    )
    
    # Validate response structure
    assert result["status"] == "success"
    assert "data" in result
    assert "timestamp" in result
```

### Integration Test Template
```python
@pytest.mark.asyncio
async def test_full_workflow(agent, database_session):
    """Test complete workflow end-to-end"""
    # 1. Setup
    ticket = await create_test_ticket(database_session)
    
    # 2. Execute
    result = await agent.execute(
        "Process ticket",
        {"ticket_id": ticket.id}
    )
    
    # 3. Verify
    assert result["status"] == "success"
    updated_ticket = await get_ticket(database_session, ticket.id)
    assert updated_ticket.status == "resolved"
```

---

## Deployment Validation

### Pre-Deployment Checklist
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Coverage ≥80% (`pytest --cov=agents --cov-report=term`)
- [ ] Linting clean (`pylint agents/ --rcfile=.pylintrc`)
- [ ] Type checking clean (`mypy agents/ --strict`)
- [ ] Security scan clean (`bandit -r agents/`)
- [ ] Docker build successful (`docker build -t twisterlab:test .`)
- [ ] Smoke tests passing (`pytest tests/integration/ -m smoke`)

### Post-Deployment Validation
- [ ] Health checks passing (all agents return `"status": "healthy"`)
- [ ] Metrics flowing to Prometheus/Grafana
- [ ] No error spikes in logs
- [ ] Response time within 10% of baseline
- [ ] Alerts configured and tested
- [ ] Rollback procedure documented

---

## Common Issues & Solutions

### Issue: Tests Failing
```bash
# Run with verbose output
pytest tests/test_your_agent.py -vv -s

# Run specific test
pytest tests/test_your_agent.py::test_specific_function -vv

# Check test coverage for specific module
pytest tests/ --cov=agents.your_agent --cov-report=term-missing
```

### Issue: Linting Errors
```bash
# Show all linting issues
pylint agents/your_agent.py

# Auto-fix formatting
black agents/your_agent.py
isort agents/your_agent.py

# Disable specific rule (use sparingly)
# pylint: disable=line-too-long
```

### Issue: Type Errors
```bash
# Check specific file
mypy agents/your_agent.py --strict

# Show error details
mypy agents/your_agent.py --strict --show-error-codes

# Add type ignore (use sparingly)
import psutil  # type: ignore
```

### Issue: Low Coverage
```bash
# Generate HTML coverage report
pytest tests/ --cov=agents --cov-report=html

# Open htmlcov/index.html to see which lines are not covered
# Add tests for uncovered lines
```

---

## Performance Validation

### Benchmarking
```python
import time

async def benchmark_agent_operation(agent, iterations=100):
    """Benchmark agent operation performance"""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        await agent.execute("Operation", {"key": "value"})
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]
    
    print(f"Average: {avg_time*1000:.2f}ms")
    print(f"P95: {p95_time*1000:.2f}ms")
```

### Load Testing
```bash
# Use locust or similar for load testing
# Example: 100 concurrent users, 1000 requests
locust -f tests/load_test.py --users 100 --spawn-rate 10 --run-time 60s
```

---

## Agent-Specific Standards

### Current Agents (v1.0.0)
| Agent | Tests | Coverage | Health Check | Metrics |
|-------|-------|----------|--------------|---------|
| ClassifierAgent | ✅ | 100% | ✅ | ✅ |
| HelpdeskAgent | ✅ | 100% | ✅ | ✅ |
| DesktopCommanderAgent | ✅ | 100% | ✅ | ✅ |
| MaestroOrchestratorAgent | 47/47 | 100% | ✅ | ✅ |
| SyncAgent | 31/31 | 100% | ✅ | ✅ |
| BackupAgent | 24/24 | 100% | ✅ | ✅ |
| MonitoringAgent | 36/36 | 100% | ✅ | ✅ |

**Total**: 138+ tests, 100% success rate

---

## Quick Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific agent tests
pytest tests/test_monitoring_agent.py -v

# Run with coverage
pytest tests/ --cov=agents --cov-report=html

# Run integration tests only
pytest tests/integration/ -v

# Run smoke tests only
pytest tests/ -v -m smoke

# Lint all code
pylint agents/ tests/

# Type check all code
mypy agents/ --strict

# Format all code
black agents/ tests/ && isort agents/ tests/

# Security scan
bandit -r agents/ -f json -o security_report.json

# Build Docker image
docker build -t twisterlab:dev .

# Run Docker Compose stack
docker-compose up -d

# Check container health
docker-compose ps

# View logs
docker-compose logs -f monitoring-agent
```

---

## Monitoring Queries

### Prometheus Queries
```promql
# Agent response time (average over 5m)
rate(agent_response_time_ms[5m])

# Error rate by agent
rate(agent_errors_total[5m]) / rate(agent_requests_total[5m])

# API latency P95
histogram_quantile(0.95, rate(api_response_time_bucket[5m]))

# System CPU usage
system_cpu_usage_percent

# Active alerts
sum(active_alerts_total) by (severity)
```

### Grafana Dashboards
- **System Overview**: CPU, memory, disk, network
- **Agent Performance**: Response time, success rate, error rate for all 7 agents
- **Database Metrics**: Connections, query time, slow queries
- **API Metrics**: Request rate, latency percentiles, status codes
- **Alerts**: Active alerts by severity, alert history

---

## Resources

- **Full Documentation**: [SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md](./SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md)
- **Development Guide**: [copilot-instructions.md](../.github/copilot-instructions.md)
- **API Documentation**: [agents/api/README.md](../agents/api/README.md)
- **Deployment Guide**: [DEPLOYMENT.md](../DEPLOYMENT.md)

---

**Last Updated**: 2025-02-11  
**Version**: 1.0.0  
**Maintainer**: TwisterLab Development Team
