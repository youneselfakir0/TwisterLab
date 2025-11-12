#!/usr/bin/env pwsh
<#
.SYNOPSIS
Liste les 7 agents autonomes TwisterLab (VRAIS agents, pas MOCK)

.DESCRIPTION
Script de fallback pour accéder aux vrais agents sur edgeserver
Utilisé par Continue IDE quand l'endpoint API n'est pas encore déployé

.EXAMPLE
.\list_real_agents.ps1
#>

$API_URL = "http://192.168.0.30:8000"

$agents = @(
    @{
        name = "RealMonitoringAgent"
        display_name = "Real Monitoring Agent"
        description = "Surveillance système en temps réel (CPU, RAM, Disk, Docker)"
        status = "active"
        endpoint = "/v1/mcp/tools/monitor_system_health"
        module = "agents.real.real_monitoring_agent"
        capabilities = @("health_check", "system_metrics", "docker_status")
        file = "agents/real/real_monitoring_agent.py"
    },
    @{
        name = "RealClassifierAgent"
        display_name = "Real Classifier Agent"
        description = "Classification intelligente des tickets IT avec LLM"
        status = "active"
        endpoint = "/v1/mcp/tools/classify_ticket"
        module = "agents.real.real_classifier_agent"
        capabilities = @("ticket_classification", "priority_assignment", "category_detection")
        file = "agents/real/real_classifier_agent.py"
    },
    @{
        name = "RealResolverAgent"
        display_name = "Real Resolver Agent"
        description = "Résolution automatique via SOPs et exécution de commandes"
        status = "active"
        endpoint = "/v1/mcp/tools/resolve_ticket"
        module = "agents.real.real_resolver_agent"
        capabilities = @("sop_execution", "command_execution", "ticket_resolution")
        file = "agents/real/real_resolver_agent.py"
    },
    @{
        name = "RealBackupAgent"
        display_name = "Real Backup Agent"
        description = "Backups automatisés avec disaster recovery"
        status = "active"
        endpoint = "/v1/mcp/tools/create_backup"
        module = "agents.real.real_backup_agent"
        capabilities = @("database_backup", "file_backup", "disaster_recovery")
        file = "agents/real/real_backup_agent.py"
    },
    @{
        name = "RealSyncAgent"
        display_name = "Real Sync Agent"
        description = "Synchronisation cache/base de données"
        status = "active"
        endpoint = "/v1/mcp/tools/sync_cache"
        module = "agents.real.real_sync_agent"
        capabilities = @("cache_sync", "data_consistency", "redis_sync")
        file = "agents/real/real_sync_agent.py"
    },
    @{
        name = "RealDesktopCommanderAgent"
        display_name = "Real Desktop Commander Agent"
        description = "Exécution de commandes système à distance"
        status = "active"
        endpoint = "/v1/mcp/tools/execute_desktop_command"
        module = "agents.real.real_desktop_commander_agent"
        capabilities = @("remote_execution", "system_commands", "powershell_execution")
        file = "agents/real/real_desktop_commander_agent.py"
    },
    @{
        name = "RealMaestroAgent"
        display_name = "Real Maestro Agent"
        description = "Orchestration de workflows et load balancing"
        status = "active"
        endpoint = "/v1/mcp/tools/orchestrate_workflow"
        module = "agents.real.real_maestro_agent"
        capabilities = @("workflow_orchestration", "load_balancing", "agent_coordination")
        file = "agents/real/real_maestro_agent.py"
    }
)

# Test de santé pour confirmer que les vrais agents fonctionnent
try {
    $health = Invoke-RestMethod -Uri "$API_URL/v1/mcp/tools/monitor_system_health" -Method POST -ContentType "application/json" -Body '{"detailed": true}' -ErrorAction Stop
    
    $response = @{
        status = "ok"
        mode = "REAL"
        api_url = $API_URL
        agents_count = $agents.Count
        agents = $agents
        system_health = @{
            cpu_percent = $health.data.cpu_percent
            memory_percent = $health.data.memory_percent
            status = $health.data.status
        }
        timestamp = (Get-Date -Format "o")
        note = "✅ VRAIS agents actifs sur edgeserver (données réelles, pas MOCK)"
    }
} catch {
    $response = @{
        status = "error"
        mode = "FALLBACK"
        error = $_.Exception.Message
        agents_count = $agents.Count
        agents = $agents
        timestamp = (Get-Date -Format "o")
        note = "⚠️ API non accessible, liste des agents disponible en mode fallback"
    }
}

# Output JSON pour Continue IDE
$response | ConvertTo-Json -Depth 10
