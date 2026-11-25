"""Tests del simulador de Monte Carlo."""

import pandas as pd

from app.services.monte_carlo import MonteCarloSimulator


def test_gbm_forma_correcta(precios_sinteticos, retornos_sinteticos):
    sim = MonteCarloSimulator(precios=precios_sinteticos, retornos=retornos_sinteticos, seed=42)
    precios_sim = sim.simular_gbm(days=1, n_scenarios=100)
    assert precios_sim.shape[0] == 100
    assert list(precios_sim.columns) == list(precios_sinteticos.columns)


def test_bootstrap_forma_correcta(precios_sinteticos, retornos_sinteticos):
    sim = MonteCarloSimulator(precios=precios_sinteticos, retornos=retornos_sinteticos, seed=42)
    precios_sim = sim.simular_bootstrap(days=1, n_scenarios=100)
    assert precios_sim.shape[0] == 100
    assert list(precios_sim.columns) == list(precios_sinteticos.columns)


def test_resumen_pnl_tiene_claves(precios_sinteticos, retornos_sinteticos):
    sim = MonteCarloSimulator(precios=precios_sinteticos, retornos=retornos_sinteticos, seed=42)
    precios_sim = sim.simular_bootstrap(days=1, n_scenarios=100)
    precios_actuales = precios_sinteticos.iloc[-1]
    resumen = sim.resumen_pnl(precios_sim, precios_actuales)
    for clave in ["p1_pnl", "p5_pnl", "p50_pnl", "p95_pnl", "prob_perdida", "expected_pnl"]:
        assert clave in resumen


def test_seed_reproducible(precios_sinteticos, retornos_sinteticos):
    sim1 = MonteCarloSimulator(precios=precios_sinteticos, retornos=retornos_sinteticos, seed=42)
    sim2 = MonteCarloSimulator(precios=precios_sinteticos, retornos=retornos_sinteticos, seed=42)
    r1 = sim1.simular_bootstrap(days=1, n_scenarios=50)
    r2 = sim2.simular_bootstrap(days=1, n_scenarios=50)
    pd.testing.assert_frame_equal(r1, r2)