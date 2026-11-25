"""Script para generar un dataset determinístico de demo/reviewer.

Crea precios sintéticos para los activos multi-asset y cripto,
guardándolos en data/cache para que la API pueda usarlos sin red.
"""

from pathlib import Path
import pandas as pd
import numpy as np

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)
n = 252
dates = pd.date_range("2025-01-01", periods=n, freq="B")

# Precios multi-asset
ma_data = pd.DataFrame(index=dates)
for ticker, vol in [("ZS=F", 0.02), ("BZ=F", 0.025), ("YPF", 0.03)]:
    returns = np.random.normal(0.0004, vol, n)
    ma_data[ticker] = 100 * np.exp(np.cumsum(returns))

ma_data.to_csv(CACHE_DIR / "ZS=F_BZ=F_YPF_2025-01-01_latest.csv")
print(f"Guardado multi-asset: {len(ma_data)} filas")

# Precios cripto
crypto_data = pd.DataFrame(index=dates)
for ticker, vol in [("BTC-USD", 0.04), ("ETH-USD", 0.05), ("SOL-USD", 0.06), ("XRP-USD", 0.05), ("BNB-USD", 0.045)]:
    returns = np.random.normal(0.0003, vol, n)
    crypto_data[ticker] = 100 * np.exp(np.cumsum(returns))

crypto_data.to_csv(CACHE_DIR / "crypto_BTC-USD_ETH-USD_SOL-USD_XRP-USD_BNB-USD_3mo.csv")
print(f"Guardado cripto: {len(crypto_data)} filas")

print("Seed de demo completado en data/cache/")