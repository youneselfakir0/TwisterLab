# ========================================
# AUTOMATISATION NOCTURNE TWISTERLAB
# Exécution pendant sommeil
# Date: 10 Novembre 2025
# ========================================

$LOG_FILE = "night_automation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Log-Message {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $LOG_FILE -Value $logEntry
}

Log-Message "=== DÉBUT AUTOMATISATION NOCTURNE ==="
Log-Message ""

# ========================================
# PHASE 1: FINALISATION SERVICES (30min)
# ========================================
Log-Message "PHASE 1: Finalisation des services Docker"
Log-Message "----------------------------------------"

try {
    # 1.1 Forcer mise à jour de tous les services
    Log-Message "1.1 Force update de tous les services..."
    $services = @(
        "twisterlab_prod_redis",
        "twisterlab_prod_ollama",
        "twisterlab_prod_postgres",
        "twisterlab_prod_webui"
    )

    foreach ($service in $services) {
        Log-Message "  → Updating $service..."
        docker service update --force $service 2>&1 | Out-File -Append $LOG_FILE
        Start-Sleep -Seconds 30
    }

    # 1.2 Attendre convergence
    Log-Message "1.2 Attente convergence services (5 min)..."
    Start-Sleep -Seconds 300

    # 1.3 Vérifier statut
    Log-Message "1.3 Vérification statut final..."
    docker service ls | Out-File -Append $LOG_FILE

    Log-Message "✅ PHASE 1 TERMINÉE"
} catch {
    Log-Message "❌ ERREUR PHASE 1: $_"
}

Log-Message ""

# ========================================
# PHASE 2: TESTS COMPLETS (1h)
# ========================================
Log-Message "PHASE 2: Exécution tests complets"
Log-Message "----------------------------------------"

try {
    # 2.1 Tests unitaires
    Log-Message "2.1 Exécution tests unitaires..."
    & .\.venv\Scripts\Activate.ps1
    pytest tests/ -v --cov=agents --cov-report=html --cov-report=term 2>&1 | Out-File -Append $LOG_FILE

    # 2.2 Tests d'intégration
    Log-Message "2.2 Exécution tests d'intégration..."
    pytest tests/test_integration_full_system.py -v -s 2>&1 | Out-File -Append $LOG_FILE

    # 2.3 Linting
    Log-Message "2.3 Vérification code quality..."
    black agents/ --check 2>&1 | Out-File -Append $LOG_FILE
    pylint agents/ 2>&1 | Out-File -Append $LOG_FILE
    mypy agents/ 2>&1 | Out-File -Append $LOG_FILE

    Log-Message "✅ PHASE 2 TERMINÉE"
} catch {
    Log-Message "❌ ERREUR PHASE 2: $_"
}

Log-Message ""

# ========================================
# PHASE 3: MONITORING & SANTÉ (30min)
# ========================================
Log-Message "PHASE 3: Collecte métriques monitoring"
Log-Message "----------------------------------------"

try {
    # 3.1 Test API Health
    Log-Message "3.1 Test API Health endpoint..."
    for ($i = 1; $i -le 10; $i++) {
        $response = ssh twister@edgeserver.twisterlab.local "wget -qO- http://localhost:8000/health 2>&1"
        Log-Message "  Test $i : $(if($response -match 'healthy') {'✅ OK'} else {'❌ FAIL'})"
        Start-Sleep -Seconds 60
    }

    # 3.2 Métriques système
    Log-Message "3.2 Collecte métriques système..."
    ssh twister@edgeserver.twisterlab.local "df -h && free -h && docker stats --no-stream" | Out-File -Append $LOG_FILE

    # 3.3 Logs services
    Log-Message "3.3 Extraction logs services..."
    docker service logs --tail 100 twisterlab_prod_api 2>&1 | Out-File -Append "logs_api_night.txt"

    Log-Message "✅ PHASE 3 TERMINÉE"
} catch {
    Log-Message "❌ ERREUR PHASE 3: $_"
}

Log-Message ""

# ========================================
# PHASE 4: NETTOYAGE & OPTIMISATION (30min)
# ========================================
Log-Message "PHASE 4: Nettoyage et optimisation"
Log-Message "----------------------------------------"

try {
    # 4.1 Nettoyage Docker local
    Log-Message "4.1 Nettoyage Docker local..."
    docker system prune -f 2>&1 | Out-File -Append $LOG_FILE

    # 4.2 Nettoyage edgeserver
    Log-Message "4.2 Nettoyage edgeserver..."
    ssh twister@edgeserver.twisterlab.local "echo 'Nadgab354`$2024' | sudo -S bash ~/TwisterLab/disk_cleanup.sh" 2>&1 | Out-File -Append $LOG_FILE

    # 4.3 Espace disque final
    Log-Message "4.3 Vérification espace disque final..."
    ssh twister@edgeserver.twisterlab.local "df -h /" | Out-File -Append $LOG_FILE

    Log-Message "✅ PHASE 4 TERMINÉE"
} catch {
    Log-Message "❌ ERREUR PHASE 4: $_"
}

Log-Message ""

# ========================================
# PHASE 5: GÉNÉRATION DOCUMENTATION (1h)
# ========================================
Log-Message "PHASE 5: Génération documentation"
Log-Message "----------------------------------------"

try {
    # 5.1 Mise à jour README
    Log-Message "5.1 Génération README complet..."
    # Le script sera créé séparément

    # 5.2 Génération rapport final
    Log-Message "5.2 Génération rapport final..."
    @"
# RAPPORT NOCTURNE - $(Get-Date -Format 'yyyy-MM-dd HH:mm')

## Services Déployés
$(docker service ls)

## Espace Disque
$(ssh twister@edgeserver.twisterlab.local "df -h /")

## Tests Exécutés
- Tests unitaires: VOIR $LOG_FILE
- Tests intégration: VOIR $LOG_FILE
- Code quality: VOIR $LOG_FILE

## Logs
- API: logs_api_night.txt
- Complet: $LOG_FILE

## Actions Restantes
1. Vérifier tous les services sont 1/1
2. Configurer TLS Docker (URGENT)
3. Tester Redis authentication
4. Valider Ollama connection

## Prochaines Étapes
Voir TODO_MATIN.md
"@ | Out-File "RAPPORT_NOCTURNE_$(Get-Date -Format 'yyyyMMdd').md"

    Log-Message "✅ PHASE 5 TERMINÉE"
} catch {
    Log-Message "❌ ERREUR PHASE 5: $_"
}

Log-Message ""

# ========================================
# RÉSUMÉ FINAL
# ========================================
Log-Message "=== RÉSUMÉ EXÉCUTION NOCTURNE ==="
Log-Message ""
Log-Message "Fichiers générés:"
Log-Message "  - $LOG_FILE (log complet)"
Log-Message "  - logs_api_night.txt (logs API)"
Log-Message "  - RAPPORT_NOCTURNE_*.md (rapport)"
Log-Message "  - htmlcov/ (couverture tests)"
Log-Message ""
Log-Message "Durée totale estimée: 3h30"
Log-Message ""
Log-Message "=== FIN AUTOMATISATION NOCTURNE ==="

# Créer fichier TODO pour le matin
@"
# ☀️ TODO MATIN - $(Get-Date -Format 'yyyy-MM-dd')

## À Vérifier en Premier
1. [ ] Lire RAPPORT_NOCTURNE_*.md
2. [ ] Vérifier $LOG_FILE pour erreurs
3. [ ] Checker docker service ls (tous 1/1?)
4. [ ] Tester http://edgeserver:8000/health

## Si Services OK (tous 1/1)
- [ ] Configurer TLS Docker (2h) - PRIORITÉ 1
- [ ] Créer diagrammes architecture (3h)
- [ ] Enregistrer démo vidéo (2h)

## Si Services KO
- [ ] Analyser logs_api_night.txt
- [ ] Débugger service en échec
- [ ] Relancer automatisation si besoin

## Résultats Tests
- Couverture: Voir htmlcov/index.html
- Pylint: Voir $LOG_FILE
- Mypy: Voir $LOG_FILE

Bonne journée ! 🚀
"@ | Out-File "TODO_MATIN.md"
