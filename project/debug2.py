import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.data.storage import ParquetStorage
import pandas as pd
import yfinance as yf

# Write a known DataFrame
ticker = "SPY_TEST"
data = yf.download(ticker, start="2020-01-01", end="2024-01-01")["Close"]
print("Original data columns:", data.columns.tolist())
print("Original data index.name:", data.index.name)

storage = ParquetStorage()
storage.write(data, ticker)

# Read back
df = storage.read(ticker)
print("\nAfter read:")
print("columns:", df.columns.tolist())
print("index.name:", df.index.name)
print("df head:", df.head(2))

# Now inspect parquet file directly
import pyarrow.parquet as pq
table = pq.read_table(storage._ticker_path(ticker))
print("\nParquet file columns:", table.column_names)
print("Parquet file data:")
print(table.to_pandas().head(2))