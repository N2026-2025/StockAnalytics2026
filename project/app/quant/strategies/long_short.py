"""Long-short strategy: longs assets with positive signals, shorts assets with negative signals."""

from typing import Dict, Any
import pandas as pd
import numpy as np


class LongShortStrategy:
    """Long-short strategy that longs assets with positive signals and shorts negative ones."""
    
    def __init__(self, signal_threshold: float = 0.0,
                 long_short_ratio: float = 1.0):
        self.signal_threshold = signal_threshold
        self.long_short_ratio = long_short_ratio
        self.name = "long_short"
    
    def generate_signals(self, features: pd.DataFrame,
                         targets: dict,
                         **kwargs) -> pd.DataFrame:
        """Generate long-short signals."""
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
            
            for ticker in date_features.index:
                if ticker not in signal_df.columns:
                    continue
                
                prob = 0.5
                if targets and isinstance(targets, dict) and date in targets:
                    date_targets = targets[date]
                    if isinstance(date_targets, dict) and ticker in date_targets:
                        prob = date_targets[ticker].get("target_24h_up_1pct", 0.5) or 0.5
                
                if prob > self.signal_threshold:
                    signal_df.loc[date, ticker] = 1
                elif prob < (1 - self.signal_threshold):
                    signal_df.loc[date, ticker] = -1
                else:
                    signal_df.loc[date, ticker] = 0
        
        return signal_df.fillna(0)