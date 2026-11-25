"""Walk-forward optimization de parámetros para hipótesis de alpha mining.

En cada fold temporal:
1. Se hace grid-search de los parámetros (umbrales) sobre el **train fold**,
   maximizando el Sharpe in-sample.
2. Se aplica el mejor set de parámetros al **test fold** (out-of-sample honesto).
3. Se registra el Sharpe OOS y los parámetros elegidos.

Esto evita el sesgo de elegir parámetros sobre toda la muestra (que es
exactamente el tipo de overfitting que el filtro DSR/PBO intenta detectar).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from app.alpha.config import settings
from app.core.logging import logger

SignalBuilder = Callable[[pd.DataFrame, dict], pd.Series]


@dataclass
class ParamGrid:
    """Grilla de parámetros a optimizar para una hipótesis."""

    name: str
    grid: dict[str, list]
    build_signal: SignalBuilder


@dataclass
class FoldResult:
    fold: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    best_params: dict
    train_sharpe: float
    oos_sharpe: float
    oos_trades: int


@dataclass
class WalkForwardResult:
    hypothesis: str
    folds: list[FoldResult] = field(default_factory=list)
    mean_oos_sharpe: float = 0.0
    mean_train_sharpe: float = 0.0
    degradation: float = 0.0
    stability: float = 0.0
    param_mode: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "hypothesis": self.hypothesis,
            "n_folds": len(self.folds),
            "mean_oos_sharpe": round(self.mean_oos_sharpe, 4),
            "mean_train_sharpe": round(self.mean_train_sharpe, 4),
            "degradation": round(self.degradation, 4),
            "stability": round(self.stability, 4),
            "param_mode": self.param_mode,
            "folds": [
                {
                    "fold": f.fold,
                    "train": f"{f.train_start}->{f.train_end}",
                    "test": f"{f.test_start}->{f.test_end}",
                    "best_params": f.best_params,
                    "train_sharpe": round(f.train_sharpe, 4),
                    "oos_sharpe": round(f.oos_sharpe, 4),
                    "oos_trades": f.oos_trades,
                }
                for f in self.folds
            ],
        }


def _annualized_sharpe(df: pd.DataFrame, signal: pd.Series, horizon_days: int = 30) -> tuple[float, int]:
    """Sharpe anualizado de la señal sobre un subset de datos."""
    mask = signal.values == 1
    rets = pd.to_numeric(df.loc[mask, "growth_future_30d"], errors="coerce").dropna() - 1.0
    n = len(rets)
    if n < 5 or rets.std(ddof=1) == 0:
        return 0.0, n
    rf = settings.RISK_FREE_ANNUAL * (horizon_days / settings.TRADING_DAYS_YEAR)
    annualization = settings.TRADING_DAYS_YEAR / horizon_days
    sharpe = ((rets.mean() - rf) / rets.std(ddof=1)) * np.sqrt(annualization)
    return float(sharpe), n


def _date_str(ts) -> str:
    try:
        return str(pd.Timestamp(ts).date())
    except Exception:
        return str(ts)


def walk_forward_optimize(
    df: pd.DataFrame,
    spec: ParamGrid,
    n_splits: int = 5,
    embargo_days: int | None = None,
    min_trades: int = 10,
) -> WalkForwardResult:
    """Ejecuta walk-forward optimization para una hipótesis parametrizada."""
    embargo = settings.EMBARGO_DAYS if embargo_days is None else embargo_days
    n = len(df)
    if n < 50:
        logger.warning("Dataset demasiado pequeño para walk-forward (%d filas)", n)
        return WalkForwardResult(hypothesis=spec.name)

    tscv = TimeSeriesSplit(n_splits=n_splits, gap=embargo)
    keys = list(spec.grid.keys())
    combos = list(itertools.product(*[spec.grid[k] for k in keys]))

    folds: list[FoldResult] = []
    for fold_i, (train_idx, test_idx) in enumerate(tscv.split(df), start=1):
        train = df.iloc[train_idx]
        test = df.iloc[test_idx]

        best_params: dict = {}
        best_train_sharpe = -np.inf
        for combo in combos:
            params = dict(zip(keys, combo))
            try:
                sig = spec.build_signal(train, params)
            except Exception:
                continue
            sharpe, ntr = _annualized_sharpe(train, sig)
            if ntr < min_trades:
                continue
            if sharpe > best_train_sharpe:
                best_train_sharpe = sharpe
                best_params = params

        if not best_params:
            logger.warning("Fold %d (%s): sin parámetros válidos", fold_i, spec.name)
            continue

        test_sig = spec.build_signal(test, best_params)
        oos_sharpe, oos_trades = _annualized_sharpe(test, test_sig)

        folds.append(
            FoldResult(
                fold=fold_i,
                train_start=_date_str(train["Date"].iloc[0]),
                train_end=_date_str(train["Date"].iloc[-1]),
                test_start=_date_str(test["Date"].iloc[0]),
                test_end=_date_str(test["Date"].iloc[-1]),
                best_params=best_params,
                train_sharpe=best_train_sharpe,
                oos_sharpe=oos_sharpe,
                oos_trades=oos_trades,
            )
        )

    if not folds:
        return WalkForwardResult(hypothesis=spec.name)

    oos = [f.oos_sharpe for f in folds]
    train = [f.train_sharpe for f in folds]
    mean_oos = float(np.mean(oos))
    mean_train = float(np.mean(train))

    # Estabilidad: fracción de folds con OOS positivo.
    stability = float(np.mean([1.0 if s > 0 else 0.0 for s in oos]))

    # Moda de parámetros (el set más elegido entre folds).
    param_mode: dict = {}
    for k in keys:
        vals = [f.best_params[k] for f in folds if k in f.best_params]
        if vals:
            param_mode[k] = max(set(vals), key=vals.count)

    result = WalkForwardResult(
        hypothesis=spec.name,
        folds=folds,
        mean_oos_sharpe=mean_oos,
        mean_train_sharpe=mean_train,
        degradation=mean_train - mean_oos,
        stability=stability,
        param_mode=param_mode,
    )
    logger.info(
        "WF-Opt %s: train=%.3f oos=%.3f degrad=%.3f estab=%.2f folds=%d",
        spec.name, mean_train, mean_oos, result.degradation, stability, len(folds),
    )
    return result


# ---------------------------------------------------------------------------
# Builders parametrizados para las hipótesis con umbrales naturales.
# ---------------------------------------------------------------------------

def _col(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return pd.to_numeric(df[name], errors="coerce")
    return pd.Series(np.nan, index=df.index, dtype="float64")


def _build_rsi_oversold(df: pd.DataFrame, p: dict) -> pd.Series:
    return (_col(df, "rsi") < p.get("rsi_threshold", 30)).fillna(False)


def _build_mfi_oversold(df: pd.DataFrame, p: dict) -> pd.Series:
    return (_col(df, "mfi") < p.get("mfi_threshold", 20)).fillna(False)


def _build_cci_oversold(df: pd.DataFrame, p: dict) -> pd.Series:
    return (_col(df, "cci") < p.get("cci_threshold", -100)).fillna(False)


def _build_momentum_breakout(df: pd.DataFrame, p: dict) -> pd.Series:
    return (
        (_col(df, "roc") > p.get("roc_threshold", 0.05))
        & (_col(df, "adx") > p.get("adx_threshold", 25))
    ).fillna(False)


def default_param_grids() -> list[ParamGrid]:
    """Grillas de parámetros por defecto para las hipótesis optimizables."""
    return [
        ParamGrid(
            name="rsi_oversold_wf",
            grid={"rsi_threshold": [20, 25, 30, 35]},
            build_signal=_build_rsi_oversold,
        ),
        ParamGrid(
            name="mfi_oversold_wf",
            grid={"mfi_threshold": [15, 20, 25, 30]},
            build_signal=_build_mfi_oversold,
        ),
        ParamGrid(
            name="cci_oversold_wf",
            grid={"cci_threshold": [-150, -120, -100, -80]},
            build_signal=_build_cci_oversold,
        ),
        ParamGrid(
            name="momentum_breakout_wf",
            grid={"roc_threshold": [0.02, 0.05, 0.10], "adx_threshold": [20, 25, 30]},
            build_signal=_build_momentum_breakout,
        ),
    ]


def run_walk_forward_optimization(
    df: pd.DataFrame,
    n_splits: int = 5,
) -> list[WalkForwardResult]:
    """Corre la optimización walk-forward sobre todas las grillas por defecto."""
    results = []
    for spec in default_param_grids():
        results.append(walk_forward_optimize(df, spec, n_splits=n_splits))
    results.sort(key=lambda r: r.mean_oos_sharpe, reverse=True)
    return results