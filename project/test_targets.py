import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.targets.engine import TargetEngine
import pandas as pd
import yfinance as yf

# Download data
ticker = "SPY"
prices = yf.download(ticker, start="2020-01-01", end="2024-01-01")
close = prices["Close"]
returns = prices.pct_change()

engine = TargetEngine()
targets = engine.compute(prices=close, returns=returns)
for name, val in targets.items():
    print(f"{name}: last={val.iloc[-1]:.4f} (type={type(val).__name__})")