# 🚀 Continue + TwisterLab MCP - Guide d'Utilisation

## ✅ Installation Complète

Le serveur MCP TwisterLab est maintenant configuré pour Continue IDE !

**Fichiers créés** :
- `agents/mcp/mcp_server_continue_sync.py` - Serveur MCP pour Continue
- `test_mcp_sync.py` - Tests de validation
- `c:\Users\Administrator\.continue\config.json` - Configuration Continue

---

## 🎯 Utilisation dans Continue

### **1. Redémarrer VS Code**
```
Ctrl+Shift+P → Developer: Reload Window
```

### **2. Ouvrir Continue Chat**
```
Ctrl+L
```

### **3. Utiliser les MCP Tools**

#### **Option A : Via mentions @**
```
@twisterlab classify this ticket: Cannot connect to WiFi eduroam
```

#### **Option B : Via commands**
```
Use the classify_ticket MCP tool to classify: "Printer not working"
```

#### **Option C : Via custom commands**
```
Ctrl+L → Dans le menu → Sélectionner "Classify Ticket"
```

---

## 🔧 MCP Tools Disponibles

### **1. classify_ticket**
Classifie un ticket IT helpdesk

**Exemple** :
```
@twisterlab classify: "Cannot access shared drive Z:"
```

**Résultat** :
```json
{
  "status": "success",
  "category": "network",
  "confidence": 0.85,
  "agent": "RealClassifierAgent"
}
```

---

### **2. resolve_ticket**
Obtient les étapes de résolution depuis la base SOP

**Exemple** :
```
@twisterlab resolve ticket category=network description="WiFi keeps disconnecting"
```

**Résultat** :
```json
{
  "status": "success",
  "resolution_steps": [
    "Step 1: Verify network issue symptoms",
    "Step 2: Check network configuration",
    "Step 3: Apply standard network troubleshooting",
    "Step 4: Escalate if unresolved"
  ],
  "estimated_time": "15-30 minutes"
}
```

---

### **3. monitor_system_health**
Vérifie la santé du système TwisterLab

**Exemple** :
```
@twisterlab check system health
```

**Résultat** :
```json
{
  "status": "warning",
  "services": {
    "postgres": "running",
    "redis": "running",
    "api": "down (0/1 replicas)",
    "ollama": "running"
  }
}
```

---

### **4. create_backup**
Crée une sauvegarde de la base de données/config

**Exemple** :
```
@twisterlab create full backup
```

**Résultat** :
```json
{
  "status": "success",
  "backup_location": "/backups/backup_20251111.tar.gz",
  "agent": "RealBackupAgent"
}
```

---

## 📚 MCP Resources Disponibles

### **1. twisterlab://system/health**
Status système en temps réel

**Utilisation** :
```
Read resource: twisterlab://system/health
```

### **2. twisterlab://agents/status**
Status de tous les agents

**Utilisation** :
```
Read resource: twisterlab://agents/status
```

---

## 🧪 Tests Locaux

### **Test rapide du serveur MCP** :
```powershell
cd C:\TwisterLab
python test_mcp_sync.py
```

**Output attendu** :
```
✅ ALL TESTS PASSED

TEST: classify_ticket
→ category: network, confidence: 0.85

TEST: monitor_system_health
→ status: warning, api: down
```

### **Test manuel du serveur** :
```powershell
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python agents/mcp/mcp_server_continue_sync.py
```

---

## ⚠️ Mode Actuel : MOCK

**Important** : Le serveur MCP retourne actuellement des **réponses simulées** car l'API TwisterLab est offline (0/1 replicas).

**Toutes les réponses incluent** :
```json
{
  "note": "⚠️ Mock response - API service offline"
}
```

**Quand l'API sera online** :
1. Le serveur MCP appellera les **vrais agents** (RealClassifierAgent, etc.)
2. Les réponses viendront de **Ollama LLM** (classification réelle)
3. Les données viendront de **PostgreSQL** (SOPs, historique)

---

## 🔄 Différence avec GitHub Copilot

| Feature | GitHub Copilot (toi) | Continue + MCP |
|---------|---------------------|----------------|
| **Agents** | ❌ Pas d'accès | ✅ Appelle agents TwisterLab |
| **LLM** | GPT-4 (cloud) | Llama 3.2 1B (local) |
| **Classification** | Simulée | **Vraie** (via RealClassifierAgent) |
| **Résolution** | Générique | **SOPs réels** (base de données) |
| **Monitoring** | N/A | **Système réel** (Docker, PostgreSQL) |
| **Backup** | N/A | **Vraies sauvegardes** (RealBackupAgent) |

---

## 🚀 Prochaines Étapes

### **1. Fixer l'API Service** (priorité haute)
```powershell
# Rebuild image avec dépendances
docker build -f infrastructure/dockerfiles/Dockerfile.api -t twisterlab/api:v1.0.1 .

# Copier vers edgeserver
docker save twisterlab/api:v1.0.1 | ssh twister@192.168.0.30 docker load

# Redéployer
ssh twister@192.168.0.30 "docker stack deploy -c docker-compose.yml twisterlab"
```

### **2. Remplacer MOCK par Agents Réels**
Modifier `mcp_server_continue_sync.py` pour appeler les agents via l'API REST :
```python
# Remplacer mock responses par :
import requests
response = requests.post(
    "http://192.168.0.30:8000/v1/mcp/tools/call",
    json={"tool": "classify_ticket", "arguments": arguments}
)
```

### **3. Tester l'Intégration Complète**
```
Continue → MCP Server → API REST → Real Agents → Ollama LLM
```

---

## � Dépannage - Erreurs Courantes

### **Erreur "Connection refused"**
Si vous obtenez `[Errno 111] Connection refused` :

1. **Vérifiez que le serveur MCP fonctionne** :
   ```bash
   python agents/mcp/mcp_server_continue_sync.py
   ```

2. **Testez la connectivité** :
   ```bash
   curl -X POST http://127.0.0.1:8000 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   ```

3. **Redémarrez VS Code** :
   ```
   Ctrl+Shift+P → Developer: Reload Window
   ```

### **Erreur "Duplicate tools/rules"**
Si Continue signale des doublons :

1. **Videz le cache Continue** :
   ```bash
   rm -rf ~/.continue/cache/
   rm -rf ~/.continue/sessions/
   rm -rf ~/.continue/index/
   ```

2. **Redémarrez VS Code**

### **MCP Tools non visibles**
Si les outils MCP n'apparaissent pas :

1. **Vérifiez la configuration** :
   ```bash
   cat ~/.continue/config.yaml
   ```

2. **Testez le serveur MCP** :
   ```bash
   python test_mcp_sync.py
   ```

3. **Redémarrez VS Code**

---

## �📖 Documentation Complète

- **MCP Protocol** : `MCP_INTEGRATION_GUIDE.md`
- **Projet TwisterLab** : `copilot-instructions.md`
- **API REST** : `API_DOCUMENTATION.md`
- **Changelog** : `CHANGELOG.md`

---

**Version** : 1.0.0
**Date** : 2025-11-11
**Status** : ✅ MCP Server opérationnel (mode MOCK)
**Next** : Fixer API service → Passer en mode REAL
