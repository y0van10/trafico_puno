@echo off
echo ===================================================
echo 🚦 Iniciando PunoTraffic AI — Servidor Único FastAPI
echo ===================================================

:: Iniciar el backend y frontend unificados en una nueva ventana de consola
echo Iniciando servidor web de FastAPI en puerto 8000...
start cmd /k "cd backend && set PYTHONPATH=./app && set MODEL_PATH=../ml_pipeline/models/traffic_model_latest.joblib && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo ===================================================
echo ¡Aplicación unificada iniciada exitosamente!
echo - Accede a la interfaz web en: http://localhost:8000/
echo - Documentación interactiva API: http://localhost:8000/docs
echo ===================================================
pause
