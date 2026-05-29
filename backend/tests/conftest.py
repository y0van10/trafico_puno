"""Configuración de pytest para el backend de PunoTraffic AI."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Cliente de prueba reutilizable para todos los tests del módulo."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def valid_payload():
    """Payload de predicción válido para reutilizar en tests."""
    return {
        "hour": 8,
        "day_of_week": 0,
        "weather": "Soleado",
        "zone": "Centro"
    }
