"""Tests del módulo de pruebas de estrés."""

from app.services.stress_testing import StressTesting


def test_fx_devaluation_25pct(precios_sinteticos, retornos_sinteticos):
    st = StressTesting(precios=precios_sinteticos, retornos=retornos_sinteticos)
    resultado = st.fx_devaluation_25pct()
    assert "YPF" in resultado.index
    # YPF debería tener un impacto negativo de ~25%
    assert resultado["YPF"] < 0


def test_soy_shock(precios_sinteticos, retornos_sinteticos):
    st = StressTesting(precios=precios_sinteticos, retornos=retornos_sinteticos)
    resultado = st.soy_shock(caida=-0.15)
    assert "ZS=F" in resultado.index
    assert resultado["ZS=F"] < 0


def test_oil_shock(precios_sinteticos, retornos_sinteticos):
    st = StressTesting(precios=precios_sinteticos, retornos=retornos_sinteticos)
    resultado = st.oil_shock(caida=-0.20)
    assert "BZ=F" in resultado.index
    assert resultado["BZ=F"] < 0


def test_joint_crisis_historica(precios_sinteticos, retornos_sinteticos):
    st = StressTesting(precios=precios_sinteticos, retornos=retornos_sinteticos)
    resultado = st.joint_crisis_historica()
    assert len(resultado) > 0


def test_ejecutar_todos(precios_sinteticos, retornos_sinteticos):
    st = StressTesting(precios=precios_sinteticos, retornos=retornos_sinteticos)
    todos = st.ejecutar_todos()
    assert "fx_devaluation_25pct" in todos
    assert "soy_shock_-15pct" in todos
    assert "oil_shock_-20pct" in todos
    assert "joint_crisis_historica" in todos


def test_pnl_cartera_igual(precios_sinteticos, retornos_sinteticos):
    st = StressTesting(precios=precios_sinteticos, retornos=retornos_sinteticos)
    pnl = st.fx_devaluation_25pct()
    pnl_cartera = st.pnl_cartera_igual(pnl)
    assert isinstance(pnl_cartera, float)