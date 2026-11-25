# Chapter 4 - Tech Stack

| Capa | Tecnología | Versión | Propósito |
|------|------------|---------|-----------|
| Lenguaje | Python | 3.10+ | Desarrollo del backend y motor quant |
| Web framework | FastAPI | >= 0.100.0 | API REST, validación Pydantic, OpenAPI automático |
| Servidor ASGI | Uvicorn | >= 0.23.0 | Ejecución de la API |
| Validación de datos | Pydantic | >= 2.0.0 | Schemas de request/response |
| Configuración | pydantic-settings | >= 2.0.0 | Carga de variables desde `.env` |
| Variables de entorno | python-dotenv | >= 1.0.0 | Carga de `.env` en desarrollo |
| Análisis de datos | pandas | >= 2.0.0 | DataFrames, retornos, correlaciones |
| Cálculo numérico | NumPy | >= 1.24.0 | Operaciones vectorizadas, Monte Carlo |
| Estadística | SciPy | >= 1.10.0 | Distribuciones, VaR paramétrico |
| Datos financieros | yfinance | >= 0.2.30 | Descarga de precios públicos |
| Visualización | Matplotlib | >= 3.7.0 | Gráficos para notebook de presentación |
| Testing | pytest | >= 7.0.0 | Tests unitarios e integración |
| Coverage | pytest-cov | >= 4.0.0 | Medición de cobertura de tests |
| Datos demo | Script interno | seed_demo.py | Dataset determinístico sin red |