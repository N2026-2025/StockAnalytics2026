"""Target engine: computes and engineers the 4 target variables."""

from typing import Dict, Literal
import pandas as pd
import numpy as np


TargetType = Literal[
    "target_24h_up_1pct",
    "target_return_7d",
    "target_vol_forecast",
    "target_drawdown_risk",
]


class TargetEngine:
    """Engine for generating target variables from price data."""
    
    def __init__(self, lookback: int = 20, volatility_window: int = 20, drawdown_window: int = 252):
        self.lookback = lookback
        self.volatility_window = volatility_window
        self.drawdown_window = drawdown_window
    
    def compute(self, prices: pd.DataFrame, returns: Optional[pd.DataFrame] = None) -> Dict[str, pd.Series]:
        """Compute all target variables.
        
        Parameters
        ----------
        prices : pd.DataFrame
            Price data with DatetimeIndex, columns include 'close'.
        returns : Optional[pd.DataFrame]
            Pre-computed daily returns. If None, computed from prices.
        
        Returns
        -------
        Dict[str, pd.Series]
            Dictionary mapping target names to values.
        """
        # Extract close prices
        close = prices.get("close") if isinstance(prices, dict) else (
            prices["Close"] if isinstance(prices, dict) and "Close" in prices.columns else
            prices.iloc[:, 0] if isinstance(prices, pd.DataFrame) else prices
        )
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        
        # Compute returns if not provided
        if returns is None:
            ret_series = close.pct_change().dropna()
        else:
            ret_series = returns
            if isinstance(ret_series, pd.DataFrame):
                ret_series = ret_series.iloc[:, 0]
        
        # Engineer all targets using inline functions
        ret_1d = (ret_series > 0.01).astype(int)
        cum_ret_7d = returns.rolling(window=7).apply(
            lambda x: np.prod(1 + x) - 1 if len(x) == 7 else np.nan, raw=True
        )
        log_ret = np.log(close / close.shift(1))
        vol = log_ret.rolling(window=self.volatility_window).std() * np.sqrt(252)
        rolling_max = close.cummax()
        drawdown = (close - rolling_max) / rolling_max
        rolling_mdd = drawdown.rolling(window=self.drawdown_window).min()
        
        return {
            "target_24h_up_1pct": ret_1d,
            "target_return_7d": cum_ret_7d,
            "target_vol_forecast": vol,
            "target_drawdown_risk": (rolling_mdd < -0.20).astype(int),
        }


def target_24h_up_1pct(returns: pd.Series) -> pd.Series:
    """Binary target: 24h horizon positive return > 1%."""
    ret_1d = returns if isinstance(returns, pd.Series) else returns.iloc[:, 0] if isinstance(returns, pd.DataFrame) else returns
    return (ret_1d > 0.01).astype(int)


def target_return_7d(returns: pd.Series) -> pd.Series:
    """7-day return prediction (cumulative return over 7 trading days)."""
    cum_ret_7d = returns.rolling(window=7).apply(
        lambda x: np.prod(1 + x) - 1 if len(x) == 7 else np.nan, raw=True
    )
    return cum_ret_7d


def target_vol_forecast(close: pd.Series, vol_window: int = 20) -> pd.Series:
    """Volatility forecasting: rolling volatility over vol_window periods."""
    log_ret = np.log(close / close.shift(1))
    vol = log_ret.rolling(window=vol_window).std() * np.sqrt(252)
    return vol


def target_drawdown_risk(close: pd.Series, window: int = 252) -> pd.Series:
    """Drawdown risk prediction: probability of drawdown > 20% over window periods."""
    rolling_max = close.cummax()
    drawdown = (close - rolling_max) / rolling_max
    rolling_mdd = drawdown.rolling(window=window).min()
    return (rolling_mdd < -0.20).astype(int)


def engineer_targets(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    **kwargs,
) -> Dict[str, pd.Series]:
    """Engineer all 4 target variables for a given ticker."""
    close = prices.get("close") if isinstance(prices, dict) else (
        prices["Close"] if isinstance(prices, dict) and "Close" in prices.columns else
        prices.iloc[:, 0] if isinstance(prices, pd.DataFrame) else prices
    )
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    
    ret_series = returns.get("close") if isinstance(returns, dict) else (
        returns.iloc[:, 0] if isinstance(returns, pd.DataFrame) else returns
    )
    
    targets: Dict[str, pd.Series] = {}
    targets["target_24h_up_1pct"] = target_24h_up_1pct(ret_series)
    targets["target_return_7d"] = target_return_7d(ret_series)
    targets["target_vol_forecast"] = target_vol_forecast(close, **kwargs)
    targets["target_drawdown_risk"] = target_drawdown_risk(close, **kwargs)
    
    return targets