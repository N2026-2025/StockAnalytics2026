# Chapter 1 - Project Overview

## Problema

El curso de Finanzas Quant contiene dos módulos con cobertura desigual:

1. **Risk analytics and financial risk modelling** (enfoque principal, baja cobertura original).
2. **Multi-asset and alternative-market applications** (aplicación sectorial, buena cobertura).

Este proyecto construye un **motor cuantitativo de riesgo de mercado** como REST API (FastAPI) que evalúa riesgos sobre una cartera expuesta a factores macro de Argentina, y añade criptoactivos como activos alternativos adicionales.

## Activos analizados

| Ticker | Descripción | Rol en la cartera |
|--------|-------------|-------------------|
| `ZS=F` | Futuros de Soja (Chicago) | Flujo de divisas comerciales del agro |
| `BZ=F` | Petróleo Brent | Factor energético y logístico global |
| `YPF` | YPF S.A. | Proxy de renta variable argentina y riesgo país |
| `BTC-USD` | Bitcoin | Criptoactivo de referencia |
| `ETH-USD` | Ethereum | Criptoactivo de contratos inteligentes |
| `SOL-USD`, `XRP-USD`, `BNB-USD` | Criptoactivos adicionales | Diversificación cripto |

## Módulos del curso integrados

- **Módulo 1 (Colab Introduction and Data Sources):** Descarga de datos con `yfinance`, FRED, web scraping, indicadores macro, yfinance Ticker API (patrón 2026).
- **Homework Q1-Q4 (resultados 2026):** Documentados en CLAUDE.md como contexto de dominio (S&P 500 additions, índices mundiales YTD, drawdowns, earnings surprise AMZN).

## Objetivo del entregable

Una API REST que exponga:

1. Descarga de precios multi-asset y cripto (`descargar_datos_multiasset`).
2. Cálculo de VaR histórico/paramétrico (95%) y Expected Shortfall.
3. Pruebas de estrés con escenarios macro argentinos (devaluación 25%, shocks soy/oil, crisis conjunta histórica).
4. Simulación de Monte Carlo de 10,000 escenarios (GBM y bootstrap).
5. Métricas de cartera (Sharpe, Sortino, Max Drawdown, Calmar).

Todo con datos de acceso público y riesgo legal cero (yfinance).