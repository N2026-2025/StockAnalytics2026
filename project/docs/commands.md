# Commands

## Setup inicial

```bash
# 0. Clonar repositorio
git clone <repo-url>
cd "c:/stock analytics 2026/project"

# 1. Crear entorno e instalar dependencias
pip install -r requirements.txt

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Generar dataset de demo (opcional, para uso sin red)
python scripts/seed_demo.py
```

## Ejecutar la API

```bash
# Modo desarrollo con recarga automática
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O directamente con Python
python app/main.py
```

## Ejecutar tests

```bash
# Todos los tests con cobertura
pytest tests/ -v --cov=app --cov-report=term-missing

# Solo servicios (sin red)
pytest tests/ -v -k "not api"

# Solo un módulo
pytest tests/test_risk_engine.py -v
```

## Detener la API

- `Ctrl+C` en la consola de uvicorn.
- Puerto 8000 es el único puerto usado por el servidor de desarrollo.

## Documentación automática

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json