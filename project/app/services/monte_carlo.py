"""Simulación de Monte Carlo: GBM y bootstrap histórico."""

from typing import Optional

import numpy as np
import pandas as pd

from app.core.config import settings
from app.core.logging import logger


class MonteCarloSimulator:
    """Simulador de escenarios de precios y P&L."""

    def __init__(self, precios: pd.DataFrame, retornos: pd.DataFrame, seed: int = 42) -> None:
        self.precios = precios
        self.retornos = retornos
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def simular_gbm(
        self,
        days: int = 1,
        n_scenarios: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Geometric Brownian Motion para simulación de precios futuros.

        Parameters
        ----------
        days : int
            Días de horizonte de simulación.
        n_scenarios : Optional[int]
            Número de escenarios (default settings.MONTE_CARLO_SCENARIOS).

        Returns
        -------
        pd.DataFrame
            Matriz (n_scenarios x n_activos) con precios simulados al final del horizonte.
        """
        n = n_scenarios or settings.MONTE_CARLO_SCENARIOS
        mu = self.retornos.mean().values
        sigma = self.retornos.std().values
        S0 = self.precios.iloc[-1].values

        dt = 1 / 252
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt)

        shocks = self.rng.standard_normal((days, n, len(S0)))
        log_returns = drift + diffusion * shocks
        log_prices = np.log(S0) + np.cumsum(log_returns, axis=0)
        prices = np.exp(log_prices)

        # Devuelve precios finales por escenario y activo
        final_prices = prices[-1]
        df = pd.DataFrame(final_prices, columns=self.precios.columns)
        df.index.name = "scenario"
        logger.info("GBM simulado: %d escenarios, %d días", n, days)
        return df

    def simular_bootstrap(
        self,
        days: int = 1,
        n_scenarios: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Resampleo histórico (bootstrap) de retornos observados.
        Conserva colas gruesas y dependencia empírica.
        """
        n = n_scenarios or settings.MONTE_CARLO_SCENARIOS
        S0 = self.precios.iloc[-1].values
        n_activos = len(S0)
        n_days_hist = len(self.retornos)

        # Muestreo con reemplazo de días históricos (filas completas de retornos)
        row_idx = self.rng.integers(0, n_days_hist, size=(days, n))
        # Obtener los retornos de esos días para todos los activos: shape (days, n, n_activos)
        sampled_returns = self.retornos.values[row_idx, :]

        # Acumular retornos sobre el horizonte: shape (n, n_activos)
        cumulative = np.prod(1 + sampled_returns, axis=0) - 1
        final_prices = S0 * (1 + cumulative)

        df = pd.DataFrame(final_prices, columns=self.precios.columns)
        df.index.name = "scenario"
        logger.info("Bootstrap simulado: %d escenarios, %d días", n, days)
        return df

    def resumen_pnl(
        self, precios_simulados: pd.DataFrame, precios_actuales: pd.Series
    ) -> dict[str, float]:
        """
        Calcula percentiles de la distribución de P&L por activo.

        Returns
        -------
        dict[str, float]
            Percentiles 1%, 5%, 50%, 95% del P&L agregado.
        """
        pnl = precios_simulados.subtract(precios_actuales.values, axis=1)
        pnl_total = pnl.sum(axis=1)

        resumen = {
            "p1_pnl": float(pnl_total.quantile(0.01)),
            "p5_pnl": float(pnl_total.quantile(0.05)),
            "p50_pnl": float(pnl_total.median()),
            "p95_pnl": float(pnl_total.quantile(0.95)),
            "p99_pnl": float(pnl_total.quantile(0.99)),
            "prob_perdida": float((pnl_total < 0).mean()),
            "expected_pnl": float(pnl_total.mean()),
        }
        logger.info("Resumen de P&L Monte Carlo calculado")
        return resumen