# 🚀 TwisterLab Autonomous Agents Integration

## Overview

TwisterLab v1.0.0 now includes a complete autonomous agent system that provides real-time IT operations automation. The system integrates three core autonomous agents:

- **MonitoringAgent**: Continuous system health monitoring and alerting
- **BackupAgent**: Automated disaster recovery and data backup
- **SyncAgent**: Cache and database synchronization management

## Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │ Autonomous       │    │   PostgreSQL    │
│   REST API      │◄──►│ Orchestrator     │◄──►│   + Redis       │
│   (Port 8000)   │    │ (Port 8001)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────────────┐
                    │   MCP Isolation    │
                    │   Tier 1-4        │
                    └────────────────────┘
```

### Agent Communication

Agents communicate through a secure **Model Context Protocol (MCP)** system with 4-tier isolation:

- **Tier 1**: TwisterLab Agent MCPs (ports 9000-9100)
- **Tier 2**: Claude Desktop MCPs (ports 9200-9300)
- **Tier 3**: Docker System MCPs (ports 9400-9500)
- **Tier 4**: Copilot MCPs (ports 9600-9700)

## Quick Start

### 1. Deploy the System

```bash
# Start all services including autonomous agents
docker-compose up -d

# Or deploy autonomous agents separately
python deploy_autonomous_agents.py
```

### 2. Verify Deployment

```bash
# Check service health
curl http://localhost:8001/autonomous/health

# Run integration tests
python test_autonomous_agents.py

# Start monitoring
python monitor_autonomous_agents.py
```

### 3. Access the API

The autonomous agents expose REST endpoints at `http://localhost:8001/autonomous/`:

```bash
# Get system health
curl http://localhost:8001/autonomous/health

# Get agent status
curl http://localhost:8001/autonomous/agents/status

# Execute agent operation
curl -X POST http://localhost:8001/autonomous/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "MonitoringAgent",
    "operation": "check_system_health",
    "params": {}
  }'
```

## API Reference

### Health Endpoints

#### GET `/autonomous/health`

Get overall system health status.

**Response:**

```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Agent Management

#### GET `/autonomous/agents/status`

Get status of all autonomous agents.

**Response:**

```json
{
  "agents": [
    {
      "name": "MonitoringAgent",
      "status": "active",
      "last_operation": "check_system_health",
      "uptime_seconds": 1800
    }
  ]
}
```

#### POST `/autonomous/agents/execute`

Execute an operation on a specific agent.

**Request:**

```json
{
  "agent_name": "MonitoringAgent",
  "operation": "check_system_health",
  "params": {
    "detailed": true
  }
}
```

**Response:**

```json
{
  "status": "success",
  "result": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  },
  "execution_time": 1.23
}
```

### Scheduling

#### GET `/autonomous/schedule/tasks`

Get all scheduled tasks.

**Response:**

```json
{
  "tasks": [
    {
      "id": "health_check_001",
      "agent": "MonitoringAgent",
      "operation": "check_system_health",
      "schedule": "*/5 * * * *",
      "next_run": "2024-01-15T10:35:00Z",
      "status": "active"
    }
  ]
}
```

#### POST `/autonomous/schedule/tasks`

Schedule a new task.

**Request:**

```json
{
  "agent_name": "BackupAgent",
  "operation": "create_backup",
  "schedule": "0 2 * * *",
  "params": {
    "backup_type": "full"
  }
}
```

### Emergency Response

#### POST `/autonomous/emergency/stop-all`

Emergency stop all agents.

**Response:**

```json
{
  "status": "success",
  "message": "All agents stopped successfully",
  "stopped_agents": ["MonitoringAgent", "BackupAgent", "SyncAgent"]
}
```

#### POST `/autonomous/emergency/restart-all`

Restart all agents after emergency stop.

### Metrics

#### GET `/autonomous/metrics`

Get system performance metrics.

**Response:**

```json
{
  "metrics": {
    "cpu_percent": 45.2,
    "memory_percent": 67.8,
    "disk_usage_percent": 23.1,
    "network_io": 1024000,
    "active_tasks": 3,
    "queued_tasks": 0
  }
}
```

## Agent Operations

### MonitoringAgent

**Operations:**

- `check_system_health`: Comprehensive system health check
- `monitor_services`: Monitor specific services
- `alert_on_threshold`: Set up alerting thresholds

**Example:**

```bash
curl -X POST http://localhost:8001/autonomous/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "MonitoringAgent",
    "operation": "check_system_health",
    "params": {"detailed": true}
  }'
```

### BackupAgent

**Operations:**

- `create_backup`: Create system/database backup
- `restore_backup`: Restore from backup
- `list_backups`: List available backups

**Example:**

```bash
curl -X POST http://localhost:8001/autonomous/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "BackupAgent",
    "operation": "create_backup",
    "params": {"backup_type": "full", "destination": "/backups"}
  }'
```

### SyncAgent

**Operations:**

- `sync_data`: Synchronize data between systems
- `validate_sync`: Validate synchronization integrity
- `repair_sync`: Repair synchronization issues

**Example:**

```bash
curl -X POST http://localhost:8001/autonomous/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "SyncAgent",
    "operation": "sync_data",
    "params": {"sync_type": "cache", "source": "redis", "target": "postgres"}
  }'
```

## Configuration

### Environment Variables

```bash
# Autonomous Agents Service
AUTONOMOUS_AGENTS_PORT=8001
AUTONOMOUS_AGENTS_HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://twisterlab:twisterlab2024!@postgres:5432/twisterlab

# Redis
REDIS_URL=redis://redis:6379/0

# Monitoring
METRICS_RETENTION_DAYS=30
ALERT_EMAIL=admin@company.com

# Security
MCP_ENCRYPTION_KEY=your-encryption-key-here
CREDENTIAL_SCOPE=enterprise
```

### Scheduling Configuration

Tasks are scheduled using cron expressions:

```python
# Examples
"*/5 * * * *"    # Every 5 minutes
"0 */1 * * *"   # Every hour
"0 2 * * *"     # Daily at 2 AM
"0 0 * * 1"     # Weekly on Monday
```

## Monitoring & Maintenance

### Health Monitoring

```bash
# Continuous monitoring
python monitor_autonomous_agents.py --continuous --interval 300

# Generate report
python monitor_autonomous_agents.py --save

# Check logs
docker-compose logs autonomous-agents
```

### Performance Tuning

1. **Memory Management**: Monitor memory usage and adjust container limits
2. **Task Queuing**: Monitor queued tasks and scale agents if needed
3. **Database Optimization**: Regular maintenance of PostgreSQL and Redis
4. **Network Isolation**: Ensure MCP tier isolation is maintained

### Backup & Recovery

```bash
# Manual backup
curl -X POST http://localhost:8001/autonomous/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "BackupAgent",
    "operation": "create_backup",
    "params": {"backup_type": "full"}
  }'

# List backups
curl -X POST http://localhost:8001/autonomous/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "BackupAgent",
    "operation": "list_backups"
  }'
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check dependencies
docker-compose ps

# Check logs
docker-compose logs autonomous-agents

# Verify configuration
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

#### Agent Operations Fail
```bash
# Check agent status
curl http://localhost:8001/autonomous/agents/status

# Check MCP connectivity
curl http://localhost:9001/health  # MonitoringAgent MCP

# Verify credentials
python agents/security/credential_manager.py check
```

#### High Resource Usage
```bash
# Check metrics
curl http://localhost:8001/autonomous/metrics

# Monitor processes
docker stats twisterlab-autonomous-agents

# Review task queue
curl http://localhost:8001/autonomous/schedule/tasks
```

### Emergency Procedures

1. **Stop All Agents**:
   ```bash
   curl -X POST http://localhost:8001/autonomous/emergency/stop-all
   ```

2. **Restart Services**:
   ```bash
   docker-compose restart autonomous-agents
   ```

3. **Full System Reset**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Security

### Credential Management

- All credentials are encrypted using Fernet cipher
- Master password stored securely in environment variables
- Credentials scoped by enterprise/personal access
- Audit trail for all credential access

### Network Security

- MCP isolation prevents cross-tier communication
- Firewall rules enforce tier separation
- Encrypted communication between components
- Regular security scans and updates

## Development

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods (`execute`, `_process`, etc.)
3. Add to orchestrator configuration
4. Update API routes if needed
5. Add tests and documentation

### Extending Operations

1. Add operation method to agent class
2. Update API validation
3. Add operation documentation
4. Test operation thoroughly

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review logs: `docker-compose logs autonomous-agents`
3. Run diagnostics: `python test_autonomous_agents.py`
4. Generate monitoring report: `python monitor_autonomous_agents.py --save`
5. Contact the development team with the generated report

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
**Documentation**: https://github.com/youneselfakir0/TwisterLab
