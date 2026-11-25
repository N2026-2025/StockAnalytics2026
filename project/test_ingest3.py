import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.data.ingestion import download_and_cache
from app.quant.data.universe import ASSETS

# Test with first 3 assets
print("=== Test download_and_cache ASSETS[:3] ===")
results = download_and_cache(tickers=ASSETS[:3], start="2020-01-01", end="2024-01-01")
for t, df in results.items():
    print(f"Ticker: {t}, rows: {len(df)}, columns: {df.columns.tolist()}, index.name: {df.index.name}")
    # Verify read back
    from app.quant.data.storage import ParquetStorage
    storage = ParquetStorage()
    df2 = storage.read(t)
    print(f"  Read back columns: {df2.columns.tolist()}, index.name: {df2.index.name}")
print("\nDone.")