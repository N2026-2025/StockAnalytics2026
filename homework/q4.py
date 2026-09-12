import yfinance as yf
import pandas as pd
import numpy as np

# 1. Descargar datos diarios históricos del S&P 500
print("Descargando historial del S&P 500...")
sp500 = yf.download('^GSPC', start='1950-01-01')
prices = sp500['Adj Close'].dropna()

# 2. Encontrar los índices de precios que marcan Máximos Históricos (ATH)
ath_indices = []
max_so_far = 0

for i in range(len(prices)):
    if prices.iloc[i] > max_so_far:
        ath_indices.append(i)
        max_so_far = prices.iloc[i]

drawdowns = []
durations = []

# 3. Analizar valles de precio entre pares sucesivos de ATHs
for k in range(len(ath_indices) - 1):
    idx1 = ath_indices[k]
    idx2 = ath_indices[k+1]
    
    # Evaluar segmentos si existen días intermedios
    if idx2 - idx1 > 1:
        segment = prices.iloc[idx1:idx2]
        high_price = prices.iloc[idx1]
        low_price = segment.min()
        
        low_date = segment.idxmin()
        high_date = prices.index[idx1]
        
        # Fórmulas requeridas por la consigna
        dd_pct = (high_price - low_price) / high_price * 100
        duration_days = (low_date - high_date).days
        
        drawdowns.append(dd_pct)
        durations.append(duration_days)

# 4. Crear DataFrame y filtrar el criterio de corrección significativa (>= 5%)
df_corrections = pd.DataFrame({'drawdown': drawdowns, 'duration': durations})
df_filtered = df_corrections[df_corrections['drawdown'] >= 5]

# 5. Imprimir resumen de cuantiles requeridos
print("\n=== PERCENTILES DE DRAWDOWN (MAGNITUD %) ===")
print(df_filtered['drawdown'].quantile([0.25, 0.50, 0.75]))

print("\n=== PERCENTILES DE DURACIÓN (DÍAS CALENDARIO) ===")
print(df_filtered['duration'].quantile([0.25, 0.50, 0.75]))
