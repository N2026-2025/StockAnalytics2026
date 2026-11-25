"""Tests del motor de datos (data_engine) con fallback a datos demo."""

import numpy as np
import pandas as pd

from app.services.data_engine import DataEngine


def test_demo_data_generado():
    engine = DataEngine(cache_dir="data/cache_test", enabled=False)
    data = engine._generar_datos_demo(["ZS=F", "BZ=F", "YPF"], period="3mo", seed=42)
    assert not data.empty
    assert list(data.columns) == ["ZS=F", "BZ=F", "YPF"]
    assert len(data) > 0


def test_demo_data_reproducible():
    engine = DataEngine(cache_dir="data/cache_test", enabled=False)
    d1 = engine._generar_datos_demo(["ZS=F"], period="3mo", seed=42)
    d2 = engine._generar_datos_demo(["ZS=F"], period="3mo", seed=42)
    np.testing.assert_array_equal(d1.iloc[:, 0].values, d2.iloc[:, 0].values)