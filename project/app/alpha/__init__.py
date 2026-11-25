"""Paquete de Alpha Mining y Research Multimodal.

Bucle cerrado de investigación cuantitativa:

1. Ingestión de datos (dataset Zoomcamp `data.parquet` y documentos de texto).
2. Extracción de factores de sentimiento (determinista + gancho LLM opcional).
3. Generación de hipótesis de trading en código Python (estructura Opportunity/Thesis/Data/Test del Módulo 5).
4. Backtest automático sobre el dataset (Módulos 2 y 4 del Zoomcamp).
5. Filtro de overfitting (walk-forward con embargo, K-Fold purgado, Deflated Sharpe Ratio).

Integra con el motor cuantitativo existente (`risk_engine`, `portfolio`, `monte_carlo`).
"""
