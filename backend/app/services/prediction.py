import joblib
import pandas as pd
import os
import logging
import threading
from app.models import PredictionRequest

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Modelo cargado desde {self.model_path}")
            else:
                logger.warning(f"Modelo no encontrado en {self.model_path}")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")

    def predict(self, request: PredictionRequest) -> float:
        if self.model is None:
            self._load_model()
            if self.model is None:
                raise ValueError("El modelo no está disponible.")

        # Convertir request a DataFrame para el pipeline de sklearn
        data = pd.DataFrame([{
            'hour': request.hour,
            'day_of_week': request.day_of_week,
            'weather': request.weather,
            'zone': request.zone
        }])

        prediction = self.model.predict(data)[0]
        # Asegurar que esté entre 0 y 100
        return max(0.0, min(100.0, float(prediction)))


# Instancia singleton thread-safe
_prediction_service = None
_lock = threading.Lock()


def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is not None:
        return _prediction_service

    with _lock:
        # Double-check locking
        if _prediction_service is not None:
            return _prediction_service

        from app.core.config import settings
        model_path = settings.MODEL_PATH

        # Fallback para desarrollo local
        if not os.path.exists(model_path):
            local_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ml_pipeline', 'models', 'traffic_model_latest.joblib')
            )
            if os.path.exists(local_path):
                model_path = local_path

        _prediction_service = PredictionService(model_path)
        return _prediction_service