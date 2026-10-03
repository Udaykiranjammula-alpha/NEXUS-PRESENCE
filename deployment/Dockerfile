# NEXUS-PRESENCE Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy repository source
COPY . .

# Expose FastAPI HTTP/WebSocket port (8000) and UDP telemetry port (5005)
EXPOSE 8000 5005/udp

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
