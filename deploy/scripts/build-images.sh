#!/bin/bash
set -e

echo "=== Construction des images Docker ==="

# Image API
echo "Construction twisterlab-api:latest..."
docker build -t twisterlab-api:latest -f deploy/docker/Dockerfile.api .

# Image MCP
echo "Construction twisterlab-mcp:latest..."
docker build -t twisterlab-mcp:latest -f deploy/docker/Dockerfile.mcp-unified .

echo "Images construites avec succès"