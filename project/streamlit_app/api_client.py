"""Cliente HTTP para consumir la API REST de Risk Analytics desde Streamlit.

Todas las funciones hablan con el backend FastAPI; no importan la logica
cuantitativa. El objetivo es demostrar arquitectura cliente-servidor.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx

DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
DEFAULT_TIMEOUT = float(os.getenv("API_TIMEOUT", "60"))


class ApiError(Exception):
    """Error de comunicacion con la API (red, timeout o respuesta no-2xx)."""


class RiskApiClient:
    """Cliente sincrono liviano sobre httpx para los endpoints v1."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.get(url, params=params, timeout=self.timeout)
        except httpx.RequestError as exc:
            raise ApiError(f"No se pudo conectar con la API en {url}: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except Exception:
                pass
            raise ApiError(f"HTTP {response.status_code} en {path}: {detail}")

        return response.json()

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        """GET genérico para endpoints no cubiertos por métodos específicos."""
        return self._get(path, params)

    def post(self, path: str, json: Optional[dict] = None) -> dict:
        """POST genérico para endpoints no cubiertos por métodos específicos."""
        url = f"{self.base_url}{path}"
        try:
            response = httpx.post(url, json=json, timeout=self.timeout)
        except httpx.RequestError as exc:
            raise ApiError(f"No se pudo conectar con la API en {url}: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except Exception:
                pass
            raise ApiError(f"HTTP {response.status_code} en {path}: {detail}")

        return response.json()

    def health(self) -> dict:
        return self._get("/health")

    def prices_all(self, start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"start": start}
        if end:
            params["end"] = end
        return self._get("/assets/prices/all", params)

    def prices(self, tickers: list[str], start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"tickers": ",".join(tickers), "start": start}
        if end:
            params["end"] = end
        return self._get("/assets/prices", params)

    def crypto_prices(self, tickers: Optional[list[str]] = None, period: str = "3mo") -> dict:
        params = {"period": period}
        if tickers:
            params["tickers"] = ",".join(tickers)
        return self._get("/assets/prices/crypto", params)

    def correlation(self, start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"start": start}
        if end:
            params["end"] = end
        return self._get("/assets/correlation", params)

    def var(self, confianza: float = 0.95, start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"confianza": confianza, "start": start}
        if end:
            params["end"] = end
        return self._get("/risk/var", params)

    def expected_shortfall(self, confianza: float = 0.95, start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"confianza": confianza, "start": start}
        if end:
            params["end"] = end
        return self._get("/risk/expected-shortfall", params)

    def drawdown(self, start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"start": start}
        if end:
            params["end"] = end
        return self._get("/risk/drawdown", params)

    def stress(self, start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"start": start}
        if end:
            params["end"] = end
        return self._get("/stress", params)

    def monte_carlo(
        self,
        n_scenarios: int = 10000,
        dias: int = 1,
        metodo: str = "bootstrap",
        start: str = "2020-01-01",
        end: Optional[str] = None,
    ) -> dict:
        params = {"n_scenarios": n_scenarios, "dias": dias, "metodo": metodo, "start": start}
        if end:
            params["end"] = end
        return self._get("/monte-carlo", params)

    def portfolio_summary(self, start: str = "2020-01-01", end: Optional[str] = None) -> dict:
        params = {"start": start}
        if end:
            params["end"] = end
        return self._get("/portfolio/summary", params)

    def portfolio_metrics(
        self, pesos: Optional[dict] = None, start: str = "2020-01-01", end: Optional[str] = None
    ) -> dict:
        import json

        params = {"start": start}
        if pesos:
            params["pesos"] = json.dumps(pesos)
        if end:
            params["end"] = end
        return self._get("/portfolio/metrics", params)
