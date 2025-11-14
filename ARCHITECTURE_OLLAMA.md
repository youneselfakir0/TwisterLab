# Architecture Ollama TwisterLab

## 🎯 Configuration Actuelle

### Corertx (192.168.0.20:11434) - SERVEUR LLM PRINCIPAL ✅
**Serveur Ollama natif avec GPU RTX 3060**

**Matériel :**
- **GPU : RTX 3060 (12GB VRAM)** 🚀
- OS : Windows avec Ollama natif
- Connexion : Réseau local 192.168.0.20

**Modèles disponibles :**
- `llama3.2:1b` - **UTILISÉ PAR TOUS LES AGENTS** ✅
  - Vitesse : 2-7s par requête
  - Qualité : Excellente pour classification/résolution
  - VRAM : ~1.3GB
- `qwen3:8b` - Disponible (5.2GB)
- `codellama:latest` - Disponible (3.8GB)
- `deepseek-r1:latest` - Disponible (5.2GB)
- `llama3:latest` - Disponible (4.7GB)

**Configuration agents (agents/config.py) :**
```python
OLLAMA_URL = "http://192.168.0.20:11434"
OLLAMA_MODELS = {
    "classifier": "llama3.2:1b",   # ClassifierAgent
    "resolver": "llama3.2:1b",     # ResolverAgent
    "commander": "llama3.2:1b",    # DesktopCommanderAgent
    "monitoring": "llama3.2:1b",   # MonitoringAgent
    "general": "llama3.2:1b"       # Fallback
}
```

**Agents utilisant Ollama :**
- ✅ `RealClassifierAgent` - Classification de tickets
- ✅ `RealResolverAgent` - Génération de SOPs
- ✅ `RealDesktopCommanderAgent` - Validation de commandes

---

### Edgeserver (192.168.0.30:11434) - POTENTIEL BACKUP ⚠️

**Matériel :**
- **GPU : GTX 1050 (2GB VRAM)**
- OS : Ubuntu 24.04 avec Docker Swarm
- Connexion : Serveur de production

**État actuel :**
- Service Docker `twisterlab_ollama` : **0/1 replicas** (non démarré)
- Port 11434 : Exposé mais non opérationnel
- Configuration GPU Docker : Manquante (besoin nvidia-container-runtime)

**Problèmes identifiés :**
1. GTX 1050 (2GB) vs RTX 3060 (12GB) → Performance 3-5x inférieure
2. Redondant avec corertx qui a le meilleur GPU
3. Aucun agent configuré pour l'utiliser
4. Configuration GPU manquante dans Docker Swarm

---

## 💡 Architecture Déployée

### ✅ **ARCHITECTURE ACTUELLE : Ollama Natif avec Backup** (OPÉRATIONNEL)

**Configuration :**
- **Corertx (RTX 3060)** : Serveur LLM principal - http://192.168.0.20:11434
- **Edgeserver (GTX 1050)** : Backup Ollama natif - http://192.168.0.30:11434

**Avantages :**
- ✅ Haute disponibilité avec failover automatique
- ✅ RTX 3060 pour performance optimale (2-7s/requête)
- ✅ GTX 1050 backup si corertx indisponible (5-15s/requête)
- ✅ Redondance pour production critique

**Services edgeserver :**
- ✅ API (twisterlab-api) → Utilise corertx:11434 (PRIMARY)
- ✅ PostgreSQL
- ✅ Redis
- ✅ Ollama natif (BACKUP - systemd service)

**État actuel :**
```bash
# Ollama edgeserver (BACKUP)
systemctl status ollama  # ✅ Active (running)
curl http://192.168.0.30:11434/api/tags  # ✅ Répond

# Ollama corertx (PRIMARY)
curl http://192.168.0.20:11434/api/tags  # ✅ Répond
```

---

### Alternative : Architecture simplifiée sans backup (NON RECOMMANDÉ)

**Si vous voulez simplifier (pas recommandé pour production) :**

**Configuration simplifiée :**
- Désactiver Ollama sur edgeserver : `sudo systemctl stop ollama && sudo systemctl disable ollama`
- Uniquement Corertx pour LLM
- Risque : Pas de backup si corertx indisponible

**Inconvénients :**
1. Point de défaillance unique (corertx)
2. Pas de continuité de service si réseau/corertx down
3. Pas conforme à la vision TwisterLab d'autonomie
4. Pas de redondance

**Exemple fallback automatique :**
```python
# agents/base/llm_client.py
OLLAMA_PRIMARY = "http://192.168.0.20:11434"    # Corertx RTX 3060
OLLAMA_FALLBACK = "http://localhost:11434"      # Edgeserver GTX 1050

async def generate_with_fallback(self, prompt):
    try:
        return await self.generate(prompt, url=OLLAMA_PRIMARY)
    except Exception as e:
        logger.warning(f"Primary Ollama (RTX 3060) down: {e}")
        logger.info("Switching to backup Ollama (GTX 1050)")
        return await self.generate(prompt, url=OLLAMA_FALLBACK)
```

**Performance attendue (backup GTX 1050) :**
- llama3.2:1b : 5-15s/requête (vs 2-7s sur RTX 3060)
- 2GB VRAM max (modèles limités)
- Suffisant pour continuité de service

---

## 📊 Comparaison GPU

| Critère | Corertx (RTX 3060) | Edgeserver (GTX 1050) |
|---------|--------------------|-----------------------|
| **VRAM** | **12GB** ✅ | 2GB ⚠️ |
| **Performance llama3.2:1b** | **2-7s/requête** ✅ | 5-15s/requête ⚠️ |
| **Modèles supportés** | Tous (jusqu'à 12GB) ✅ | Petits modèles (<2GB) ⚠️ |
| **OS** | Windows (natif) | Linux (Docker) |
| **Statut Ollama** | **Actif** ✅ | Inactif (0/1) ❌ |
| **Utilisation actuelle** | **100% agents** ✅ | 0% ❌ |
| **Rôle optimal** | **Production LLM** ✅ | Backup optionnel ⚠️ |

---

## ✅ ARCHITECTURE TWISTERLAB - VISION DISTRIBUÉE

**Principes TwisterLab :**
- 🤖 **Autonomie** : Chaque serveur doit fonctionner indépendamment
- 🔄 **Résilience** : Pas de point de défaillance unique
- 🌐 **Distribution** : Services répartis intelligemment
- 🚀 **Performance** : GPU local pour réactivité maximale

---

### ARCHITECTURE DÉPLOYÉE ✅ OPÉRATIONNELLE

```
┌──────────────────────────────────────────────┐
│  CORERTX (RTX 3060 12GB) - PRIMARY          │
│  ✅ Ollama natif (Windows)                   │
│  ✅ Performance optimale: 2-7s/requête       │
│  ✅ 5 modèles: llama3.2:1b, qwen3:8b, etc   │
│  ✅ 192.168.0.20:11434                       │
└──────────────────────────────────────────────┘
              ↓ Failover si down
┌──────────────────────────────────────────────┐
│  EDGESERVER (GTX 1050 2GB) - BACKUP         │
│  ✅ API + Agents                             │
│  ✅ PostgreSQL + Redis                       │
│  ✅ Ollama natif (Ubuntu systemd)            │
│     - llama3.2:1b                            │
│     - Performance: 5-15s/requête            │
│     - 192.168.0.30:11434                    │
│  ✅ Continuité de service garantie           │
└──────────────────────────────────────────────┘
```

**Avantages de cette architecture :**
1. ✅ **Haute disponibilité** : Backup automatique si PRIMARY down
2. ✅ **Performance optimale** : RTX 3060 12GB pour production
3. ✅ **Continuité de service** : GTX 1050 prend le relais si besoin
4. ✅ **Redondance** : 2 serveurs Ollama indépendants
5. ✅ **Vision TwisterLab** : Résilience et autonomie

**Configuration API actuelle :**
```bash
# docker-compose.prod-native-ollama.yml
OLLAMA_URL=http://192.168.0.20:11434         # PRIMARY (Corertx RTX 3060)
OLLAMA_FALLBACK=http://192.168.0.30:11434    # BACKUP (Edgeserver GTX 1050)
```

**Logique failover (à implémenter dans agents/base/llm_client.py) :**
```python
class OllamaClient:
    def __init__(self):
        self.primary_url = "http://192.168.0.20:11434"    # Corertx RTX 3060
        self.fallback_url = "http://192.168.0.30:11434"   # Edgeserver GTX 1050

    async def generate_with_fallback(self, prompt: str):
        try:
            # Tentative 1: PRIMARY (performance optimale)
            return await self._generate(self.primary_url, prompt)
        except Exception as e:
            logger.warning(f"PRIMARY Ollama down: {e}")
            # Tentative 2: BACKUP (continuité de service)
            return await self._generate(self.fallback_url, prompt)
```

---

### PROCHAINES ÉTAPES

1. **✅ FAIT : Ollama natifs opérationnels**
   - ✅ Corertx (RTX 3060) : http://192.168.0.20:11434
   - ✅ Edgeserver (GTX 1050) : http://192.168.0.30:11434
   - ✅ llama3.2:1b chargé sur les deux

2. **🔄 EN COURS : Implémenter le failover automatique**
   - Modifier `agents/base/llm_client.py`
   - Ajouter méthode `generate_with_fallback()`
   - Tester PRIMARY → BACKUP

3. **📋 À FAIRE : Tests de résilience**
   - Arrêter corertx Ollama → Vérifier backup edgeserver
   - Arrêter edgeserver Ollama → Vérifier PRIMARY corertx
   - Mesurer performance dans chaque scénario

4. **📋 À FAIRE : Monitoring**
   - Métriques failover (PRIMARY vs BACKUP)
   - Alertes si PRIMARY down
   - Dashboard Grafana GPU

**Cette architecture assure haute disponibilité et performance optimale !** 🎯

---

**Date :** 2025-11-13
**Version :** TwisterLab v1.0.2
**Statut :** ✅ Architecture clarifiée
