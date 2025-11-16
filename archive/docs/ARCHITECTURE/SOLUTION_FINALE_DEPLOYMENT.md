# SOLUTION FINALE - Construction sur edgeserver

## RESUME DU PROBLEME

- Image `twisterlab-api:latest` doit etre Linux
- Docker Desktop Windows ne peut pas construire d'images Linux pour Swarm
- WSL ne fonctionne pas correctement avec Docker

## SOLUTION: CONSTRUIRE DIRECTEMENT SUR EDGESERVER

### ETAPE 1: Preparer l'archive

```powershell
# Dans PowerShell sur CoreServer-RTX
cd C:\TwisterLab

# Creer l'archive avec les fichiers necessaires uniquement
$files = @("Dockerfile.api", "requirements.txt", "pyproject.toml", "docker-compose.production.yml")
New-Item -ItemType Directory -Force -Path "deploy"
Copy-Item -Path $files -Destination "deploy/"
Copy-Item -Path "api" -Destination "deploy/" -Recurse -Force
Copy-Item -Path "agents" -Destination "deploy/" -Recurse -Force

# Compresser
Compress-Archive -Path "deploy\*" -DestinationPath "twisterlab-deploy.zip" -Force

# Verifier
Get-Item twisterlab-deploy.zip
```

### ETAPE 2: Transferer vers edgeserver

**Methode A - SCP (si SSH configure)**:
```powershell
scp twisterlab-deploy.zip administrator@edgeserver.twisterlab.local:/tmp/
```

**Methode B - Partage reseau**:
```powershell
# Copier vers partage reseau
Copy-Item twisterlab-deploy.zip \\edgeserver.twisterlab.local\c$\temp\
```

**Methode C - WinSCP/FileZilla**: Interface graphique

### ETAPE 3: Se connecter a edgeserver

```powershell
ssh administrator@edgeserver.twisterlab.local
```

### ETAPE 4: Sur edgeserver, construire et deployer

```bash
# Se positionner
cd /tmp

# Extraire
unzip -o twisterlab-deploy.zip

# Construire l'image (CETTE FOIS CA MARCHERA - c'est Linux!)
docker build -t twisterlab-api:latest -f Dockerfile.api .

# Verifier que l'image est creee
docker images | grep twisterlab-api

# IMPORTANT: Redployer le stack complet
docker stack deploy -c docker-compose.production.yml twisterlab_prod

# Attendre quelques secondes
sleep 10

# Verifier les services
docker service ls
docker service ps twisterlab_prod_api
docker service ps twisterlab_prod_webui
```

### ETAPE 5: Verification finale

Sur **CoreServer-RTX** (Windows):

```powershell
# Verifier tous les services
docker service ls

# Valider le systeme
.\validate_docker_simple.ps1

# Tester l'API
curl http://edgeserver.twisterlab.local:8000/health
```

## SCRIPT AUTOMATISE (si SSH fonctionne)

```powershell
# Preparer
cd C:\TwisterLab
$files = @("Dockerfile.api", "requirements.txt", "pyproject.toml", "docker-compose.production.yml")
New-Item -ItemType Directory -Force -Path "deploy" | Out-Null
Copy-Item -Path $files -Destination "deploy/"
Copy-Item -Path "api" -Destination "deploy/" -Recurse -Force
Copy-Item -Path "agents" -Destination "deploy/" -Recurse -Force
Compress-Archive -Path "deploy\*" -DestinationPath "twisterlab-deploy.zip" -Force

# Transferer
scp twisterlab-deploy.zip administrator@edgeserver.twisterlab.local:/tmp/

# Construire et deployer
ssh administrator@edgeserver.twisterlab.local "cd /tmp && unzip -o twisterlab-deploy.zip && docker build -t twisterlab-api:latest -f Dockerfile.api . && docker stack deploy -c docker-compose.production.yml twisterlab_prod"

# Verifier
Start-Sleep -Seconds 15
docker service ls
.\validate_docker_simple.ps1
```

## RESULTATS ATTENDUS

Apres execution:

```
twisterlab_prod_api          1/1     <- DOIT ETRE 1/1 (pas 0/1)
twisterlab_prod_webui        1/1     <- DOIT ETRE 1/1 (pas pending)
```

Validation: **100% de reussite** avec `.\validate_docker_simple.ps1`

## DEPANNAGE

### Probleme: SSH ne fonctionne pas

**Solution**: Utiliser la methode manuelle (copie reseau + connexion RDP)

### Probleme: "No such image" persiste

**Cause**: Image pas construite sur edgeserver
**Solution**: Verifier que vous etes bien connecte a edgeserver quand vous executez `docker build`

```bash
# Sur edgeserver, verifier
hostname  # Doit afficher "edgeserver"
docker images  # Doit lister twisterlab-api:latest
```

### Probleme: Contrainte de placement

**Verifier**: La contrainte WebUI doit etre `node.labels.os == linux` (PAS `node.role == worker`)

```bash
# Sur n'importe quel noeud manager
docker service inspect twisterlab_prod_webui --format '{{json .Spec.TaskTemplate.Placement}}'
```

## FICHIERS CREES

- `twisterlab-deploy.zip` - Archive prete a deployer
- `deploy/` - Dossier temporaire (peut etre supprime apres)
