# Plan: Streamlit Demo sobre API FastAPI existente (Opción A)

## Objetivo

Crear una app Streamlit (`streamlit_app/app.py`) que **consume la API REST ya construida** (`/api/v1/*`) y expone 5 pestañas/paneles de visualización interactiva. Sirve como "ventana rápida" para demostrar el motor cuantitativo en entrevistas.

## Contexto verificado

- **Backend:** FastAPI corriendo en `project/app/main.py` (uvicorn puerto 8000).
- **Endpoints disponibles:** `/health`, `/assets/prices`, `/assets/prices/all`, `/assets/prices/crypto`, `/assets/correlation`, `/risk/var`, `/risk/expected-shortfall`, `/risk/drawdown`, `/stress`, `/monte-carlo`, `/portfolio/summary`, `/portfolio/metrics`.
- **Estructura actual:** sin `streamlit_app/` ni frontend; hay `docs/interview/` con PDF generado.

## Decisiones de diseño

1. **Arquitectura:** Streamlit = cliente HTTP; **no** importa `services/`. Usa `httpx` (async) o `requests` con timeout.
2. **Pestañas (5):**
   - **Dashboard** — health, últimos precios multi-asset/cripto, matriz de correlación (tabla + heatmap `st.dataframe` o `st.plotly_chart`).
   - **Riesgo** — sliders para `confianza` (0.90-0.99) y `start`; tablas VaR histórico/paramétrico, ES/CVaR, MDD.
   - **Estrés** — botón "Ejecutar escenarios"; tabla P&L por activo en los 4 escenarios.
   - **Monte Carlo** — inputs `n_scenarios` (100-50000), `dias` (1-30), `metodo` (gbm/bootstrap); muestra percentiles P&L, `prob_perdida`, gráfico histograma P&L total.
   - **Cartera** — pesos editables (data editor) o botón "Igual ponderada"; métricas Sharpe, Sortino, MDD, Calmar, retorno/vol anualizados.
3. **Configuración:** variable de entorno `API_BASE_URL` (default `http://localhost:8000/api/v1`).
4. **Caché cliente:** `@st.cache_data(ttl=60)` en llamadas a endpoints que no cambian rápido (precios, correlación).
5. **Manejo de errores:** muestra `st.error` con detail del 503/404; botón "Reintentar".
6. **Dependencias nuevas:** `streamlit>=1.35`, `httpx>=0.27`, `plotly>=5.20` (para heatmap/histograma). En `requirements-streamlit.txt` aparte (no tocar `requirements.txt` del runtime).
7. **Estructura de carpetas:**
   ```
   streamlit_app/
   ├── app.py              # punto de entrada
   ├── api_client.py       # httpx client + helpers
   ├── components/         # funciones de render por pestaña
   │   ├── dashboard.py
   │   ├── risk.py
   │   ├── stress.py
   │   ├── monte_carlo.py
   │   └── portfolio.py
   └── utils/
       └── formatting.py   # helpers de formateo (%, 4 decimales)
   ```
8. **Fullstack con SQLite:** **fuera de alcance** (el usuario solo pidió Streamlit como prototipo; fullstack = frontend real + DB + auth se haría en otro repositorio/plan).

## Tareas de implementación (ordenadas)

1. Crear `project/requirements-streamlit.txt` con `streamlit`, `httpx`, `plotly`, `pandas`.
2. Crear `project/streamlit_app/` con la estructura arriba.
3. Implementar `api_client.py`: `AsyncClient` base, funciones `get_prices`, `get_correlation`, `get_var`, `get_es`, `get_drawdown`, `get_stress`, `get_montecarlo`, `get_portfolio_summary`, `get_portfolio_metrics`, `health_check`.
4. Implementar cada `components/*.py` recibiendo `api_client` y renderizando UI + llamadas cacheadas.
5. Implementar `app.py`: `st.set_page_config`, sidebar con `API_BASE_URL`, pestañas (`st.tabs`), orquestación de componentes.
6. Añadir README corto en `streamlit_app/README.md` con:
   - Cómo levantar: `uvicorn app.main:app --port 8000` (terminal 1) + `streamlit run streamlit_app/app.py` (terminal 2).
   - Variables: `API_BASE_URL`.
   - Qué demuestra cada pestaña.
7. Probar end-to-end: levantar API, levantar Streamlit, navegar pestañas, verificar datos y errores 503 simulados.

## Validación

- `streamlit run streamlit_app/app.py` arranca sin errores.
- Todas las pestañas cargan datos reales de la API (health ok, precios, riesgo, estrés, MC, cartera).
- Cambiar `confianza`, `start`, `n_scenarios`, `pesos` actualiza resultados.
- Manejo grácil si API está caída (muestra error, no crashea Streamlit).
- Código formateado (black/ruff si existe config).

## Riesgos y mitigaciones

- **API no corriendo:** verificar health check al inicio y mostrar banner visible.
- **Timeouts en Monte Carlo (10k escenarios):** `httpx` timeout 60s; mostrar spinner.
- **CORS:** FastAPI ya permite `*` (verificar `main.py`); si no, añadir `CORSMiddleware`.
- **Plotly no renderiza en headless:** Streamlit incluye `kaleido` automáticamente; si falla, fallback a `st.bar_chart` / `st.dataframe`.

## Fuera de alcance

- Autenticación/usuarios.
- Base de datos (SQLite o Postgres).
- Despliegue (Docker, cloud).
- Tests automatizados de la UI (manual only).
- Modificaciones al backend FastAPI.

## Nota de ejecución

La implementación la realiza un agente con permisos de código (fuera del modo plan). Este plan es implementation-ready.