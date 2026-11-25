"""Router agregado de la API v1."""

from fastapi import APIRouter

from app.api.v1 import health, assets, risk, stress, montecarlo, portfolio, alpha

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(stress.router, prefix="/stress", tags=["stress"])
api_router.include_router(montecarlo.router, prefix="/monte-carlo", tags=["monte-carlo"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(alpha.router, prefix="/alpha", tags=["alpha"])