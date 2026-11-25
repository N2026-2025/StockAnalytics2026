"""API v2 router for the quantitative trading platform.

Exposes endpoints under /api/v2 for the already-implemented modules:
- Backtesting engine
- Trading strategies
- Target variables

ML, features and optimization modules will be added in subsequent weeks (see roadmap).
"""

from fastapi import APIRouter

from app.api.v2 import backtest, strategies, targets

api_router = APIRouter()

api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(targets.router, prefix="/targets", tags=["targets"])

# TODO: Add ML, features, optimization routers in subsequent weeks
# api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
# api_router.include_router(features.router, prefix="/features", tags=["features"])
# api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])