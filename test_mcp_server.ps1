#!/usr/bin/env pwsh
<#
.SYNOPSIS
Test MCP Server - list_autonomous_agents tool

.DESCRIPTION
Teste le serveur MCP en envoyant une requête JSON-RPC via stdio
pour appeler l'outil list_autonomous_agents
#>

$ErrorActionPreference = "Stop"

Write-Host "`n🧪 TEST MCP SERVER - list_autonomous_agents" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Requêtes MCP (JSON-RPC 2.0)
$requests = @(
    @{
        jsonrpc = "2.0"
        id = 1
        method = "initialize"
        params = @{
            protocolVersion = "2024-11-05"
            capabilities = @{}
            clientInfo = @{
                name = "test-client"
                version = "1.0.0"
            }
        }
    },
    @{
        jsonrpc = "2.0"
        id = 2
        method = "tools/list"
        params = @{}
    },
    @{
        jsonrpc = "2.0"
        id = 3
        method = "tools/call"
        params = @{
            name = "list_autonomous_agents"
            arguments = @{}
        }
    }
)

# Lancer le serveur MCP
$pythonPath = (Get-Command python).Source
$scriptPath = "agents\mcp\mcp_server_continue_sync.py"

Write-Host "`n📍 Python: $pythonPath" -ForegroundColor White
Write-Host "📍 Script: $scriptPath" -ForegroundColor White
Write-Host "`n🚀 Démarrage du serveur MCP...`n" -ForegroundColor Yellow

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $pythonPath
$psi.Arguments = $scriptPath
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true
$psi.WorkingDirectory = $PWD.Path

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $psi
$process.Start() | Out-Null

Start-Sleep -Seconds 1

try {
    foreach ($req in $requests) {
        $reqJson = ($req | ConvertTo-Json -Depth 10 -Compress) + "`n"
        
        Write-Host "📤 Request $($req.id): $($req.method)" -ForegroundColor Cyan
        
        # Envoyer la requête
        $process.StandardInput.WriteLine($reqJson)
        $process.StandardInput.Flush()
        
        # Lire la réponse (timeout 5s)
        $response = $null
        $timeout = [datetime]::Now.AddSeconds(5)
        
        while ([datetime]::Now -lt $timeout -and !$process.StandardOutput.EndOfStream) {
            $line = $process.StandardOutput.ReadLine()
            if ($line) {
                $response = $line | ConvertFrom-Json
                break
            }
        }
        
        if ($response) {
            Write-Host "📥 Response $($req.id): " -ForegroundColor Green -NoNewline
            
            if ($req.method -eq "tools/list") {
                $tools = $response.result.tools
                Write-Host "$($tools.Count) tools found" -ForegroundColor White
                foreach ($tool in $tools) {
                    Write-Host "   • $($tool.name)" -ForegroundColor Yellow
                }
            }
            elseif ($req.method -eq "tools/call" -and $req.params.name -eq "list_autonomous_agents") {
                $content = $response.result.content[0].text | ConvertFrom-Json
                Write-Host "Status: $($content.status)" -ForegroundColor White
                Write-Host "   Mode: $($content.mode)" -ForegroundColor White
                Write-Host "   Total agents: $($content.total)" -ForegroundColor White
                Write-Host "`n   📋 Agents:" -ForegroundColor Cyan
                foreach ($agent in $content.agents) {
                    $name = $agent.name.PadRight(30)
                    $desc = $agent.description
                    Write-Host "      $name - $desc" -ForegroundColor White
                }
            }
            else {
                Write-Host "OK" -ForegroundColor White
            }
        }
        else {
            Write-Host "❌ Timeout - Pas de réponse" -ForegroundColor Red
        }
        
        Write-Host ""
    }
    
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host "✅ Test terminé avec succès!`n" -ForegroundColor Green
}
catch {
    Write-Host "`n❌ Erreur: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    # Arrêter le processus
    if (!$process.HasExited) {
        $process.Kill()
    }
    $process.Dispose()
}

# Lire les logs stderr
Start-Sleep -Milliseconds 500
Write-Host "`n📄 Logs du serveur MCP:" -ForegroundColor Yellow
$process = Start-Process -FilePath $pythonPath -ArgumentList $scriptPath `
    -RedirectStandardError "mcp_test_stderr.log" -NoNewWindow -PassThru -Wait
if (Test-Path "mcp_test_stderr.log") {
    Get-Content "mcp_test_stderr.log" | Select-Object -First 20
    Remove-Item "mcp_test_stderr.log"
}
