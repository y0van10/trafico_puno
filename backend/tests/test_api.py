"""Tests de integración para la API de PunoTraffic AI."""


class TestHealthCheck:
    """Tests para el endpoint GET /api/v1/health."""

    def test_health_check_returns_200(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_check_contains_service_name(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["service"] == "PunoTraffic AI Backend"

    def test_health_check_reports_model_status(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "model_loaded" in data
        assert isinstance(data["model_loaded"], bool)

    def test_health_check_status_field(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] in ("healthy", "degraded")


class TestPredictTraffic:
    """Tests para el endpoint POST /api/v1/predict."""

    def test_predict_returns_200(self, client, valid_payload):
        response = client.post("/api/v1/predict", json=valid_payload)
        assert response.status_code == 200

    def test_predict_traffic_level_in_range(self, client, valid_payload):
        response = client.post("/api/v1/predict", json=valid_payload)
        data = response.json()
        assert "predicted_traffic_level" in data
        assert 0 <= data["predicted_traffic_level"] <= 100

    def test_predict_returns_model_version(self, client, valid_payload):
        response = client.post("/api/v1/predict", json=valid_payload)
        data = response.json()
        assert "model_version" in data
        assert data["model_version"] == "latest"

    def test_predict_returns_timestamp(self, client, valid_payload):
        response = client.post("/api/v1/predict", json=valid_payload)
        data = response.json()
        assert "timestamp" in data


class TestPredictValidation:
    """Tests de validación de inputs — deben retornar HTTP 422."""

    def test_invalid_weather_rejected(self, client):
        payload = {
            "hour": 10,
            "day_of_week": 2,
            "weather": "Tormenta",
            "zone": "Centro"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_invalid_zone_rejected(self, client):
        payload = {
            "hour": 10,
            "day_of_week": 2,
            "weather": "Soleado",
            "zone": "ZonaInventada"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_hour_out_of_range_rejected(self, client):
        payload = {
            "hour": 25,
            "day_of_week": 0,
            "weather": "Soleado",
            "zone": "Centro"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_negative_hour_rejected(self, client):
        payload = {
            "hour": -1,
            "day_of_week": 0,
            "weather": "Soleado",
            "zone": "Centro"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_day_of_week_out_of_range_rejected(self, client):
        payload = {
            "hour": 10,
            "day_of_week": 7,
            "weather": "Soleado",
            "zone": "Centro"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_missing_field_rejected(self, client):
        payload = {
            "hour": 10,
            "day_of_week": 2,
            "weather": "Soleado"
            # Falta "zone"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_empty_payload_rejected(self, client):
        response = client.post("/api/v1/predict", json={})
        assert response.status_code == 422


class TestPredictEdgeCases:
    """Tests de edge cases — valores límite que SÍ deben funcionar."""

    def test_midnight_hour_zero(self, client):
        payload = {
            "hour": 0,
            "day_of_week": 0,
            "weather": "Soleado",
            "zone": "Centro"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200
        assert 0 <= response.json()["predicted_traffic_level"] <= 100

    def test_last_hour_23(self, client):
        payload = {
            "hour": 23,
            "day_of_week": 6,
            "weather": "Nevada",
            "zone": "Terminal"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200
        assert 0 <= response.json()["predicted_traffic_level"] <= 100

    def test_sunday_rainy(self, client):
        payload = {
            "hour": 12,
            "day_of_week": 6,
            "weather": "Lluvioso",
            "zone": "Bellavista"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200

    def test_all_zones_valid(self, client):
        """Verifica que todas las zonas válidas producen predicciones."""
        zones = ["Centro", "Bellavista", "Salcedo", "Huaje", "Terminal"]
        for zone in zones:
            payload = {
                "hour": 10,
                "day_of_week": 2,
                "weather": "Soleado",
                "zone": zone
            }
            response = client.post("/api/v1/predict", json=payload)
            assert response.status_code == 200, f"Falló para zona: {zone}"

    def test_all_weather_conditions_valid(self, client):
        """Verifica que todas las condiciones climáticas producen predicciones."""
        weathers = ["Soleado", "Lluvioso", "Nublado", "Nevada"]
        for weather in weathers:
            payload = {
                "hour": 10,
                "day_of_week": 2,
                "weather": weather,
                "zone": "Centro"
            }
            response = client.post("/api/v1/predict", json=payload)
            assert response.status_code == 200, f"Falló para clima: {weather}"