"""Backtest automático de señales sobre el dataset del Zoomcamp.

Cada fila con señal==1 es una operación independiente (consistencia con los
ejercicios HW2/HW4 del Zoomcamp: invertir una cuantía fija por señal). Se
reutiliza el motor de riesgo existente para el drawdown.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.alpha.config import settings
from app.core.logging import logger
from app.services.risk_engine import RiskEngine


@dataclass
class BacktestResult:
    hypothesis: str
    n_trades: int
    trades_per_day: float
    win_rate: float
    mean_return: float
    std_return: float
    sharpe_annualized: float
    total_return_compounded: float
    cagr: float
    max_drawdown: float
    start_date: str
    end_date: str
    years_spanned: float

    def as_dict(self) -> dict:
        return {
            "hypothesis": self.hypothesis,
            "n_trades": int(self.n_trades),
            "trades_per_day": round(self.trades_per_day, 4),
            "win_rate": round(self.win_rate, 4),
            "mean_return": round(self.mean_return, 6),
            "std_return": round(self.std_return, 6),
            "sharpe_annualized": round(self.sharpe_annualized, 4),
            "total_return_compounded": round(self.total_return_compounded, 6),
            "cagr": round(self.cagr, 6),
            "max_drawdown": round(self.max_drawdown, 6),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "years_spanned": round(self.years_spanned, 2),
        }


def _rf_per_trade(horizon_days: int = 30) -> float:
    """Tasa libre de riesgo por operación (30 días hábiles ~ horizonte)."""
    return settings.RISK_FREE_ANNUAL * (horizon_days / settings.TRADING_DAYS_YEAR)


def backtest_signal(
    df: pd.DataFrame,
    signal: pd.Series,
    hypothesis_name: str = "signal",
    context: dict | None = None,
) -> BacktestResult | None:
    """Ejecuta el backtest de una señal binaria sobre el dataset alineado.

    Returns None si no hay suficientes operaciones.
    """
    import numpy as np

    ctx = context or {}
    data = df.copy()
    data["signal"] = signal.values
    trades = data[data["signal"] == 1].copy()
    if trades.empty:
        logger.warning("Sin operaciones para %s", hypothesis_name)
        return None

    horizon_days = int(ctx.get("horizon_days", 30))
    trade_returns = trades["growth_future_30d"].astype(float).dropna() - 1.0
    n_trades = len(trade_returns)
    if n_trades < settings.MIN_TRADES:
        logger.warning(
            "%s: solo %d trades (mínimo %d), se omite",
            hypothesis_name,
            n_trades,
            settings.MIN_TRADES,
        )
        return None

    dates = pd.to_datetime(trades["Date"]).sort_values()
    start_date = str(dates.iloc[0].date())
    end_date = str(dates.iloc[-1].date())
    days_spanned = max((dates.iloc[-1] - dates.iloc[0]).days, 1)
    years_spanned = days_spanned / 365.25

    win_rate = float((trade_returns > 0).mean())
    mean_return = float(trade_returns.mean())
    std_return = float(trade_returns.std(ddof=1)) if n_trades > 1 else 0.0

    # Sharpe anualizado: exceso por operación sobre rf anualizado al número de ops/año.
    rf_per_trade = settings.RISK_FREE_ANNUAL * (horizon_days / settings.TRADING_DAYS_YEAR)
    trades_per_year = n_trades / years_spanned if years_spanned > 0 else n_trades
    annualization = settings.TRADING_DAYS_YEAR / horizon_days  # ~8.4 ops-equivalentes/año
    if std_return > 0:
        sharpe_annualized = ((mean_return - rf_per_trade) / std_return) * np.sqrt(annualization)
    else:
        sharpe_annualized = 0.0

    # Total compuesto y CAGR de la curva de equity.
    equity = (1.0 + trade_returns.sort_index()).cumprod()
    total_return_compounded = float(equity.iloc[-1] - 1.0)
    cagr = float(equity.iloc[-1] ** (1.0 / years_spanned) - 1.0) if years_spanned > 0 else 0.0

    # Drawdown máximo reutilizando el motor de riesgo existente.
    mdd_series = RiskEngine.max_drawdown(equity.to_frame(name="equity"))
    max_drawdown = float(mdd_series["equity"])

    trades_per_day = n_trades / days_spanned

    logger.info(
        "Backtest %s: trades=%d sharpe=%.3f CAGR=%.4f MDD=%.4f win=%.3f",
        hypothesis_name,
        n_trades,
        sharpe_annualized,
        cagr,
        max_drawdown,
        win_rate,
    )
    return BacktestResult(
        hypothesis=hypothesis_name,
        n_trades=int(n_trades),
        trades_per_day=trades_per_day,
        win_rate=win_rate,
        mean_return=mean_return,
        std_return=std_return,
        sharpe_annualized=sharpe_annualized,
        total_return_compounded=total_return_compounded,
        cagr=cagr,
        max_drawdown=max_drawdown,
        start_date=start_date,
        end_date=end_date,
        years_spanned=years_spanned,
    )