import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

import yfinance as yf
import pandas as pd

for tkr in ["SPY", "QQQ", "IWM"]:
    try:
        data = yf.download(tkr, start="2020-01-01", end="2024-01-01")["Close"]
        print(f"{tkr}: columns={data.columns.tolist() if isinstance(data, pd.DataFrame) else 'Series'}, shape={data.shape if isinstance(data, pd.DataFrame) else 'N/A'}, index.name={data.index.name}")
    except Exception as e:
        print(f"{tkr}: ERROR {e}")