# 🚦 PunoTraffic AI - Arquitectura MLOps

Proyecto profesional de Machine Learning Operations (MLOps) diseñado para predecir el tráfico vehicular en la ciudad de Puno utilizando un modelo de XGBoost, servido a través de una API REST en FastAPI y consumido por una interfaz moderna en Streamlit.

## 🏗 Arquitectura del Sistema

La arquitectura está dividida en 3 componentes principales:

1.  **ML Pipeline (Entrenamiento):** Scripts para generación de datos sintéticos, preprocesamiento, entrenamiento (XGBoost), optimización de hiperparámetros (GridSearch) y versionado de modelos (.joblib).
2.  **Backend (FastAPI):** API REST robusta que carga el modelo en memoria (Singleton), expone el endpoint `/predict` y realiza validaciones de datos usando Pydantic.
3.  **Frontend (Streamlit):** Interfaz de usuario interactiva y amigable.

## 📂 Estructura del Proyecto

```text
pryecto2/
├── .github/workflows/       # GitHub Actions CI/CD Pipeline
├── backend/                 # API REST (FastAPI)
│   ├── app/
│   │   ├── api.py           # Rutas y Endpoints
│   │   ├── core/config.py   # Variables de entorno
│   │   ├── main.py          # Punto de entrada
│   │   ├── models.py        # Pydantic schemas
│   │   └── services/        # Lógica de predicción
│   ├── tests/               # Unit testing (Pytest)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Interfaz de Usuario (Streamlit)
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── ml_pipeline/             # Entrenamiento del Modelo
│   ├── data/                # Dataset generado
│   ├── models/              # Modelos versionados (joblib)
│   ├── generate_data.py
│   ├── retrain.py           # Pipeline de reentrenamiento
│   ├── train.py             # Entrenamiento y evaluación
│   └── requirements.txt
├── docker-compose.yml       # Orquestación de contenedores
├── .env                     # Variables de entorno globales
└── README.md                # Documentación
```

## 🚀 Despliegue Local (Docker Compose)

El proyecto está completamente dockerizado. Para ejecutarlo:

1.  Asegúrate de tener Docker y Docker Compose instalados.
2.  Clona el repositorio o ubícate en la carpeta raíz.
3.  Genera y entrena el modelo por primera vez (Requerido antes de levantar los contenedores):
    ```bash
    cd ml_pipeline
    pip install -r requirements.txt
    python train.py
    cd ..
    ```
4.  Levanta los servicios con Docker Compose:
    ```bash
    docker-compose up --build -d
    ```
5.  Accede a la aplicación:
    *   **Frontend (UI):** [http://localhost:8501](http://localhost:8501)
    *   **Backend (API Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Pruebas Unitarias

Para ejecutar los tests del backend de forma local:

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=./app pytest tests/
```

## 🔄 Integración Continua (CI/CD)

El proyecto cuenta con un archivo `.github/workflows/ci_cd.yml` que:
1. Instala dependencias.
2. Entrena el modelo para generar los artefactos necesarios.
3. Ejecuta las pruebas automatizadas (Pytest).
4. Prepara el entorno para un eventual despliegue y construcción de imágenes Docker (CD).

## 📊 Pipeline de Reentrenamiento

Para ejecutar un reentrenamiento manual del modelo con nuevos datos:
```bash
python ml_pipeline/retrain.py
```
*Este script simula el proceso de ingesta de nuevos datos, optimización y actualización del modelo "latest" usado por el Backend.*