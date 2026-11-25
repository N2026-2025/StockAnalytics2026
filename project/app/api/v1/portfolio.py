"""Endpoints de métricas de cartera."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.api.deps import get_data_engine
from app.services.risk_engine import RiskEngine
from app.services.portfolio import Portfolio
from app.core.config import settings
from app.schemas.risk import PortfolioSummaryResponse
from app.utils.helpers import to_json_safe

router = APIRouter()


@router.get("/summary", response_model=PortfolioSummaryResponse, summary="Resumen de cartera igual ponderada")
async def resumen_cartera(
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """Métricas de una cartera igual ponderada (1/3 por activo)."""
    try:
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        retornos = RiskEngine.retornos_diarios(data)

        n = len(data.columns)
        pesos = {col: 1.0 / n for col in data.columns}

        port = Portfolio(retornos=retornos, precios=data)
        metricas = port.metricas(pesos=pesos)

        return PortfolioSummaryResponse(pesos=pesos, metricas=metricas)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/metrics", summary="Métricas detalladas de cartera")
async def metricas_cartera(
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
    pesos: Optional[str] = Query(None, description="Pesos JSON como string, ej. {\"ZS=F\":0.4,\"BZ=F\":0.3,\"YPF\":0.3}"),
):
    """Métricas de cartera con pesos personalizables."""
    try:
        import json

        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        retornos = RiskEngine.retornos_diarios(data)

        if pesos:
            pesos_dict = json.loads(pesos)
        else:
            n = len(data.columns)
            pesos_dict = {col: 1.0 / n for col in data.columns}

        port = Portfolio(retornos=retornos, precios=data)
        metricas = port.metricas(pesos=pesos_dict)

        return {"pesos": pesos_dict, "metricas": to_json_safe(metricas)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))