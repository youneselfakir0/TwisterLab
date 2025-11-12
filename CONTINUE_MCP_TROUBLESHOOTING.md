# 🔧 Continue v1.2.10 - Support MCP Troubleshooting

## Problème Actuel
- Continue détecte `@twisterlab` comme **dossier** (fichiers .py)
- Au lieu de détecter comme **serveur MCP** (tools)

## Version Continue
- **Installée** : v1.2.10
- **Support MCP** : ✅ Oui (depuis v0.9.x)
- **Syntaxe** : Peut varier selon versions

---

## Solutions à Tester (dans l'ordre)

### ✅ Solution 1 : Chemin Python complet (DÉJÀ FAIT)

**Fichier** : `c:\Users\Administrator\.continue\config.json`

**Changement** :
```json
"mcpServers": {
  "twisterlab": {
    "command": "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
    "args": ["C:\\TwisterLab\\agents\\mcp\\mcp_server_continue_sync.py"],
    "env": {"PYTHONPATH": "C:\\TwisterLab"}
  }
}
```

**Test** :
1. Redémarre VS Code : `Ctrl+Shift+P` → `Developer: Reload Window`
2. Ouvre Continue : `Ctrl+L`
3. Tape : `List MCP tools` ou `Show available tools`
4. Ou regarde en bas de Continue pour un indicateur MCP

---

### 🔄 Solution 2 : Syntaxe "experimental"

Si Solution 1 ne marche pas, certaines versions utilisent `experimental.modelContextProtocolServers`.

**Fichier de test créé** : `c:\Users\Administrator\.continue\config.experimental.json`

**Test** :
1. Renomme `config.json` → `config.json.old`
2. Renomme `config.experimental.json` → `config.json`
3. Redémarre VS Code
4. Teste Continue

---

### 🔄 Solution 3 : Syntaxe "tools" alternative

Continue peut aussi utiliser cette syntaxe :

```json
{
  "tools": [
    {
      "name": "twisterlab",
      "type": "mcp",
      "config": {
        "command": "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
        "args": ["C:\\TwisterLab\\agents\\mcp\\mcp_server_continue_sync.py"],
        "env": {"PYTHONPATH": "C:\\TwisterLab"}
      }
    }
  ]
}
```

---

### 🔄 Solution 4 : Vérifier les logs Continue

**Étapes** :
1. `Ctrl+Shift+P` → `Developer: Show Logs`
2. Sélectionne `Extension Host`
3. Cherche dans les logs :
   - `mcp`
   - `twisterlab`
   - `error`
   - `spawn`
   - `ENOENT`

**Erreurs communes** :
- `ENOENT` → Python introuvable
- `Permission denied` → Problème de droits
- `Parse error` → JSON invalide
- `Cannot spawn` → Mauvais chemin command

---

## Test Sans Continue (Validation Serveur MCP)

Vérifie que le serveur MCP fonctionne standalone :

```powershell
# Test 1: Initialize
$request = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
echo $request | C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe C:\TwisterLab\agents\mcp\mcp_server_continue_sync.py

# Test 2: List tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe C:\TwisterLab\agents\mcp\mcp_server_continue_sync.py

# Test 3: Suite complète
cd C:\TwisterLab
python test_mcp_sync.py
```

**Si ces tests passent** → Serveur MCP OK, problème = config Continue
**Si ces tests échouent** → Serveur MCP cassé, fixer d'abord

---

## Alternatives si MCP ne fonctionne pas

### Alternative 1 : Custom Commands Continue

Au lieu de MCP, utilise les `customCommands` :

```json
"customCommands": [
  {
    "name": "Classify Ticket",
    "prompt": "Execute this Python script to classify the ticket:\n\n```python\nimport subprocess\nimport json\nresult = subprocess.run(['python', 'test_mcp_sync.py'], capture_output=True)\nprint(result.stdout.decode())\n```",
    "description": "Classify IT ticket using TwisterLab"
  }
]
```

### Alternative 2 : Continue Context Provider

Utilise `@codebase` pour inclure le code TwisterLab :

```
@codebase agents/real/real_classifier_agent.py

Use this agent to classify: "WiFi broken"
```

---

## Checklist de Diagnostic

Après redémarrage VS Code, vérifie :

- [ ] Continue démarre sans erreur
- [ ] Logs Extension Host ne montrent pas d'erreur MCP
- [ ] En bas de Continue, indicateur MCP visible ?
- [ ] `@twisterlab` affiche toujours fichiers ou tools ?
- [ ] Commande "List MCP tools" fonctionne ?
- [ ] `python test_mcp_sync.py` passe 6/6 tests ?

---

## Prochaines Étapes

1. **Redémarre VS Code** maintenant
2. **Ouvre Continue** (`Ctrl+L`)
3. **Vérifie logs** (`Ctrl+Shift+P` → Show Logs → Extension Host)
4. **Teste** : Tape "List available MCP tools" dans Continue
5. **Rapporte résultats** : Copie-moi les erreurs exactes

---

**Si rien ne marche après tout ça, on passera à l'alternative REST API** (appels HTTP directs depuis Continue au lieu de MCP stdio).
