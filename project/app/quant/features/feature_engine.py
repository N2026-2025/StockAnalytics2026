"""Motor de feature engineering para la plataforma cuantitativa.

Genera el conjunto de features para cada ticker: retornos, volatilidad,
indicadores técnicos, volumen, régimen de mercado y correlación a benchmark.
"""

import pandas as pd
import numpy as np
from typing import Dict, List

from app.quant.features.indicators import (
    returns,
    volatility,
    rsi,
    macd,
    bollinger_bands,
    atr,
    momentum,
    obv,
    volume_change,
    market_regime,
)
from app.quant.data.universe import ASSETS, BENCHMARK, get_asset_info


def feature_engine(
    prices: Dict[str, pd.DataFrame],
    benchmark: str = BENCHMARK,
    lookback: int = 20,
) -> Dict[str, pd.DataFrame]:
    """
    Engendra features completas para cada ticker dado un diccionario de precios.

    Parameters
    ----------
    prices : Dict[str, pd.DataFrame]
        Diccionario ticker → DataFrameclose prices (índice=fecha, columna=close).
    benchmark : str
        Ticker del benchmark para correlación (default: SPY).
    lookback : int
        Ventana para indicadores rolling (RSI, Bollinger, etc.).

    Returns
    -------
    Dict[str, pd.DataFrame]
        Diccionario ticker → DataFrame de features.
    """
    features_dict: Dict[str, pd.DataFrame] = {}

    for ticker, price_df in prices.items():
        close = price_df["close"] if isinstance(price_df, dict) else price_df["Close"] if "Close" in price_df.columns else price_df.iloc[:, 0]

        # Asegurar Series si viene DataFrame multi-columna
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        feat = pd.DataFrame(index=close.index)

        # --- Returns ---
        feat["ret_1d"] = returns(close, periods=1)
        feat["ret_5d"] = returns(close, periods=5)
        feat["ret_20d"] = returns(close, periods=20)

        # --- Volatility ---
        feat["vol_20d"] = volatility(close, window=lookback, annualize=False)

        # --- RSI ---
        feat["rsi_14"] = rsi(close, window=14)

        # --- MACD ---
        macd_line, macd_signal, macd_hist = macd(close, fast=12, slow=26, signal=9)
        feat["macd"] = macd_line
        feat["macd_signal"] = macd_signal
        feat["macd_hist"] = macd_hist

        # --- Bollinger Bands ---
        upper, middle, lower = bollinger_bands(close, window=lookback)
        feat["bb_upper"] = upper
        feat["bb_middle"] = middle
        feat["bb_lower"] = lower
        feat["bb_width"] = (upper - lower) / middle  # ancho relativo
        feat["bb_pos"] = (close - lower) / (upper - lower)  # posición dentro de bands

        # --- ATR ---
        high = price_df.get("high", close) if isinstance(price_df, dict) else price_df["High"] if "High" in price_df.columns else close
        low = price_df.get("low", close) if isinstance(price_df, dict) else price_df["Low"] if "Low" in price_df.columns else close
        if not isinstance(high, pd.Series):
            high = high.squeeze() if high.ndim > 1 else close
        if not isinstance(low, pd.Series):
            low = low.squeeze() if low.ndim > 1 else close
        feat["atr_14"] = atr(high, low, close, window=14)

        # --- Momentum ---
        feat["momentum_10d"] = momentum(close, period=10)

        # --- Volume ---
        vol_series = price_df.get("volume", pd.Series(1, index=close.index)) if isinstance(price_df, dict) else price_df["Volume"] if "Volume" in price_df.columns else pd.Series(1, index=close.index)
        if isinstance(vol_series, pd.DataFrame):
            vol_series = vol_series.iloc[:, 0]
        feat["volume"] = vol_series
        feat["vol_pct_change"] = volume_change(vol_series, period=1)

        # --- Market Regime ---
        feat["regime"] = market_regime(close, vol_window=20, vol_threshold=0.20)

        # --- Correlation to Benchmark ---
        if benchmark in prices and benchmark != ticker:
            b_close = prices[benchmark]["close"] if isinstance(prices[benchmark], dict) else prices[benchmark]["Close"] if "Close" in prices[benchmark].columns else prices[benchmark].iloc[:, 0]
            if isinstance(b_close, pd.DataFrame):
                b_close = b_close.iloc[:, 0]
            ret_feat = returns(close, periods=1)
            ret_bench = returns(b_close, periods=1)
            # Alinear por índice común
            combined = pd.concat([ret_feat, ret_bench], axis=1, join="inner").dropna()
            if len(combined) > 20:
                corr = combined.iloc[:, 0].corr(combined.iloc[:, 1])
                feat["corr_benchmark"] = corr
            else:
                feat["corr_benchmark"] = np.nan
        else:
            feat["corr_benchmark"] = np.nan

        # --- Asset info basic ---
        info = get_asset_info(ticker)
        for k, v in info.items():
            feat[f"asset_{k}"] = v

        features_dict[ticker] = feat

    return features_dict