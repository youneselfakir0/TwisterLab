# GUIDE RAPIDE - Continue MCP TwisterLab

**Status**: ✅ FONCTIONNEL (mode MOCK)

---

## 🚀 UTILISATION DANS VS CODE

### Dans Continue.dev, tape:

```
/classify "WiFi broken in conference room"
```

**Résultat attendu**:
```
Category: network
Confidence: 0.85
Agent: RealClassifierAgent
```

---

## 🛠️ COMMANDES DISPONIBLES

### 1. Classifier un ticket
```
/classify "text du ticket"
```

### 2. Obtenir résolution
```
/resolve category:network description:"WiFi intermittent"
```

### 3. Vérifier santé système
```
/monitor_system_health
```

### 4. Créer backup
```
/create_backup backup_type:full
```

---

## ⚠️ MODE ACTUEL

**MOCK MODE** = Réponses simulées

Pour mode PRODUCTION:
1. Démarrer API: `python api/main.py`
2. Vérifier Docker services running
3. Tester `/classify` à nouveau

---

## 📁 FICHIERS

- Serveur: `agents/mcp/mcp_server_continue_sync.py`
- Config: `.continue/config.yaml`
- Tests: `.continue/VERIFICATION_MCP.md`

---

**Prêt à utiliser !** 🎉
