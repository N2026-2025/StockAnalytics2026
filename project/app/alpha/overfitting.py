"""Filtro de overfitting para hipótesis de alpha mining.

Implementa:

1. **Walk-forward / K-Fold purgado con embargo** (TimeSeriesSplit con `gap`):
   separa temporalmente train y test para evitar fuga de información entre folds.
2. **Deflated Sharpe Ratio** (Bailey & López de Prado, 2014): ajusta el Sharpe por
   no-normalidad y por número de pruebas múltiples (n_trials).
3. **PBO simplificado por bootstrap**: probabilidad de que el Sharpe sea <= 0
   estimada mediante remuestreo de los retornos de operación.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from scipy import stats

from app.core.logging import logger


@dataclass
class OverfittingReport:
    hypothesis: str
    full_sample_sharpe: float
    fold_sharpes: list[float]
    mean_oos_sharpe: float
    deflated_sharpe: float
    pbo_bootstrap: float
    passes_filter: bool
    reason: str

    def as_dict(self) -> dict:
        return {
            "hypothesis": self.hypothesis,
            "full_sample_sharpe": round(self.full_sample_sharpe, 4),
            "fold_sharpes": [round(float(s), 4) for s in self.fold_sharpes],
            "mean_oos_sharpe": round(self.mean_oos_sharpe, 4),
            "deflated_sharpe": round(self.deflated_sharpe, 4),
            "pbo_bootstrap": round(self.pbo_bootstrap, 4),
            "passes_filter": bool(self.passes_filter),
            "reason": self.reason,
        }


def _expected_max_sr_null(n_trials: int, sr_variance: float) -> float:
    """Sharpe esperado del máximo bajo nulo (Euler–Mascheroni)."""
    euler = 0.5772156649015329
    term1 = (1.0 - euler) * stats.norm.ppf(1.0 - 1.0 / n_trials)
    term2 = euler * stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e))
    return float(np.sqrt(sr_variance) * (term1 + term2))


def deflated_sharpe_ratio(
    trade_returns: pd.Series,
    n_trials: int = 1,
    sr_variance: float | None = None,
) -> float:
    """Deflated Sharpe Ratio (probabilidad de que el Sharpe verdadero supere el nulo)."""
    n = len(trade_returns)
    if n < 2:
        return 0.0
    sr = float(trade_returns.mean() / trade_returns.std(ddof=1)) if trade_returns.std(ddof=1) > 0 else 0.0
    skew = float(stats.skew(trade_returns)) if n > 2 else 0.0
    kurt = float(stats.kurtosis(trade_returns, fisher=True)) if n > 3 else 0.0
    sr_variance = sr_variance if sr_variance is not None else 1.0 / max(n - 1, 1)

    sr0 = _expected_max_sr_null(max(n_trials, 1), sr_variance)
    denom = np.sqrt(1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr * sr)
    if denom <= 0:
        denom = 1e-8
    z = (sr - sr0) * np.sqrt(n - 1) / denom
    return float(stats.norm.cdf(z))


def pbo_bootstrap(trade_returns: pd.Series, n_boot: int = 300) -> float:
    """Probabilidad de backtest overfitting: fracción de bootstrap con Sharpe <= 0."""
    n = len(trade_returns)
    if n < 2:
        return 1.0
    rng = np.random.default_rng(42)
    count_nonpositive = 0
    for _ in range(n_boot):
        sample = trade_returns.sample(n=n, replace=True, random_state=int(rng.integers(0, 1_000_000)))
        sr = float(sample.mean() / sample.std(ddof=1)) if sample.std(ddof=1) > 0 else 0.0
        if sr <= 0:
            count_nonpositive += 1
    return float(count_nonpositive / n_boot)


def walk_forward_sharpes(
    df: pd.DataFrame,
    signal: pd.Series,
    n_splits: int = 5,
    embargo_days: int = 5,
) -> list[float]:
    """Sharpe de cada fold fuera de muestra usando TimeSeriesSplit con gap (embargo)."""
    n = len(df)
    if n < 4:
        return []
    tscv = TimeSeriesSplit(n_splits=n_splits, gap=embargo_days)
    sharpes: list[float] = []
    for train_idx, test_idx in tscv.split(df):
        sub = df.iloc[test_idx][["growth_future_30d"]].copy()
        sub["signal"] = signal.loc[sub.index].astype(bool)
        sub["ret"] = pd.to_numeric(sub["growth_future_30d"], errors="coerce") - 1.0
        sub = sub.dropna(subset=["ret"])
        selected = sub[sub["signal"]]
        if len(selected) < 5:
            continue
        rets = selected["ret"]
        std = float(rets.std(ddof=1)) if len(rets) > 1 else 0.0
        sharpes.append(float(rets.mean() / std) if std > 0 else 0.0)
    return sharpes


def evaluate_overfitting(
    hypothesis_name: str,
    df: pd.DataFrame,
    signal: pd.Series,
    trade_returns: pd.Series,
    full_sharpe: float,
    n_trials: int,
    settings_obj,
) -> OverfittingReport:
    """Evalúa si una hipótesis pasa el filtro de overfitting.

    ``df`` es el dataset completo alineado y ``signal`` la serie binaria, para que
    el walk-forward se calcule sobre los folds temporales reales.
    """
    n_splits = max(1, min(5, len(df) // 10))
    fold_sharpes = walk_forward_sharpes(
        df,
        signal,
        n_splits=n_splits,
        embargo_days=settings_obj.EMBARGO_DAYS,
    )
    mean_oos = float(np.mean(fold_sharpes)) if fold_sharpes else full_sharpe
    dsr = deflated_sharpe_ratio(trade_returns, n_trials=n_trials)
    pbo = pbo_bootstrap(trade_returns)

    passes = (
        mean_oos >= settings_obj.MIN_OOS_SHARPE
        and dsr >= settings_obj.MIN_DEFLATED_SHARPE
        and pbo <= settings_obj.MAX_PBO
    )
    if passes:
        reason = "Pasa filtro de overfitting"
    else:
        parts = []
        if mean_oos < settings_obj.MIN_OOS_SHARPE:
            parts.append(f"OOS sharpe {mean_oos:.2f} < {settings_obj.MIN_OOS_SHARPE}")
        if dsr < settings_obj.MIN_DEFLATED_SHARPE:
            parts.append(f"DSR {dsr:.2f} < {settings_obj.MIN_DEFLATED_SHARPE}")
        if pbo > settings_obj.MAX_PBO:
            parts.append(f"PBO {pbo:.2f} > {settings_obj.MAX_PBO}")
        reason = "Falla: " + "; ".join(parts) if parts else "Falla sin detalle"

    logger.info(
        "Overfitting %s: sharpe=%.3f DSR=%.3f PBO=%.3f oos=%.3f pasa=%s",
        hypothesis_name,
        full_sharpe,
        dsr,
        pbo,
        mean_oos,
        passes,
    )
    return OverfittingReport(
        hypothesis=hypothesis_name,
        full_sample_sharpe=full_sharpe,
        fold_sharpes=fold_sharpes,
        mean_oos_sharpe=mean_oos,
        deflated_sharpe=dsr,
        pbo_bootstrap=pbo,
        passes_filter=passes,
        reason=reason,
    )
