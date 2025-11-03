# 🧬 **TWISTERLAB - SYSTEM PROMPT (TECHNICAL EXCELLENCE)**

***

## **CONTEXT**

TwisterLab is a multi-agent AI orchestration system designed for autonomous IT infrastructure management. This prompt defines operational standards and quality gates for all agents, modules, integrations, and contributors.

***

## **CORE PRINCIPLES**

### 1. **Traceability**
- Every operation MUST produce logs (structured, timestamped, parsable).
- Every decision MUST be auditable (agent ID, input, output, confidence, timestamp).
- Every failure MUST be captured with diagnostic context (error type, stack trace, recovery action).

### 2. **Reproducibility**
- All builds, tests, deployments MUST be scriptable and repeatable.
- Environments MUST be version-controlled (Docker, config files, dependencies).
- Test suites MUST run identically across dev/staging/prod.

### 3. **Robustness**
- Every critical path MUST have error handling (try/catch, fallback, retry logic).
- Every agent MUST implement health checks (self-diagnostic, status reporting).
- Every workflow MUST be tested under failure conditions (network loss, service down, data corruption).

### 4. **Observability**
- Every agent MUST expose metrics (response time, success rate, error rate).
- Every system component MUST integrate with monitoring (Prometheus, Grafana).
- Every alert MUST have actionable context (threshold exceeded, affected service, recommended action).

### 5. **Modularity**
- Every agent MUST follow the BaseAgent pattern (standardized interface).
- Every module MUST have clear boundaries (input/output contracts, no side effects).
- Every integration point MUST be abstracted (swappable backends, configurable endpoints).

### 6. **Test Coverage**
- Every module MUST achieve ≥80% code coverage.
- Every agent MUST have unit tests (isolated logic) AND integration tests (end-to-end workflow).
- Every edge case MUST be documented and tested (timeout, null input, concurrent access).

### 7. **Documentation**
- Every API endpoint MUST have OpenAPI/Swagger specs.
- Every agent MUST have a README (purpose, dependencies, configuration, examples).
- Every workflow MUST have a sequence diagram (visual flow, decision points).

### 8. **Performance**
- Every critical operation MUST have performance benchmarks (baseline, target, threshold).
- Every bottleneck MUST be profiled and logged (CPU, memory, I/O, network).
- Every optimization MUST be validated with before/after metrics.

***

## **OPERATIONAL REQUIREMENTS**

### **For AI Agents (Copilot, Claude, etc.):**
1. Generate code that passes linting (mypy, pylint, black).
2. Include type hints for all functions (PEP 484).
3. Write docstrings for all public methods (Google style).
4. Propose test cases alongside implementation.
5. Flag potential failure modes and suggest mitigation.

### **For Code Reviews:**
1. Verify adherence to BaseAgent pattern.
2. Check for proper error handling (try/except, logging).
3. Validate test coverage (pytest --cov).
4. Ensure metrics tracking (response time, success rate).
5. Confirm documentation completeness (README, inline comments).

### **For Deployment:**
1. Run full test suite (unit + integration).
2. Validate environment configuration (env vars, secrets).
3. Execute smoke tests (critical paths, health checks).
4. Monitor initial metrics (latency, error rate, resource usage).
5. Document rollback procedure (if deployment fails).

***

## **QUALITY GATES**

Before merging/deploying, ALL of the following MUST pass:

- ✅ **Linting**: No errors (pylint, mypy, black)
- ✅ **Tests**: ≥80% coverage, all passing
- ✅ **Performance**: Within 10% of baseline benchmarks
- ✅ **Security**: No high/critical vulnerabilities (bandit, safety)
- ✅ **Documentation**: README updated, API specs current
- ✅ **Observability**: Metrics exposed, alerts configured
- ✅ **Reproducibility**: Deployment script tested, rollback verified

***

## **EXPECTED BEHAVIOR**

### **On Success:**
- Log success with context (agent ID, operation, duration, result).
- Update metrics (increment success counter, record latency).
- Return structured response (status, data, metadata).

### **On Failure:**
- Log failure with diagnostic data (error type, stack trace, input).
- Update metrics (increment error counter, tag error type).
- Trigger alert if threshold exceeded (email, Slack, PagerDuty).
- Attempt recovery (retry, fallback, escalate).

### **On Anomaly:**
- Flag unusual patterns (latency spike, error rate increase, resource exhaustion).
- Generate diagnostic report (affected component, timeline, correlation).
- Recommend investigation (potential causes, diagnostic commands).

***

## **SUCCESS CRITERIA**

A TwisterLab system is considered **production-ready** when:

1. All 7 agents operational with 100% health checks passing.
2. Full test suite passing with ≥80% coverage.
3. All critical paths tested under failure conditions.
4. Monitoring dashboards live with real-time metrics.
5. Alert rules configured with documented response procedures.
6. Deployment fully automated with validated rollback.
7. Documentation complete and accessible (README, API docs, runbooks).

***

## **CONTINUOUS IMPROVEMENT**

- Every incident MUST generate a post-mortem (root cause, timeline, action items).
- Every performance bottleneck MUST be profiled and optimized.
- Every recurring error MUST trigger a permanent fix (not just a workaround).
- Every new feature MUST include tests, docs, and monitoring.

***

## **TWISTERLAB-SPECIFIC IMPLEMENTATION**

### **Agent Architecture (BaseAgent Pattern)**

All agents MUST inherit from `TwisterAgent` and implement:

```python
class TwisterAgent:
    """Base class for all TwisterLab agents"""
    
    def __init__(self, name: str, display_name: str, ...):
        self.name = name  # Unique agent identifier
        self.display_name = display_name
        self.tools = []  # MCP tool definitions
        self.metrics = {}  # Performance metrics
        
    async def execute(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agent task with full traceability"""
        
    async def health_check(self) -> Dict[str, Any]:
        """Return agent health status"""
```

### **Current Agent Status (v1.0.0-alpha.1)**

| Agent | Status | Tests | Coverage | Health Check | Metrics |
|-------|--------|-------|----------|--------------|---------|
| ClassifierAgent | ✅ Production | ✅ | 100% | ✅ | ✅ |
| HelpdeskAgent | ✅ Production | ✅ | 100% | ✅ | ✅ |
| DesktopCommanderAgent | ✅ Production | ✅ | 100% | ✅ | ✅ |
| MaestroOrchestratorAgent | ✅ Production | 47/47 | 100% | ✅ | ✅ |
| SyncAgent | ✅ Production | 31/31 | 100% | ✅ | ✅ |
| BackupAgent | ✅ Production | 24/24 | 100% | ✅ | ✅ |
| MonitoringAgent | ✅ Production | 36/36 | 100% | ✅ | ✅ |

**Total**: 138+ tests, 100% success rate, all agents operational.

### **Testing Standards**

```python
# Unit test template
@pytest.mark.asyncio
async def test_agent_operation(agent_fixture):
    """Test agent operation with full context"""
    result = await agent_fixture.execute(
        "Operation description",
        {"key": "value"}
    )
    
    # Validate response structure
    assert result["status"] == "success"
    assert "data" in result
    assert "timestamp" in result
    
    # Validate metrics updated
    assert agent_fixture.metrics["operations_total"] > 0
```

### **Monitoring Integration**

All agents expose metrics via MonitoringAgent:

```python
# System metrics (psutil)
system_cpu_usage_percent
system_memory_usage_percent
system_disk_usage_percent
system_network_bytes_sent
system_network_bytes_recv

# Agent metrics (per agent)
agent_{name}_response_time_ms
agent_{name}_success_rate
agent_{name}_error_rate
agent_{name}_requests_total

# Database metrics
db_connections_active
db_query_time_avg_ms
db_slow_queries

# API metrics
api_response_time_avg_ms
api_response_time_p95_ms
api_response_time_p99_ms
api_status_2xx
api_status_4xx
api_status_5xx
```

### **Alert Thresholds**

```python
thresholds = {
    "cpu_usage": 80.0,           # Percent
    "memory_usage": 85.0,        # Percent
    "disk_usage": 90.0,          # Percent (CRITICAL)
    "api_response_time": 2.0,    # Seconds
    "error_rate": 10.0,          # Percent (CRITICAL)
    "agent_response_time": 5.0   # Seconds
}
```

### **Error Handling Pattern**

```python
async def execute(self, task: str, context: Dict[str, Any]):
    """Execute with comprehensive error handling"""
    try:
        # Log operation start
        logger.info(f"Agent {self.name} executing: {task}")
        start_time = time.time()
        
        # Execute operation
        result = await self._perform_operation(context)
        
        # Update metrics
        duration = time.time() - start_time
        self.metrics["operations_total"] += 1
        self.metrics["response_time_ms"].append(duration * 1000)
        self.metrics["success_count"] += 1
        
        # Log success
        logger.info(f"Operation completed in {duration:.2f}s")
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration * 1000
        }
        
    except Exception as e:
        # Update error metrics
        self.metrics["operations_total"] += 1
        self.metrics["error_count"] += 1
        self.metrics["last_error"] = str(e)
        
        # Log failure with context
        logger.error(
            f"Operation failed: {e}",
            extra={
                "agent": self.name,
                "task": task,
                "context": context,
                "stack_trace": traceback.format_exc()
            }
        )
        
        # Return structured error
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
```

### **Deployment Checklist**

Before deploying to production:

1. ✅ Run full test suite: `pytest tests/ -v --cov=agents --cov-report=html`
2. ✅ Check lint: `pylint agents/ --rcfile=.pylintrc`
3. ✅ Type check: `mypy agents/ --strict`
4. ✅ Security scan: `bandit -r agents/ -f json -o security_report.json`
5. ✅ Build Docker image: `docker build -t twisterlab:v1.0.0 .`
6. ✅ Test in staging: `docker-compose -f docker-compose.staging.yml up -d`
7. ✅ Run smoke tests: `pytest tests/integration/ -v -m smoke`
8. ✅ Validate metrics: Check Grafana dashboards
9. ✅ Configure alerts: Verify Prometheus rules
10. ✅ Document rollback: Update `DEPLOYMENT.md`

***

## **COMPLIANCE VERIFICATION**

Use this checklist to verify any module/agent/integration:

### **Code Quality**
- [ ] Type hints on all functions (PEP 484)
- [ ] Docstrings on all public methods (Google style)
- [ ] No linting errors (pylint score ≥8.0)
- [ ] No type errors (mypy --strict)
- [ ] Code formatted (black, isort)

### **Testing**
- [ ] Unit tests written (isolated logic)
- [ ] Integration tests written (end-to-end)
- [ ] Edge cases covered (timeout, null, concurrent)
- [ ] Test coverage ≥80%
- [ ] All tests passing

### **Observability**
- [ ] Metrics exposed (response time, success rate, error rate)
- [ ] Health check implemented
- [ ] Structured logging (JSON format, timestamp, context)
- [ ] Alert thresholds defined
- [ ] Monitoring dashboard created

### **Documentation**
- [ ] README exists (purpose, setup, usage, examples)
- [ ] API specs current (OpenAPI/Swagger)
- [ ] Inline comments for complex logic
- [ ] Sequence diagram for workflows
- [ ] Troubleshooting guide

### **Robustness**
- [ ] Error handling on all critical paths
- [ ] Retry logic with exponential backoff
- [ ] Fallback mechanisms defined
- [ ] Timeout configurations set
- [ ] Resource cleanup (connections, files)

### **Performance**
- [ ] Benchmarks established (baseline, target)
- [ ] Profiling completed (CPU, memory, I/O)
- [ ] Bottlenecks identified and optimized
- [ ] Load testing performed
- [ ] Performance within 10% of target

***

## **VERSION HISTORY**

- **v1.0.0** (2025-02-11): Initial system prompt based on 7-agent production deployment
- **v1.0.0-alpha.1** (2025-01-28): All 7 agents operational with 100% test coverage

***

**END SYSTEM PROMPT**

---

**Usage**: This document serves as the authoritative reference for all TwisterLab development, review, testing, deployment, and monitoring activities. Any deviation from these standards MUST be documented with justification and approved by the technical lead.

**Enforcement**: All AI agents (GitHub Copilot, Claude, etc.) MUST follow these guidelines when generating code, reviewing changes, or proposing solutions.

**Updates**: This document MUST be updated when new patterns emerge, lessons are learned, or system requirements change. All updates MUST be versioned and communicated to the team.
