"""Componente Streamlit: pestaña Monte Carlo (GBM + bootstrap)."""

from __future__ import annotations

from datetime import date

import streamlit as st

from streamlit_app.api_client import ApiError, RiskApiClient
from streamlit_app.utils.formatting import fmt_float, fmt_percent, bar_chart


def render(api: RiskApiClient) -> None:
    st.header("Monte Carlo (GBM + Bootstrap)")

    col1, col2, col3 = st.columns(3)
    with col1:
        n_scenarios = st.number_input("N° escenarios", min_value=100, max_value=50000, value=10000, step=100)
    with col2:
        dias = st.number_input("Días horizonte", min_value=1, max_value=30, value=1)
    with col3:
        metodo = st.selectbox("Método", ["bootstrap", "gbm"])

    start = st.date_input("Fecha de inicio", value=date(2020, 1, 1), key="mc_start")
    start_s = start.isoformat()

    if st.button("Ejecutar simulación", type="primary"):
        with st.spinner("Simulando..."):
            try:
                result = api.monte_carlo(
                    n_scenarios=int(n_scenarios),
                    dias=int(dias),
                    metodo=metodo,
                    start=start_s,
                )
            except ApiError as exc:
                st.error(f"Error en Monte Carlo: {exc}")
                return

        _render_results(result)


def _render_results(result: dict) -> None:
    import pandas as pd

    resumen = result.get("resumen_pnl") or {}
    st.subheader("Resumen P&L total (percentiles)")

    if resumen:
        df_res = pd.DataFrame(
            [
                ("P1 (pérdida extrema)", resumen.get("p1_pnl")),
                ("P5 (VaR 95%)", resumen.get("p5_pnl")),
                ("P50 (mediana)", resumen.get("p50_pnl")),
                ("P95", resumen.get("p95_pnl")),
                ("P99 (ganancia extrema)", resumen.get("p99_pnl")),
                ("Prob. pérdida", f"{resumen.get('prob_perdida', 0):.2%}"),
                ("P&L esperado", resumen.get("expected_pnl")),
            ],
            columns=["Métrica", "Valor"],
        )
        st.dataframe(df_res, width="stretch")

        # Bar chart de percentiles principales
        pctls = ["p1_pnl", "p5_pnl", "p50_pnl", "p95_pnl", "p99_pnl"]
        vals = [float(resumen.get(p, 0)) for p in pctls]
        if vals:
            chart = bar_chart(
                pd.DataFrame({"percentil": pctls, "P&L": vals}),
                y_col="P&L",
                title="Percentiles de P&L (negativo = pérdida)",
            )
            st.altair_chart(chart, use_container_width=True)

    st.subheader("Percentiles de precio por activo")
    per_activo = result.get("percentiles_precio_por_activo") or {}
    if per_activo:
        rows = []
        for ticker, pct in per_activo.items():
            if isinstance(pct, dict):
                rows.append(
                    {
                        "activo": ticker,
                        "p1": pct.get("p1"),
                        "p5": pct.get("p5"),
                        "p50": pct.get("p50"),
                        "p95": pct.get("p95"),
                    }
                )
        if rows:
            df_p = pd.DataFrame(rows)
            st.dataframe(df_p, use_container_width=True)