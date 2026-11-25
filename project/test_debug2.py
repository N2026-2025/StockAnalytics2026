import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

import yfinance as yf
import pandas as pd
from app.quant.data.storage import ParquetStorage

ticker = "QQQ"
start = "2020-01-01"
end = "2024-01-01"

data = yf.download(ticker, start=start, end=end)["Close"]
print("After .close:")
print("  type:", type(data))
print("  columns:", data.columns.tolist() if isinstance(data, pd.DataFrame) else 'N/A')
print("  index.name:", data.index.name)
print("  shape:", data.shape)

if isinstance(data, pd.Series):
    data = data.to_frame(ticker)
    print("\nAfter .to_frame:")
    print("  columns:", data.columns.tolist())
    print("  index.name:", data.index.name)

data = data.dropna(how="all")
print("\nAfter .dropna(how='all'):")
print("  type:", type(data))
print("  columns:", data.columns.tolist() if isinstance(data, pd.DataFrame) else 'N/A')
print("  index.name:", data.index.name)
print("  shape:", data.shape)
print("  empty:", data.empty)

storage = ParquetStorage()
storage.write(data, ticker)

df = storage.read(ticker)
print("\nRead result:")
print("  columns:", df.columns.tolist())
print("  index.name:", df.index.name)