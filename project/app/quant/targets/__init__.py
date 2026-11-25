"""Target variables for the quantitative trading platform.

4 target variables defined per requirements:
  1. target_24h_up_1pct: 24h positive return > 1%
  2. target_return_7d: 7-day return prediction
  3. target_vol_forecast: Volatility forecasting
  4. target_drawdown_risk: Drawdown risk prediction
"""

from .engine import engineer_targets, TargetType

__all__ = [
    "engineer_targets", "TargetType",
    "target_24h_up_1pct", "target_return_7d",
    "target_vol_forecast", "target_drawdown_risk"
]