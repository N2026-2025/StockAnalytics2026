"""Utilidades de conversión y formateo para respuestas JSON-safe."""

from typing import Any

import pandas as pd


def to_json_safe(obj: Any) -> Any:
    """Convierte objetos de pandas/numpy a tipos serializables por JSON."""
    if isinstance(obj, pd.DataFrame):
        # {columna: {indice: valor}} - serializable directamente por JSON
        return obj.round(6).to_dict()
    if isinstance(obj, pd.Series):
        return obj.round(6).to_dict()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    return obj