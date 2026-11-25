"""API v2 routes for the quantitative trading platform.

Exposes endpoints under /api/v2 for the already-implemented modules:
- Backtesting engine
- Trading strategies
- Target variables

ML, features and optimization modules will be added in subsequent weeks (see roadmap).
"""

from . import backtest, strategies, targets  # noqa: F401/F403 (register modules)