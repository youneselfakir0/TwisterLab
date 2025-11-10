# Dockerfile for TwisterLab Swarm IA Agents
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    asyncpg \
    redis \
    pydantic \
    python-multipart \
    httpx \
    structlog

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Start the FastAPI application
CMD ["python3", "entrypoint.py"]
