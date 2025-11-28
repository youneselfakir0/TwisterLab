#!/bin/bash
set -e

echo "=== Pinning Dependencies for Reproducible Builds ==="

# 1. Generate requirements.txt with exact versions
pip freeze > requirements.txt.pinned

# 2. Generate requirements-dev.txt (dev dependencies)
pip freeze | grep -E "(pytest|black|ruff|mypy|pre-commit)" > requirements-dev.txt.pinned

# 3. Create requirements.in (source of truth - unpinned)
cat > requirements.in <<EOF
# Core Framework
fastapi>=0.115.0
pydantic>=2.9.0
uvicorn[standard]>=0.32.0
starlette>=0.41.0

# Database
asyncpg>=0.29.0
sqlalchemy[asyncio]>=2.0.0
alembic>=1.13.0

# Communication
httpx>=0.27.0
websockets>=13.1
msgpack>=1.1.0

# AI/LLM
openai>=1.54.0
anthropic>=0.39.0

# Monitoring
prometheus-client>=0.21.0
opentelemetry-api>=1.27.0
opentelemetry-sdk>=1.27.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.0
pydantic-settings>=2.6.0
EOF

echo "✅ Created requirements.in (unpinned source)"
echo "✅ Created requirements.txt.pinned (exact versions)"
echo "✅ Created requirements-dev.txt.pinned (dev tools)"

# 4. Use pip-tools for better dependency resolution
pip install pip-tools

# Compile requirements.in → requirements.txt (with hashes for security)
pip-compile --generate-hashes --output-file=requirements.txt.pinned requirements.in
mv requirements.txt.pinned requirements.txt

echo "✅ Compiled requirements.txt with hashes for security"
