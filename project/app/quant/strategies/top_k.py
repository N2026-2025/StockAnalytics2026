"""Top-K ranking strategy: ranks assets by signal score and holds top K."""

from typing import Dict, Any
import pandas as pd
import numpy as np


class TopKStrategy:
    """Top-K ranking strategy that holds the top K assets by signal score."""
    
    def __init__(self, k: int = 5, signal_threshold: float = 0.0):
        self.k = k
        self.signal_threshold = signal_threshold
        self.name = "top_k"
    
    def generate_signals(self, features: pd.DataFrame,
                         targets: dict,
                         **kwargs) -> pd.DataFrame:
        """Generate Top-K signals."""
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
            
            signal_scores = {}
            if targets and isinstance(targets, dict) and date in targets:
                date_targets = targets[date]
                if isinstance(date_targets, dict):
                    for ticker in date_features.index:
                        if ticker in date_targets:
                            signal_scores[ticker] = date_targets[ticker].get("target_24h_up_1pct", 0.5) or 0.5
                        else:
                            signal_scores[ticker] = 0.5
            
            if not signal_scores:
                for ticker in date_features.index:
                    if ticker in date_features.index:
                        score = date_features[ticker] if not isinstance(date_features[ticker], (list, pd.Series)) else 0.5
                        signal_scores[ticker] = score
            
            sorted_assets = sorted(signal_scores.items(), key=lambda x: x[1], reverse=True)
            n_to_select = min(self.k, len(sorted_assets))
            selected = [asset for asset, _ in sorted_assets[:n_to_select]]
            
            for ticker in selected:
                if ticker in signal_df.columns:
                    signal_df.loc[date, ticker] = 1
        
        return signal_df.fillna(0)