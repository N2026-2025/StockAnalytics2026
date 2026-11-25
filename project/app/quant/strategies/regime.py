"""Volatility regime strategy: adjusts exposure based on market volatility regime."""

from typing import Dict, Any
import pandas as pd
import numpy as np


class RegimeStrategy:
    """Strategy that adjusts position size based on market volatility regime."""
    
    def __init__(self, high_vol_threshold: float = 0.30,
                 low_vol_threshold: float = 0.15,
                 high_vol_reduction: float = 0.5,
                 low_vol_increase: float = 1.5):
        self.high_vol_threshold = high_vol_threshold
        self.low_vol_threshold = low_vol_threshold
        self.high_vol_reduction = high_vol_reduction
        self.low_vol_increase = low_vol_increase
        self.name = "regime"
    
    def generate_signals(self, features: pd.DataFrame,
                         targets: dict,
                         **kwargs) -> pd.DataFrame:
        """Generate signals based on volatility regime."""
        signal_df = pd.DataFrame(index=features.index,
                                  columns=features.columns if isinstance(features, pd.DataFrame) else [])
        
        if features.empty:
            return signal_df.fillna(0)
        
        for date in features.index:
            if date not in features.index:
                continue
            date_features = features.loc[date]
            if date_features is None:
                continue
            
            vol_feature = None
            if "vol_20d" in date_features.index:
                vol_feature = date_features["vol_20d"]
            elif "target_vol_forecast" in date_features:
                vol_feature = date_features["target_vol_forecast"]
            
            if vol_feature is None:
                continue
            
            if vol_feature > self.high_vol_threshold:
                regime = "high"
            elif vol_feature < self.low_vol_threshold:
                regime = "low"
            else:
                regime = "normal"
            
            for ticker in date_features.index:
                if ticker not in signal_df.columns:
                    continue
                
                base_signal = 0.5
                
                if regime == "high":
                    adjusted_signal = base_signal * self.high_vol_reduction
                elif regime == "low":
                    adjusted_signal = base_signal * self.low_vol_increase
                else:
                    adjusted_signal = base_signal
                
                if adjusted_signal > self._get_threshold(regime):
                    signal_df.loc[date, ticker] = 1
                elif adjusted_signal < (1 - self._get_threshold(regime)):
                    signal_df.loc[date, ticker] = -1
                else:
                    signal_df.loc[date, ticker] = 0
        
        return signal_df.fillna(0)
    
    def _get_threshold(self, regime: str) -> float:
        if regime == "high":
            return self.signal_threshold if hasattr(self, 'signal_threshold') else 0.5
        elif regime == "low":
            return 0.5
        return 0.5