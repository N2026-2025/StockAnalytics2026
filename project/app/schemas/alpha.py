"""Schemas para los endpoints de Alpha Mining."""

from pydantic import BaseModel


class DatasetSummaryResponse(BaseModel):
    path: str
    rows: int
    columns: int
    tickers: int
    start_date: str | None = None
    end_date: str | None = None


class HypothesisInfo(BaseModel):
    name: str
    scope: str
    thesis: str
    edge: str
    data_sources: str
    test_code: str
    risks: str
    horizon_days: int


class HypothesisListResponse(BaseModel):
    n_hypotheses: int
    hypotheses: list[HypothesisInfo]


class AlphaRunRequest(BaseModel):
    dataset_path: str | None = None
    doc_paths: list[str] | None = None
    include_sentiment: bool = False
    sample_rows: int | None = 20000


class AlphaRunResponse(BaseModel):
    dataset_rows: int
    n_hypotheses: int
    n_passed: int
    n_failed: int
    macro_sentiment: float
    rankings: list[dict]
    overfitting_reports: list[dict]


class WalkForwardRequest(BaseModel):
    dataset_path: str | None = None
    sample_rows: int | None = 20000
    n_splits: int = 5


class WalkForwardResponse(BaseModel):
    dataset_rows: int
    n_hypotheses: int
    results: list[dict]