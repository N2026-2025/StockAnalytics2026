import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.data.ingestion import download_and_cache
from app.quant.data.universe import ASSETS

# Test with single ticker first
print("=== Test single ticker SPY ===")
results = download_and_cache(tickers=["SPY"], start="2020-01-01", end="2024-01-01")
for t, df in results.items():
    print(f"Ticker: {t}")
    print(f"  rows: {len(df)}")
    print(f"  columns: {df.columns.tolist()}")
    print(f"  index name: {df.index.name}")
    # Try reading back
    from app.quant.data.storage import ParquetStorage
    storage = ParquetStorage()
    df2 = storage.read(t)
    print(f"  read back columns: {df2.columns.tolist()}")
    print(f"  read back index name: {df2.index.name}")
    print()

print("=== Test ASSETS[:3] ===")
results2 = download_and_cache(tickers=ASSETS[:3], start="2020-01-01", end="2024-01-01")
for t, df in results2.items():
    print(f"Ticker: {t}, rows: {len(df)}, columns: {df.columns.tolist()}, index name: {df.index.name}")