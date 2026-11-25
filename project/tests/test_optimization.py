"""Tests del módulo de walk-forward optimization (Fase 2)."""

import numpy as np
import pandas as pd

from app.alpha.optimization import (
    ParamGrid,
    WalkForwardResult,
    _annualized_sharpe,
    _build_rsi_oversold,
    default_param_grids,
    run_walk_forward_optimization,
    walk_forward_optimize,
)


def _make_df(n: int = 2000) -> pd.DataFrame:
    """Genera un DataFrame sintético con columnas de indicadores."""
    rng = np.random.default_rng(0)
    dates = pd.date_range("2015-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {
            "Date": dates,
            "Ticker": "TEST",
            "growth_future_30d": 1.0 + rng.normal(0.005, 0.05, n),
            "rsi": rng.uniform(10, 70, n),
            "mfi": rng.uniform(5, 40, n),
            "cci": rng.uniform(-200, 50, n),
            "roc": rng.normal(0, 0.1, n),
            "adx": rng.uniform(10, 40, n),
        }
    )


def test_annualized_sharpe_empty():
    df = pd.DataFrame({"growth_future_30d": []})
    sig = pd.Series([], dtype=int)
    sharpe, n = _annualized_sharpe(df, sig)
    assert sharpe == 0.0
    assert n == 0


def test_annualized_sharpe_positive_returns():
    df = _make_df(200)
    df["growth_future_30d"] = 1.0 + np.random.default_rng(1).normal(0.02, 0.01, len(df))
    sig = pd.Series([1] * len(df))
    sharpe, n = _annualized_sharpe(df, sig)
    assert n == len(df)
    assert sharpe > 0  # retornos positivos constantes -> sharpe alto


def test_build_rsi_oversold_threshold():
    df = _make_df(6)
    df["rsi"] = [10, 20, 25, 30, 40, 50]
    sig = _build_rsi_oversold(df, {"rsi_threshold": 30})
    expected = [True, True, True, False, False, False]  # <30
    assert list(sig.astype(bool)) == expected


def test_default_param_grids():
    grids = default_param_grids()
    assert len(grids) == 4
    assert all(isinstance(g, ParamGrid) for g in grids)
    assert "rsi_oversold_wf" in {g.name for g in grids}
    assert "momentum_breakout_wf" in {g.name for g in grids}


def test_walk_forward_small_dataset():
    df = _make_df(20)  # demasiado pequeño
    spec = ParamGrid(name="test", grid={"x": [1]}, build_signal=lambda d, p: pd.Series([1] * len(d)))
    result = walk_forward_optimize(df, spec, n_splits=3)
    assert isinstance(result, WalkForwardResult)
    assert result.hypothesis == "test"
    assert result.mean_oos_sharpe == 0.0  # sin folds


def test_walk_forward_valid_dataset():
    df = _make_df(1000)
    spec = ParamGrid(
        name="rsi_test",
        grid={"rsi_threshold": [20, 30, 40]},
        build_signal=_build_rsi_oversold,
    )
    result = walk_forward_optimize(df, spec, n_splits=3, min_trades=5)
    assert len(result.folds) > 0
    assert result.mean_oos_sharpe != 0.0
    assert "rsi_threshold" in result.param_mode
    d = result.as_dict()
    assert d["hypothesis"] == "rsi_test"
    assert "mean_oos_sharpe" in d


def test_run_walk_forward_all():
    df = _make_df(2000)
    results = run_walk_forward_optimization(df, n_splits=3)
    assert len(results) == 4
    # Ordenados por OOS Sharpe descendente
    oos = [r.mean_oos_sharpe for r in results]
    assert oos == sorted(oos, reverse=True)