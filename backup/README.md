# TwisterLab Automated Backup System

## Overview

The TwisterLab Automated Backup System provides comprehensive, scheduled backups for all production components including databases, configurations, logs, and full system snapshots. The system is designed for high reliability, security, and monitoring.

## Features

- **Automated Scheduling**: Daily, hourly, and weekly backup schedules
- **Multi-Storage**: Local filesystem and Azure Blob Storage support
- **Compression & Encryption**: All backups are compressed and encrypted
- **Integrity Checks**: Automatic validation of backup integrity
- **Monitoring & Alerts**: Real-time monitoring with Grafana dashboards
- **Retention Policies**: Configurable retention periods for different backup types
- **Audit Trail**: Complete logging of all backup operations

## Backup Types

### Database Backups

- **Schedule**: Daily at 2:00 AM
- **Retention**: 30 days
- **Storage**: Local + Remote
- **Content**: PostgreSQL database dumps with point-in-time recovery

### Configuration Backups

- **Schedule**: Daily at 3:00 AM
- **Retention**: 90 days
- **Storage**: Local + Remote
- **Content**: All configuration files, secrets, and Docker configurations

### Log Backups

- **Schedule**: Hourly
- **Retention**: 7 days
- **Storage**: Local only
- **Content**: Application logs, system logs, and audit trails

### Full System Backups

- **Schedule**: Weekly on Sunday at 4:00 AM
- **Retention**: 365 days
- **Storage**: Local + Remote
- **Content**: Complete system snapshot including all data and configurations

## Quick Start

### 1. Start the Backup Service

```powershell
# Start the backup service
.\backup\manage_backup_service.ps1 -Action start

# Check service status
.\backup\manage_backup_service.ps1 -Action status
```

### 2. Run Manual Backup

```powershell
# Run a specific backup type
.\backup\manage_backup_service.ps1 -Action manual -BackupType database

# Available types: database, config, logs, full_system
```

### 3. View Backup Statistics

```powershell
# Show backup statistics
.\backup\manage_backup_service.ps1 -Action stats
```

## Configuration

Backup configuration is managed in `backup/backup_config.py`:

```python
BACKUP_CONFIG = {
    'database': {
        'schedule': 'daily',
        'time': '02:00',
        'retention_days': 30,
        'compression': True,
        'encryption': True,
        'storage_locations': ['local', 'remote']
    }
    # ... other configurations
}
```

## Monitoring

### Grafana Dashboard

Access the backup monitoring dashboard at:
`http://grafana.twisterlab.local/d/twisterlab-backup-monitoring`

### Key Metrics

- **Success Rate**: Percentage of successful backups
- **Duration Trends**: Backup execution times over time
- **Storage Usage**: Current storage utilization
- **Recent Operations**: Latest backup activities
- **Alerts**: Active backup-related alerts

### Log Files

- **Service Logs**: `logs/backup_service.log`
- **Backup Metadata**: `backup/backup_metadata.log`
- **Notifications**: `backup/notifications.log`
- **Alerts**: `backup/alerts.log`

## Storage Configuration

### Local Storage

- **Path**: `/opt/twisterlab/backups`
- **Max Size**: 100 GB
- **Cleanup Threshold**: 80% (automatic cleanup when reached)

### Remote Storage (Azure Blob)

- **Container**: `twisterlab-backups`
- **Redundancy**: Geo-redundant storage (GRS)
- **Encryption**: Server-side encryption enabled

## Security

### Encryption

- All backups are encrypted using Fernet cipher
- Master encryption keys are rotated every 90 days
- Keys are stored securely in the credential vault

### Access Control

- Backup operations are audited
- Access to backup files is restricted
- Integrity checks prevent tampering

## Troubleshooting

### Service Won't Start

```powershell
# Check service logs
.\backup\manage_backup_service.ps1 -Action logs

# Validate configuration
python backup/backup_config.py
```

### Backup Failures

```powershell
# Check recent logs
Get-Content logs/backup_service.log -Tail 20

# Run manual backup for testing
.\backup\manage_backup_service.ps1 -Action manual -BackupType database
```

### Storage Issues

```powershell
# Check storage usage
# View Grafana dashboard for storage metrics

# Manual cleanup if needed
# The system automatically cleans up old backups
```

## API Integration

The backup system integrates with the TwisterLab API:

```python
# Manual backup via API
POST /api/v1/autonomous/agents/backup/execute
{
    "operation": "backup",
    "context": {"backup_type": "database"}
}
```

## Maintenance

### Regular Tasks

- **Weekly**: Review backup success rates in Grafana
- **Monthly**: Verify backup integrity manually
- **Quarterly**: Test disaster recovery procedures
- **Annually**: Review and update retention policies

### Emergency Procedures

1. **Backup Failure Alert**:
   - Check service status
   - Review error logs
   - Run manual backup if needed
   - Escalate to engineering if persistent

2. **Storage Full**:
   - Automatic cleanup triggers at 80%
   - Manual intervention if automatic cleanup fails
   - Consider increasing storage capacity

3. **Data Corruption**:
   - Stop backup service
   - Run integrity checks
   - Restore from last known good backup
   - Investigate root cause

## Support

For issues or questions:

1. Check this documentation
2. Review logs and monitoring dashboards
3. Contact the DevOps team
4. Escalate to engineering leadership for critical issues

---

**Version**: 1.0.0
**Last Updated**: 2025-01-02
**Maintained By**: TwisterLab Operations Team
