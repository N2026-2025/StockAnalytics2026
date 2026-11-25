"""Performance metrics for the quantitative trading platform.

Computes: CAGR, Sharpe, Sortino, Max Drawdown, Win Rate, Profit Factor,
Alpha (vs benchmark), Beta (vs benchmark).
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from scipy import stats


def calculate_cagr(total_return: float, n_years: float) -> float:
    """Calculate Compound Annual Growth Rate."""
    if n_years <= 0:
        return 0.0
    return (1 + total_return) ** (1 / n_years) - 1


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, 
                           annualization: int = 252) -> float:
    """Calculate annualized Sharpe Ratio."""
    excess_returns = returns - risk_free_rate / annualization
    if returns.std() == 0:
        return 0.0
    return (excess_returns.mean() / returns.std()) * np.sqrt(annualization)


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0,
                            annualization: int = 252) -> float:
    """Calculate annualized Sortino Ratio using downside deviation."""
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    excess_downside = returns.mean() - risk_free_rate / annualization
    return (excess_downside / downside_returns.std()) * np.sqrt(annualization)


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """Calculate maximum drawdown from equity curve."""
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    return drawdown.min()


def calculate_win_rate(pnl_series: pd.Series) -> float:
    """Calculate win rate (fraction of profitable trades)."""
    if len(pnl_series) == 0:
        return 0.0
    return (pnl_series > 0).mean()


def calculate_profit_factor(gross_profit: float, gross_loss: float) -> float:
    """Calculate profit factor."""
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def calculate_alpha_beta(returns: pd.Series, benchmark_returns: pd.Series,
                         risk_free_rate: float = 0.0) -> Dict[str, float]:
    """Calculate alpha and beta against a benchmark.
    
    Uses simple linear regression: Rp = alpha + beta * Rb + epsilon
    """
    # Align returns
    aligned = pd.concat([returns, benchmark_returns], axis=1, join="inner").dropna()
    if len(aligned) < 2:
        return {"alpha": 0.0, "beta": 0.0}
    
    y = aligned.iloc[:, 0] - risk_free_rate / 252  # excess portfolio return
    x = aligned.iloc[:, 1] - risk_free_rate / 252  # excess benchmark return
    
    # Linear regression: y = alpha + beta * x
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    return {"alpha": intercept, "beta": slope}


def calculate_all_metrics(trades: List[Any], equity_curve: pd.Series,
                          returns: pd.Series, benchmark_returns: Optional[pd.Series] = None,
                          n_years: float = 1.0) -> Dict[str, float]:
    """Calculate all performance metrics from trades and equity curve."""
    # Basic metrics
    win_rate = calculate_win_rate(returns)
    max_dd = calculate_max_drawdown(equity_curve)
    sharpe = calculate_sharpe_ratio(returns)
    sortino = calculate_sortino_ratio(returns)
    cagr = calculate_cagr(total_return if 'total_return' in dir() else 0.0, n_years)
    
    # Profit factor needs gross profit/loss - simplified
    profit_factor = 1.0  # placeholder
    
    result = {
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
    }
    
    # Alpha and beta if benchmark provided
    if benchmark_returns is not None:
        alpha_beta = calculate_alpha_beta(returns, benchmark_returns)
        result.update(alpha_beta)
    
    return result