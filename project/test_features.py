import sys
sys.path.insert(0, r'C:\stock analytics 2026\project')

from app.quant.features.indicators import returns, volatility, rsi, macd, bollinger_bands, atr, momentum, obv, volume_change, market_regime
from app.quant.features.feature_engine import feature_engine
print("Features imports OK")

# Quick test of indicators
import pandas as pd
import yfinance as yf

data = yf.download("SPY", start="2020-01-01", end="2024-01-01")["Close"]
print("RSI 14:", rsi(data, 14).iloc[-1])
print("Vol 20d:", volatility(data, 20, annualize=False).iloc[-1])
macd_line, macd_signal, macd_hist = macd(data, 12, 26, 9)
print("MACD last:", macd_line.iloc[-1])
print("BB upper last:", bollinger_bands(data, 20).iloc[-1][0])
print("ATR 14:", atr(data, data, data, 14).iloc[-1] if hasattr(data, '__getitem__') else 'N/A')
print("Momentum 10d:", momentum(data, 10).iloc[-1])