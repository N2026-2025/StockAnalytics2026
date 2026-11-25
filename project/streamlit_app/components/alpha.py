"""Componente Streamlit: pestaña Alpha Mining (Fase 1).

Consume los endpoints de /api/v1/alpha y muestra el ranking de hipótesis
con métricas de riesgo y anti-overfitting.
"""

from __future__ import annotations

import streamlit as st

from streamlit_app.api_client import ApiError, RiskApiClient


def render(api: RiskApiClient) -> None:
    st.header("📈 Alpha Mining — Fase 1")
    st.markdown(
        "Generación automática de hipótesis de trading sobre el dataset del Zoomcamp. "
        "Cada hipótesis se backtea y se filtra con **Deflated Sharpe Ratio**, "
        "**PBO** (probabilidad de backtest overfitting) y **walk-forward**."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Ver catálogo de hipótesis", use_container_width=True):
            _show_catalog(api)
    with col2:
        if st.button("Ejecutar pipeline (3k filas)", use_container_width=True, key="run_small"):
            _run_pipeline(api, sample_rows=3000)
    with col3:
        if st.button("Ejecutar pipeline (10k filas)", use_container_width=True, key="run_medium"):
            _run_pipeline(api, sample_rows=10000)

    st.divider()
    st.info(
        "Los resultados se calculan sobre un submuestreo determinista del dataset "
        "para mantener la respuesta interactiva. El dataset completo (229k filas) "
        "requiere optimización de memoria (ver Phase 2)."
    )


def _show_catalog(api: RiskApiClient) -> None:
    try:
        data = api.get("/alpha/hypotheses")
        st.subheader(f"Catálogo: {data['n_hypotheses']} hipótesis")
        for h in data["hypotheses"]:
            with st.expander(f"**{h['name']}** (horizonte {h['horizon_days']}d)"):
                st.markdown(f"- **Alcance:** {h['scope']}")
                st.markdown(f"- **Tesis:** {h['thesis']}")
                st.markdown(f"- **Edge:** {h['edge']}")
                st.markdown(f"- **Datos:** {h['data_sources']}")
                st.markdown(f"- **Test:** `{h['test_code']}`")
                st.markdown(f"- **Riesgos:** {h['risks']}")
    except ApiError as exc:
        st.error(f"Error cargando catálogo: {exc}")


def _run_pipeline(api: RiskApiClient, sample_rows: int) -> None:
    try:
        with st.spinner(f"Ejecutando pipeline sobre {sample_rows} filas..."):
            data = api.post("/alpha/run", json={"sample_rows": sample_rows})
    except ApiError as exc:
        st.error(f"Error ejecutando pipeline: {exc}")
        return

    st.success(
        f"Dataset: {data['dataset_rows']} filas | "
        f"Hipótesis: {data['n_hypotheses']} | "
        f"Pasaron: {data['n_passed']} | "
        f"Fallaron: {data['n_failed']}"
    )

    if data["macro_sentiment"]:
        st.info(f"Sentimiento macro agregado: {data['macro_sentiment']:.4f}")

    if not data["rankings"]:
        st.warning("Ninguna hipótesis generó operaciones suficientes.")
        return

    # Tabla de ranking
    df = _build_ranking_df(data["rankings"])
    st.subheader("Ranking (ordenado por Sharpe anualizado)")
    st.dataframe(df, width="stretch", hide_index=True)

    # Detalle de cada hipótesis
    st.subheader("Detalles de overfitting")
    for r in data["rankings"]:
        status = "✅ Pasa" if r["passes_filter"] else "❌ Falla"
        with st.expander(f"**{r['hypothesis']}** — Sharpe={r['sharpe_annualized']:.3f} {status}"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Sharpe anualizado", f"{r['sharpe_annualized']:.3f}")
            with col2:
                st.metric("CAGR", f"{r['cagr']:.4%}")
            with col3:
                st.metric("Win rate", f"{r['win_rate']:.2%}")
            with col4:
                st.metric("Max Drawdown", f"{r['max_drawdown']:.2%}")
            st.markdown(f"**Operaciones:** {r['n_trades']} | **Período:** {r['start_date']} → {r['end_date']}")
            st.markdown(f"**Deflated Sharpe:** {r['deflated_sharpe']:.3f} | **PBO:** {r['pbo']:.3f}")


def _build_ranking_df(rows: list[dict]):
    """Convierte la respuesta del pipeline en un DataFrame legible."""
    df_rows = []
    for r in rows:
        df_rows.append({
            "Hipótesis": r["hypothesis"],
            "Sharpe": f"{r['sharpe_annualized']:.3f}",
            "CAGR": f"{r['cagr']:.2%}",
            "Win Rate": f"{r['win_rate']:.1%}",
            "MDD": f"{r['max_drawdown']:.1%}",
            "Ops": r["n_trades"],
            "DSR": f"{r['deflated_sharpe']:.3f}",
            "PBO": f"{r['pbo']:.3f}",
            "Estado": "✅ Pasa" if r["passes_filter"] else "❌ Falla",
        })
    import pandas as pd
    return pd.DataFrame(df_rows)