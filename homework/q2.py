import yfinance as yf
import pandas as pd

# Lista de índices bursátiles solicitados
tickers = {
    '^GSPC': 'Estados Unidos', '000001.SS': 'China', '^HSI': 'Hong Kong',
    '^AXJO': 'Australia', '^NSEI': 'India', '^GSPTSE': 'Canadá',
    '^GDAXI': 'Alemania', '^FTSE': 'United Kingdom', '^N225': 'Japón',
    '^MXX': 'México', '^BVSP': 'Brasil'
}

# Descarga de datos diarios usando los parámetros recomendados del Hint
df_data = yf.download(list(tickers.keys()), start='2026-01-01', end='2026-08-21')['Adj Close']

# Obtener los precios de cierre del primer y último día disponible en el rango
precio_inicial = df_data.iloc[0]
precio_final = df_data.iloc[-1]

# Cálculo exacto del crecimiento porcentual YTD
retornos_ytd = ((precio_final - precio_inicial) / precio_inicial) * 100

# Separar el rendimiento del S&P 500 para comparar
sp500_ret = retornos_ytd['^GSPC']

print(f"Rendimiento S&P 500: {sp500_ret:.2f}%\n")
print("Índices que superaron a EE.UU. en 2026:")
for t, name in tickers.items():
    if t != '^GSPC' and retornos_ytd[t] > sp500_ret:
        print(f"- {name} ({t}): {retornos_ytd[t]:.2f}%")
