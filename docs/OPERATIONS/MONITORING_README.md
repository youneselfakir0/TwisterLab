# 📊 TwisterLab Monitoring Stack

Complete monitoring and observability infrastructure for TwisterLab v1.0.0.

## 🚀 Quick Start

### Deploy Monitoring Services

```powershell
# Deploy the complete monitoring stack
.\deploy_monitoring.ps1
```

### Check Service Status

```powershell
# Verify all services are running
.\check_monitoring.ps1
```

## 🎯 Service Access URLs

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Grafana** | `http://localhost:3000` | admin (credentials via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD or Docker secret) | Dashboards & Visualization |
| **Prometheus** | `http://localhost:9091` | - | Metrics Collection & Alerting |
| **Jaeger** | `http://localhost:16686` | - | Distributed Tracing |
| **Alertmanager** | `http://localhost:9093` | - | Alert Management |

## 🏗️ Architecture

### Services Overview

- **Prometheus**: Time-series database for metrics collection
- **Grafana**: Dashboard and visualization platform
- **Jaeger**: Distributed tracing system
- **Alertmanager**: Alert routing and notification management

### Configuration Files

```
monitoring/
├── prometheus/
│   ├── config/prometheus.yml      # Main Prometheus configuration
│   └── rules/twisterlab-alerts.yml # Alerting rules
├── grafana/
│   ├── config/grafana.ini         # Grafana configuration
│   └── dashboards/twisterlab-overview.json # System dashboard
├── jaeger/
│   └── config/jaeger-config.yml   # Jaeger configuration
└── alertmanager/
    └── config/alertmanager.yml    # Alertmanager configuration
```

### System Metrics

- CPU usage and load
- Memory usage
- Disk I/O and space
- Network traffic

### Application Metrics

- API response times (95th percentile)
- Agent execution counts
- Error rates and failure counts
- Request rates and throughput

### Infrastructure Metrics

- Docker container stats
- Traefik load balancer metrics
- Database connection pools
- Cache hit/miss ratios

## 🚨 Alerting Rules

### Critical Alerts

- **TwisterLabAPIDown**: API unavailable for 5+ minutes
- **TwisterLabAPIHighResponseTime**: 95th percentile > 2 seconds for 5+ minutes

### Warning Alerts

- **TwisterLabAgentExecutionFailed**: Agent execution failures detected
- **TwisterLabHighCPUUsage**: CPU usage > 90% for 5+ minutes
- **TwisterLabHighMemoryUsage**: Memory usage > 90% for 5+ minutes
```

### Docker Deployment

- **Stack Name**: `twisterlab-monitoring`
- **Network**: `twisterlab_prod` (external overlay network)
- **Volumes**: `prometheus_data`, `grafana_data`, `alertmanager_data` (external)
- **Constraints**: Linux nodes only

## 📈 Available Metrics

### System Metrics
- CPU usage and load
- Memory usage
- Disk I/O and space
- Network traffic

### Application Metrics
- API response times (95th percentile)
- Agent execution counts
- Error rates and failure counts
- Request rates and throughput

### Infrastructure Metrics
- Docker container stats
- Traefik load balancer metrics
- Database connection pools
- Cache hit/miss ratios

## 🚨 Alerting Rules

### Critical Alerts
- **TwisterLabAPIDown**: API unavailable for 5+ minutes
- **TwisterLabAPIHighResponseTime**: 95th percentile > 2 seconds for 5+ minutes

### Warning Alerts
- **TwisterLabAgentExecutionFailed**: Agent execution failures detected
- **TwisterLabHighCPUUsage**: CPU usage > 90% for 5+ minutes
- **TwisterLabHighMemoryUsage**: Memory usage > 90% for 5+ minutes

## 🔧 Configuration

### Grafana Setup

1. Access Grafana at `http://localhost:3000`
2. Login with Grafana admin account (credentials set via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD or Docker secret)
3. Change default password on first login
4. Import dashboards from `monitoring/grafana/dashboards/`

### Prometheus Configuration

- Scrapes metrics every 15 seconds
- Evaluates alerting rules every 15 seconds
- Retains data for 200 hours
- Auto-discovers services via Docker Swarm

### Alertmanager Configuration

- Routes all alerts to email notifications
- Groups alerts by alertname
- Waits 10s before sending, repeats every 1 hour
- SMTP configuration ready for email alerts

## 🐛 Troubleshooting

### Services Not Starting

```powershell
# Check Docker Swarm status
docker node ls

# Check stack services
docker stack ps twisterlab-monitoring

# Check service logs
docker service logs twisterlab-monitoring_prometheus
```

### Port Conflicts

If ports are already in use:

```powershell
# Check what's using the ports
netstat -ano | findstr :9091
netstat -ano | findstr :3000

# Modify ports in docker-compose.monitoring.yml if needed
```

### Data Persistence

Monitoring data is persisted in Docker volumes:

```powershell
# List volumes
docker volume ls

# Inspect volume details
docker volume inspect prometheus_data
```

## 📊 Dashboards

### Pre-configured Dashboards

1. **TwisterLab System Overview**
   - API response times
   - Agent execution metrics
   - System CPU/memory usage

### Custom Dashboards

Create custom dashboards in Grafana:

1. Go to `http://localhost:3000`
2. Click "Create" → "Dashboard"
3. Add panels with Prometheus queries
4. Save and share with the team

## 🔄 Integration with TwisterLab

### Metrics Collection

The monitoring stack automatically collects metrics from:

- **TwisterLab API**: HTTP request metrics, response times
- **Agent System**: Execution counts, success/failure rates
- **Infrastructure**: Docker stats, system resources
- **Traefik**: Load balancer metrics and routing stats

### Alert Integration

Alerts are configured to trigger on:

- Service downtime
- Performance degradation
- Resource exhaustion
- Agent execution failures

## 🚀 Scaling & High Availability

### Production Deployment

For production environments:

1. Deploy multiple Prometheus instances
2. Use external storage for metrics retention
3. Configure Alertmanager clustering
4. Set up Grafana high availability
5. Implement backup strategies for volumes

### Backup Strategy

```bash
# Backup monitoring data
docker run --rm -v prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus_backup.tar.gz -C /data .
docker run --rm -v grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana_backup.tar.gz -C /data .
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

## 🆘 Support

For issues with the monitoring stack:

1. Check service logs: `docker service logs <service_name>`
2. Verify network connectivity: `docker network inspect twisterlab_prod`
3. Review configuration files in `monitoring/` directory
4. Check Docker Swarm status: `docker node ls`

---

**Status**: ✅ Production Ready
**Version**: v1.0.0
**Last Updated**: 2025-01-02
