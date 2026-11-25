# Dashboard / API Verification

Generated after running the API locally. Pending execution.

| Check | Status | Evidence |
|-------|--------|----------|
| `/api/v1/health` returns 200 | pending | `curl http://localhost:8000/api/v1/health` |
| `/api/v1/risk/var` returns 200 | pending | `curl http://localhost:8000/api/v1/risk/var?confianza=0.95` |
| `/api/v1/stress` returns 200 | pending | `curl http://localhost:8000/api/v1/stress` |
| `/api/v1/monte-carlo` returns 200 | pending | `curl http://localhost:8000/api/v1/monte-carlo?n_scenarios=100` |
| `/api/v1/portfolio/summary` returns 200 | pending | `curl http://localhost:8000/api/v1/portfolio/summary` |
| Tests pass with coverage >= 80% | pending | `pytest tests/ --cov=app` |