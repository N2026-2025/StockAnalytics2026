"""Endpoints de Alpha Mining y Research Multimodal.

Expone el pipeline agéntico: generación de hipótesis, backtest automático y
filtro de overfitting sobre el dataset del Zoomcamp.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.alpha.hypothesis import generate_hypotheses
from app.alpha.ingestion import align_dataset, load_zoomcamp_dataset
from app.alpha.optimization import run_walk_forward_optimization
from app.alpha.pipeline import _ALPHA_COLUMNS, run_alpha_pipeline
from app.schemas.alpha import (
    AlphaRunRequest,
    AlphaRunResponse,
    DatasetSummaryResponse,
    HypothesisListResponse,
    WalkForwardRequest,
    WalkForwardResponse,
)
from app.core.logging import logger

router = APIRouter()


@router.get("/dataset/summary", response_model=DatasetSummaryResponse, summary="Resumen del dataset Zoomcamp")
async def dataset_summary() -> DatasetSummaryResponse:
    """Devuelve metadatos del dataset usado por el motor de alpha mining."""
    try:
        df = load_zoomcamp_dataset()
        start = df["Date"].min() if "Date" in df.columns else None
        end = df["Date"].max() if "Date" in df.columns else None
        return DatasetSummaryResponse(
            path=str(df.attrs.get("path", "data.parquet")),
            rows=len(df),
            columns=len(df.columns),
            tickers=int(df["Ticker"].nunique()) if "Ticker" in df.columns else 0,
            start_date=str(start.date()) if start is not None else None,
            end_date=str(end.date()) if end is not None else None,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/hypotheses", response_model=HypothesisListResponse, summary="Catálogo de hipótesis")
async def list_hypotheses(include_sentiment: bool = False) -> HypothesisListResponse:
    """Lista las hipótesis que el motor puede generar (estructura del Módulo 5)."""
    hyps = generate_hypotheses(include_sentiment=include_sentiment)
    return HypothesisListResponse(n_hypotheses=len(hyps), hypotheses=[h.as_dict() for h in hyps])


@router.post("/run", response_model=AlphaRunResponse, summary="Ejecutar pipeline de alpha mining")
async def run_alpha(request: AlphaRunRequest) -> AlphaRunResponse:
    """Corre generación → backtest → filtro de overfitting y devuelve el ranking."""
    try:
        result = run_alpha_pipeline(
            dataset_path=request.dataset_path,
            doc_paths=request.doc_paths,
            include_sentiment=request.include_sentiment,
            sample_rows=request.sample_rows,
        )
        return AlphaRunResponse(**result.as_dict())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("Error en pipeline de alpha: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/optimize", response_model=WalkForwardResponse, summary="Walk-forward optimization (Fase 2)")
async def optimize_walk_forward(request: WalkForwardRequest) -> WalkForwardResponse:
    """Ejecuta optimización walk-forward de parámetros para las 4 hipótesis con umbrales."""
    try:
        df = align_dataset(load_zoomcamp_dataset(path=request.dataset_path, columns=_ALPHA_COLUMNS))
        if request.sample_rows and len(df) > request.sample_rows:
            df = df.sample(n=request.sample_rows, random_state=42).sort_values("Date").reset_index(drop=True)

        results = run_walk_forward_optimization(df, n_splits=request.n_splits)
        return WalkForwardResponse(
            dataset_rows=len(df),
            n_hypotheses=len(results),
            results=[r.as_dict() for r in results],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("Error en optimización walk-forward: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))