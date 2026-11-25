"""Backtesting engine for the quantitative trading platform.

Supports walk-forward validation, capital compounding, transaction costs,
slippage, and position sizing. Evaluates long-only and long-short strategies.
"""

from .engine import BacktestEngine, BacktestConfig, Trade, BacktestResult
from .metrics import calculate_all_metrics, calculate_cagr, calculate_sharpe_ratio, \
    calculate_sortino_ratio, calculate_max_drawdown, calculate_win_rate, \
    calculate_profit_factor, calculate_alpha_beta

__all__ = [
    "BacktestEngine", "BacktestConfig", "Trade", "BacktestResult",
    "calculate_all_metrics", "calculate_cagr", "calculate_sharpe_ratio",
    "calculate_sortino_ratio", "calculate_max_drawdown", "calculate_win_rate",
    "calculate_profit_factor", "calculate_alpha_beta"
]