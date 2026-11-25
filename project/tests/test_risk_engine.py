"""Tests del motor de riesgo (VaR, Expected Shortfall, Drawdown)."""

from app.services.risk_engine import RiskEngine


def test_var_historico_rango(retornos_sinteticos):
    var = RiskEngine.var_historico(retornos_sinteticos, confianza=0.95)
    for col in retornos_sinteticos.columns:
        assert col in var.index
        assert var[col] < 0  # VaR es pérdida esperada (negativo)


def test_var_parametrico_rango(retornos_sinteticos):
    var = RiskEngine.var_parametrico(retornos_sinteticos, confianza=0.95)
    for col in retornos_sinteticos.columns:
        assert col in var.index
        assert var[col] < 0


def test_expected_shortfall_menor_que_var(retornos_sinteticos):
    var = RiskEngine.var_historico(retornos_sinteticos, confianza=0.95)
    es = RiskEngine.expected_shortfall(retornos_sinteticos, confianza=0.95)
    for col in retornos_sinteticos.columns:
        # Expected Shortfall debería ser <= VaR (más negativo o igual)
        assert es[col] <= var[col]


def test_max_drawdown_negativo_o_cero(precios_sinteticos):
    mdd = RiskEngine.max_drawdown(precios_sinteticos)
    for col in precios_sinteticos.columns:
        assert mdd[col] <= 0


def test_volatilidad_anualizada_positiva(retornos_sinteticos):
    vol = RiskEngine.volatilidad_anualizada(retornos_sinteticos)
    for col in retornos_sinteticos.columns:
        assert vol[col] > 0