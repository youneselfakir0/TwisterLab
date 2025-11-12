# 🧪 Guide de Test - Continue + MCP TwisterLab

## Étape 1 : Redémarrer VS Code

1. **Ouvre la palette de commandes** : `Ctrl+Shift+P`
2. **Tape** : `Developer: Reload Window`
3. **Appuie sur Entrée**

VS Code va redémarrer et charger la nouvelle config Continue avec le serveur MCP.

---

## Étape 2 : Vérifier que Continue détecte le serveur MCP

### **A. Ouvrir Continue**
- Appuie sur `Ctrl+L` pour ouvrir le chat Continue

### **B. Vérifier les MCP Servers**
Dans Continue, en bas de la fenêtre de chat, tu devrais voir :
- 🔌 **MCP Servers** : `twisterlab` (avec un indicateur vert si connecté)

**Si tu vois `twisterlab` en vert** → ✅ Serveur MCP détecté !
**Si tu vois `twisterlab` en rouge/orange** → ❌ Erreur de connexion

---

## Étape 3 : Tester l'appel MCP

### **Test 1 : Mention @twisterlab**

Dans le chat Continue, tape :
```
@twisterlab
```

**Résultat attendu** :
Continue devrait afficher une liste déroulante avec :
- 📋 **Tools** (4) : classify_ticket, resolve_ticket, monitor_system_health, create_backup
- 📁 **Resources** (2) : system/health, agents/status
- 💬 **Prompts** (2) : classify_it_ticket, resolve_network_issue

**Si tu vois cette liste** → ✅ MCP fonctionne !
**Si rien ne s'affiche** → ❌ MCP non détecté

---

### **Test 2 : Appeler un tool MCP**

Dans Continue, tape :
```
@twisterlab/classify_ticket Classify this ticket: Cannot connect to WiFi eduroam
```

**OU** (plus simple) :
```
Use the classify_ticket tool to classify: "Printer not working"
```

**Résultat attendu** :
```json
{
  "status": "success",
  "agent": "RealClassifierAgent",
  "category": "network" (ou "hardware" pour imprimante),
  "confidence": 0.85,
  "timestamp": "2025-11-12T...",
  "note": "⚠️ Mock response - API service offline"
}
```

**Si tu vois ce JSON** → ✅ Tool MCP exécuté avec succès !
**Si erreur** → Copie-moi l'erreur exacte

---

### **Test 3 : Lire une resource MCP**

Dans Continue, tape :
```
Read the resource twisterlab://system/health
```

**Résultat attendu** :
```json
{
  "status": "degraded",
  "api_service": "offline",
  "database": "online",
  "cache": "online",
  "llm": "online"
}
```

---

### **Test 4 : Utiliser un prompt MCP**

Dans Continue, tape :
```
Use the classify_it_ticket prompt with: "My email is not syncing"
```

**Résultat attendu** :
Continue devrait afficher le prompt formaté et potentiellement appeler classify_ticket automatiquement.

---

## Étape 4 : Vérifier les logs du serveur MCP

Si Continue ne détecte pas le serveur MCP, vérifie les logs :

### **A. Logs Continue**
1. `Ctrl+Shift+P` → `Developer: Show Logs`
2. Sélectionne `Extension Host`
3. Cherche des lignes contenant `mcp` ou `twisterlab`

### **B. Tester le serveur ManuellemenT**

Ouvre un terminal PowerShell et exécute :
```powershell
cd C:\TwisterLab
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python agents/mcp/mcp_server_continue_sync.py
```

**Output attendu** :
```json
{"jsonrpc": "2.0", "id": 1, "result": {"tools": [...]}}
```

**Si tu vois le JSON** → Serveur MCP fonctionne en standalone
**Si erreur Python** → Copie-moi l'erreur

---

## Étape 5 : Diagnostics en cas de problème

### **Problème 1 : Continue ne voit pas @twisterlab**

**Vérifications** :
1. Ouvre `c:\Users\Administrator\.continue\config.json`
2. Vérifie que la section `mcpServers` existe :
```json
"mcpServers": {
  "twisterlab": {
    "command": "python",
    "args": ["C:\\TwisterLab\\agents\\mcp\\mcp_server_continue_sync.py"],
    "env": {"PYTHONPATH": "C:\\TwisterLab"}
  }
}
```

3. Si la section manque, le fichier n'a pas été chargé → Redémarre VS Code

---

### **Problème 2 : Erreur "Cannot spawn python"**

**Solution** :
Remplace `"command": "python"` par le chemin complet de Python :
```json
"command": "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
```

Ou utilise l'environnement virtuel :
```json
"command": "C:\\TwisterLab\\.venv\\Scripts\\python.exe"
```

---

### **Problème 3 : MCP server crash au démarrage**

**Debug** :
1. Exécute le serveur en mode debug :
```powershell
cd C:\TwisterLab
$env:PYTHONPATH = "C:\TwisterLab"
python agents/mcp/mcp_server_continue_sync.py
# Tape quelques requêtes JSON manuellement
```

2. Cherche les erreurs dans stderr (logs en rouge)

---

## Résultats à me communiquer

Après avoir testé, dis-moi :

1. ✅ ou ❌ **Continue détecte @twisterlab** ?
2. ✅ ou ❌ **Liste des tools s'affiche** ?
3. ✅ ou ❌ **classify_ticket retourne un JSON** ?
4. ✅ ou ❌ **Resource system/health lisible** ?
5. 📋 **Copie-moi les erreurs exactes si problèmes**

---

## Commandes rapides de test

```powershell
# Test 1: Serveur MCP standalone
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python agents/mcp/mcp_server_continue_sync.py

# Test 2: Liste des tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python agents/mcp/mcp_server_continue_sync.py

# Test 3: Appel classify
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"classify_ticket","arguments":{"ticket_text":"WiFi broken"}}}' | python agents/mcp/mcp_server_continue_sync.py

# Test 4: Suite complète
python test_mcp_sync.py
```

---

**Teste maintenant et reviens avec les résultats !** 🚀
