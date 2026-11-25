"""Componente Streamlit: pestaña Cartera (métricas con pesos iguales o personalizados)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from streamlit_app.api_client import ApiError, RiskApiClient
from streamlit_app.utils.formatting import fmt_float, fmt_percent, style_metrics


DEFAULT_TICKERS = ["ZS=F", "BZ=F", "YPF"]


def render(api: RiskApiClient) -> None:
    st.header("Métricas de Cartera")

    with st.sidebar:
        st.subheader("Pesos de cartera")
        modo = st.radio("Modo", ["Igual ponderada", "Personalizado"], key="port_mode")

    start = st.date_input("Fecha de inicio", value=date(2020, 1, 1), key="port_start")
    start_s = start.isoformat()

    if modo == "Igual ponderada":
        if not st.button("Calcular métricas (igual ponderada)", type="primary", key="port_eq"):
            return
        try:
            result = api.portfolio_summary(start=start_s)
            _render_summary(result)
        except ApiError as exc:
            st.error(f"Error calculando cartera: {exc}")
        return

    # Modo personalizado
    st.subheader("Pesos por activo")
    pesos_df = st.data_editor(
        pd.DataFrame({"activo": DEFAULT_TICKERS, "peso": [1.0 / 3] * 3}),
        column_config={"peso": st.column_config.NumberColumn("Peso", min_value=0.0, max_value=1.0, step=0.01)},
        use_container_width=True,
        num_rows="dynamic",
        key="weights_editor",
    )

    if not st.button("Calcular métricas (personalizado)", type="primary", key="port_cust"):
        return

    pesos = {row["activo"]: float(row["peso"]) for _, row in pesos_df.iterrows()}
    try:
        result = api.portfolio_metrics(pesos=pesos, start=start_s)
        _render_summary(result)
    except ApiError as exc:
        st.error(f"Error calculando cartera: {exc}")


def _render_summary(result: dict) -> None:
    import pandas as pd

    # Respuesta portfolio_summary: {pesos, metricas}
    # Respuesta portfolio_metrics: {pesos, metricas} (api_client lo devuelve así)
    metricas = {}
    if isinstance(result, dict):
        metricas = result.get("metricas", {}) or result.get("pesos", {}).get("metricas", {}) or {}
    pesos = result.get("pesos") or {}

    if metricas:
        df_m = pd.DataFrame({"métrica": list(metricas.keys()), "valor": list(metricas.values())})
        st.subheader("Métricas")
        st.dataframe(df_m, use_container_width=True)

        # Mostrar también como tarjetas bonitas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Sharpe", fmt_float(metricas.get("sharpe", 0)))
            st.metric("Sortino", fmt_float(metricas.get("sortino", 0)))
        with col2:
            st.metric("Max Drawdown", fmt_percent(metricas.get("max_drawdown", 0)))
            st.metric("Calmar", fmt_float(metricas.get("calmar", 0)))
        with col3:
            st.metric("Retorno anualizado", fmt_percent(metricas.get("retorno_anualizado", 0)))
            st.metric("Vol. anualizada", fmt_percent(metricas.get("volatilidad_anualizada", 0)))
        with col4:
            st.metric("VaR 95% diario", fmt_percent(metricas.get("var_95_diario", 0)))
            st.metric("ES 95% diario", fmt_percent(metricas.get("expected_shortfall_95_diario", 0)))

    if pesos:
        st.subheader("Pesos utilizados")
        df_w = pd.DataFrame({"activo": list(pesos.keys()), "peso": list(pesos.values())})
        st.dataframe(df_w, use_container_width=True)