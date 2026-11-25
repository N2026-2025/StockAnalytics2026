import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

import pandas as pd
import yfinance as yf
from app.quant.data.storage import ParquetStorage

# 1. Descargar datos con yfinance
ticker = "SPY"
data = yf.download(ticker, start="2020-01-01", end="2024-01-01")["Close"]
print("=== yfinance raw ===")
print("Type:", type(data))
print("Shape:", data.shape)
print("Columns:", data.columns.tolist() if isinstance(data, pd.DataFrame) else "N/A")
print("Index name:", data.index.name)
print("Index type:", type(data.index))
print()

# 2. Escribir con storage.write
storage = ParquetStorage()
print("=== Writing to Parquet ===")
storage.write(data, ticker)

# 3. Leer de vuelta
print("=== Reading from Parquet ===")
df = storage.read(ticker)
print("Columns:", df.columns.tolist())
print("Index name:", df.index.name)
print("Head:", df.head(2).to_dict())
print()

# 4. Inspeccionar archivo parquet generado
import os
parquet_path = str(storage._ticker_path(ticker))
print("Parquet path:", parquet_path)
print("File exists:", os.path.exists(parquet_path))
if os.path.exists(parquet_path):
    import pyarrow.parquet as pq
    table = pq.read_table(parquet_path)
    print("Parquet columns:", table.column_names)
    print("Parquet num rows:", table.num_rows)