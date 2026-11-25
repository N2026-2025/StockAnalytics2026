# Coding Standards

## Estilo

- Comentarios y docstrings en español.
- Type hints en todas las funciones públicas.
- Pydantic v2 para schemas de request/response.
- Logging estructurado en lugar de `print`.
- Manejo de excepciones con `HTTPException` en routers.

## Convenciones de nombres

- Módulos: `snake_case` (ej. `risk_engine.py`).
- Clases: `PascalCase` (ej. `MonteCarloSimulator`).
- Funciones/variables: `snake_case` (ej. `calcular_var_historico`).
- Constantes: `MAYUSCULAS` (ej. `VAR_CONFIDENCE`).

## Commits

- Mensajes en español, imperativo, cortos.
- Ejemplo: `feat: agregar endpoint de Monte Carlo con bootstrap`.

## Requisitos de calidad

- Sin `print` en código de producción (usar `logger`).
- Sin credenciales hardcodeadas.
- Toda función pública con docstring que describa parámetros y retorno.
- Tests para cada nuevo módulo en `services/`.