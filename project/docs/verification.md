# Verification Evidence

## Verification records

| Record | File | Description |
|--------|------|-------------|
| Dashboard verification | `docs/criteria/dashboard_verification.md` | Pendiente de generación tras ejecutar tests |
| REQ coverage | `docs/criteria/req_coverage_verification.md` | Mapeo de requisitos a archivos de evidencia |

## Reviewer screenshots

Pendientes de capturar tras ejecutar la API y el notebook de presentación.

| File | Description |
|------|-------------|
| `docs/screenshots/health-check.png` | Respuesta de `/api/v1/health` |
| `docs/screenshots/var-endpoint.png` | Respuesta de `/api/v1/risk/var` |
| `docs/screenshots/stress-endpoint.png` | Respuesta de `/api/v1/stress` |
| `docs/screenshots/montecarlo-endpoint.png` | Respuesta de `/api/v1/monte-carlo` |

## Live verification in five minutes

1. `pip install -r requirements.txt`
2. `cp .env.example .env`
3. `uvicorn app.main:app --reload`
4. Abrir http://localhost:8000/docs
5. Probar `/api/v1/health`, `/api/v1/risk/var`, `/api/v1/stress`, `/api/v1/monte-carlo`
6. `Ctrl+C` para detener

## Local verification in five minutes

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```