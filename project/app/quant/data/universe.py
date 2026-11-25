"""Universo de activos y benchmark para la plataforma cuantitativa."""

ASSETS = [
    "SPY",     # S&P 500 ETF
    "QQQ",     # Nasdaq-100 ETF
    "IWM",     # Russell 2000
    "EEM",     # Mercados emergentes
    "GLD",     # Oro
    "TLH",     # Treasury Long Bond
    "SLV",     # Plata
    "USO",     # Petróleo crudo
    "BTC-USD", # Bitcoin
    "ETH-USD", # Ethereum
    "SOL-USD", # Solana
    "ZS=F",    # Soja Chicago (activo ARG existente)
    "BZ=F",    # Petróleo Brent (activo ARG existente)
    "YPF",     # YPF S.A. (activo ARG existente)
]

BENCHMARK = "SPY"

# Universo expandido para ML y estrategias; se conservan los activos ARG
ASSET_INFO = {
    "SPY":  {"name": "S&P 500 ETF",  "type": "equity", "sector": "large_cap_us"},
    "QQQ":  {"name": "Nasdaq-100 ETF", "type": "equity", "sector": "large_cap_us"},
    "IWM":  {"name": "Russell 2000",   "type": "equity", "sector": "small_cap_us"},
    "EEM":  {"name": "Emerging Markets", "type": "equity", "sector": "emerging"},
    "GLD":  {"name": "Gold ETF",     "type": "commodity", "sector": "precious_metal"},
    "TLH":  {"name": "Long Bond",    "type": "bond", "sector": "treasury"},
    "SLV":  {"name": "Silver ETF",   "type": "commodity", "sector": "precious_metal"},
    "USO":  {"name": "Oil ETF",      "type": "commodity", "sector": "energy"},
    "BTC-USD": {"name": "Bitcoin", "type": "crypto", "sector": "crypto"},
    "ETH-USD": {"name": "Ethereum", "type": "crypto", "sector": "crypto"},
    "SOL-USD": {"name": "Solana", "type": "crypto", "sector": "crypto"},
    "ZS=F":  {"name": "Soja Chicago", "type": "future", "sector": "agro_ar"},
    "BZ=F":  {"name": "Petroleo Brent", "type": "future", "sector": "energy_ar"},
    "YPF":   {"name": "YPF S.A.", "type": "stock", "sector": "stock_ar"},
}

BENCHMARK_INFO = {"SPY": {"name": "S&P 500 ETF", "type": "equity", "sector": "large_cap_us"}}


def get_universe() -> list[str]:
    """Retorna lista de tickers del universo."""
    return ASSETS.copy()


def get_asset_info(ticker: str) -> dict:
    """Retorna metadatos de un activo."""
    return ASSET_INFO.get(ticker, BENCHMARK_INFO.get(ticker, {"name": ticker, "type": "unknown"}))