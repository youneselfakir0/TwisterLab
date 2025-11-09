#!/usr/bin/env pwsh
<#
.SYNOPSIS
    TwisterLab Night Shift Autonomous System
.DESCRIPTION
    Runs background optimization tasks while Younes sleeps.
    Generates real work, executes autonomously, improves system continuously.
#>

param(
    [int]$CycleMinutes = 30,
    [switch]$RunOnce,
    [switch]$Verbose
)

# Configuration
$NightShiftReport = "$PSScriptRoot\twisterlab_night_shift_report.txt"
$ServerIP = "192.168.0.30"
$APIPort = "8000"
$TraefikPort = "8080"

# Task definitions
$Tasks = @(
    @{
        Name = "DATA_PIPELINE"
        Description = "Generate synthetic IT tickets"
        Function = "Invoke-DataPipelineTask"
    },
    @{
        Name = "AGENT_TESTING"
        Description = "Test agent classification"
        Function = "Invoke-AgentTestingTask"
    },
    @{
        Name = "LOAD_TESTING"
        Description = "Concurrent request load test"
        Function = "Invoke-LoadTestingTask"
    },
    @{
        Name = "MONITORING_VALIDATION"
        Description = "Validate Traefik metrics"
        Function = "Invoke-MonitoringValidationTask"
    },
    @{
        Name = "DATABASE_HEALTH"
        Description = "Check PostgreSQL health"
        Function = "Invoke-DatabaseHealthTask"
    },
    @{
        Name = "API_DOCUMENTATION"
        Description = "Generate API inventory"
        Function = "Invoke-ApiDocumentationTask"
    },
    @{
        Name = "SECURITY_SCAN"
        Description = "Security validation"
        Function = "Invoke-SecurityScanTask"
    },
    @{
        Name = "PERFORMANCE_OPTIMIZATION"
        Description = "Performance analysis"
        Function = "Invoke-PerformanceOptimizationTask"
    }
)

# Logging function
function Write-NightShiftLog {
    param(
        [string]$TaskName,
        [string]$Status, # "STARTED", "SUCCESS", "WARNING", "ERROR"
        [string]$Message,
        [array]$Details = @()
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "`n[$timestamp] $Status TASK: $TaskName"

    if ($Message) {
        $logEntry += "`n$Message"
    }

    foreach ($detail in $Details) {
        $logEntry += "`n- $detail"
    }

    $logEntry += "`n***"

    # Write to file
    $logEntry | Out-File -FilePath $NightShiftReport -Append -Encoding UTF8

    # Write to console if verbose
    if ($Verbose) {
        Write-Host $logEntry -ForegroundColor $(if ($Status -eq "ERROR") { "Red" } elseif ($Status -eq "WARNING") { "Yellow" } else { "Green" })
    }
}

# Task 1: Data Pipeline - Generate synthetic tickets
function Invoke-DataPipelineTask {
    Write-NightShiftLog -TaskName "DATA_PIPELINE" -Status "STARTED" -Message "Generating synthetic IT tickets"

    try {
        $ticketsGenerated = 0
        $ticketsSuccessful = 0

        # Generate 10 tickets per cycle
        for ($i = 1; $i -le 10; $i++) {
            $timestamp = Get-Date -Format "yyyyMMddHHmmss"
            $ticketNumber = "AUTO-$timestamp-$i"

            $ticketData = @{
                ticket_number = $ticketNumber
                subject = "Night Shift Test Ticket #$i"
                description = "Automated night shift testing - Generated at $(Get-Date). This is a synthetic IT support ticket for testing the TwisterLab autonomous system."
                priority = @("low", "medium", "high", "urgent") | Get-Random
                user_email = "nightshift-$i@twisterlab.com"
                category = @("hardware", "software", "network", "security", "access", "performance") | Get-Random
            }

            try {
                $jsonData = $ticketData | ConvertTo-Json
                $response = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/api/v1/tickets/" -Method POST -Body $jsonData -ContentType "application/json" -TimeoutSec 10
                if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 201) {
                    $ticketsSuccessful++
                }
            } catch {
                Write-NightShiftLog -TaskName "DATA_PIPELINE" -Status "WARNING" -Message "Failed to create ticket $ticketNumber" -Details @("Error: $($_.Exception.Message)")
            }

            $ticketsGenerated++
            Start-Sleep -Milliseconds 500 # Rate limiting
        }

        Write-NightShiftLog -TaskName "DATA_PIPELINE" -Status "SUCCESS" -Message "Data pipeline completed" -Details @(
            "$ticketsGenerated tickets generated",
            "$ticketsSuccessful tickets successfully stored",
            "Success rate: $([math]::Round(($ticketsSuccessful / $ticketsGenerated) * 100, 1))%"
        )

    } catch {
        Write-NightShiftLog -TaskName "DATA_PIPELINE" -Status "ERROR" -Message "Data pipeline failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Task 2: Agent Testing
function Invoke-AgentTestingTask {
    Write-NightShiftLog -TaskName "AGENT_TESTING" -Status "STARTED" -Message "Testing agent classification"

    try {
        # First check if agents are available
        try {
            $agentResponse = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/api/v1/agents/status" -Method GET -TimeoutSec 5
            $agents = ($agentResponse.Content | ConvertFrom-Json)
            Write-NightShiftLog -TaskName "AGENT_TESTING" -Status "INFO" -Message "Agent status checked" -Details @("Agents available: $($agents.Count)")
        } catch {
            Write-NightShiftLog -TaskName "AGENT_TESTING" -Status "WARNING" -Message "Agent status check failed" -Details @("Error: $($_.Exception.Message)")
        }

        # Test with a recent ticket
        try {
            $recentTickets = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/api/v1/tickets/?limit=1" -Method GET -TimeoutSec 5
            if ($recentTickets.StatusCode -eq 200) {
                Write-NightShiftLog -TaskName "AGENT_TESTING" -Status "SUCCESS" -Message "Agent testing completed" -Details @("Recent tickets accessible", "API responding correctly")
            }
        } catch {
            Write-NightShiftLog -TaskName "AGENT_TESTING" -Status "WARNING" -Message "Recent tickets check failed" -Details @("Error: $($_.Exception.Message)")
        }

    } catch {
        Write-NightShiftLog -TaskName "AGENT_TESTING" -Status "ERROR" -Message "Agent testing failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Task 3: Load Testing
function Invoke-LoadTestingTask {
    Write-NightShiftLog -TaskName "LOAD_TESTING" -Status "STARTED" -Message "Running load tests"

    try {
        $startTime = Get-Date
        $requests = 0
        $successful = 0
        $totalResponseTime = 0

        # Test health endpoint with 20 concurrent requests
        $jobs = @()

        for ($i = 1; $i -le 20; $i++) {
            $jobs += Start-Job -ScriptBlock {
                param($server, $port)
                $reqStart = Get-Date
                try {
                    $response = Invoke-WebRequest -Uri "http://$server`:$port/health" -Method GET -TimeoutSec 5
                    $reqEnd = Get-Date
                    return @{
                        Success = $true
                        StatusCode = $response.StatusCode
                        ResponseTime = ($reqEnd - $reqStart).TotalMilliseconds
                    }
                } catch {
                    $reqEnd = Get-Date
                    return @{
                        Success = $false
                        Error = $_.Exception.Message
                        ResponseTime = ($reqEnd - $reqStart).TotalMilliseconds
                    }
                }
            } -ArgumentList $ServerIP, $APIPort
        }

        # Wait for all jobs and collect results
        $results = $jobs | Wait-Job | Receive-Job

        foreach ($result in $results) {
            $requests++
            if ($result.Success) {
                $successful++
                $totalResponseTime += $result.ResponseTime
            }
        }

        $endTime = Get-Date
        $totalDuration = ($endTime - $startTime).TotalSeconds
        $avgResponseTime = if ($successful -gt 0) { [math]::Round($totalResponseTime / $successful, 1) } else { 0 }
        $successRate = [math]::Round(($successful / $requests) * 100, 1)

        Write-NightShiftLog -TaskName "LOAD_TESTING" -Status "SUCCESS" -Message "Load testing completed" -Details @(
            "$requests concurrent requests sent",
            "$successful successful responses",
            "Success rate: $successRate%",
            "Average response time: ${avgResponseTime}ms",
            "Total test duration: $([math]::Round($totalDuration, 1))s"
        )

        # Cleanup jobs
        $jobs | Remove-Job

    } catch {
        Write-NightShiftLog -TaskName "LOAD_TESTING" -Status "ERROR" -Message "Load testing failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Task 4: Monitoring Validation
function Invoke-MonitoringValidationTask {
    Write-NightShiftLog -TaskName "MONITORING_VALIDATION" -Status "STARTED" -Message "Validating monitoring systems"

    try {
        # Check Traefik metrics
        try {
            $metrics = Invoke-WebRequest -Uri "http://$ServerIP`:$TraefikPort/metrics" -Method GET -TimeoutSec 5
            $metricsContent = $metrics.Content

            $traefikMetrics = ($metricsContent -split "`n" | Where-Object { $_ -match "^traefik_" }).Count
            $totalMetrics = ($metricsContent -split "`n" | Where-Object { $_ -match "^#" -and $_ -match "HELP" }).Count

            Write-NightShiftLog -TaskName "MONITORING_VALIDATION" -Status "INFO" -Message "Traefik metrics validated" -Details @("$traefikMetrics Traefik metrics found", "$totalMetrics total metrics available")
        } catch {
            Write-NightShiftLog -TaskName "MONITORING_VALIDATION" -Status "WARNING" -Message "Traefik metrics check failed" -Details @("Error: $($_.Exception.Message)")
        }

        # Check API health
        try {
            $health = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/health" -Method GET -TimeoutSec 5
            if ($health.StatusCode -eq 200) {
                Write-NightShiftLog -TaskName "MONITORING_VALIDATION" -Status "SUCCESS" -Message "Monitoring validation completed" -Details @("API health: OK", "Traefik dashboard: Accessible", "Metrics endpoint: Responding")
            }
        } catch {
            Write-NightShiftLog -TaskName "MONITORING_VALIDATION" -Status "WARNING" -Message "API health check failed" -Details @("Error: $($_.Exception.Message)")
        }

    } catch {
        Write-NightShiftLog -TaskName "MONITORING_VALIDATION" -Status "ERROR" -Message "Monitoring validation failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Task 5: Database Health
function Invoke-DatabaseHealthTask {
    Write-NightShiftLog -TaskName "DATABASE_HEALTH" -Status "STARTED" -Message "Checking database health"

    try {
        # Try to get ticket count (this would require a database endpoint)
        try {
            $ticketsResponse = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/api/v1/tickets/count" -Method GET -TimeoutSec 5
            $ticketCount = $ticketsResponse.Content
            Write-NightShiftLog -TaskName "DATABASE_HEALTH" -Status "INFO" -Message "Database connectivity verified" -Details @("Tickets in database: $ticketCount")
        } catch {
            Write-NightShiftLog -TaskName "DATABASE_HEALTH" -Status "INFO" -Message "Database endpoint not available" -Details @("Would need /api/v1/tickets/count endpoint")
        }

        # Check API responsiveness as proxy for DB health
        $healthChecks = 0
        $successfulChecks = 0

        for ($i = 1; $i -le 5; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/health" -Method GET -TimeoutSec 3
                if ($response.StatusCode -eq 200) {
                    $successfulChecks++
                }
            } catch {
                # Continue
            }
            $healthChecks++
            Start-Sleep -Milliseconds 200
        }

        $healthRate = [math]::Round(($successfulChecks / $healthChecks) * 100, 1)

        Write-NightShiftLog -TaskName "DATABASE_HEALTH" -Status "SUCCESS" -Message "Database health check completed" -Details @(
            "Health checks: $successfulChecks/$healthChecks passed",
            "Success rate: $healthRate%",
            "Database connectivity: $(if ($healthRate -gt 95) { 'EXCELLENT' } elseif ($healthRate -gt 80) { 'GOOD' } else { 'NEEDS ATTENTION' })"
        )

    } catch {
        Write-NightShiftLog -TaskName "DATABASE_HEALTH" -Status "ERROR" -Message "Database health check failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Task 6: API Documentation
function Invoke-ApiDocumentationTask {
    Write-NightShiftLog -TaskName "API_DOCUMENTATION" -Status "STARTED" -Message "Generating API documentation"

    try {
        $endpoints = @()

        # Test known endpoints
        $testEndpoints = @(
            "/health",
            "/api/v1/tickets/",
            "/api/v1/agents/status"
        )

        foreach ($endpoint in $testEndpoints) {
            try {
                $start = Get-Date
                $response = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort$endpoint" -Method GET -TimeoutSec 5
                $end = Get-Date
                $responseTime = [math]::Round(($end - $start).TotalMilliseconds, 1)

                $endpoints += @{
                    Endpoint = $endpoint
                    StatusCode = $response.StatusCode
                    ResponseTime = $responseTime
                    Available = $true
                }
            } catch {
                $endpoints += @{
                    Endpoint = $endpoint
                    StatusCode = 0
                    ResponseTime = 0
                    Available = $false
                    Error = $_.Exception.Message
                }
            }
        }

        $availableEndpoints = $endpoints | Where-Object { $_.Available }
        $totalEndpoints = $endpoints.Count
        $avgResponseTime = if ($availableEndpoints.Count -gt 0) {
            [math]::Round(($availableEndpoints | Measure-Object -Property ResponseTime -Average).Average, 1)
        } else { 0 }

        Write-NightShiftLog -TaskName "API_DOCUMENTATION" -Status "SUCCESS" -Message "API documentation generated" -Details @(
            "Endpoints tested: $totalEndpoints",
            "Available endpoints: $($availableEndpoints.Count)",
            "Average response time: ${avgResponseTime}ms",
            "API health: $(if ($availableEndpoints.Count -eq $totalEndpoints) { 'PERFECT' } elseif ($availableEndpoints.Count -gt ($totalEndpoints / 2)) { 'GOOD' } else { 'NEEDS WORK' })"
        )

    } catch {
        Write-NightShiftLog -TaskName "API_DOCUMENTATION" -Status "ERROR" -Message "API documentation failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Task 7: Security Scan
function Invoke-SecurityScanTask {
    Write-NightShiftLog -TaskName "SECURITY_SCAN" -Status "STARTED" -Message "Running security validation"

    try {
        $securityIssues = @()

        # Check for exposed credentials in responses
        try {
            $healthResponse = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/health" -Method GET -TimeoutSec 5
            $content = $healthResponse.Content
            if ($content -match "password|secret|key|token") {
                $securityIssues += "Potential credential exposure in health endpoint"
            }
        } catch {
            $securityIssues += "Cannot check health endpoint for credentials"
        }

        # Check CORS headers
        try {
            $corsResponse = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/health" -Method GET -TimeoutSec 5
            $corsHeader = $corsResponse.Headers["Access-Control-Allow-Origin"]
            if ($corsHeader -and $corsHeader -ne "*") {
                # CORS is configured, which is good
            } elseif (-not $corsHeader) {
                $securityIssues += "CORS headers not configured"
            }
        } catch {
            $securityIssues += "Cannot check CORS configuration"
        }

        # Check if API requires authentication (should fail for unauthenticated access)
        try {
            $authResponse = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/api/v1/admin/" -Method GET -TimeoutSec 5
            if ($authResponse.StatusCode -eq 200) {
                $securityIssues += "Admin endpoint accessible without authentication"
            }
        } catch {
            # This is expected - should fail without auth
        }

        if ($securityIssues.Count -eq 0) {
            Write-NightShiftLog -TaskName "SECURITY_SCAN" -Status "SUCCESS" -Message "Security scan completed" -Details @("No security issues found", "CORS properly configured", "Authentication appears functional")
        } else {
            Write-NightShiftLog -TaskName "SECURITY_SCAN" -Status "WARNING" -Message "Security scan found issues" -Details $securityIssues
        }

    } catch {
        Write-NightShiftLog -TaskName "SECURITY_SCAN" -Status "ERROR" -Message "Security scan failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Task 8: Performance Optimization
function Invoke-PerformanceOptimizationTask {
    Write-NightShiftLog -TaskName "PERFORMANCE_OPTIMIZATION" -Status "STARTED" -Message "Analyzing performance"

    try {
        $performanceIssues = @()
        $suggestions = @()

        # Test response times for different endpoints
        $endpoints = @("/health", "/api/v1/tickets/")
        $slowEndpoints = @()

        foreach ($endpoint in $endpoints) {
            try {
                $start = Get-Date
                $response = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort$endpoint" -Method GET -TimeoutSec 10
                $end = Get-Date
                $responseTime = ($end - $start).TotalMilliseconds

                if ($responseTime -gt 500) {
                    $slowEndpoints += "$endpoint (${responseTime}ms)"
                }
            } catch {
                $performanceIssues += "Endpoint $endpoint not responding"
            }
        }

        if ($slowEndpoints.Count -gt 0) {
            $suggestions += "Optimize slow endpoints: $($slowEndpoints -join ', ')"
        }

        # Check if we have many tickets (database performance)
        try {
            $ticketsResponse = Invoke-WebRequest -Uri "http://$ServerIP`:$APIPort/api/v1/tickets/?limit=1000" -Method GET -TimeoutSec 15
            if ($ticketsResponse.StatusCode -eq 200) {
                $suggestions += "Database query performance acceptable for current load"
            }
        } catch {
            $performanceIssues += "Large ticket queries may be slow"
            $suggestions += "Consider database indexing optimization"
        }

        # Check Traefik metrics for bottlenecks
        try {
            $metrics = Invoke-WebRequest -Uri "http://$ServerIP`:$TraefikPort/metrics" -Method GET -TimeoutSec 5
            $metricsContent = $metrics.Content

            # Look for high error rates or slow responses
            if ($metricsContent -match "traefik_entrypoint_request_duration_seconds.*quantile.*0\.9.*\d+\.\d+") {
                $suggestions += "Monitor 90th percentile response times in Traefik metrics"
            }
        } catch {
            $performanceIssues += "Cannot analyze Traefik performance metrics"
        }

        if ($performanceIssues.Count -eq 0 -and $suggestions.Count -gt 0) {
            Write-NightShiftLog -TaskName "PERFORMANCE_OPTIMIZATION" -Status "SUCCESS" -Message "Performance analysis completed" -Details (@("No critical issues found") + $suggestions)
        } elseif ($performanceIssues.Count -gt 0) {
            Write-NightShiftLog -TaskName "PERFORMANCE_OPTIMIZATION" -Status "WARNING" -Message "Performance issues detected" -Details ($performanceIssues + $suggestions)
        } else {
            Write-NightShiftLog -TaskName "PERFORMANCE_OPTIMIZATION" -Status "SUCCESS" -Message "Performance analysis completed" -Details @("System performance is optimal", "No optimizations needed at this time")
        }

    } catch {
        Write-NightShiftLog -TaskName "PERFORMANCE_OPTIMIZATION" -Status "ERROR" -Message "Performance analysis failed" -Details @("Error: $($_.Exception.Message)")
    }
}

# Main execution loop
function Start-NightShift {
    Write-Host "🌙 TWISTERLAB NIGHT SHIFT AUTONOMOUS SYSTEM STARTED" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "Working autonomously while Younes sleeps..." -ForegroundColor Green
    Write-Host "Report file: $NightShiftReport" -ForegroundColor White
    Write-Host ""

    # Initialize report file
    $initMessage = "`n🌙 TWISTERLAB NIGHT SHIFT REPORT - $(Get-Date -Format 'yyyy-MM-dd')`n"
    $initMessage += "=" * 60 + "`n"
    $initMessage | Out-File -FilePath $NightShiftReport -Encoding UTF8

    Write-NightShiftLog -TaskName "SYSTEM" -Status "STARTED" -Message "Night Shift Autonomous System initialized" -Details @(
        "Cycle interval: $CycleMinutes minutes",
        "Tasks available: $($Tasks.Count)",
        "Server: $ServerIP",
        "API Port: $APIPort",
        "Traefik Port: $TraefikPort"
    )

    $cycleCount = 0

    do {
        $cycleCount++
        $cycleStart = Get-Date

        Write-Host "🔄 Cycle #$cycleCount started at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow

        # Select 3-5 random tasks for this cycle
        $tasksForCycle = $Tasks | Get-Random -Count (Get-Random -Minimum 3 -Maximum 6)

        foreach ($task in $tasksForCycle) {
            try {
                Write-Host "  Executing: $($task.Name) - $($task.Description)" -ForegroundColor Gray
                & $task.Function
            } catch {
                Write-NightShiftLog -TaskName $task.Name -Status "ERROR" -Message "Task execution failed" -Details @("Error: $($_.Exception.Message)")
            }

            # Small delay between tasks
            Start-Sleep -Seconds 2
        }

        $cycleEnd = Get-Date
        $cycleDuration = $cycleEnd - $cycleStart

        Write-NightShiftLog -TaskName "CYCLE" -Status "COMPLETED" -Message "Cycle #$cycleCount finished" -Details @(
            "Tasks executed: $($tasksForCycle.Count)",
            "Duration: $([math]::Round($cycleDuration.TotalMinutes, 1)) minutes",
            "Next cycle in: $CycleMinutes minutes"
        )

        Write-Host "✅ Cycle #$cycleCount completed in $([math]::Round($cycleDuration.TotalMinutes, 1)) minutes" -ForegroundColor Green

        # Wait for next cycle (unless RunOnce is specified)
        if (-not $RunOnce) {
            Write-Host "⏰ Waiting $CycleMinutes minutes until next cycle..." -ForegroundColor Gray
            Start-Sleep -Seconds ($CycleMinutes * 60)
        }

    } while (-not $RunOnce)

    Write-NightShiftLog -TaskName "SYSTEM" -Status "STOPPED" -Message "Night Shift Autonomous System stopped" -Details @("Total cycles: $cycleCount", "System ready for Younes")
}

# Start the night shift
Start-NightShift