"""Ingestión de datos para el motor de alpha mining.

Carga el dataset del Zoomcamp (`data.parquet`) y documentos de texto (10-K, earnings calls,
noticias macro). Los datos se alinean temporalmente para backtestear sobre el mismo universo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from app.alpha.config import settings
from app.core.logging import logger


def load_zoomcamp_dataset(path: Optional[str] = None, columns: Optional[list[str]] = None) -> pd.DataFrame:
    """Carga el dataset del Zoomcamp y normaliza tipos/columnas clave."""
    p = Path(path or settings.DATASET_PATH)
    if not p.exists():
        raise FileNotFoundError(f"Dataset del Zoomcamp no encontrado en: {p}")

    logger.info("Cargando dataset del Zoomcamp desde %s", p)
    df = pd.read_parquet(p, columns=columns) if columns else pd.read_parquet(p)

    # Normalizar tipos
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    if "Ticker" in df.columns:
        df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()

    # Asegurar columnas clave usadas por el motor
    required = ["Date", "Ticker", "Close_x", "growth_future_30d", "is_positive_growth_30d_future"]
    for col in required:
        if col not in df.columns:
            logger.warning("Columna clave '%s' ausente en el dataset; se usará NaN", col)
            df[col] = pd.Series(dtype="float64")

    logger.info("Dataset cargado: %d filas, %d columnas, %d tickers",
                df.shape[0], df.shape[1], df["Ticker"].nunique())
    return df


def load_text_documents(paths: list[str]) -> list[dict]:
    """Carga documentos de texto (10-K, earnings calls, noticias macro)."""
    docs = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            logger.warning("Documento no encontrado: %s", p)
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            logger.error("Error leyendo %s: %s", p, exc)
            continue
        docs.append({"path": str(path), "content": content, "name": path.name})
    return docs


def align_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Alinea el dataset a un índice temporal por ticker y elimina NaN del target."""
    if "Date" not in df.columns:
        return df
    df = df.copy()
    df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    # Eliminar filas sin target
    if "is_positive_growth_30d_future" in df.columns:
        df = df.dropna(subset=["is_positive_growth_30d_future"])
    return df