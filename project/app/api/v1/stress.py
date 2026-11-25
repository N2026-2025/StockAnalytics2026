"""Endpoints de pruebas de estrés con escenarios macro argentinos."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.api.deps import get_data_engine
from app.services.risk_engine import RiskEngine
from app.services.stress_testing import StressTesting
from app.core.config import settings
from app.schemas.risk import StressResponse, StressScenarioResponse
from app.utils.helpers import to_json_safe

router = APIRouter()


@router.get("", response_model=StressResponse, summary="Pruebas de estrés (escenarios macro ARG)")
async def stress_test(
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """
    Ejecuta todos los escenarios de estrés:
    - fx_devaluation_25pct: devaluación del 25% (tipo Argentina)
    - soy_shock_-15pct: caída de soja -15%
    - oil_shock_-20pct: caída de petróleo -20%
    - joint_crisis_historica: peor día histórico desde 2020
    """
    try:
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        retornos = RiskEngine.retornos_diarios(data)

        st = StressTesting(precios=data, retornos=retornos)
        resultados = st.ejecutar_todos()

        escenarios = {}
        for nombre, pnl_serie in resultados.items():
            escenarios[nombre] = StressScenarioResponse(
                escenario=nombre,
                pnl_por_activo=to_json_safe(pnl_serie),
                pnl_cartera_igual=st.pnl_cartera_igual(pnl_serie),
            )

        return StressResponse(escenarios=escenarios)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))