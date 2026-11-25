"""Schemas para endpoints de riesgo, estrés y Monte Carlo."""

from pydantic import BaseModel
from typing import Optional, List, Dict


class VaRResponse(BaseModel):
    metodo: str
    confianza: float
    var_por_activo: dict[str, dict[str, float]]


class ExpectedShortfallResponse(BaseModel):
    confianza: float
    es_por_activo: dict[str, float]


class StressScenarioResponse(BaseModel):
    escenario: str
    pnl_por_activo: dict[str, Optional[float]]
    pnl_cartera_igual: Optional[float]


class StressResponse(BaseModel):
    escenarios: dict[str, StressScenarioResponse]


class MonteCarloResponse(BaseModel):
    n_scenarios: int
    dias: int
    metodo: str
    resumen_pnl: dict[str, float]
    percentiles_precio_por_activo: dict[str, dict[str, Optional[float]]]


class PortfolioSummaryResponse(BaseModel):
    pesos: dict[str, float]
    metricas: dict[str, float]