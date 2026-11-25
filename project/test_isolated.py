import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.data.storage import ParquetStorage
import pandas as pd
import yfinance as yf
import os

# Test isolated write/read
ticker = "SPY"
data = yf.download(ticker, start="2020-01-01", end="2024-01-01")["Close"]
print("Original data columns:", data.columns.tolist())
print("Original data index.name:", data.index.name)

storage = ParquetStorage()

# Write
storage.write(data, ticker)

# Check what was written
parquet_path = storage._ticker_path(ticker)
print("\nParquet file exists:", os.path.exists(parquet_path))
if os.path.exists(parquet_path):
    import pyarrow.parquet as pq
    table = pq.read_table(parquet_path)
    print("Parquet columns:", table.column_names)
    print("Parquet rows:", table.num_rows)

# Read
df = storage.read(ticker)
print("\nRead result columns:", df.columns.tolist())
print("Read result index.name:", df.index.name)
print("Read result head:", df.head(2).to_dict())