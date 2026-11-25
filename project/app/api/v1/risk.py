"""Endpoints de cálculo de riesgo: VaR y Expected Shortfall."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.api.deps import get_data_engine
from app.services.risk_engine import RiskEngine
from app.core.config import settings
from app.schemas.risk import VaRResponse, ExpectedShortfallResponse
from app.utils.helpers import to_json_safe

router = APIRouter()


@router.get("/var", response_model=VaRResponse, summary="Value at Risk (histórico y paramétrico)")
async def calcular_var(
    confianza: float = Query(0.95, ge=0.50, le=0.999, description="Nivel de confianza"),
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """Devuelve VaR histórico y paramétrico al nivel de confianza indicado."""
    try:
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        retornos = RiskEngine.retornos_diarios(data)

        var_hist = RiskEngine.var_historico(retornos, confianza=confianza)
        var_param = RiskEngine.var_parametrico(retornos, confianza=confianza)

        return VaRResponse(
            metodo="historico_y_parametrico",
            confianza=confianza,
            var_por_activo={
                "historico": to_json_safe(var_hist),
                "parametrico": to_json_safe(var_param),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get(
    "/expected-shortfall",
    response_model=ExpectedShortfallResponse,
    summary="Expected Shortfall / CVaR",
)
async def calcular_es(
    confianza: float = Query(0.95, ge=0.50, le=0.999),
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """Devuelve Expected Shortfall (media de la cola inferior al VaR)."""
    try:
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        retornos = RiskEngine.retornos_diarios(data)

        es = RiskEngine.expected_shortfall(retornos, confianza=confianza)
        return ExpectedShortfallResponse(
            confianza=confianza,
            es_por_activo=to_json_safe(es),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/drawdown", summary="Maximum Drawdown por activo")
async def drawdown(
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """Devuelve el Maximum Drawdown histórico por activo."""
    try:
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        mdd = RiskEngine.max_drawdown(data)
        return to_json_safe(mdd)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))