# Chapter 3 - Non-Functional Requirements

| ID | Requisito | Descripción | Métrica |
|----|-----------|-------------|---------|
| REQ-NONFUN-001 | Disponibilidad | La API debe responder en localhost:8000 sin errores 500 en endpoints básicos. | 100% health checks OK |
| REQ-NONFUN-002 | Latencia sincrónica | Endpoints de riesgo (VaR, estrés) con datos en caché deben responder < 2s. | < 2s (p95) |
| REQ-NONFUN-003 | Reproducibilidad | Monte Carlo y datos demo deben ser determinísticos con `RANDOM_SEED=42`. | Idénticos resultados con misma semilla |
| REQ-NONFUN-004 | Sin credenciales hardcodeadas | No hay API keys, passwords o secretos en el código. | 0 hallazgos en gitleaks |
| REQ-NONFUN-005 | Datos públicos | Todas las fuentes son de acceso público y riesgo legal cero (yfinance). | Auditoría de fuentes |
| REQ-NONFUN-006 | Tipado y schemas | Todas las respuestas de la API usan Pydantic schemas y OpenAPI. | 100% endpoints tipados |
| REQ-NONFUN-007 | Logging estructurado | Logs con timestamp, nivel, nombre de módulo y mensaje. | Logs en stdout |
| REQ-NONFUN-008 | Manejo de errores | Respuestas HTTP apropiadas (404, 422, 503) con cuerpo JSON descriptivo. | Pruebas de error |
| REQ-NONFUN-009 | Test coverage | Cobertura de tests unitarios sobre servicios de riesgo > 80%. | pytest-cov >= 80% |
| REQ-NONFUN-010 | Documentación | README, OpenAPI, y docs de requisitos completos. | Revisión de revisor en < 10 min |