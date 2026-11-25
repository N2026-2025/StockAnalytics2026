"""Ingestión de datos: yfinance → particionado Parquet + catálogo SQLite."""

from pathlib import Path
from typing import Optional
import pandas as pd
import yfinance as yf
import numpy as np

from app.quant.data.universe import ASSETS, BENCHMARK, get_asset_info, ASSET_INFO, BENCHMARK_INFO


class ParquetStorage:
    """Maneja lectura/escritura de archivos Parquet particionados por ticker."""

    def __init__(self, base_dir: str = "data/raw"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _ticker_path(self, ticker: str) -> Path:
        """Ruta del archivo Parquet para un ticker dado."""
        safe = ticker.replace("/", "_").replace("\\", "_")
        return self.base_dir / f"{safe}.parquet"

    def write(self, df: pd.DataFrame, ticker: str) -> None:
        """Escribe un DataFrame de precios al archivo Parquet del ticker."""
        path = self._ticker_path(ticker)
        # Asegurar que el índice sea fecha y columna sea el ticker
        out = df.copy()
        if out.index.name != "Date":
            out = out.reset_index().rename(columns={"index": "Date"})
        # Guardar solo la columna de cierre ajustado o close relevante
        if ticker not in out.columns and "Close" in out.columns:
            out = out[["Date", "Close"]].rename(columns={"Close": ticker})
        elif ticker in out.columns:
            out = out[["Date", ticker]]
        out.to_parquet(path, index=False, compression="snappy")

    def read(self, ticker: str) -> pd.DataFrame:
        """Lee precios de un ticker desde Parquet."""
        path = self._ticker_path(ticker)
        if not path.exists():
            raise FileNotFoundError(f"No hay datos Parquet para {ticker} en {path}")
        df = pd.read_parquet(path)
        if "Date" in df.columns:
            df = df.set_index("Date")
        return df

    def exists(self, ticker: str) -> bool:
        return self._ticker_path(ticker).exists()


class SQLiteCatalog:
    """Catálogo simple en SQLite para metadatos de runs, señales y métricas."""

    def __init__(self, db_path: str = "data/catalog.db"):
        self.db_path = db_path
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        c = self.conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT,
                dataset_rows INTEGER,
                parameters TEXT
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                run_id TEXT,
                ticker TEXT,
                date TEXT,
                signal REAL,
                model TEXT,
               FOREIGN KEY (run_id) REFERENCES runs(run_id)
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS metrics (
                metric_id TEXT PRIMARY KEY,
                run_id TEXT,
                ticker TEXT,
                metric_name TEXT,
                metric_value REAL,
                FOREIGN KEY (run_id) REFERENCES runs(run_id)
            )"""
        )
        self.conn.commit()

    def log_run(self, run_id: str, timestamp: str, dataset_rows: int, parameters: str) -> None:
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?)",
            (run_id, timestamp, dataset_rows, parameters),
        )
        self.conn.commit()

    def log_signal(self, signal_id: str, run_id: str, ticker: str, date: str, signal: float, model: str) -> None:
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO signals VALUES (?, ?, ?, ?, ?, ?)",
            (signal_id, run_id, ticker, date, signal, model),
        )
        self.conn.commit()

    def log_metric(self, metric_id: str, run_id: str, ticker: str, metric_name: str, metric_value: float) -> None:
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO metrics VALUES (?, ?, ?, ?, ?)",
            (metric_id, run_id, ticker, metric_name, metric_value),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


def download_and_cache(
    tickers: Optional[list[str]] = None,
    start: str = "2020-01-01",
    end: Optional[str] = None,
    force_refresh: bool = False,
) -> dict[str, pd.DataFrame]:
    """
    Descarga precios para los tickers dados y los guarda en particiones Parquet
    individuales, además de registrar metadatos en el catálogo SQLite.

    Returns
    -------
    dict[str, pd.DataFrame]
        Diccionario ticker → DataFrame de precios (close ajustados), índice=fecha.
    """
    import json

    if tickers is None:
        tickers = ASSETS

    storage = ParquetStorage()
    catalog = SQLiteCatalog()

    results: dict[str, pd.DataFrame] = {}

    for ticker in tickers:
        try:
            path = storage._ticker_path(ticker)
            if not force_refresh and storage.exists(ticker):
                df = storage.read(ticker)
                if not df.empty:
                    results[ticker] = df
                    continue

            logger_msg = f"Descargando {ticker} desde {start}"
            if end:
                logger_msg += f" hasta {end}"

            data = yf.download(ticker, start=start, end=end)["Close"]
            if isinstance(data, pd.Series):
                data = data.to_frame(ticker)

            # Limpiar: quitar filas NaN al final, asegurar tipo float
            data = data.dropna(how="all")
            if data.empty:
                raise ValueError(f"Sin datos válidos para {ticker}")

            storage.write(data, ticker)
            results[ticker] = data

            # Registrar en catálogo
            run_id = f"ingest_{ticker}_{start}_{end or 'latest'}"
            catalog.log_run(
                run_id=run_id,
                timestamp=pd.Timestamp.today().isoformat(),
                dataset_rows=len(data),
                parameters=json.dumps({"ticker": ticker, "start": start, "end": end}),
            )

        except Exception as exc:
            import logging as _logging
            _logging.getLogger(__name__).error("Error descargando %s: %s", ticker, exc)

    catalog.close()
    return results