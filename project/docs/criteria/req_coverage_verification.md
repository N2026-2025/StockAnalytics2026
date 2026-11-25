# Requirements Coverage Verification

| REQ ID | Requirement | Evidence File |
|--------|-------------|---------------|
| REQ-FUN-001 | Descarga multi-asset | `app/api/v1/assets.py`, `app/services/data_engine.py` |
| REQ-FUN-002 | Descarga cripto | `app/api/v1/assets.py`, `app/services/data_engine.py` |
| REQ-FUN-003 | Matriz de correlación | `app/api/v1/assets.py` |
| REQ-FUN-004 | VaR histórico | `app/api/v1/risk.py`, `app/services/risk_engine.py` |
| REQ-FUN-005 | VaR paramétrico | `app/api/v1/risk.py`, `app/services/risk_engine.py` |
| REQ-FUN-006 | Expected Shortfall | `app/api/v1/risk.py`, `app/services/risk_engine.py` |
| REQ-FUN-007 | Maximum Drawdown | `app/api/v1/risk.py`, `app/services/risk_engine.py` |
| REQ-FUN-008 | Stress test FX | `app/api/v1/stress.py`, `app/services/stress_testing.py` |
| REQ-FUN-009 | Stress test commodities | `app/api/v1/stress.py`, `app/services/stress_testing.py` |
| REQ-FUN-010 | Stress test conjunta | `app/api/v1/stress.py`, `app/services/stress_testing.py` |
| REQ-FUN-011 | Monte Carlo | `app/api/v1/montecarlo.py`, `app/services/monte_carlo.py` |
| REQ-FUN-012 | Métricas de cartera | `app/api/v1/portfolio.py`, `app/services/portfolio.py` |
| REQ-FUN-013 | Health check | `app/api/v1/health.py`, `app/main.py` |
| REQ-FUN-014 | Caché de datos | `app/services/data_engine.py` |
| REQ-FUN-015 | Fallback determinista | `app/services/data_engine.py` |
| REQ-NONFUN-001 | Disponibilidad | `tests/test_api.py` |
| REQ-NONFUN-003 | Reproducibilidad | `tests/test_monte_carlo.py`, `scripts/seed_demo.py` |
| REQ-NONFUN-009 | Test coverage | `tests/`, `pytest-cov` |