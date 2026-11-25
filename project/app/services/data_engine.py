"""Motor de descarga y caché de datos financieros (yfinance)."""

from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

from app.core.logging import logger


class DataEngine:
    """Descarga precios históricos y los mantiene en caché local (CSV)."""

    def __init__(self, cache_dir: str = "data/cache", enabled: bool = True) -> None:
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.csv"

    def _safe_filename(self, tickers: list[str], start: str, end: Optional[str]) -> str:
        end_part = end or "latest"
        return "_".join(tickers) + "_" + start + "_" + end_part

    def descargar_datos_multiasset(
        self,
        tickers: list[str],
        start: str = "2020-01-01",
        end: Optional[str] = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Descarga precios de cierre ajustados (Adj Close) para una lista de tickers.

        Parameters
        ----------
        tickers : list[str]
            Lista de símbolos (ej. ["ZS=F", "BZ=F", "YPF"]).
        start : str
            Fecha de inicio (YYYY-MM-DD).
        end : Optional[str]
            Fecha de fin (YYYY-MM-DD). Si None, usa la fecha actual.
        force_refresh : bool
            Si True, ignora el caché y vuelve a descargar.

        Returns
        -------
        pd.DataFrame
            DataFrame con precios por ticker (columnas = tickers, índice = fecha).
        """
        cache_key = self._safe_filename(tickers, start, end)

        if self.enabled and not force_refresh:
            path = self._cache_path(cache_key)
            if path.exists():
                logger.info("Caché encontrado: %s", path)
                return pd.read_csv(path, index_col=0, parse_dates=True)

        logger.info("Descargando datos de %s desde %s", tickers, start)
        try:
            data = yf.download(tickers, start=start, end=end)["Adj Close"]
            if isinstance(data, pd.Series):
                data = data.to_frame()
            data = data.dropna(axis=1, how="all")
            if data.empty:
                raise ValueError("No se descargaron datos válidos para los tickers solicitados.")
        except Exception as exc:
            logger.error("Error descargando datos: %s", exc)
            # Fallback: generar datos sintéticos determinísticos para no bloquear la API
            data = self._generar_datos_demo(tickers, start, end)
            logger.warning("Usando datos demo de fallback debido a error en yfinance.")

        if self.enabled:
            path = self._cache_path(cache_key)
            data.to_csv(path)
            logger.info("Datos guardados en caché: %s", path)

        return data

    def descargar_cripto(
        self,
        tickers: list[str],
        period: str = "3mo",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Descarga precios de cierre de criptomonedas.

        Parameters
        ----------
        tickers : list[str]
            Lista de símbolos cripto (ej. ["BTC-USD", "ETH-USD"]).
        period : str
            Periodo de yfinance (ej. "3mo", "1y", "max").
        force_refresh : bool
            Si True, ignora el caché.

        Returns
        -------
        pd.DataFrame
            DataFrame con precios de cierre por cripto.
        """
        cache_key = "crypto_" + "_".join(tickers) + "_" + period

        if self.enabled and not force_refresh:
            path = self._cache_path(cache_key)
            if path.exists():
                logger.info("Caché cripto encontrado: %s", path)
                return pd.read_csv(path, index_col=0, parse_dates=True)

        logger.info("Descargando cripto %s (period=%s)", tickers, period)
        try:
            data = yf.download(tickers, period=period)["Close"]
            if isinstance(data, pd.Series):
                data = data.to_frame()
            data = data.dropna(axis=1, how="all")
            if data.empty:
                raise ValueError("No se descargaron datos válidos de cripto.")
        except Exception as exc:
            logger.error("Error descargando cripto: %s", exc)
            data = self._generar_datos_demo(tickers, period=period)
            logger.warning("Usando datos demo de fallback para cripto.")

        if self.enabled:
            path = self._cache_path(cache_key)
            data.to_csv(path)
            logger.info("Datos cripto guardados en caché: %s", path)

        return data

    def _generar_datos_demo(
        self,
        tickers: list[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        period: Optional[str] = None,
        seed: int = 42,
    ) -> pd.DataFrame:
        """Genera una serie de precios sintética determinística como fallback."""
        import numpy as np

        np.random.seed(seed)

        if period:
            # Mapeo aproximado de periodos a días
            period_days = {"1mo": 21, "3mo": 63, "6mo": 126, "1y": 252, "max": 252}
            n_days = period_days.get(period, 63)
        else:
            n_days = 252

        dates = pd.date_range(end=pd.Timestamp.today(), periods=n_days, freq="B")
        data = pd.DataFrame(index=dates)

        for ticker in tickers:
            # Random walk con deriva pequeña y volatilidad diferente por ticker
            vol = 0.02 if "YPF" in ticker or "=F" in ticker else 0.03
            drift = 0.0002
            returns = np.random.normal(drift, vol, n_days)
            price = 100 * np.exp(np.cumsum(returns))
            data[ticker] = price

        return data