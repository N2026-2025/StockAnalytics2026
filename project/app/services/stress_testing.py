"""Pruebas de estrés con escenarios macro argentinos."""

from typing import Optional

import numpy as np
import pandas as pd

from app.core.logging import logger


class StressTesting:
    """Escenarios determinísticos de estrés sobre la cartera."""

    def __init__(self, precios: pd.DataFrame, retornos: pd.DataFrame) -> None:
        self.precios = precios
        self.retornos = retornos
        self.ultimos_precios = precios.iloc[-1]

    def _aplicar_shock(self, shocks: dict[str, float]) -> pd.Series:
        """
        Aplica shocks porcentuales sobre los últimos precios conocidos.

        Parameters
        ----------
        shocks : dict[str, float]
            Diccionario {ticker: cambio_porcentual} (ej. {"YPF": -0.25}).

        Returns
        -------
        pd.Series
            P&L simulado por activo (en términos del precio actual).
        """
        pnl = {}
        for ticker, shock in shocks.items():
            if ticker in self.ultimos_precios.index:
                precio_actual = self.ultimos_precios[ticker]
                precio_shockeado = precio_actual * (1 + shock)
                pnl[ticker] = precio_shockeado - precio_actual
            else:
                pnl[ticker] = np.nan
        return pd.Series(pnl)

    def fx_devaluation_25pct(self) -> pd.Series:
        """
        Escenario: salto cambiario del 25% (devaluación tipo Argentina).
        Impacto directo en YPF y transmisión parcial a commodities.
        """
        shocks = {
            "YPF": -0.25,
            "ZS=F": -0.10,  # transmisión parcial vía costos logísticos
            "BZ=F": -0.05,
        }
        logger.info("Ejecutando stress test: devaluación 25%%")
        return self._aplicar_shock(shocks)

    def soy_shock(self, caida: float = -0.15) -> pd.Series:
        """Escenario: caída de la soja (ZS=F) del X%."""
        shocks = {"ZS=F": caida, "YPF": caida * 0.5, "BZ=F": caida * 0.3}
        logger.info("Ejecutando stress test: shock soja %.1f%%", caida * 100)
        return self._aplicar_shock(shocks)

    def oil_shock(self, caida: float = -0.20) -> pd.Series:
        """Escenario: caída del petróleo Brent (BZ=F) del X%."""
        shocks = {"BZ=F": caida, "YPF": caida * 0.4, "ZS=F": caida * 0.2}
        logger.info("Ejecutando stress test: shock petróleo %.1f%%", caida * 100)
        return self._aplicar_shock(shocks)

    def joint_crisis_historica(self) -> pd.Series:
        """
        Escenario: peor día de crisis conjunta observado desde 2020,
        reaplicado sobre los precios actuales.
        """
        peor_dia = self.retornos.min()
        logger.info("Ejecutando stress test: crisis conjunta histórica")
        return self._aplicar_shock(peor_dia.to_dict())

    def ejecutar_todos(self) -> dict[str, pd.Series]:
        """Ejecuta todos los escenarios y devuelve un diccionario con resultados."""
        return {
            "fx_devaluation_25pct": self.fx_devaluation_25pct(),
            "soy_shock_-15pct": self.soy_shock(),
            "oil_shock_-20pct": self.oil_shock(),
            "joint_crisis_historica": self.joint_crisis_historica(),
        }

    def pnl_cartera_igual(self, pnl_por_activo: pd.Series) -> float:
        """P&L de una cartera igual ponderada (1/3 por activo)."""
        activos_comunes = pnl_por_activo.dropna().index
        if len(activos_comunes) == 0:
            return 0.0
        return float(pnl_por_activo[activos_comunes].mean())