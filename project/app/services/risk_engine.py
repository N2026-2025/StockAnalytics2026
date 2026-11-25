"""Motor de cálculo de riesgo: VaR histórico, paramétrico y Expected Shortfall."""

from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

from app.core.config import settings
from app.core.logging import logger


class RiskEngine:
    """Cálculo de métricas de riesgo de mercado."""

    @staticmethod
    def retornos_diarios(precios: pd.DataFrame) -> pd.DataFrame:
        """Calcula retornos porcentuales diarios eliminando NaN."""
        return precios.pct_change().dropna()

    @staticmethod
    def var_historico(
        retornos: pd.DataFrame, confianza: Optional[float] = None
    ) -> pd.Series:
        """
        Value at Risk histórico (percentil empírico de la cola inferior).

        Parameters
        ----------
        retornos : pd.DataFrame
            Retornos diarios por activo.
        confianza : Optional[float]
            Nivel de confianza (default 0.95).

        Returns
        -------
        pd.Series
            VaR por activo (valor negativo representa pérdida).
        """
        c = confianza if confianza is not None else settings.VAR_CONFIDENCE
        alpha = 1 - c
        var = retornos.quantile(alpha)
        logger.info("VaR histórico calculado (confianza=%.2f)", c)
        return var

    @staticmethod
    def var_parametrico(
        retornos: pd.DataFrame, confianza: Optional[float] = None
    ) -> pd.Series:
        """
        Value at Risk paramétrico asumiendo normalidad:
        VaR = mu + sigma * z_alpha
        """
        c = confianza if confianza is not None else settings.VAR_CONFIDENCE
        alpha = 1 - c
        z = stats.norm.ppf(alpha)
        mu = retornos.mean()
        sigma = retornos.std()
        var = mu + sigma * z
        logger.info("VaR paramétrico calculado (confianza=%.2f)", c)
        return var

    @staticmethod
    def expected_shortfall(
        retornos: pd.DataFrame, confianza: Optional[float] = None
    ) -> pd.Series:
        """
        Expected Shortfall (CVaR): media de retornos por debajo del VaR histórico.
        """
        c = confianza if confianza is not None else settings.VAR_CONFIDENCE
        var = RiskEngine.var_historico(retornos, confianza=c)
        es = retornos.apply(lambda col: col[col <= var[col.name]].mean())
        logger.info("Expected Shortfall calculado (confianza=%.2f)", c)
        return es

    @staticmethod
    def max_drawdown(precios: pd.DataFrame) -> pd.Series:
        """Calcula Maximum Drawdown por activo."""
        roll_max = precios.cummax()
        drawdown = (precios - roll_max) / roll_max
        mdd = drawdown.min()
        logger.info("Maximum Drawdown calculado")
        return mdd

    @staticmethod
    def volatilidad_anualizada(retornos: pd.DataFrame) -> pd.Series:
        """Volatilidad anualizada (252 días hábiles)."""
        return retornos.std() * np.sqrt(252)