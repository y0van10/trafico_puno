FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear usuario non-root
RUN useradd --create-home --shell /bin/bash appuser

# Copiar el código
COPY . .

# Variables de entorno
ENV API_URL=http://backend:8000/api/v1

EXPOSE 8501

# Cambiar a usuario non-root
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]