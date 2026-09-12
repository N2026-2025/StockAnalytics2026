import yfinance as yf
import pandas as pd
import numpy as np

# 1. Descargar el historial diario del S&P 500 desde 1950
print("Descargando datos históricos del S&P 500...")
sp500 = yf.download('^GSPC', start='1950-01-01')
prices = sp500['Adj Close'].dropna()

# 2. Identificar puntos de máximos históricos secuenciales
ath_indices = []
max_so_far = -1

for i in range(len(prices)):
    if prices.iloc[i] > max_so_far:
        ath_indices.append(i)
        max_so_far = prices.iloc[i]

drawdowns = []
durations = []

# 3. Calcular caídas y duraciones entre picos máximos consecutivos
for k in range(len(ath_indices) - 1):
    idx1 = ath_indices[k]
    idx2 = ath_indices[k+1]
    
    if idx2 - idx1 > 1:
        segment = prices.iloc[idx1:idx2]
        high_price = prices.iloc[idx1]
        low_price = segment.min()
        low_date = segment.idxmin()
        high_date = prices.index[idx1]
        
        # Fórmula de Drawdown solicitada
        dd = (high_price - low_price) / high_price * 100
        # Duración en días calendario (Pico a Valle)
        days = (low_date - high_date).days
        
        drawdowns.append(dd)
        durations.append(days)

# 4. Crear DataFrame y filtrar correcciones >= 5%
df_corrections = pd.DataFrame({'drawdown': drawdowns, 'duration': durations})
df_filtered = df_corrections[df_corrections['drawdown'] >= 5]

# 5. Mostrar percentiles requeridos
print("\n--- RESULTADOS ESTADÍSTICOS DE CORRECCIONES ---")
print("Percentiles del Drawdown (%):")
print(df_filtered['drawdown'].quantile([0.25, 0.50, 0.75]))

print("\nPercentiles de Duración (Días calendario):")
print(df_filtered['duration'].quantile([0.25, 0.50, 0.75]))
