"""Tests del módulo de cartera."""

from app.services.portfolio import Portfolio


def test_retornos_cartera_igual_ponderada(precios_sinteticos, retornos_sinteticos):
    port = Portfolio(retornos=retornos_sinteticos, precios=precios_sinteticos)
    rc = port.retornos_cartera()
    assert len(rc) == len(retornos_sinteticos)
    assert rc.name == "cartera"


def test_metricas_cartera(precios_sinteticos, retornos_sinteticos):
    port = Portfolio(retornos=retornos_sinteticos, precios=precios_sinteticos)
    n = len(precios_sinteticos.columns)
    pesos = {col: 1.0 / n for col in precios_sinteticos.columns}
    m = port.metricas(pesos=pesos)
    assert "sharpe" in m
    assert "sortino" in m
    assert "max_drawdown" in m
    assert "calmar" in m
    assert "var_95_diario" in m
    assert "expected_shortfall_95_diario" in m
    assert m["max_drawdown"] <= 0
    assert m["var_95_diario"] < 0


def test_pesos_normalizados(precios_sinteticos, retornos_sinteticos):
    port = Portfolio(retornos=retornos_sinteticos, precios=precios_sinteticos)
    pesos = {"ZS=F": 0.5, "BZ=F": 0.3, "YPF": 0.2}
    rc = port.retornos_cartera(pesos=pesos)
    assert len(rc) == len(retornos_sinteticos)