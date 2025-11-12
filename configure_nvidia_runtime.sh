#!/bin/bash
# Configuration NVIDIA Runtime pour Docker

echo "Configuration NVIDIA Container Runtime..."

# Backup daemon.json
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup

# Ajouter nvidia runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Redémarrer Docker
sudo systemctl restart docker

# Vérifier
echo "Verification runtime NVIDIA..."
sudo docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

echo "Configuration terminee!"
