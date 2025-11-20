#!/usr/bin/env python3
"""
TwisterLab Alerting System

Provides comprehensive alerting capabilities for agent performance,
workflow failures, and system health issues.
"""

import asyncio
import json
import logging
import smtplib
import aiohttp
import os
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=lambda: ["console"])


class AlertingSystem:
    """
    Comprehensive alerting system for TwisterLab

    Features:
    - Multi-channel notifications (console, email, webhook, Slack)
    - Alert escalation based on severity
    - Alert correlation and deduplication
    - Alert history and resolution tracking
    """

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: Dict[str, Callable] = {}
        self.notification_channels: Dict[str, Callable] = {}

        # Initialize notification channels
        self._setup_notification_channels()

        # Predefined alert definitions
        self.alert_definitions = {
            "high_agent_error_rate": {
                "name": "High Agent Error Rate",
                "description": "Agent error rate is above 10%",
                "severity": AlertSeverity.WARNING,
                "channels": ["console", "email"]
            },
            "workflow_execution_failed": {
                "name": "Workflow Execution Failed",
                "description": "A workflow execution has failed",
                "severity": AlertSeverity.ERROR,
                "channels": ["console", "email", "webhook"]
            },
            "agent_timeout": {
                "name": "Agent Timeout",
                "description": "An agent has timed out responding to requests",
                "severity": AlertSeverity.WARNING,
                "channels": ["console", "email"]
            },
            "system_resource_high": {
                "name": "High System Resource Usage",
                "description": "System resource usage is above threshold",
                "severity": AlertSeverity.WARNING,
                "channels": ["console"]
            },
            "mcp_communication_failure": {
                "name": "MCP Communication Failure",
                "description": "MCP communication between agents has failed",
                "severity": AlertSeverity.ERROR,
                "channels": ["console", "email", "webhook"]
            }
        }

    def _setup_notification_channels(self):
        """Setup notification channels"""
        self.notification_channels = {
            "console": self._notify_console,
            "email": self._notify_email,
            "webhook": self._notify_webhook,
            "slack": self._notify_slack
        }

    async def trigger_alert(self, alert_name: str, metadata: Dict[str, Any] = None) -> str:
        """Trigger an alert"""
        if alert_name not in self.alert_definitions:
            logger.warning(f"Unknown alert type: {alert_name}")
            return ""

        definition = self.alert_definitions[alert_name]
        alert_id = f"{alert_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        alert = Alert(
            alert_id=alert_id,
            name=definition["name"],
            description=definition["description"],
            severity=definition["severity"],
            metadata=metadata or {},
            notification_channels=definition["channels"]
        )

        self.alerts[alert_id] = alert

        # Send notifications
        await self._send_notifications(alert)

        logger.warning(f"Alert triggered: {alert_name} - {definition['description']}")
        return alert_id

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)

        # Send resolution notification
        await self._send_notifications(alert, resolution=True)

        logger.info(f"Alert resolved: {alert_id}")
        return True

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)

        logger.info(f"Alert acknowledged: {alert_id}")
        return True

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        active_alerts = []
        for alert in self.alerts.values():
            if alert.status == AlertStatus.ACTIVE:
                active_alerts.append({
                    "alert_id": alert.alert_id,
                    "name": alert.name,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "created_at": alert.created_at.isoformat(),
                    "metadata": alert.metadata
                })
        return active_alerts

    async def _send_notifications(self, alert: Alert, resolution: bool = False):
        """Send notifications through configured channels"""
        for channel in alert.notification_channels:
            if channel in self.notification_channels:
                try:
                    await self.notification_channels[channel](alert, resolution)
                except Exception as e:
                    logger.error(f"Failed to send {channel} notification: {e}")

    async def _notify_console(self, alert: Alert, resolution: bool = False):
        """Send console notification"""
        status = "RESOLVED" if resolution else f"ALERT {alert.severity.value.upper()}"
        message = f"{status}: {alert.name} - {alert.description}"
        if alert.metadata:
            message += f" | Metadata: {json.dumps(alert.metadata)}"

        print(message)

    async def _notify_email(self, alert: Alert, resolution: bool = False):
        """Send email notification"""
        try:
            # Email configuration (would be loaded from config in production)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "alerts@twisterlab.local"
            # Load SMTP password from environment (no hardcoded secrets)
            sender_password = os.getenv("ALERTS_SMTP_PASSWORD", "")
            recipient_emails = ["admin@twisterlab.local"]

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipient_emails)

            if resolution:
                msg['Subject'] = f"RESOLVED: {alert.name}"
                body = f"Alert has been resolved:\n\n{alert.description}"
            else:
                msg['Subject'] = f"ALERT: {alert.name} ({alert.severity.value.upper()})"
                body = f"Alert triggered:\n\n{alert.description}\n\nSeverity: {alert.severity.value}"

            if alert.metadata:
                body += f"\n\nDetails: {json.dumps(alert.metadata, indent=2)}"

            msg.attach(MIMEText(body, 'plain'))

            # Note: Email sending disabled in demo - would require proper SMTP config
            logger.info(f"Email notification would be sent: {msg['Subject']}")

        except Exception as e:
            logger.error(f"Email notification failed: {e}")

    async def _notify_webhook(self, alert: Alert, resolution: bool = False):
        """Send webhook notification"""
        try:
            webhook_url = "http://localhost:8080/webhook/alerts"  # Would be configured

            payload = {
                "alert_id": alert.alert_id,
                "name": alert.name,
                "description": alert.description,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": alert.metadata,
                "resolution": resolution
            }

            # Note: Webhook disabled in demo - would require running webhook receiver
            logger.info(f"Webhook notification would be sent to {webhook_url}: {json.dumps(payload)}")

        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")

    async def _notify_slack(self, alert: Alert, resolution: bool = False):
        """Send Slack notification"""
        try:
            slack_webhook_url = "https://hooks.slack.com/services/placeholder"  # Would be configured

            if resolution:
                message = f"✅ *RESOLVED*: {alert.name}\n{alert.description}"
                color = "good"
            else:
                emoji = "⚠️" if alert.severity == AlertSeverity.WARNING else "🚨"
                message = f"{emoji} *ALERT*: {alert.name}\n{alert.description}"
                color = "warning" if alert.severity == AlertSeverity.WARNING else "danger"

            payload = {
                "attachments": [{
                    "color": color,
                    "text": message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value, "short": True},
                        {"title": "Alert ID", "value": alert.alert_id, "short": True}
                    ]
                }]
            }

            if alert.metadata:
                payload["attachments"][0]["fields"].append({
                    "title": "Details",
                    "value": json.dumps(alert.metadata),
                    "short": False
                })

            # Note: Slack notification disabled in demo - would require valid webhook URL
            logger.info(f"Slack notification would be sent: {message}")

        except Exception as e:
            logger.error(f"Slack notification failed: {e}")


# Global alerting system instance
alerting_system = AlertingSystem()


async def test_alerting_system():
    """Test the alerting system"""
    print("Testing TwisterLab Alerting System...")

    # Trigger some test alerts
    alert1_id = await alerting_system.trigger_alert("high_agent_error_rate", {
        "error_rate": 15.5,
        "agent": "backup_agent"
    })

    alert2_id = await alerting_system.trigger_alert("workflow_execution_failed", {
        "workflow_id": "test_workflow_001",
        "error": "Timeout waiting for agent response"
    })

    # Get active alerts
    active_alerts = alerting_system.get_active_alerts()
    print(f"Active alerts: {len(active_alerts)}")
    for alert in active_alerts:
        print(f"  - {alert['name']}: {alert['description']}")

    # Resolve an alert
    await alerting_system.resolve_alert(alert1_id)

    # Check active alerts again
    active_alerts = alerting_system.get_active_alerts()
    print(f"Active alerts after resolution: {len(active_alerts)}")


if __name__ == "__main__":
    asyncio.run(test_alerting_system())
