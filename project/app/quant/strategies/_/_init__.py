"""Strategies for the quantitative trading platform.

Long-only, long-short, Top-K ranking, volatility regime, risk parity,
and adaptive allocation based on model confidence.
"""

from .long_only import LongOnlyStrategy
from .long_short import LongShortStrategy
from .top_k import TopKStrategy
from .regime import RegimeStrategy
from .risk_parity import RiskParityStrategy
from .adaptive import AdaptiveStrategy

__all__ = [
    "LongOnlyStrategy", "LongShortStrategy", "TopKStrategy",
    "RegimeStrategy", "RiskParityStrategy", "AdaptiveStrategy"
]