"""Risk parity strategy: allocates capital equally based on risk contribution."""

from typing import Dict, Any
import pandas as pd
import numpy as np


class RiskParityStrategy:
    """Risk parity strategy that equalizes risk contribution across assets."""
    
    def __init__(self, lookback: int = 252, target_vol: float = 0.15):
        self.lookback = lookback
        self.target_vol = target_vol
        self.name = "risk_parity"
    
    def generate_signals(self, features: pd.DataFrame,
                         targets: dict,
                         **kwargs) -> pd.DataFrame:
        """Generate risk parity signals."""
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
            
            asset_vols = {}
            for ticker in date_features.index:
                if ticker in date_features.index:
                    vol = date_features[ticker]
                    if isinstance(vol, (int, float)) and not pd.isna(vol):
                        asset_vols[ticker] = vol
            
            if not asset_vols:
                continue
            
            total_vol = sum(asset_vols.values())
            
            if total_vol > 0:
                for ticker in asset_vols:
                    if ticker in signal_df.columns:
                        weight = (1 / asset_vols[ticker]) / total_vol
                        signal_df.loc[date, ticker] = weight
            else:
                n_assets = len([t for t in signal_df.columns if t in asset_vols])
                if n_assets > 0:
                    equal_weight = 1.0 / n_assets
                    for ticker in signal_df.columns:
                        signal_df.loc[date, ticker] = equal_weight
        
        return signal_df.fillna(0)