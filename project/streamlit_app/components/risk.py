"""Componente Streamlit: pestaña Riesgo (VaR, Expected Shortfall, Drawdown)."""

from __future__ import annotations

from datetime import date

import streamlit as st

from streamlit_app.api_client import ApiError, RiskApiClient
from streamlit_app.utils.formatting import fmt_float, fmt_percent


def render(api: RiskApiClient) -> None:
    st.header("Riesgo")

    col1, col2 = st.columns([2, 1])
    with col1:
        start = st.date_input("Fecha de inicio", value=date(2020, 1, 1))
    with col2:
        confianza = st.slider("Nivel de confianza", min_value=0.90, max_value=0.99, value=0.95, step=0.005)

    start_s = start.isoformat()
    end_s = date(2026, 8, 1).isoformat()

    if not st.button("Calcular riesgo", type="primary"):
        return

    try:
        var = api.var(confianza=confianza, start=start_s, end=end_s)
    except ApiError as exc:
        st.error(f"Error calculando VaR: {exc}")
        return

    st.subheader(f"Value at Risk ({fmt_percent(1 - confianza)} de confianza)")
    var_por = var.get("var_por_activo") or {}
    for metodo in ("historico", "parametrico"):
        data = var_por.get(metodo) if isinstance(var_por, dict) else None
        if data is None:
            continue
        df = pd_frame_from_asset_map(data)
        if df is not None and not df.empty:
            st.markdown(f"**VaR {metodo}**")
            st.dataframe(df, use_container_width=True)

    st.subheader("Expected Shortfall (CVaR)")
    try:
        es = api.expected_shortfall(confianza=confianza, start=start_s, end=end_s)
        es_por = es.get("es_por_activo") or {}
        df_es = pd_frame_from_asset_map(es_por, value_name="ES")
        if df_es is not None and not df_es.empty:
            st.dataframe(df_es, use_container_width=True)
    except ApiError as exc:
        st.error(f"Error calculando Expected Shortfall: {exc}")

    st.subheader("Maximum Drawdown")
    try:
        dd = api.drawdown(start=start_s, end=end_s)
        df_dd = pd_frame_from_asset_map(dd, value_name="MDD")
        if df_dd is not None and not df_dd.empty:
            st.dataframe(df_dd, use_container_width=True)
    except ApiError as exc:
        st.error(f"Error calculando drawdown: {exc}")


def pd_frame_from_asset_map(payload: dict, value_name: str = "valor") -> "object | None":
    """Convierte {activo: valor} a DataFrame."""
    import pandas as pd

    if not isinstance(payload, dict) or not payload:
        return None
    return pd.DataFrame({"activo": list(payload.keys()), value_name: list(payload.values())})
