"""FastAPI application entry point for Risk Analytics & Multi-Asset Argentina API."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging, logger

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Motor cuantitativo de riesgo de mercado para activos multi-asset "
        "vinculados a Argentina (soja, petróleo Brent, YPF) y criptoactivos. "
        "Incluye VaR histórico/paramétrico, Expected Shortfall, pruebas de estrés "
        "con escenarios macro argentinos y simulación de Monte Carlo (10k escenarios)."
    ),
    contact={"name": "Quant Developer / ML Engineer", "email": "quant@example.com"},
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"], summary="Health check")
async def health() -> dict:
    """Endpoint de salud de la API."""
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)