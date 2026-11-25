import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.data.ingestion import download_and_cache
from app.quant.data.universe import ASSETS

# Test with first 3 assets, force refresh
print("=== Test download_and_cache ASSETS[:3] force_refresh=True ===")
results = download_and_cache(tickers=ASSETS[:3], start="2020-01-01", end="2024-01-01", force_refresh=True)
for t, df in results.items():
    print(f"Ticker: {t}, rows: {len(df)}, columns: {df.columns.tolist()}, index.name: {df.index.name}")
print("\nDone.")