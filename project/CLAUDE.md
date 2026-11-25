# Contexto de Proyecto: Risk Analytics & Multi-Asset Argentina

## Estado Actual y Decisiones

Este proyecto es para la cohorte **2026**. Combina dos módulos del curso:

1. **Risk analytics and financial risk modelling** (Enfoque principal, baja cobertura original).
2. **Multi-asset and alternative-market applications** (Aplicación sectorial, buena cobertura).

Se ha desarrollado un **motor cuantitativo de riesgo de mercado** como **REST API (FastAPI)** para evaluar riesgos de mercado y realizar pruebas de estrés sobre una cartera expuesta a factores macro de Argentina, con integración de criptoactivos como activos alternativos adicionales.

## Arquitectura Implementada

### Capa API (FastAPI)
- `app/main.py` — Instancia FastAPI, health check, enrutador v1
- `app/api/v1/` — Routers: `health.py`, `assets.py`, `risk.py`, `stress.py`, `montecarlo.py`, `portfolio.py`
- `app/api/deps.py` — Dependencias (DataEngine singleton, validación de tickers)
- `app/schemas/` — Pydantic schemas: `common.py`, `asset.py`, `risk.py`
- `app/utils/helpers.py` — Conversión JSON-safe

### Capa de Servicios (Motor Quant)
- `app/services/data_engine.py` — `descargar_datos_multiasset()`, `descargar_cripto()`, caché CSV, fallback determinista (semilla 42)
- `app/services/risk_engine.py` — VaR histórico, VaR paramétrico, Expected Shortfall, Maximum Drawdown, volatilidad anualizada
- `app/services/stress_testing.py` — Escenarios: devaluación FX 25%, shock soja -15%, shock petróleo -20%, crisis conjunta histórica
- `app/services/monte_carlo.py` — GBM y bootstrap histórico, 10,000 escenarios, resumen de P&L
- `app/services/portfolio.py` — Cartera igual ponderada, Sharpe, Sortino, MDD, Calmar, VaR 95%, ES 95%

### Capa de Configuración
- `app/core/config.py` — Settings con pydantic-settings + `.env`
- `app/core/logging.py` — Logging estructurado

### Tests
- `tests/test_data_engine.py`, `test_risk_engine.py`, `test_stress_testing.py`, `test_monte_carlo.py`, `test_portfolio.py`, `test_api.py`
- `tests/conftest.py` — Fixtures sintéticas determinísticas

### Documentación
- `README.md` — Siguiendo patrón `aidev_example.md` (features, quick start, scoring map, criteria mapping, verification)
- `openapi.yaml` — Contrato OpenAPI 3.1.0 machine-readable
- `docs/requirements/` — Capítulos 1, 2, 3, 4, 11
- `docs/architecture.md`, `docs/coding_standards.md`, `docs/commands.md`, `docs/ai-workflow.md`, `docs/verification.md`
- `docs/criteria/` — Verification evidence plantillas
- `presentacion.ipynb` — Notebook narrativo para presentar
- `scripts/seed_demo.py` — Dataset determinístico sin red

## Activos del Portafolio

Se analizan tres activos clave de libre acceso (Riesgo legal cero):

- `ZS=F` (Futuros de Soja Chicago): Representa el flujo de divisas comerciales del agro.
- `BZ=F` (Petróleo Brent): Factor energético y de costos logísticos globales.
- `YPF` (YPF S.A.): Proxy de renta variable argentina y riesgo país.

Activos cripto adicionales (anexo): `BTC-USD`, `ETH-USD`, `SOL-USD`, `XRP-USD`, `BNB-USD`.

## Tareas del Módulo 1 ya Resueltas y Validadas (Resultados 2026)

- **Q1 (S&P 500 Additions):** Año con más adiciones desde 2020 fue **2025** (18 adiciones). Acciones con >20 años en el índice = **218**.
- **Q2 (World Indices YTD):** Solo **2** índices mundiales (Japón e India) superaron el YTD del S&P 500 en el tramo ene-ago 2026.
- **Q3 (Corrections):** Mediana del drawdown histórico de correcciones (>=5%) es **8.71%**, con una duración media de caída de **85 días**.
- **Q4 (Earnings Surprise - AMZN):** Mediana de retorno de 2 días pos-sorpresa positiva = **+2.45%** (Correlación moderada de ~0.38).

## Endpoints REST Implementados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/assets/prices` | Precios históricos multi-asset |
| GET | `/api/v1/assets/prices/crypto` | Precios cripto |
| GET | `/api/v1/assets/correlation` | Matriz de correlación |
| GET | `/api/v1/risk/var` | VaR histórico y paramétrico (95%) |
| GET | `/api/v1/risk/expected-shortfall` | Expected Shortfall / CVaR |
| GET | `/api/v1/risk/drawdown` | Maximum Drawdown |
| GET | `/api/v1/stress` | Pruebas de estrés (4 escenarios macro ARG) |
| GET | `/api/v1/monte-carlo` | Simulación Monte Carlo 10k escenarios |
| GET | `/api/v1/portfolio/summary` | Métricas cartera igual ponderada |
| GET | `/api/v1/portfolio/metrics` | Métricas con pesos personalizados |

## Ejecución Rápida

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
# Abrir http://localhost:8000/docs
```

## Reproducibilidad

- Semilla fija `RANDOM_SEED=42` en Monte Carlo y datos demo.
- Caché CSV en `data/cache/` para evitar llamadas repetidas a yfinance.
- Fallback determinista con datos sintéticos si la red no está disponible.
