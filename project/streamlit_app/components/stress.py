"""Componente Streamlit: pestaña Estrés (4 escenarios de riesgo macro argentino)."""

from __future__ import annotations

import streamlit as st

from streamlit_app.api_client import ApiError, RiskApiClient
from streamlit_app.utils.formatting import fmt_percent


def render(api: RiskApiClient) -> None:
    st.header("Pruebas de Estrés (escenarios macro argentino)")

    with st.expander("ℹ️ Ver detalle de escenarios"):
        st.markdown(
            "Escenarios predefinidos con shocks porcentuales sobre activos vinculados a Argentina:\n"
            "- fx_devaluation_25pct: devaluación 25% + transmisión parcial a commodities\n"
            "- soy_shock_-15pct: caída soja -15% (impacto a YPF/BP)\n"
            "- oil_shock_-20pct: caída petróleo -20% (transmisión a soja/YPF)\n"
            "- joint_crisis_historica: peor día histórico desde 2020 reaplicado"
        )

    if st.button("Ejecutar todos los escenarios", type="primary"):
        try:
            result = api.stress()
            escenarios = result.get("escenarios") or {}
        except ApiError as exc:
            st.error(f"Error ejecutando estrés: {exc}")
            return

        if not escenarios:
            st.warning("No hay resultados de estrés disponibles.")
            return

        for nombre, info in escenarios.items():
            st.markdown(f"### {nombre}")
            pnl_por_activo = info.get("pnl_por_activo") or {}
            pnl_cartera = info.get("pnl_cartera_igual")

            # P&L por activo
            df_pnl = pd_frame_from_asset_map_optional(pnl_por_activo, "P&L")
            if df_pnl is not None and not df_pnl.empty:
                st.dataframe(df_pnl, use_container_width=True)

            # P&L cartera igual ponderada
            if pnl_cartera is not None:
                st.metric("P&L Cartera Igual Ponderada", value=fmt_float(pnl_cartera))
            else:
                st.write("P&L cartera: N/A")

            st.divider()


def pd_frame_from_asset_map_optional(payload: dict, col_name: str = "valor") -> "pd.DataFrame | None | bool":
    """Convierte {activo: valor} a DataFrame; devuelve False si vacío."""
    import pandas as pd

    if not isinstance(payload, dict) or not payload:
        return None
    return pd.DataFrame({"activo": list(payload.keys()), col_name: [float(v) if v is not None else float("nan") for v in payload.values()]})