"""Agregación de cartera y métricas de rendimiento."""

from typing import Optional

import numpy as np
import pandas as pd

from app.core.logging import logger


class Portfolio:
    """Métricas de cartera: igual ponderada o risk parity."""

    def __init__(self, retornos: pd.DataFrame, precios: pd.DataFrame) -> None:
        self.retornos = retornos
        self.precios = precios

    def retornos_cartera(self, pesos: Optional[dict[str, float]] = None) -> pd.Series:
        """Calcula retornos diarios de la cartera."""
        if pesos is None:
            n = len(self.retornos.columns)
            pesos = {col: 1.0 / n for col in self.retornos.columns}

        pesos_series = pd.Series(pesos)
        activos_comunes = self.retornos.columns.intersection(pesos_series.index)
        if len(activos_comunes) == 0:
            raise ValueError("No hay activos comunes entre retornos y pesos.")

        w = pesos_series[activos_comunes]
        w = w / w.sum()  # normalizar
        retornos_cartera = self.retornos[activos_comunes] @ w
        retornos_cartera.name = "cartera"
        logger.info("Retornos de cartera calculados (%d activos)", len(activos_comunes))
        return retornos_cartera

    def metricas(
        self, pesos: Optional[dict[str, float]] = None, rf_diario: float = 0.0
    ) -> dict[str, float]:
        """
        Métricas de rendimiento y riesgo de la cartera.

        Returns
        -------
        dict[str, float]
            Sharpe, Sortino, Max Drawdown, Calmar, VaR 95%, Expected Shortfall 95%.
        """
        rc = self.retornos_cartera(pesos)

        # Sharpe ratio (anualizado)
        exceso = rc - rf_diario
        sharpe = (exceso.mean() / rc.std()) * np.sqrt(252) if rc.std() > 0 else 0.0

        # Sortino ratio (solo downside deviation)
        downside = rc[rc < 0]
        downside_std = downside.std() if len(downside) > 0 else rc.std()
        sortino = (exceso.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0.0

        # Maximum Drawdown de la cartera (precios acumulados)
        precios_cartera = (1 + rc).cumprod()
        roll_max = precios_cartera.cummax()
        drawdown = (precios_cartera - roll_max) / roll_max
        mdd = float(drawdown.min())

        # Calmar ratio
        cagrr = (precios_cartera.iloc[-1] ** (252 / len(rc))) - 1
        calmar = cagrr / abs(mdd) if mdd != 0 else 0.0

        # VaR y Expected Shortfall al 95%
        var_95 = float(rc.quantile(0.05))
        es_95 = float(rc[rc <= var_95].mean()) if (rc <= var_95).any() else var_95

        metricas = {
            "sharpe": round(sharpe, 4),
            "sortino": round(sortino, 4),
            "max_drawdown": round(mdd, 4),
            "calmar": round(calmar, 4),
            "var_95_diario": round(var_95, 4),
            "expected_shortfall_95_diario": round(es_95, 4),
            "retorno_anualizado": round(float(rc.mean() * 252), 4),
            "volatilidad_anualizada": round(float(rc.std() * np.sqrt(252)), 4),
        }
        logger.info("Métricas de cartera calculadas")
        return metricas