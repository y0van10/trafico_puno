from fastapi import APIRouter, HTTPException, Depends
from app.models import PredictionRequest, PredictionResponse
from app.services.prediction import get_prediction_service, PredictionService
import logging
import os
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=PredictionResponse)
async def predict_traffic(
    request: PredictionRequest,
    service: PredictionService = Depends(get_prediction_service)
):
    try:
        prediction = service.predict(request)
        return PredictionResponse(
            predicted_traffic_level=round(prediction, 2),
            model_version="latest"
        )
    except ValueError as ve:
        logger.error(f"Error de validación: {ve}")
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        logger.error(f"Error durante predicción: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/health")
async def health_check(
    service: PredictionService = Depends(get_prediction_service)
):
    model_loaded = service.model is not None
    status = "healthy" if model_loaded else "degraded"
    return {
        "status": status,
        "service": "PunoTraffic AI Backend",
        "model_loaded": model_loaded
    }


@router.get("/metrics-history")
async def get_metrics_history():
    """Obtiene el historial de métricas del modelo entrenado (MLOps)."""
    paths_to_try = [
        "../ml_pipeline/models/metrics_history.json",
        "ml_pipeline/models/metrics_history.json",
        "./ml_pipeline/models/metrics_history.json",
        "../../ml_pipeline/models/metrics_history.json"
    ]
    
    for path in paths_to_try:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al leer metrics_history.json en {abs_path}: {e}")
                raise HTTPException(status_code=500, detail="Error interno al leer archivo de métricas")
                
    logger.warning("No se encontró el archivo metrics_history.json en ninguna de las rutas intentadas.")
    return []