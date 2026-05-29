from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Literal


class PredictionRequest(BaseModel):
    hour: int = Field(..., ge=0, le=23, description="Hora del día (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Día de la semana (0=Lunes, 6=Domingo)")
    weather: Literal["Soleado", "Lluvioso", "Nublado", "Nevada"] = Field(
        ..., description="Condición climática"
    )
    zone: Literal["Centro", "Bellavista", "Salcedo", "Huaje", "Terminal"] = Field(
        ..., description="Zona de Puno"
    )


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    predicted_traffic_level: float = Field(
        ..., ge=0, le=100, description="Nivel de tráfico predicho (0-100)"
    )
    model_version: str = Field(..., description="Versión del modelo utilizado")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )