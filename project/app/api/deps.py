"""Dependencias de la API: caché de datos y validación de tickers."""

from functools import lru_cache
from typing import Optional

import pandas as pd

from app.core.config import settings
from app.core.logging import logger
from app.services.data_engine import DataEngine


@lru_cache()
def get_data_engine() -> DataEngine:
    """Devuelve una instancia singleton del motor de datos con caché."""
    return DataEngine(cache_dir=settings.CACHE_DIR, enabled=settings.CACHE_ENABLED)


def validate_tickers(tickers: Optional[list[str]] = None) -> list[str]:
    """Valida y normaliza la lista de tickers solicitada."""
    if not tickers:
        return list(settings.DEFAULT_TICKERS)
    return [t.strip().upper() for t in tickers if t.strip()]