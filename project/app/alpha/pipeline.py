"""Pipeline orquestador de alpha mining: genera → backtestea → filtra → ranking.

Reutiliza el dataset del Zoomcamp y el motor de riesgo existente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from app.alpha.backtest import backtest_signal
from app.alpha.config import settings
from app.alpha.hypothesis import generate_hypotheses
from app.alpha.ingestion import align_dataset, load_zoomcamp_dataset, load_text_documents
from app.alpha.overfitting import evaluate_overfitting
from app.alpha.sentiment import aggregate_document_sentiment
from app.core.logging import logger

_ALPHA_COLUMNS = [
    "Date", "Ticker", "Close_x", "growth_future_30d", "is_positive_growth_30d_future",
    "rsi", "macd", "macdsignal", "cci", "mfi",
    "SMA10", "SMA20",
    "roc", "adx", "plus_di", "minus_di",
]


@dataclass
class AlphaPipelineResult:
    dataset_rows: int
    n_hypotheses: int
    n_passed: int
    n_failed: int
    macro_sentiment: float = 0.0
    rankings: list[dict] = field(default_factory=list)
    overfitting_reports: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "dataset_rows": self.dataset_rows,
            "n_hypotheses": self.n_hypotheses,
            "n_passed": self.n_passed,
            "n_failed": self.n_failed,
            "macro_sentiment": round(self.macro_sentiment, 4),
            "rankings": self.rankings,
            "overfitting_reports": self.overfitting_reports,
        }


def run_alpha_pipeline(
    dataset_path: Optional[str] = None,
    doc_paths: Optional[list[str]] = None,
    include_sentiment: bool = False,
    sample_rows: Optional[int] = None,
) -> AlphaPipelineResult:
    """Ejecuta el pipeline completo de generación y validación de hipótesis."""
    df = align_dataset(load_zoomcamp_dataset(path=dataset_path, columns=_ALPHA_COLUMNS))

    # Orden temporal global (los folds de walk-forward son por fecha).
    if "Date" in df.columns:
        df = df.sort_values("Date").reset_index(drop=True)

    # Muestreo opcional determinista para endpoints interactivos.
    if sample_rows and len(df) > sample_rows:
        df = df.sample(n=sample_rows, random_state=42).sort_values("Date").reset_index(drop=True)
        logger.info("Submuestreo determinista a %d filas", sample_rows)

    macro_sentiment = 0.0
    if include_sentiment and doc_paths:
        docs = load_text_documents(doc_paths)
        agg = aggregate_document_sentiment(docs)
        macro_sentiment = float(agg.get("macro_sentiment", 0.0))
        logger.info("Sentimiento macro agregado: %.4f", macro_sentiment)

    hypotheses = generate_hypotheses(include_sentiment=include_sentiment)
    n_hypotheses = len(hypotheses)
    n_passed = 0
    n_failed = 0
    rankings: list[dict] = []
    overfitting_reports: list[dict] = []

    for hyp in hypotheses:
        try:
            signal = hyp.build_signal(df, {"macro_sentiment": macro_sentiment})
            result = backtest_signal(df, signal, hypothesis_name=hyp.name, context={"horizon_days": hyp.horizon_days})
            if result is None:
                n_failed += 1
                continue

            mask = signal.values == 1
            trade_returns = (
                df.loc[mask, "growth_future_30d"].astype(float).dropna() - 1.0
            )

            report = evaluate_overfitting(
                hypothesis_name=hyp.name,
                df=df,
                signal=signal,
                trade_returns=trade_returns,
                full_sharpe=result.sharpe_annualized,
                n_trials=n_hypotheses,
                settings_obj=settings,
            )
            overfitting_reports.append(report.as_dict())

            if report.passes_filter:
                n_passed += 1
            else:
                n_failed += 1

            rankings.append(
                {
                    "hypothesis": hyp.name,
                    "n_trades": result.n_trades,
                    "sharpe_annualized": round(result.sharpe_annualized, 4),
                    "cagr": round(result.cagr, 6),
                    "win_rate": round(result.win_rate, 4),
                    "trades_per_day": round(result.trades_per_day, 4),
                    "max_drawdown": round(result.max_drawdown, 6),
                    "deflated_sharpe": round(report.deflated_sharpe, 4),
                    "pbo": round(report.pbo_bootstrap, 4),
                    "passes_filter": report.passes_filter,
                    "start_date": result.start_date,
                    "end_date": result.end_date,
                }
            )
        except Exception as exc:
            logger.error("Fallo en hipótesis %s: %s", hyp.name, exc)
            n_failed += 1

    rankings.sort(key=lambda r: r["sharpe_annualized"], reverse=True)
    logger.info(
        "Pipeline completado: %d hipótesis, %d pasaron, %d fallaron",
        n_hypotheses,
        n_passed,
        n_failed,
    )
    return AlphaPipelineResult(
        dataset_rows=len(df),
        n_hypotheses=n_hypotheses,
        n_passed=n_passed,
        n_failed=n_failed,
        macro_sentiment=macro_sentiment,
        rankings=rankings,
        overfitting_reports=overfitting_reports,
    )