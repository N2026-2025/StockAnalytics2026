from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno (.env)."""

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Proyecto
    PROJECT_NAME: str = "Risk Analytics & Multi-Asset Argentina API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Activos por defecto (string separada por coma desde .env;
    # convertir a lista con .split(",") donde se usen)
    DEFAULT_TICKERS: str = "ZS=F,BZ=F,YPF"
    DEFAULT_CRYPTO_TICKERS: str = "BTC-USD,ETH-USD,SOL-USD,XRP-USD,BNB-USD"

    # Fechas por defecto para descarga de datos
    DEFAULT_START: str = "2020-01-01"
    DEFAULT_END: str | None = None

    # Motor cuantitativo
    MONTE_CARLO_SCENARIOS: int = 10000
    RANDOM_SEED: int = 42
    VAR_CONFIDENCE: float = 0.95

    # Caché
    CACHE_DIR: str = "data/cache"
    CACHE_ENABLED: bool = True

    @property
    def default_tickers_list(self) -> list[str]:
        return [t.strip() for t in self.DEFAULT_TICKERS.split(",") if t.strip()]

    @property
    def default_crypto_tickers_list(self) -> list[str]:
        return [t.strip() for t in self.DEFAULT_CRYPTO_TICKERS.split(",") if t.strip()]


settings = Settings()