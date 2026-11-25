# Chapter 2 - Functional Requirements

| ID | Requisito | Descripción | Prioridad |
|----|-----------|-------------|-----------|
| REQ-FUN-001 | Descarga multi-asset | Endpoint `GET /api/v1/assets/prices` que devuelve precios históricos de ZS=F, BZ=F, YPF (y cualquier ticker solicitado). | Alta |
| REQ-FUN-002 | Descarga cripto | Endpoint `GET /api/v1/assets/prices/crypto` que devuelve precios de BTC-USD, ETH-USD, SOL-USD, XRP-USD, BNB-USD. | Alta |
| REQ-FUN-003 | Matriz de correlación | Endpoint `GET /api/v1/assets/correlation` con matriz de correlación de retornos diarios. | Alta |
| REQ-FUN-004 | VaR histórico | Endpoint `GET /api/v1/risk/var` con VaR histórico al nivel de confianza configurable. | Alta |
| REQ-FUN-005 | VaR paramétrico | Mismo endpoint que REQ-FUN-004, incluye VaR paramétrico asumiendo normalidad. | Alta |
| REQ-FUN-006 | Expected Shortfall | Endpoint `GET /api/v1/risk/expected-shortfall` con CVaR al nivel de confianza indicado. | Alta |
| REQ-FUN-007 | Maximum Drawdown | Endpoint `GET /api/v1/risk/drawdown` con MDD por activo. | Media |
| REQ-FUN-008 | Stress test FX | Escenario de devaluación cambiaria del 25% (tipo Argentina). | Alta |
| REQ-FUN-009 | Stress test commodities | Escenarios de shock de soja (-15%) y petróleo (-20%). | Alta |
| REQ-FUN-010 | Stress test conjunta | Peor día histórico desde 2020 reaplicado sobre precios actuales. | Alta |
| REQ-FUN-011 | Monte Carlo | Endpoint `GET /api/v1/monte-carlo` con 10,000 escenarios (GBM o bootstrap). | Alta |
| REQ-FUN-012 | Métricas de cartera | Endpoint `GET /api/v1/portfolio/summary` con Sharpe, Sortino, MDD, Calmar, VaR 95%, ES 95%. | Alta |
| REQ-FUN-013 | Health check | Endpoint `GET /api/v1/health` y `GET /health`. | Alta |
| REQ-FUN-014 | Caché de datos | Almacenamiento local en CSV para evitar llamadas repetidas a yfinance. | Media |
| REQ-FUN-015 | Fallback determinista | Datos sintéticos con semilla fija si yfinance no está disponible. | Media |