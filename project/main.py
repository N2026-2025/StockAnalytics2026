#🟢 Proyecto 1: Multi-asset and alternative-market applications
import pandas as pd
import yfinance as yf

# 1. Definición de la canasta Multi-Asset (Soja, Petróleo y Energía Argentina)
activos_alternativos = {
    'ZS=F': 'Soja (Chicago)',
    'BZ=F': 'Petróleo Brent',
    'YPF': 'YPF S.A. (Argentina)'
}

print("--- PROYECTO: MULTI-ASSET APPLICATIONS ---")
print("Descargando precios históricos de activos alternativos...")

# Descarga de datos objetivos en formato DataFrame
precios = yf.download(list(activos_alternativos.keys()), start='2020-01-01', end='2026-08-01')['Adj Close']
precios.rename(columns=activos_alternativos, inplace=True)

# 2. Análisis del comportamiento cruzado (Matriz de correlación entre activos)
retornos = precios.pct_change().dropna()
matriz_correlacion = retornos.corr()

print("\nMatriz de relación entre los activos raros (Correlación):")
print(matriz_correlacion)
