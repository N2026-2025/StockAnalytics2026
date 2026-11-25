"""Schemas comunes (respuestas de error, salud, etc.)."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None