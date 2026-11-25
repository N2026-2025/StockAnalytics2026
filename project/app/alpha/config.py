"""Configuración del módulo Alpha Mining.

Todos los valores son sobreescritibles mediante variables de entorno prefijadas con `ALPHA_`.
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class AlphaSettings(BaseSettings):
    """Ajustes del motor de alpha mining."""

    # Ruta al dataset del Zoomcamp (raíz del repositorio)
    DATASET_PATH: str = os.getenv("ALPHA_DATASET_PATH", str(Path(__file__).resolve().parents[3] / "data.parquet"))

    # División temporal train / validación / test (fracciones)
    TRAIN_FRAC: float = Field(0.70, ge=0.0, le=1.0)
    VAL_FRAC: float = Field(0.15, ge=0.0, le=1.0)
    TEST_FRAC: float = Field(0.15, ge=0.0, le=1.0)

    # Embargo (días) entre train y test para evitar fuga de información
    EMBARGO_DAYS: int = Field(5, ge=0)

    # Umbrales de aceptación de hipótesis
    MIN_OOS_SHARPE: float = Field(0.5, description="Sharpe mínimo fuera de muestra")
    MIN_DEFLATED_SHARPE: float = Field(0.0, description="Deflated Sharpe mínimo")
    MAX_PBO: float = Field(0.30, description="Probabilidad máxima de backtest overfitting")
    MIN_TRADES: int = Field(10, description="Número mínimo de trades para considerar una hipótesis")

    # Backtest
    RISK_FREE_ANNUAL: float = Field(0.05, description="Tasa libre de riesgo anual (Treasury 10Y proxy)")
    TRADING_DAYS_YEAR: int = Field(252)

    model_config = {"env_file": ".env", "env_prefix": "ALPHA_", "extra": "ignore"}


settings = AlphaSettings()
