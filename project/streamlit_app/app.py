"""App Streamlit: prototipo visual sobre la API FastAPI existente.

No reimplementa la lógica cuantitativa: consume los endpoints vía httpx.
Demuestra arquitectura cliente-servidor (REST API + UI separada).

Para correr:
    Terminal 1: uvicorn app.main:app --host 0.0.0.0 --port 8000
    Terminal 2: streamlit run streamlit_app/app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Streamlit agrega el directorio del script al sys.path; insertamos la raíz
# del proyecto para que "streamlit_app.*" sea importable en todos los modulos.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from streamlit_app.api_client import DEFAULT_BASE_URL, RiskApiClient
from streamlit_app.components.alpha import render as render_alpha
from streamlit_app.components.dashboard import render as render_dashboard
from streamlit_app.components.risk import render as render_risk
from streamlit_app.components.stress import render as render_stress
from streamlit_app.components.monte_carlo import render as render_monte_carlo
from streamlit_app.components.portfolio import render as render_portfolio



def _init_client() -> RiskApiClient:
    base_url = os.getenv("API_BASE_URL", DEFAULT_BASE_URL)
    return RiskApiClient(base_url=base_url)


def main() -> None:
    st.set_page_config(
        page_title="Risk Analytics & Multi-Asset Argentina API",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Risk Analytics & Multi-Asset Argentina API")
    st.markdown(
        "Prototipo visual que consume la **API REST FastAPI** (puerto 8000). "
        "La lógica cuantitativa vive en el backend; esta app solo muestra resultados."
    )

    with st.sidebar:
        st.subheader("Configuración")
        base_url = st.text_input("API_BASE_URL", value=DEFAULT_BASE_URL, key="api_base_url")
        if st.button("Reconectar", use_container_width=True):
            st.rerun()
        st.divider()
        st.markdown(
            "**Arquitectura**\n"
            "- Backend: FastAPI + capas de servicios\n"
            "- Frontend: Streamlit (este app)\n"
            "- Comunicación: HTTP JSON"
        )

    api = _init_client()
    api.base_url = base_url

    tabs = st.tabs(
        [
            "📊 Dashboard",
            "⚠️ Riesgo",
            "🔥 Estrés",
            "🎲 Monte Carlo",
            "💼 Cartera",
            "📈 Alpha Mining",
        ]
    )

    with tabs[0]:
        render_dashboard(api)
    with tabs[1]:
        render_risk(api)
    with tabs[2]:
        render_stress(api)
    with tabs[3]:
        render_monte_carlo(api)
    with tabs[4]:
        render_portfolio(api)
    with tabs[5]:
        render_alpha(api)


if __name__ == "__main__":
    main()