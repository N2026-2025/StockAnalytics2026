"""Fixtures compartidas para tests: datos sintéticos determinísticos."""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def precios_sinteticos():
    """DataFrame de precios sintéticos para 3 activos, 100 días."""
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    data = pd.DataFrame(index=dates)
    for ticker in ["ZS=F", "BZ=F", "YPF"]:
        returns = np.random.normal(0.0005, 0.02, n)
        price = 100 * np.exp(np.cumsum(returns))
        data[ticker] = price
    return data


@pytest.fixture
def retornos_sinteticos(precios_sinteticos):
    """Retornos diarios calculados a partir de precios sintéticos."""
    return precios_sinteticos.pct_change().dropna()