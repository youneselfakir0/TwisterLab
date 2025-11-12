"""
Backup Configuration for TwisterLab Production
Defines backup schedules, retention policies, and storage locations
"""

from typing import Any, Dict, List

# Backup Configuration
BACKUP_CONFIG = {
    "database": {
        "schedule": "daily",
        "time": "02:00",
        "retention_days": 30,
        "compression": True,
        "encryption": True,
        "storage_locations": ["local", "remote"],
        "description": "PostgreSQL database backup",
    },
    "config": {
        "schedule": "daily",
        "time": "03:00",
        "retention_days": 90,
        "compression": True,
        "encryption": True,
        "storage_locations": ["local", "remote"],
        "description": "Configuration files and secrets",
    },
    "logs": {
        "schedule": "hourly",
        "retention_days": 7,
        "compression": True,
        "encryption": False,
        "storage_locations": ["local"],
        "description": "Application and system logs",
    },
    "full_system": {
        "schedule": "weekly",
        "time": "04:00",
        "day": "sunday",
        "retention_days": 365,
        "compression": True,
        "encryption": True,
        "storage_locations": ["local", "remote"],
        "description": "Complete system backup",
    },
}

# Storage Configuration
STORAGE_CONFIG = {
    "local": {
        "type": "filesystem",
        "path": "/opt/twisterlab/backups",
        "max_size_gb": 100,
        "cleanup_threshold": 0.8,  # Clean up when 80% full
    },
    "remote": {
        "type": "azure_blob",
        "container": "twisterlab-backups",
        "account_name": "twisterlabstorage",
        "retention_policy": "GRS",  # Geo-redundant storage
        "encryption": True,
    },
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "alert_on_failure": True,
    "alert_channels": ["email", "slack"],
    "success_notifications": True,
    "notification_channels": ["email"],
    "dashboard_update": True,
    "metrics_retention_days": 90,
}

# Security Configuration
SECURITY_CONFIG = {
    "encryption_key_rotation_days": 90,
    "access_audit_enabled": True,
    "integrity_checks_enabled": True,
    "backup_validation_enabled": True,
}


def get_backup_config(backup_type: str) -> Dict[str, Any]:
    """Get configuration for a specific backup type."""
    return BACKUP_CONFIG.get(backup_type, {})


def get_storage_config(storage_type: str) -> Dict[str, Any]:
    """Get configuration for a specific storage type."""
    return STORAGE_CONFIG.get(storage_type, {})


def get_all_backup_types() -> List[str]:
    """Get all configured backup types."""
    return list(BACKUP_CONFIG.keys())


def get_retention_policy(backup_type: str) -> int:
    """Get retention days for a backup type."""
    config = get_backup_config(backup_type)
    return config.get("retention_days", 30)


def should_compress(backup_type: str) -> bool:
    """Check if backup type should be compressed."""
    config = get_backup_config(backup_type)
    return config.get("compression", True)


def should_encrypt(backup_type: str) -> bool:
    """Check if backup type should be encrypted."""
    config = get_backup_config(backup_type)
    return config.get("encryption", True)


def get_storage_locations(backup_type: str) -> List[str]:
    """Get storage locations for a backup type."""
    config = get_backup_config(backup_type)
    return config.get("storage_locations", ["local"])


def validate_config() -> List[str]:
    """Validate backup configuration."""
    errors = []

    # Check backup types
    required_fields = ["schedule", "retention_days", "storage_locations"]
    for backup_type, config in BACKUP_CONFIG.items():
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing {field} for backup type {backup_type}")

    # Check storage locations
    for storage_type, config in STORAGE_CONFIG.items():
        if "type" not in config:
            errors.append(f"Missing type for storage {storage_type}")

    # Check retention policies
    for backup_type, config in BACKUP_CONFIG.items():
        retention = config.get("retention_days", 0)
        if retention <= 0:
            errors.append(f"Invalid retention days for {backup_type}: {retention}")

    return errors


# Export configuration for external use
__all__ = [
    "BACKUP_CONFIG",
    "STORAGE_CONFIG",
    "MONITORING_CONFIG",
    "SECURITY_CONFIG",
    "get_backup_config",
    "get_storage_config",
    "get_all_backup_types",
    "get_retention_policy",
    "should_compress",
    "should_encrypt",
    "get_storage_locations",
    "validate_config",
]
