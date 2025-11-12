#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Configure TwisterLab monitoring alerts and notifications
.DESCRIPTION
    Sets up Prometheus alerting rules and Alertmanager configuration
    for comprehensive system monitoring and notifications
.NOTES
    Run as Administrator
    Requires: Docker, Docker Compose
#>

param(
    [string]$SmtpServer = "smtp.twisterlab.local",
    [string]$SmtpPort = "587",
    [string]$AlertEmail = "admin@twisterlab.local",
    [string]$SmtpUsername = "alerts@twisterlab.local",
    [string]$SmtpPassword = "",
    [switch]$EnableSlack = $false,
    [string]$SlackWebhook = ""
)

function Write-MonitorLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path "C:\TwisterLab\monitoring_setup.log" -Value $logMessage
}

function Test-MonitoringPrerequisites {
    Write-MonitorLog "Checking monitoring prerequisites..."

    # Check if Docker is running
    try {
        $dockerStatus = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-MonitorLog "Docker is not running or accessible" "ERROR"
            return $false
        }
    }
    catch {
        Write-MonitorLog "Docker check failed: $($_.Exception.Message)" "ERROR"
        return $false
    }

    # Check if monitoring stack is running
    $services = docker ps --filter "label=com.docker.compose.project=twisterlab" --format "{{.Names}}"
    $monitoringServices = $services | Where-Object { $_ -match "prometheus|grafana|alertmanager" }

    if ($monitoringServices.Count -lt 3) {
        Write-MonitorLog "Monitoring stack not fully running. Found $($monitoringServices.Count) services, expected 3" "ERROR"
        Write-MonitorLog "Please start the monitoring stack first: docker-compose -f docker-compose.monitoring.yml up -d"
        return $false
    }

    Write-MonitorLog "Prerequisites check passed"
    return $true
}

function Update-AlertmanagerConfig {
    param([string]$ConfigPath)

    Write-MonitorLog "Updating Alertmanager configuration..."

    if (!(Test-Path $ConfigPath)) {
        Write-MonitorLog "Alertmanager config not found: $ConfigPath" "ERROR"
        return $false
    }

    try {
        $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json

        # Update SMTP settings
        $config.global.smtp_smarthost = "$SmtpServer`:$SmtpPort"
        $config.global.smtp_from = $AlertEmail
        $config.global.smtp_auth_username = $SmtpUsername
        if ($SmtpPassword) {
            $config.global.smtp_auth_password = $SmtpPassword
        }

        # Update email receivers
        foreach ($receiver in $config.receivers) {
            if ($receiver.name -eq "twisterlab-alerts") {
                $receiver.email_configs[0].to = $AlertEmail
            }
            elseif ($receiver.name -eq "twisterlab-critical") {
                $receiver.email_configs[0].to = $AlertEmail
            }
            elseif ($receiver.name -eq "twisterlab-backup") {
                $receiver.email_configs[0].to = $AlertEmail
            }
        }

        # Add Slack integration if enabled
        if ($EnableSlack -and $SlackWebhook) {
            Write-MonitorLog "Enabling Slack notifications..."

            foreach ($receiver in $config.receivers) {
                if ($receiver.name -eq "twisterlab-critical") {
                    if (!$receiver.slack_configs) {
                        $receiver | Add-Member -MemberType NoteProperty -Name "slack_configs" -Value @()
                    }
                    $receiver.slack_configs += @{
                        api_url = $SlackWebhook
                        channel = "#twisterlab-critical"
                        title = "🚨 CRITICAL: {{ .GroupLabels.alertname }}"
                        text = "{{ range .Alerts }}• {{ .Annotations.summary }}{{ end }}"
                    }
                }
            }
        }

        # Convert back to JSON and save
        $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigPath -Encoding UTF8

        Write-MonitorLog "Alertmanager configuration updated successfully"
        return $true
    }
    catch {
        Write-MonitorLog "Failed to update Alertmanager config: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Restart-MonitoringServices {
    Write-MonitorLog "Restarting monitoring services..."

    try {
        # Restart Alertmanager to pick up new config
        docker-compose -f docker-compose.monitoring.yml restart alertmanager

        # Reload Prometheus configuration
        $prometheusContainer = docker ps --filter "name=twisterlab_prometheus" --format "{{.Names}}"
        if ($prometheusContainer) {
            docker exec $prometheusContainer kill -HUP 1
            Write-MonitorLog "Prometheus configuration reloaded"
        }

        Write-MonitorLog "Monitoring services restarted successfully"
        return $true
    }
    catch {
        Write-MonitorLog "Failed to restart monitoring services: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-AlertingRules {
    Write-MonitorLog "Testing alerting rules..."

    try {
        # Check if Prometheus can load the rules
        $prometheusContainer = docker ps --filter "name=twisterlab_prometheus" --format "{{.Names}}"
        if ($prometheusContainer) {
            $ruleCheck = docker exec $prometheusContainer promtool check rules /etc/prometheus/alert_rules.yml 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-MonitorLog "Alerting rules validation passed"
                return $true
            } else {
                Write-MonitorLog "Alerting rules validation failed: $ruleCheck" "ERROR"
                return $false
            }
        } else {
            Write-MonitorLog "Prometheus container not found" "ERROR"
            return $false
        }
    }
    catch {
        Write-MonitorLog "Alerting rules test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-EmailConfiguration {
    Write-MonitorLog "Testing email configuration..."

    if (!$SmtpPassword) {
        Write-MonitorLog "SMTP password not provided, skipping email test"
        return $true
    }

    try {
        # Send test email
        $testSubject = "TwisterLab Monitoring Setup Test"
        $testBody = @"
TwisterLab Monitoring Configuration Test

This is a test email to verify SMTP configuration for TwisterLab alerts.

Configuration Details:
- SMTP Server: $SmtpServer
- SMTP Port: $SmtpPort
- From: $AlertEmail
- To: $AlertEmail

If you received this email, the monitoring alerts are properly configured.

Timestamp: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

        Send-MailMessage -From $AlertEmail -To $AlertEmail -Subject $testSubject -Body $testBody -SmtpServer $SmtpServer -Port $SmtpPort -Credential (New-Object System.Management.Automation.PSCredential ($SmtpUsername, (ConvertTo-SecureString $SmtpPassword -AsPlainText -Force)))

        Write-MonitorLog "Test email sent successfully"
        return $true
    }
    catch {
        Write-MonitorLog "Email test failed: $($_.Exception.Message)" "ERROR"
        Write-MonitorLog "Please verify SMTP settings and credentials" "WARNING"
        return $false
    }
}

function Show-MonitoringStatus {
    Write-MonitorLog "=== Monitoring Configuration Status ==="

    # Check service status
    $services = docker ps --filter "label=com.docker.compose.project=twisterlab" --format "table {{.Names}}\t{{.Status}}"
    Write-MonitorLog "Docker Services:"
    $services | ForEach-Object { Write-MonitorLog "  $_" }

    # Check alert rules
    $ruleCount = (Get-Content "C:\TwisterLab\monitoring\alert_rules.yml" | Where-Object { $_ -match "- alert:" }).Count
    Write-MonitorLog "Alert Rules: $ruleCount configured"

    # Check alertmanager config
    if (Test-Path "C:\TwisterLab\monitoring\alertmanager.yml") {
        Write-MonitorLog "Alertmanager: Configured"
    } else {
        Write-MonitorLog "Alertmanager: Not configured" "WARNING"
    }

    Write-MonitorLog "Grafana URL: http://localhost:3001"
    Write-MonitorLog "Prometheus URL: http://localhost:9090"
    Write-MonitorLog "Alertmanager URL: http://localhost:9093"
}

# Main configuration process
try {
    Write-MonitorLog "=== Starting TwisterLab Monitoring Configuration ==="

    # Check prerequisites
    if (!(Test-MonitoringPrerequisites)) {
        Write-MonitorLog "Prerequisites not met. Exiting." "ERROR"
        exit 1
    }

    # Update Alertmanager configuration
    $alertmanagerConfig = "C:\TwisterLab\monitoring\alertmanager.yml"
    if (!(Update-AlertmanagerConfig $alertmanagerConfig)) {
        Write-MonitorLog "Alertmanager configuration failed. Exiting." "ERROR"
        exit 1
    }

    # Test alerting rules
    if (!(Test-AlertingRules)) {
        Write-MonitorLog "Alerting rules validation failed. Please check the rules file." "ERROR"
        exit 1
    }

    # Restart services
    Restart-MonitoringServices

    # Test email configuration
    Test-EmailConfiguration

    # Show final status
    Show-MonitoringStatus

    Write-MonitorLog "=== Monitoring Configuration Completed ==="
    Write-Host "✅ TwisterLab monitoring and alerting configured successfully!" -ForegroundColor Green
    Write-Host "📊 Grafana: http://localhost:3001 (admin/admin)" -ForegroundColor Cyan
    Write-Host "📈 Prometheus: http://localhost:9090" -ForegroundColor Cyan
    Write-Host "🚨 Alertmanager: http://localhost:9093" -ForegroundColor Cyan
    Write-Host "📧 Alerts will be sent to: $AlertEmail" -ForegroundColor Cyan

    if ($EnableSlack) {
        Write-Host "💬 Slack notifications: Enabled" -ForegroundColor Cyan
    }

    exit 0
}
catch {
    Write-MonitorLog "Monitoring configuration failed: $($_.Exception.Message)" "ERROR"
    exit 1
}
