"""Storage handler for Parquet files and SQLite catalog."""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np


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
        """Escribe un DataFrame de precios al archivo Parquet del ticker.

        Garantiza que la columna 'Date' exista siempre (se resetea el índice).
        """
        path = self._ticker_path(ticker)
        out = df.copy()
        # Siempre resetear índice Datetime a columna 'Date'
        if isinstance(out.index, pd.DatetimeIndex):
            out = out.reset_index()
            # Si el índice no tenía nombre, llamarlo 'Date'
            if out.columns[0] != "Date":
                out = out.rename(columns={out.columns[0]: "Date"})
        # Ahora 'Date' es columna segura
        # Seleccionar/renombrar columna de precio a ticker
        price_col = "Close" if "Close" in out.columns else (out.columns[0] if len(out.columns) > 0 and out.columns[0] != "Date" else None)
        if price_col:
            if ticker not in out.columns:
                if "Date" in out.columns:
                    out = out[["Date", price_col]].rename(columns={price_col: ticker})
                else:
                    out = out.reset_index().rename(columns={"index": "Date"})
                    if "Date" in out.columns and price_col in out.columns:
                        out = out[["Date", price_col]].rename(columns={price_col: ticker})
            elif ticker in out.columns and "Date" in out.columns:
                out = out[["Date", ticker]]
        # Si no hay columna de precio identificada, usar la primera numérica distinta a Date
        if not price_col and len(out.columns) > 1:
            numeric_cols = out.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0 and numeric_cols[0] != "Date":
                if "Date" in out.columns:
                    out = out[["Date", numeric_cols[0]]].rename(columns={numeric_cols[0]: ticker})
                else:
                    out = out.reset_index()
                    if len(out.columns) >= 2:
                        out = out.iloc[:, [0, 1]].rename(columns={out.columns[1]: ticker})
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
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        c = self.conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS runs ("
            "run_id TEXT PRIMARY KEY, "
            "timestamp TEXT, "
            "dataset_rows INTEGER, "
            "parameters TEXT"
            ")"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS signals ("
            "signal_id TEXT PRIMARY KEY, "
            "run_id TEXT, "
            "ticker TEXT, "
            "date TEXT, "
            "signal REAL, "
            "model TEXT, "
            "FOREIGN KEY (run_id) REFERENCES runs(run_id)"
            ")"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS metrics ("
            "metric_id TEXT PRIMARY KEY, "
            "run_id TEXT, "
            "ticker TEXT, "
            "metric_name TEXT, "
            "metric_value REAL, "
            "FOREIGN KEY (run_id) REFERENCES runs(run_id)"
            ")"
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