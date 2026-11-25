import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.data.storage import ParquetStorage
import pandas as pd
import yfinance as yf

# Test with SPY
ticker = "SPY"
data = yf.download(ticker, start="2020-01-01", end="2024-01-01")["Close"]
print("Original data:")
print("  columns:", data.columns.tolist())
print("  index.name:", data.index.name)
print("  shape:", data.shape)

storage = ParquetStorage()
storage.write(data, ticker)

df = storage.read(ticker)
print("\nAfter read:")
print("  columns:", df.columns.tolist())
print("  index.name:", df.index.name)
print("  head:", df.head(2).to_dict())

# Also inspect parquet file
import pyarrow.parquet as pq
table = pq.read_table(storage._ticker_path(ticker))
print("\nParquet file columns:", table.column_names)
print("Parquet file rows:", table.num_rows)
print("Parquet file sample:")
print(table.to_pandas().head(2))