import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')
import traceback
from app.quant.data.ingestion import download_and_cache
from app.quant.data.universe import ASSETS
try:
    results = download_and_cache(tickers=["SPY"], start="2020-01-01", end="2024-01-01")
    for t, df in results.items():
        print(f"Ticker: {t}, rows: {len(df)}")
        print("columns:", df.columns.tolist())
        print("index.name:", df.index.name)
except Exception as e:
    traceback.print_exc()