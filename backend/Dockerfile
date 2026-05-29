# ---- Stage 1: Build ----
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Production ----
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias compiladas desde builder
COPY --from=builder /install /usr/local

# Crear usuario non-root
RUN useradd --create-home --shell /bin/bash appuser

# Copiar el código fuente
COPY ./app /app/app

# Variables de entorno
ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/models/traffic_model_latest.joblib

EXPOSE 8000

# Cambiar a usuario non-root
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]