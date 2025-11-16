# GUIDE DE DEPLOIEMENT MANUEL - TwisterLab sur edgeserver

## PROBLEME IDENTIFIE

L'image `twisterlab-api:latest` est une image **Linux** mais Docker Desktop sur Windows ne peut pas la construire correctement pour le Swarm.

**Solution**: Construire l'image **directement sur edgeserver** (noeud Linux).

---

## OPTION 1: DEPLOIEMENT AUTOMATIQUE (Recommande)

```powershell
# Execute le script automatique
.\deploy_to_edgeserver.ps1
```

**Pre-requis**:
- Acces SSH a edgeserver.twisterlab.local
- Commande `ssh` et `scp` disponibles (OpenSSH)

---

## OPTION 2: DEPLOIEMENT MANUEL (Si SSH ne fonctionne pas)

### Etape 1: Creer l'archive

```powershell
# Compresser les fichiers necessaires
Compress-Archive -Path Dockerfile.api,requirements.txt,pyproject.toml,docker-compose.production.yml,api,agents -DestinationPath twisterlab-deploy.zip -Force
```

### Etape 2: Transferer vers edgeserver

**Via reseau Windows**:
```powershell
# Copier vers partage reseau
Copy-Item twisterlab-deploy.zip \\edgeserver.twisterlab.local\c$\temp\
```

**Via SCP** (si OpenSSH installe):
```powershell
scp twisterlab-deploy.zip administrator@edgeserver.twisterlab.local:/tmp/
```

**Via WinSCP/FileZilla**: Interface graphique

### Etape 3: Se connecter a edgeserver

**Via SSH**:
```powershell
ssh administrator@edgeserver.twisterlab.local
```

**Via RDP/Console**: Ouvrir un terminal

### Etape 4: Sur edgeserver, construire et deployer

```bash
# Extraire l'archive
cd /tmp
unzip -o twisterlab-deploy.zip

# Construire l'image Docker
docker build -t twisterlab-api:latest -f Dockerfile.api .

# Verifier que l'image est creee
docker images | grep twisterlab-api

# Redeployer le stack
docker stack deploy -c docker-compose.production.yml twisterlab_prod

# Verifier les services
docker service ls
docker service ps twisterlab_prod_api
docker service ps twisterlab_prod_webui
```

---

## OPTION 3: UTILISER UN REGISTRE DOCKER (Production)

### Sur CoreServer-RTX (Windows)

```powershell
# 1. Installer un registre local (une seule fois)
docker run -d -p 5000:5000 --name registry registry:2

# 2. Construire pour Linux (buildx)
docker buildx create --use
docker buildx build --platform linux/amd64 -t localhost:5000/twisterlab-api:latest -f Dockerfile.api --push .
```

### Modifier docker-compose.production.yml

```yaml
# Ligne ~110, changer:
api:
  image: localhost:5000/twisterlab-api:latest  # Au lieu de twisterlab-api:latest
```

### Redeployer

```powershell
docker stack deploy -c docker-compose.production.yml twisterlab_prod
```

---

## VERIFICATION FINALE

Sur **n'importe quel noeud du Swarm**:

```powershell
# Etat des services
docker service ls

# Details API
docker service ps twisterlab_prod_api --no-trunc

# Details WebUI
docker service ps twisterlab_prod_webui --no-trunc

# Logs
docker service logs twisterlab_prod_api
docker service logs twisterlab_prod_webui

# Validation complete
.\validate_docker_simple.ps1
```

---

## RESULTATS ATTENDUS

Apres deploiement reussi:

```
NAME                                 REPLICAS
twisterlab_prod_api                  1/1       <- Doit etre 1/1
twisterlab_prod_webui                1/1       <- Doit etre 1/1
twisterlab-monitoring_grafana        1/1       <- Deja OK
twisterlab-monitoring_prometheus     1/1       <- Deja OK
```

**Validation**: `.\validate_docker_simple.ps1` doit afficher **100% de reussite**.

---

## DEPANNAGE

### Probleme: "No such image: twisterlab-api:latest"

**Cause**: Image pas construite sur edgeserver
**Solution**: Executer l'etape 4 sur edgeserver

### Probleme: "unsupported platform"

**Cause**: Service essaie de demarrer sur noeud Windows
**Solution**: Verifier que la contrainte est `node.labels.os == linux`

```bash
# Sur edgeserver
docker service inspect twisterlab_prod_api --format '{{json .Spec.TaskTemplate.Placement.Constraints}}'
```

### Probleme: Service en "Pending"

**Causes possibles**:
1. Contraintes non satisfaites
2. Ressources insuffisantes
3. Volume externe manquant

```bash
# Diagnostic
docker service ps twisterlab_prod_api --no-trunc
docker service ps twisterlab_prod_webui --no-trunc
```

---

## CONTACTS / AIDE

- Documentation complete: `DOCKER_ANALYSIS_REPORT.md`
- Validation rapide: `.\validate_docker_simple.ps1`
- Deploiement auto: `.\deploy_to_edgeserver.ps1`
