"""Endpoints de precios de activos multi-asset y cripto."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.api.deps import get_data_engine, validate_tickers
from app.schemas.asset import PriceResponse, CorrelationResponse
from app.utils.helpers import to_json_safe

router = APIRouter()


@router.get("/prices", response_model=PriceResponse, summary="Precios históricos multi-asset")
async def precios_multiasset(
    tickers: Optional[str] = Query(None, description="Tickers separados por coma (ej. ZS=F,BZ=F,YPF)"),
    start: str = Query("2020-01-01", description="Fecha de inicio YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="Fecha de fin YYYY-MM-DD"),
):
    """Devuelve precios de cierre ajustados para los activos solicitados."""
    try:
        ticker_list = validate_tickers([t.strip() for t in tickers.split(",")] if tickers else None)
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(ticker_list, start=start, end=end)

        if ticker_list[0] not in data.columns:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker_list[0]} no disponible en los datos descargados.")

        # Devolver el primer ticker solicitado como representación principal
        principal = ticker_list[0]
        precios = data[principal].dropna()
        return PriceResponse(
            ticker=principal,
            prices={str(idx.date()): round(float(val), 4) for idx, val in precios.items()},
            last_price=round(float(precios.iloc[-1]), 4),
            n_points=len(precios),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/prices/all", summary="Todos los precios multi-asset")
async def precios_todos(
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """Devuelve precios de todos los activos multi-asset por defecto."""
    try:
        from app.core.config import settings
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        return to_json_safe(data)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/prices/crypto", response_model=PriceResponse, summary="Precios cripto")
async def precios_cripto(
    tickers: Optional[str] = Query("BTC-USD,ETH-USD,SOL-USD,XRP-USD,BNB-USD", description="Tickers cripto separados por coma"),
    period: str = Query("3mo", description="Periodo yfinance (ej. 3mo, 1y)"),
):
    """Devuelve precios de cierre de criptomonedas."""
    try:
        ticker_list = validate_tickers([t.strip() for t in tickers.split(",")] if tickers else None)
        engine = get_data_engine()
        data = engine.descargar_cripto(ticker_list, period=period)

        principal = ticker_list[0]
        if principal not in data.columns:
            raise HTTPException(status_code=404, detail=f"Ticker cripto {principal} no disponible.")

        precios = data[principal].dropna()
        return PriceResponse(
            ticker=principal,
            prices={str(idx.date()): round(float(val), 4) for idx, val in precios.items()},
            last_price=round(float(precios.iloc[-1]), 4),
            n_points=len(precios),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/correlation", response_model=CorrelationResponse, summary="Matriz de correlación")
async def correlacion(
    start: str = Query("2020-01-01"),
    end: Optional[str] = Query(None),
):
    """Matriz de correlación de retornos diarios entre activos."""
    try:
        from app.core.config import settings
        engine = get_data_engine()
        data = engine.descargar_datos_multiasset(settings.default_tickers_list, start=start, end=end)
        retornos = data.pct_change().dropna()
        matriz = retornos.corr()
        return CorrelationResponse(
            matrix=to_json_safe(matriz),
            n_points=len(retornos),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))