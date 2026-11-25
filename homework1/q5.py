import yfinance as yf
import pandas as pd
import numpy as np

# 1. Configuración de parámetros y descarga de datos de Yahoo Finance
ticker_symbol = 'AMZN'
print(f"Descargando datos de ganancias e históricos para {ticker_symbol}...")
ticker_obj = yf.Ticker(ticker_symbol)

# Extraer fechas de reportes históricos de ganancias
earnings_dates = ticker_obj.get_earnings_dates(limit=30)

# Descargar el historial completo de precios diarios de cotización
prices = ticker_obj.history(start='2020-01-01', end='2026-08-01')

# 2. Calcular los retornos porcentuales de la ventana de 2 días (Secuencia de 3 días)
# Day 1: Cierre previo al anuncio, Day 2: Día del anuncio, Day 3: Reacción posterior
prices['2Day_Return'] = prices['Close'].shift(-1) / prices['Close'].shift(1) - 1

# Limpiar el índice de la tabla de ganancias para poder cruzarlo
earnings_dates = earnings_dates.dropna(subset=['Reported EPS', 'Surprise %'])
earnings_dates.index = pd.to_datetime(earnings_dates.index).tz_localize(None)
prices.index = pd.to_datetime(prices.index).tz_localize(None)

# 3. Alinear y cruzar ambas tablas mediante las fechas
combined = earnings_dates.join(prices[['2Day_Return']], how='inner')

# 4. Filtrar únicamente las sorpresas de ganancias que fueron positivas (> 0)
positive_surprises = combined[combined['Surprise %'] > 0]

# 5. Calcular la mediana de retornos y la matriz de correlación solicitada
median_return = positive_surprises['2Day_Return'].median() * 100
correlation_matrix = positive_surprises[['2Day_Return', 'Surprise %']].corr()

print("\n--- INFORME DE GANANCIAS (EARNINGS SURPRISE) AMZN ---")
print(f"Cantidad de sorpresas positivas detectadas: {len(positive_surprises)}")
print(f"Mediana del retorno de 2 días pos-anuncio: {median_return:.2f}%")
print("\nMatriz de correlación obtenida a través de pd.corr():")
print(correlation_matrix)

