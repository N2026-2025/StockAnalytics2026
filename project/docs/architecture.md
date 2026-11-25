# Architecture

## Diagrama de componentes (texto)

```
Cliente (curl / navegador / revisor)
        |
        v
+---------------------+
|   FastAPI (app)     |
|  - main.py          |
|  - uvicorn          |
+---------------------+
        |
        v
+---------------------+
|   API Routers v1    |
|  - health, assets   |
|  - risk, stress     |
|  - monte-carlo      |
|  - portfolio        |
+---------------------+
        |
        v
+---------------------+
|   Services Layer    |
|  - data_engine      |  yfinance + caché CSV + fallback demo
|  - risk_engine      |  VaR, ES, MDD, volatilidad
|  - stress_testing   |  Escenarios macro ARG
|  - monte_carlo      |  GBM + bootstrap 10k
|  - portfolio        |  Métricas de cartera
+---------------------+
        |
        v
+---------------------+
|   Config / Logging  |
|  - config.py (pydantic-settings)
|  - logging.py       |
+---------------------+
```

## Flujo de datos (ejemplo: VaR)

1. Cliente llama `GET /api/v1/risk/var?confianza=0.95`.
2. `risk.py` obtiene `DataEngine` vía dependencia `get_data_engine()`.
3. `data_engine.descargar_datos_multiasset()` devuelve precios (caché o descarga).
4. `risk_engine.retornos_diarios()` calcula retornos.
5. `risk_engine.var_historico()` y `var_parametrico()` calculan VaR.
6. Se devuelve JSON con Pydantic schema `VaRResponse`.

## Patrones de diseño

- **Singleton con caché:** `DataEngine` usa `@lru_cache` vía `get_data_engine()` y guarda CSV en `data/cache/`.
- **Dependency Injection:** FastAPI `Depends` para acceso a datos y configuración.
- **Fallback determinista:** Si yfinance falla, `data_engine` genera precios sintéticos con semilla fija.
- **Separación de capas:** API routers solo manejan HTTP; lógica cuantitativa vive en `services/`.