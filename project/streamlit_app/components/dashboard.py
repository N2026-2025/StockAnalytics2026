"""Componente Streamlit: pestaña Dashboard (salud, precios, correlación)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from streamlit_app.api_client import ApiError, RiskApiClient


def render(api: RiskApiClient) -> None:
    st.header("Dashboard")

    try:
        health = api.health()
        st.success(f"API OK: status={health.get('status')} service={health.get('service')} version={health.get('version')}")
    except ApiError as exc:
        st.error(f"No se pudo conectar con la API: {exc}")
        st.info("Iniciá la API con: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        st.stop()

    st.subheader("Precios multi-asset (frame ancho: fechas x tickers)")
    try:
        prices = api.prices_all()
        df = _frame_from_all(prices)
        if df is not None and not df.empty:
            st.dataframe(df, width="stretch")
    except ApiError as exc:
        st.error(f"Error cargando precios multi-asset: {exc}")

    st.subheader("Precios cripto")
    try:
        crypto = api.crypto_prices()
        df_crypto = _frame_from_crypto(crypto)
        if df_crypto is not None and not df_crypto.empty:
            st.dataframe(df_crypto, width="stretch")
    except ApiError as exc:
        st.error(f"Error cargando precios cripto: {exc}")

    st.subheader("Correlación de retornos")
    try:
        corr = api.correlation()
        df_corr = _corr_frame(corr)
        if df_corr is not None:
            st.dataframe(df_corr, width="stretch")
    except ApiError as exc:
        st.error(f"Error calculando correlación: {exc}")


def _frame_from_all(payload: dict) -> pd.DataFrame | None:
    """Payload /assets/prices/all: {ticker: {fecha: precio}} -> DataFrame (fechas x tickers)."""
    if not isinstance(payload, dict):
        return None
    frames = []
    for ticker, series in payload.items():
        if isinstance(series, dict) and series:
            s = pd.Series(series, dtype=float)
            frames.append(pd.DataFrame({ticker: s.values}, index=s.index))
    if not frames:
        return None
    df = pd.concat(frames, axis=1)
    return df.sort_index(axis=0).sort_index(axis=1)
    # index = fechas, columns = tickers


def _frame_from_crypto(payload: dict) -> pd.DataFrame | None:
    """Payload /assets/prices/crypto: {ticker, prices, last_price, n_points} -> DataFrame ticker x fecha."""
    if not isinstance(payload, dict):
        return None
    prices = payload.get("prices") or {}
    ticker = payload.get("ticker") or "CRYPTO"
    if not isinstance(prices, dict) or not prices:
        return None
    s = pd.Series(prices, dtype=float)
    return pd.DataFrame({ticker: s.values}, index=s.index)


def _corr_frame(payload: dict) -> pd.DataFrame | None:
    """Payload /assets/correlation: {matriz, n_points} -> DataFrame ticker x ticker."""
    if not isinstance(payload, dict):
        return None
    matriz = payload.get("matrix")
    if matriz is None:
        return None
    rows = list(matriz.keys())
    cols = list(next(iter(matriz.values())).keys()) if matriz else rows
    data = [[float(matriz.get(r, {}).get(c, float("nan"))) for c in cols] for r in rows]
    return pd.DataFrame(data, index=rows, columns=cols)
