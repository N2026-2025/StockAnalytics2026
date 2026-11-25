# Chapter 11 - Testing Strategy

## Niveles de prueba

| Nivel | Archivo | Qué prueba | Datos |
|-------|---------|------------|-------|
| Unit | `tests/test_data_engine.py` | Generación de datos demo, reproducibilidad con semilla. | Sintéticos |
| Unit | `tests/test_risk_engine.py` | VaR histórico, VaR paramétrico, Expected Shortfall, MDD, volatilidad. | Sintéticos |
| Unit | `tests/test_stress_testing.py` | 4 escenarios de estrés, P&L por activo, P&L de cartera igual. | Sintéticos |
| Unit | `tests/test_monte_carlo.py` | GBM y bootstrap, forma de salida, resumen P&L, reproducibilidad. | Sintéticos |
| Unit | `tests/test_portfolio.py` | Retornos de cartera, métricas (Sharpe, Sortino, MDD, Calmar, VaR, ES). | Sintéticos |
| Integration | `tests/test_api.py` | TestClient de FastAPI: health, activos, riesgo, estrés, Monte Carlo, portfolio. | Datos reales o caché |

## Comandos de prueba

```bash
# Instalar dependencias de test
pip install -r requirements.txt

# Ejecutar todos los tests con cobertura
pytest tests/ -v --cov=app --cov-report=term-missing

# Ejecutar solo tests de servicios (sin red)
pytest tests/test_*.py -v -k "not api"
```

## Criterios de aceptación

- Todos los tests unitarios de servicios pasan sin necesidad de red (datos sintéticos).
- Los tests de API pueden devolver 503 si yfinance no está disponible (fallback a demo).
- Cobertura de líneas en `app/services` >= 80%.
- Los tests son determinísticos: misma semilla = mismos resultados.