"""Adaptive allocation strategy: adjusts position size based on model confidence."""

from typing import Dict, Any
import pandas as pd
import numpy as np


class AdaptiveStrategy:
    """Adaptive allocation based on model confidence scores."""
    
    def __init__(self, confidence_threshold: float = 0.6,
                 max_exposure: float = 1.0,
                 min_exposure: float = 0.2):
        self.confidence_threshold = confidence_threshold
        self.max_exposure = max_exposure
        self.min_exposure = min_exposure
        self.name = "adaptive"
    
    def generate_signals(self, features: pd.DataFrame,
                         targets: dict,
                         **kwargs) -> pd.DataFrame:
        """Generate adaptive signals based on model confidence."""
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
            
            confidence_map = {}
            if targets and isinstance(targets, dict) and date in targets:
                date_targets = targets[date]
                if isinstance(date_targets, dict):
                    for ticker in date_features.index:
                        if ticker in date_targets:
                            conf = date_targets[ticker].get("confidence",
                                                              date_targets[ticker].get(
                                                                  "target_24h_up_1pct", 0.5))
                            confidence_map[ticker] = conf
            
            if not confidence_map:
                n_assets = len(signal_df.columns)
                if n_assets > 0:
                    equal_weight = 1.0 / n_assets
                    for ticker in signal_df.columns:
                        signal_df.loc[date, ticker] = equal_weight
                continue
            
            total_confidence = sum(confidence_map.values())
            n_active = len([c for c in confidence_map.values() if c > self.confidence_threshold])
            
            if total_confidence > 0 and n_active > 0:
                for ticker in confidence_map:
                    if ticker in signal_df.columns:
                        conf = confidence_map[ticker]
                        if conf > self.confidence_threshold:
                            exposure = self.min_exposure + (
                                self.max_exposure - self.min_exposure
                            ) * (conf - self.confidence_threshold) / (
                                1.0 - self.confidence_threshold
                            )
                            exposure = min(max(exposure, self.min_exposure), self.max_exposure)
                            signal_df.loc[date, ticker] = exposure / n_active
                        else:
                            signal_df.loc[date, ticker] = 0
            else:
                n_assets = len([c for c in confidence_map.values()])
                if n_assets > 0:
                    equal_weight = 1.0 / n_assets
                    for ticker in signal_df.columns:
                        signal_df.loc[date, ticker] = equal_weight
        
        return signal_df.fillna(0)