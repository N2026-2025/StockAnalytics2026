"""Indicadores técnicos puros pandas (sin dependencia ta-lib)."""

import pandas as pd
import numpy as np


def returns(close: pd.Series, periods: int = 1) -> pd.Series:
    """Retorno simple: (close_t / close_{t-1}) - 1."""
    return close.pct_change(periods=periods)


def volatility(close: pd.Series, window: int = 20, annualize: bool = True, trading_days: int = 252) -> pd.Series:
    """Volatilidad logarítmica rolling window, opcionalmente anualizada."""
    log_ret = np.log(close / close.shift(1))
    vol = log_ret.rolling(window=window).std() * np.sqrt(trading_days) if annualize else log_ret.rolling(window=window).std()
    return vol


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Índice de Fuerza Relativa (RSI)."""
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(window=window).mean()
    ma_down = down.rolling(window=window).mean()
    rs = ma_up / ma_down
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD (Moving Average Convergence Divergence).
    Returns: (macd_line, signal_line, histogram)
    """
    fast_ema = close.ewm(span=fast, adjust=False).mean()
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(
    close: pd.Series, window: int = 20, n_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bands de Bollinger (media móvil ± n_std * desviación estándar)."""
    sma = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    upper = sma + n_std * std
    lower = sma - n_std * std
    return upper, sma, lower


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Average True Range (ATR)."""
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()


def momentum(close: pd.Series, period: int = 1) -> pd.Series:
    """Momento puro: cambio de precio sobre 'period' períodos."""
    return close - close.shift(period)


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    chg = close.diff()
    sign = chg.sign().fillna(0)
    daily_obv = (sign * volume).fillna(0).cumsum()
    return daily_obv


def volume_change(volume: pd.Series, period: int = 1) -> pd.Series:
    """Cambio porcentual de volumen sobre 'period' períodos."""
    return volume.pct_change(periods=period)


def market_regime(
    close: pd.Series, vol_window: int = 20, vol_threshold: float = 0.20
) -> pd.Series:
    """Clasificación de régimen de mercado:
    0 = Low Vol, 1 = Normal Vol, 2 = High Vol
    Basado en volatilidad anualizada vs umbral.
    """
    vol = volatility(close, window=vol_window, annualize=False)
    # Normalizar volatilidad por su rolling mean
    vol_norm = vol / vol.rolling(window=vol_window * 2).mean()
    regime = pd.Series(0, index=vol.index)
    regime[vol_norm > vol_threshold] = 2   # High Vol
    regime[vol_norm < (1 - vol_threshold)] = 0  # Low Vol
    regime[(vol_norm >= (1 - vol_threshold)) & (vol_norm <= (1 + vol_threshold))] = 1  # Normal
    return regime