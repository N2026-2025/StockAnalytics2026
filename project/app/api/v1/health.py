"""Endpoint de salud de la API."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    """Devuelve el estado de la API."""
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
    )