"""Target engine: computes and engineers the 4 target variables."""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import numpy as np

from app.quant.targets.engine import engineer_targets, TargetType
from app.quant.features.indicators import returns as ind_returns


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
        
        # Engineer all targets
        targets = engineer_targets(prices=close, returns=ret_series)
        
        return targets