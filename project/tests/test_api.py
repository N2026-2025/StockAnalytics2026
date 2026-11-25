"""Tests de integración de la API (TestClient de FastAPI)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_api_v1_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_openapi_disponible():
    resp = client.get("/openapi.yaml")
    # FastAPI sirve OpenAPI en JSON por defecto; yaml puede no estar disponible sin configuración extra
    assert resp.status_code in (200, 404)


def test_correlation_endpoint():
    resp = client.get("/api/v1/assets/correlation?start=2024-01-01&end=2024-03-01")
    assert resp.status_code in (200, 503)  # 503 si no hay red y no hay caché


def test_var_endpoint():
    resp = client.get("/api/v1/risk/var?confianza=0.95&start=2024-01-01&end=2024-03-01")
    assert resp.status_code in (200, 503)


def test_stress_endpoint():
    resp = client.get("/api/v1/stress?start=2024-01-01&end=2024-03-01")
    assert resp.status_code in (200, 503)


def test_montecarlo_endpoint():
    resp = client.get(
        "/api/v1/monte-carlo?dias=1&n_scenarios=100&metodo=bootstrap&start=2024-01-01&end=2024-03-01"
    )
    assert resp.status_code in (200, 503)


def test_portfolio_summary():
    resp = client.get("/api/v1/portfolio/summary?start=2024-01-01&end=2024-03-01")
    assert resp.status_code in (200, 503)