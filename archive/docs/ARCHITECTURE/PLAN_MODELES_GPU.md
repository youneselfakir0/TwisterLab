# PLAN MODÈLES OLLAMA - AVEC GPU RTX 3060 (12GB VRAM)

## 🎯 SITUATION ACTUELLE

### Hardware disponible
- **edgeserver** (192.168.0.30) : GTX 1050 (2GB VRAM) - GPU non utilisé actuellement
- **core** (machine locale) : RTX 3060 (12GB VRAM) - Disponible

### Problème identifié
❌ **Ollama sur edgeserver n'utilise PAS le GPU** (mode CPU uniquement)
- Logs montrent `"total vram"="0 B"`
- Conteneur Docker n'a pas accès au GPU NVIDIA
- Besoin d'activer NVIDIA Container Runtime

---

## 📊 STRATÉGIE RECOMMANDÉE

### Option 1 : ACTIVER GPU SUR EDGESERVER (GTX 1050 - 2GB) 🔧
**Avantage** : Ollama déjà déployé, proche des agents
**Inconvénient** : GTX 1050 limitée (2GB VRAM seulement)

**Capacités GTX 1050 (2GB)** :
- ✅ Modèles 1B-3B (quantized Q4) : llama3.2:1b, gemma2:2b, phi3.5:3.8b
- ⚠️ Modèles 7B : Possible mais lent (offloading partiel)
- ❌ Modèles >7B : Impossible (pas assez de VRAM)

**Actions requises** :
```bash
# 1. Installer NVIDIA Container Toolkit sur edgeserver
ssh twister@192.168.0.30
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 2. Modifier docker-compose pour exposer GPU
# Ajouter dans twisterlab_ollama service:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]

# 3. Redéployer
docker stack deploy -c docker-compose.production.yml twisterlab
```

---

### Option 2 : DÉPLOYER OLLAMA SUR CORE (RTX 3060 - 12GB) 🚀 **RECOMMANDÉ**
**Avantage** : GPU puissant (6x plus de VRAM), modèles plus gros et rapides
**Inconvénient** : Latence réseau légère (agents sur edgeserver → Ollama sur core)

**Capacités RTX 3060 (12GB)** :
- ✅ Modèles 1B-7B : Ultra-rapide (100% GPU)
- ✅ Modèles 13B : Possible (quantized Q4)
- ✅ Modèles 30B+ : Possible (quantized Q2/Q3 avec offloading)
- 🚀 Multi-modèles en parallèle (3-4 modèles 3B simultanés)

**Architecture proposée** :
```
edgeserver (192.168.0.30)          core (machine locale)
┌─────────────────────────┐        ┌─────────────────────────┐
│ TwisterLab Agents       │        │ Ollama + RTX 3060       │
│ - ClassifierAgent   ────┼───────→│ - llama3.2:3b (2s→0.2s) │
│ - ResolverAgent     ────┼───────→│ - qwen2.5:7b (5s→0.5s)  │
│ - DesktopCommander  ────┼───────→│ - mistral:7b (5s→0.5s)  │
│ - MonitoringAgent   ────┼───────→│ - Modèles parallèles OK │
└─────────────────────────┘        └─────────────────────────┘
         API réseau (LAN)                  12GB VRAM
         Latence: ~5-10ms                  10x-20x plus rapide
```

**Actions requises** :
```powershell
# 1. Installer Ollama sur core (Windows)
# Télécharger depuis https://ollama.com/download
# ou via winget:
winget install Ollama.Ollama

# 2. Configurer pour écouter sur réseau (pas juste localhost)
# Créer/modifier variable d'environnement:
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'Machine')

# 3. Redémarrer service Ollama
Restart-Service Ollama

# 4. Tester depuis edgeserver
ssh twister@192.168.0.30 "curl -s http://CORE_IP:11434/api/tags"

# 5. Modifier agents pour pointer vers core
# Dans agents/config.py ou .env:
OLLAMA_URL=http://CORE_IP:11434
```

---

## 🎯 MODÈLES RECOMMANDÉS PAR OPTION

### Si Option 1 (GTX 1050 - 2GB VRAM)
**Modèles légers uniquement** :
```bash
ollama pull gemma2:2b-instruct-q4_K_M          # 1.6GB - MonitoringAgent (analyse rapide)
ollama pull phi3.5:3.8b-mini-instruct-q4_K_M   # 2.3GB - DesktopCommander (validation)
ollama pull qwen2.5:3b-instruct-q4_K_M         # 2GB - ClassifierAgent (IT/code)
```
⚠️ **1 seul modèle en mémoire à la fois** (2GB VRAM limite)

---

### Si Option 2 (RTX 3060 - 12GB VRAM) 🚀 **RECOMMANDÉ**
**Modèles optimisés pour performance ET qualité** :

#### Tier 1 - Production (toujours en VRAM)
```bash
# ClassifierAgent - Classification ultra-rapide
ollama pull qwen2.5:3b-instruct-q4_K_M         # 2GB - Spécialisé IT/code
ollama pull phi3.5:3.8b-mini-instruct-q4_K_M   # 2.3GB - Rapide et précis

# ResolverAgent - Solutions complexes
ollama pull qwen2.5:7b-instruct-q4_K_M         # 4.4GB - Excellent pour IT
ollama pull mistral:7b-instruct-v0.3-q4_K_M    # 4.1GB - Raisonnement avancé

# DesktopCommanderAgent - Validation sécurité
ollama pull gemma2:9b-instruct-q4_K_M          # 5.4GB - Précision maximale
```

**Total Tier 1** : ~11GB VRAM (tient dans 12GB avec 3-4 modèles actifs)

#### Tier 2 - Avancé (pour cas complexes)
```bash
# Raisonnement profond (tickets critiques)
ollama pull llama3.1:8b-instruct-q4_K_M        # 4.7GB - Meta latest
ollama pull deepseek-coder:6.7b-instruct-q4_K_M # 3.8GB - Code specialist

# Multi-modal (si besoin screenshots)
ollama pull llava:7b-v1.6-q4_K_M               # 4.7GB - Vision + Text
```

#### Tier 3 - Expérimental (modèles géants)
```bash
# Pour tests uniquement (nécessite offloading CPU)
ollama pull qwen2.5:14b-instruct-q4_K_M        # 8.3GB - Top qualité
ollama pull mixtral:8x7b-instruct-q3_K_M       # 26GB - MoE (partiel GPU)
```

---

## ⚡ COMPARAISON PERFORMANCE

### Temps de réponse estimés

| Agent | Requête | CPU (i5-6600K) | GTX 1050 (2GB) | RTX 3060 (12GB) |
|-------|---------|----------------|----------------|-----------------|
| **ClassifierAgent** | Analyser ticket (50 tokens) | 15-30s | 3-5s | 0.2-0.5s ⚡ |
| **ResolverAgent** | Générer solution (200 tokens) | 60-90s | 10-15s | 1-2s ⚡ |
| **DesktopCommander** | Valider commande (20 tokens) | 5-10s | 2-3s | 0.1-0.2s ⚡ |
| **MonitoringAgent** | Analyser métriques (100 tokens) | 30-45s | 5-8s | 0.5-1s ⚡ |

**Gain avec RTX 3060** : **10x-30x plus rapide** qu'en CPU !

---

## 🔧 CONFIGURATION OLLAMA POUR GPU

### Vérifier détection GPU
```bash
# Sur machine avec GPU
ollama run llama3.2:3b "test"
# Regarder les logs (doit afficher GPU utilization)

# Ou vérifier manuellement
nvidia-smi -l 1  # Monitoring en temps réel pendant requête
```

### Variables d'environnement optimales (RTX 3060)
```bash
# Dans docker-compose ou service Ollama
environment:
  - OLLAMA_NUM_PARALLEL=4           # 4 requêtes parallèles (12GB VRAM)
  - OLLAMA_MAX_LOADED_MODELS=3      # 3 modèles en VRAM simultanément
  - OLLAMA_GPU_OVERHEAD=2048        # Réserver 2GB pour système
  - OLLAMA_FLASH_ATTENTION=true     # Optimisation mémoire
  - CUDA_VISIBLE_DEVICES=0          # Utiliser GPU 0
```

---

## 🎯 RECOMMANDATION FINALE

### 🥇 **Option 2 (RTX 3060 sur core)** - FORTEMENT RECOMMANDÉ

**Pourquoi** :
- ✅ 6x plus de VRAM (12GB vs 2GB)
- ✅ GPU moderne (Ampere vs Pascal)
- ✅ Peut charger 3-4 modèles simultanément
- ✅ Réponses 10x-30x plus rapides
- ✅ Peut gérer modèles 7B-13B sans problème
- ✅ Latence réseau négligeable sur LAN (~5-10ms)

**Prochaines étapes** :
1. Installer Ollama sur core (Windows)
2. Configurer pour écouter sur réseau (OLLAMA_HOST=0.0.0.0)
3. Pull les 5 modèles Tier 1 (~11GB total)
4. Modifier config agents pour pointer vers core
5. Tester workflow complet avec GPU

**Performance attendue** :
- Ticket classifié : < 1 seconde
- Solution générée : < 2 secondes
- Commande validée : < 0.5 seconde

**Le système deviendra quasiment instantané ! 🚀**

---

## 📝 ALTERNATIVE : HYBRID SETUP

Si tu veux utiliser **les deux GPUs** :

```
edgeserver (GTX 1050 - 2GB)     core (RTX 3060 - 12GB)
┌────────────────────────┐      ┌────────────────────────┐
│ Ollama #1 (léger)      │      │ Ollama #2 (puissant)   │
│ - gemma2:2b            │      │ - qwen2.5:7b           │
│ - phi3.5:3.8b          │      │ - mistral:7b           │
│                        │      │ - llama3.1:8b          │
│ Load balancing:        │      │ - gemma2:9b            │
│ - Requêtes simples     │      │ - Requêtes complexes   │
│ - Fallback si core     │      │ - Primary inference    │
└────────────────────────┘      └────────────────────────┘
```

Agents choisissent dynamiquement selon complexité de la requête.

---

**Quelle option préfères-tu ?**
1. Activer GTX 1050 sur edgeserver (modèles légers)
2. Déployer Ollama sur core avec RTX 3060 (modèles puissants) 🚀
3. Hybrid setup (les deux GPUs)
