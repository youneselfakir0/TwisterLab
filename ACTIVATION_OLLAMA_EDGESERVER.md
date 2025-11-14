# Activation Ollama sur Edgeserver (GTX 1050)

## 🎯 Objectif
Activer Ollama avec GPU GTX 1050 sur edgeserver pour rendre TwisterLab vraiment autonome et distribué.

## 📋 Prérequis

### Vérification GPU
```bash
# GPU détecté
nvidia-smi
# NVIDIA GeForce GTX 1050, 2048 MiB ✅

# Driver installé
nvidia-smi --query-gpu=driver_version --format=csv,noheader
# 565.57.01 ✅
```

### Docker + NVIDIA Container Runtime
```bash
# Vérifier runtime nvidia
docker info | grep -i nvidia

# Si absent, installer :
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## 🚀 Étapes d'activation

### 1. Configurer Docker Swarm pour GPU

```bash
# Vérifier capacité GPU du nœud
docker node inspect edgeserver.twisterlab.local --format '{{json .Description.Resources}}' | jq
```

### 2. Mettre à jour docker-compose avec GPU

```yaml
# docker-compose.prod-with-ollama.yml
version: "3.8"

services:
  postgres:
    # ... config existante

  redis:
    # ... config existante

  api:
    # ... config existante
    environment:
      - OLLAMA_URL=http://ollama:11434          # Priorité LOCAL
      - OLLAMA_FALLBACK=http://192.168.0.20:11434  # Backup corertx

  ollama:
    image: ollama/ollama:latest
    ports:
      - target: 11434
        published: 11434
    volumes:
      - ollama_models:/root/.ollama
    networks:
      - twisterlab-prod-network
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    deploy:
      placement:
        constraints:
          - node.labels.gpu==true
      resources:
        reservations:
          generic_resources:
            - discrete_resource_spec:
                kind: 'NVIDIA-GPU'
                value: 1
      restart_policy:
        condition: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 120s

volumes:
  postgres_data:
  redis_data:
  ollama_models:
```

### 3. Ajouter label GPU au nœud

```bash
# Marquer edgeserver comme ayant GPU
docker node update --label-add gpu=true edgeserver.twisterlab.local
```

### 4. Déployer avec Ollama

```bash
cd /home/twister/TwisterLab
docker stack deploy -c docker-compose.prod-with-ollama.yml twisterlab

# Attendre démarrage
sleep 60

# Vérifier
docker service logs twisterlab_ollama
docker service ps twisterlab_ollama
```

### 5. Charger llama3.2:1b

```bash
# Dans container Ollama
docker exec -it $(docker ps -q -f name=twisterlab_ollama) ollama pull llama3.2:1b

# Vérifier
docker exec -it $(docker ps -q -f name=twisterlab_ollama) ollama list
```

### 6. Configurer Failover dans Code

```python
# agents/base/llm_client.py

class OllamaClient:
    def __init__(self):
        # PRIMARY : Local Ollama (edgeserver GTX 1050)
        self.primary_url = os.getenv("OLLAMA_URL", "http://ollama:11434")

        # FALLBACK : Corertx Ollama (RTX 3060)
        self.fallback_url = os.getenv("OLLAMA_FALLBACK", "http://192.168.0.20:11434")

        self.timeout = 30
        self.max_retries = 2

    async def generate_with_fallback(self, prompt: str, **kwargs):
        """Try primary first, fallback to secondary if fails"""

        # Tentative 1 : GPU local (latence minimale)
        try:
            logger.info("Using primary Ollama (edgeserver GTX 1050)")
            return await self._generate(self.primary_url, prompt, **kwargs)
        except Exception as e:
            logger.warning(f"Primary Ollama failed: {e}")

        # Tentative 2 : GPU distant (meilleure performance)
        try:
            logger.info("Falling back to corertx Ollama (RTX 3060)")
            return await self._generate(self.fallback_url, prompt, **kwargs)
        except Exception as e:
            logger.error(f"All Ollama endpoints failed: {e}")
            raise
```

## ✅ Tests de Validation

### Test 1 : Ollama Local Fonctionne
```bash
# Direct
curl http://192.168.0.30:11434/api/tags

# Depuis container API
docker exec $(docker ps -q -f name=twisterlab_api) curl http://ollama:11434/api/tags
```

### Test 2 : Agent Utilise GPU Local
```python
# Test classification
from agents.real.real_classifier_agent import RealClassifierAgent

agent = RealClassifierAgent()
result = await agent.classify_ticket("Mon ordinateur est lent")
# Devrait utiliser ollama:11434 (GTX 1050)
```

### Test 3 : Failover Fonctionne
```bash
# Arrêter Ollama local
docker service scale twisterlab_ollama=0

# Tester agent → devrait fallback vers corertx
# ...

# Redémarrer
docker service scale twisterlab_ollama=1
```

## 📊 Performance Attendue

| Scénario | Latence | GPU Utilisé | Performance |
|----------|---------|-------------|-------------|
| **Normal (local)** | ~10ms | GTX 1050 | 5-15s/requête |
| **Fallback (corertx)** | ~50ms | RTX 3060 | 2-7s/requête |
| **Charge élevée** | Variable | Les 2 GPU | Load balancing |

## 🎯 Résultat Final

```
✅ Edgeserver autonome avec Ollama + GPU GTX 1050
✅ Failover automatique vers corertx RTX 3060
✅ Latence minimale (LLM local)
✅ Haute disponibilité (2 GPU indépendants)
✅ Conforme à la vision TwisterLab distribuée
```

---

**Date** : 2025-11-13
**Status** : 📋 Plan validé, prêt pour exécution
