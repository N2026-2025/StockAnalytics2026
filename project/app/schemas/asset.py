"""Schemas para endpoints de activos y precios."""

from pydantic import BaseModel
from typing import Optional, List


class PriceResponse(BaseModel):
    ticker: str
    prices: dict[str, Optional[float]]  # fecha ISO -> precio
    last_price: Optional[float]
    n_points: int


class CorrelationResponse(BaseModel):
    matrix: dict[str, dict[str, Optional[float]]]
    n_points: int