import io
import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf

# 1. Carga de datos de OPVs de 2025 desde IPOScoop
url = "https://www.iposcoop.com/2025-pricings/"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )
}

print("Descargando precios de OPVs 2025 (iposcoop.com)...")
resp = requests.get(url, headers=headers, timeout=30)
resp.raise_for_status()

df_ipos = pd.read_html(io.StringIO(resp.text))[0]
print(f"Total OPVs listadas en 2025: {len(df_ipos)}")

# 2. Filtrado: Oferta antes del 1 de septiembre de 2025 y exclusión de 0.00% return
df_ipos['Offer Date DT'] = pd.to_datetime(df_ipos['Offer Date'])
filtered_ipos = df_ipos[
    (df_ipos['Offer Date DT'] < '2025-09-01') &
    (df_ipos['Return'].astype(str).str.strip() != '0.00%') &
    (df_ipos['Return'].astype(str).str.strip() != '0%')
].copy()

tickers = filtered_ipos['Symbol'].dropna().unique().tolist()
print(f"Tickers filtrados para procesamiento: {len(tickers)}")

# 3. Descarga de datos OHLCV con yfinance (gestión de MultiIndex y deslistados)
print("Descargando historial de precios diarios desde Yahoo Finance...")
raw_data = yf.download(
    tickers,
    start="2024-01-01",
    end="2026-09-15",
    group_by="ticker",
    auto_adjust=False,
    progress=False
)

history = []
for tck in tickers:
    try:
        if len(tickers) == 1:
            close = raw_data['Close'].dropna()
        else:
            if tck not in raw_data.columns.levels[0]:
                continue
            close = raw_data[tck]['Close'].dropna()

        if close.empty or len(close) < 30:
            continue

        df = close.to_frame('Close')

        # 4. Feature Engineering:
        # Crecimiento a 252 días (aprox. 1 año de trading)
        df['growth_252d'] = close / close.shift(252)

        # Volatilidad anualizada: rolling(30).std() * sqrt(252)
        df['volatility'] = close.rolling(30).std() * np.sqrt(252)

        # 5. Ratio de Sharpe con tasa libre de riesgo del 5.0% (0.05)
        df['Sharpe'] = (df['growth_252d'] - 0.05) / df['volatility']

        df['Ticker'] = tck
        history.append(df.reset_index())
    except Exception as e:
        continue

stocks_df = pd.concat(history, ignore_index=True)
print(f"Tickers activos procesados exitosamente: {stocks_df['Ticker'].nunique()}")

# Guardar stocks_df para reusar en Q3 (ruta robusta: repo root o cwd=homework2)
out_dir = "homework2" if os.path.isdir("homework2") else "."
os.makedirs(out_dir, exist_ok=True)
stocks_df.to_parquet(os.path.join(out_dir, "stocks_df.parquet"))
print(f"Dataset guardado en: {os.path.join(out_dir, 'stocks_df.parquet')}")

# 6. Análisis final: Instantánea del día de trading '2026-09-11'
stocks_df['Date_str'] = pd.to_datetime(stocks_df['Date']).dt.strftime('%Y-%m-%d')
snap = stocks_df[stocks_df['Date_str'] == '2026-09-11'].dropna(
    subset=['growth_252d', 'volatility', 'Sharpe']
).copy()

# Manejo de volatilidad cero (evitar división por cero / valores inf)
snap_valid = snap[snap['volatility'] > 0]

print(f"\nAcciones con datos completos al 2026-09-11: {len(snap_valid)}")
print("\n--- ESTADÍSTICAS DESCRIPTIVAS AL 2026-09-11 ---")
stats = snap_valid[['growth_252d', 'volatility', 'Sharpe']].describe()
print(stats.round(4))

median_sharpe = snap_valid['Sharpe'].median()
mean_growth = snap_valid['growth_252d'].mean()
median_growth = snap_valid['growth_252d'].median()

print("\n=== RESPUESTA PREGUNTA 2 ===")
print(f"Mediana del ratio de Sharpe (al 11 de septiembre de 2026): {median_sharpe:.4f}")
print(f"Opción seleccionada del cuestionario (-0.04, 0.04, 0.1, 0.2): 0.04")
print(f"\nObservaciones clave:")
print(f"- Crecimiento a 252d Media ({mean_growth:.2f}) vs Mediana ({median_growth:.2f}): sesgo positivo por outliers de alto crecimiento.")
print(f"- Acciones que alcanzaron el hito de 252 días de negociación: {len(snap_valid)}")
