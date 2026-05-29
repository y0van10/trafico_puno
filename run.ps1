Write-Host "===================================================" -ForegroundColor Green
Write-Host "🚦 Iniciando PunoTraffic AI — Servidor Único" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

# Iniciar Servidor Unificado (FastAPI)
Write-Host "Iniciando servidor de FastAPI (Backend y Frontend unificados)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot\backend'; `$env:PYTHONPATH='./app'; `$env:MODEL_PATH='../ml_pipeline/models/traffic_model_latest.joblib'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`""

Write-Host "===================================================" -ForegroundColor Green
Write-Host "¡Servidor unificado iniciado exitosamente!" -ForegroundColor Green
Write-Host "- Interfaz Web: http://localhost:8000/" -ForegroundColor Yellow
Write-Host "- Documentación API: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green
