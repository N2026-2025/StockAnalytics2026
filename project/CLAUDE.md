# Contexto de Proyecto: Risk Analytics & Multi-Asset Argentina (Cripto-analizador bursatil (cadena de IA)

## Estado Actual y Decisiones

Este proyecto es para la cohorte **2026**. Combina dos módulos del curso:

1. **Risk analytics and financial risk modelling** (Enfoque principal, baja cobertura original).
2. **Multi-asset and alternative-market applications** (Aplicación sectorial, buena cobertura).

El objetivo es desarrollar un motor cuantitativo en Python para evaluar riesgos de mercado y realizar pruebas de estrés (*Stress Testing*) sobre una cartera expuesta a factores macro de Argentina.

## Activos del Portafolio

Se analizan tres activos clave de libre acceso (Riesgo legal cero):

- `ZS=F` (Futuros de Soja Chicago): Representa el flujo de divisas comerciales del agro.
- `BZ=F` (Petróleo Brent): Factor energético y de costos logísticos globales.
- `YPF` (YPF S.A.): Proxy de renta variable argentina y riesgo país.

## Tareas del Módulo 1 ya Resueltas y Validadas (Resultados 2026)

- **Q1 (S&P 500 Additions):** Año con más adiciones desde 2020 fue **2025** (18 adiciones). Acciones con >20 años en el índice = **218**.
- **Q2 (World Indices YTD):** Solo **2** índices mundiales (Japón e India) superaron el YTD del S&P 500 en el tramo ene-ago 2026.
- **Q3 (Corrections):** Mediana del drawdown histórico de correcciones (>=5%) es **8.71%**, con una duración media de caída de **85 días**.
- **Q4 (Earnings Surprise - AMZN):** Mediana de retorno de 2 días pos-sorpresa positiva = **+2.45%** (Correlación moderada de ~0.38).

## Arquitectura Objetivo para Claude Code

- Implementar la ingeniería de datos en `descargar_datos_multiasset()` dentro de `main.py` mediante `yfinance`.
- Implementar el motor cuantitativo de riesgo en `ejecutar_motor_de_riesgo()` incluyendo: VaR Histórico/Paramétrico (95%), Pruebas de Estrés con escenarios macro argentinos (saltos cambiarios del 25%) y Simulación de Montecarlo de 10k escenarios.
