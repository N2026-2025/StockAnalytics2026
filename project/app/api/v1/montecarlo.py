"""Endpoints de simulación de Monte Carlo (10k escenarios)."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.api.deps import get_data_engine
from app.services.risk_engine import RiskEngine
from app.services.monte_carlo import MonteCarloSimulator
from app.core.config import settings
from app.schemas.risk import MonteCarloResponse
from app.utils.helpers import to_json_safe

router = APIRouter()


@router.get("", response_model=MonteCarloResponse, summary="Simulación de Monte Carlo")
async def simulacion_montecarlo(
    dias: int = Query(1, ge=1, le=30, description="Días de horizonte"),
    n_scenarios: int = Query(settings.MONTE_CARLO_SCENARIOS, ge=100, le=100000),
    metodo: str = Query("bootstrap", description="gbm o bootstrap"),
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """
    Ejecuta simulación de Monte Carlo sobre la cartera multi-asset.

    - gbm: Geometric Brownian Motion
    - bootstrap: resampleo histórico de retornos observados
    """
    try:
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        retornos = RiskEngine.retornos_diarios(data)

        sim = MonteCarloSimulator(precios=data, retornos=retornos, seed=settings.RANDOM_SEED)

        if metodo.lower() == "gbm":
            precios_sim = sim.simular_gbm(days=dias, n_scenarios=n_scenarios)
            metodo_nombre = "gbm"
        else:
            precios_sim = sim.simular_bootstrap(days=dias, n_scenarios=n_scenarios)
            metodo_nombre = "bootstrap"

        precios_actuales = data.iloc[-1]
        resumen_pnl = sim.resumen_pnl(precios_sim, precios_actuales)

        # Percentiles de precio por activo para el reporte
        percentiles = {}
        for col in precios_sim.columns:
            s = precios_sim[col]
            percentiles[col] = {
                "p1": round(float(s.quantile(0.01)), 4),
                "p5": round(float(s.quantile(0.05)), 4),
                "p50": round(float(s.median()), 4),
                "p95": round(float(s.quantile(0.95)), 4),
            }

        return MonteCarloResponse(
            n_scenarios=n_scenarios,
            dias=dias,
            metodo=metodo_nombre,
            resumen_pnl=resumen_pnl,
            percentiles_precio_por_activo=percentiles,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))