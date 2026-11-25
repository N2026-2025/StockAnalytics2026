"""Generación de hipótesis de trading en Python (estructura del Módulo 5 del Zoomcamp).

Cada hipótesis sigue el formato pedido en el homework 5:

1. Market and scope
2. Investment thesis
3. Potential edge
4. Data and sources
5. Research approach (señal/regla en código)
6. Validation and risks

Se generan reglas deterministas sobre indicadores técnicos y, opcionalmente, se
superpone el sentimiento macro extraído de documentos (factores multimodales).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from app.core.logging import logger


@dataclass
class Hypothesis:
    """Hipótesis de inversión testeable."""

    name: str
    scope: str
    thesis: str
    edge: str
    data_sources: str
    test_code: str
    risks: str
    signal_fn: Callable[[pd.DataFrame, dict], pd.Series] = field(repr=False)
    horizon_days: int = 30

    def build_signal(self, df: pd.DataFrame, context: dict | None = None) -> pd.Series:
        """Genera la serie binaria de señal (1 = invertir, 0 = no)."""
        return self.signal_fn(df, context or {}).astype(int)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "scope": self.scope,
            "thesis": self.thesis,
            "edge": self.edge,
            "data_sources": self.data_sources,
            "test_code": self.test_code,
            "risks": self.risks,
            "horizon_days": self.horizon_days,
        }


def _col(df: pd.DataFrame, name: str, default: float = float("nan")) -> pd.Series:
    """Devuelve una columna como float; si no existe, rellena con default."""
    if name in df.columns:
        return pd.to_numeric(df[name], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def _signal_rsi_oversold(df: pd.DataFrame, ctx: dict) -> pd.Series:
    return (_col(df, "rsi") < 30).fillna(False)


def _signal_golden_cross(df: pd.DataFrame, ctx: dict) -> pd.Series:
    return (_col(df, "SMA10") > _col(df, "SMA20")).fillna(False)


def _signal_macd_bullish(df: pd.DataFrame, ctx: dict) -> pd.Series:
    return (_col(df, "macd") > _col(df, "macdsignal")).fillna(False)


def _signal_cci_oversold(df: pd.DataFrame, ctx: dict) -> pd.Series:
    return (_col(df, "cci") < -100).fillna(False)


def _signal_mfi_oversold(df: pd.DataFrame, ctx: dict) -> pd.Series:
    return (_col(df, "mfi") < 20).fillna(False)


def _signal_momentum_breakout(df: pd.DataFrame, ctx: dict) -> pd.Series:
    return ((_col(df, "roc") > 0.05) & (_col(df, "adx") > 25)).fillna(False)


def _signal_rsi_recovery(df: pd.DataFrame, ctx: dict) -> pd.Series:
    return ((_col(df, "rsi") > 40) & (_col(df, "rsi") < 60) & (_col(df, "plus_di") > _col(df, "minus_di"))).fillna(False)


def _signal_sentiment_overlay(df: pd.DataFrame, ctx: dict) -> pd.Series:
    """Momentum + sentimiento macro positivo (si hay documentos)."""
    macro = float(ctx.get("macro_sentiment", 0.0))
    base = ((_col(df, "roc") > 0.0) & (_col(df, "rsi") < 60)).fillna(False)
    return base & (macro >= 0.0)


def generate_hypotheses(include_sentiment: bool = False) -> list[Hypothesis]:
    """Devuelve el catálogo de hipótesis a testear."""
    hyps = [
        Hypothesis(
            name="rsi_oversold_mean_reversion",
            scope="Mayores acciones de India/EU/US del dataset Zoomcamp, horizonte 30 días.",
            thesis="Tras una caída por sobreventa (RSI<30) el precio tiende a revertir a la media.",
            edge="Sobre-reacción conductual de corto plazo en acciones con cobertura limitada.",
            data_sources="data.parquet (indicador RSI), target growth_future_30d.",
            test_code="signal = df['rsi'] < 30",
            risks="Puede comprar cuchillos cayendo; sensible a régimen bajista y costos.",
            signal_fn=_signal_rsi_oversold,
        ),
        Hypothesis(
            name="golden_cross_trend",
            scope="Universo del dataset, horizonte 30 días.",
            thesis="Cuando la media corta supera a la larga, el momentum de tendencia persiste.",
            edge="Captura regímenes alcistas sostenidos que el mercado tarda en precioar.",
            data_sources="data.parquet (SMA10, SMA20), target growth_future_30d.",
            test_code="signal = df['SMA10'] > df['SMA20']",
            risks="Señales tardías en mercados laterales; whipsaws.",
            signal_fn=_signal_golden_cross,
        ),
        Hypothesis(
            name="macd_bullish_momentum",
            scope="Universo del dataset, horizonte 30 días.",
            thesis="MACD por encima de su señal indica aceleración del momentum.",
            edge="Combina tendencia y velocidad; filtra ruido de corto plazo.",
            data_sources="data.parquet (macd, macdsignal), target growth_future_30d.",
            test_code="signal = df['macd'] > df['macdsignal']",
            risks="Falsos cruces en baja volatilidad.",
            signal_fn=_signal_macd_bullish,
        ),
        Hypothesis(
            name="cci_oversold_reversal",
            scope="Universo del dataset, horizonte 30 días.",
            thesis="CCI<-100 marca sobreventa extrema con reversión esperada.",
            edge="Detecta extremos de desviación respecto a la media típica.",
            data_sources="data.parquet (cci), target growth_future_30d.",
            test_code="signal = df['cci'] < -100",
            risks="Sobreventa puede prolongarse; alta varianza.",
            signal_fn=_signal_cci_oversold,
        ),
        Hypothesis(
            name="mfi_oversold_flow",
            scope="Universo del dataset, horizonte 30 días.",
            thesis="MFI<20 indica presión de flujo vendedor agotada (oversold ponderado por volumen).",
            edge="Incorpora volumen, no solo precio.",
            data_sources="data.parquet (mfi), target growth_future_30d.",
            test_code="signal = df['mfi'] < 20",
            risks="Liquidez irregular distorsiona el MFI.",
            signal_fn=_signal_mfi_oversold,
        ),
        Hypothesis(
            name="momentum_breakout_adx",
            scope="Universo del dataset, horizonte 30 días.",
            thesis="ROC alto con ADX>25 confirma tendencia fuerte y continuación.",
            edge="Doble filtro (retorno + fuerza de tendencia) reduce falsos positivos.",
            data_sources="data.parquet (roc, adx), target growth_future_30d.",
            test_code="signal = (df['roc'] > 0.05) & (df['adx'] > 25)",
            risks="Entradas tardías; reversión abrupta de tendencia.",
            signal_fn=_signal_momentum_breakout,
        ),
        Hypothesis(
            name="rsi_recovery_with_di",
            scope="Universo del dataset, horizonte 30 días.",
            thesis="RSI en zona media con +DI>-DI indica recuperación saludable.",
            edge="Evita extremos y confirma dirección con DI.",
            data_sources="data.parquet (rsi, plus_di, minus_di), target growth_future_30d.",
            test_code="signal = (40 < df['rsi'] < 60) & (df['plus_di'] > df['minus_di'])",
            risks="Señal frecuente; costos de transacción erosionan retorno.",
            signal_fn=_signal_rsi_recovery,
        ),
    ]

    if include_sentiment:
        hyps.append(
            Hypothesis(
                name="sentiment_overlay_momentum",
                scope="Universo del dataset + documentos (10-K/earnings/news).",
                thesis="Momentum positivo amplificado por sentimiento macro favorable en documentos.",
                edge="El LLM/baseline detecta tono de guía y riesgos antes de que se refleje en precio.",
                data_sources="data.parquet (roc, rsi) + sentimiento de documentos.",
                test_code="signal = (df['roc'] > 0) & (df['rsi'] < 60) & (macro_sentiment >= 0)",
                risks="Sesgo del léxico/LLM; posible look-ahead si los documentos no están fechados.",
                signal_fn=_signal_sentiment_overlay,
            )
        )

    logger.info("Generadas %d hipótesis", len(hyps))
    return hyps