"""Model registry for the quantitative trading platform.

Handles persistence, loading, and versioning of trained ML models.
Supports scikit-learn, XGBoost, LightGBM, Logistic Regression, and LSTM models.
"""

from pathlib import Path
from typing import Dict, Optional, Any, Literal
import joblib
import numpy as np
import pandas as pd

try:
    import tensorflow as tf
    HAS_TF = True
except ImportError:
    HAS_TF = False

ModelName = Literal["random_forest", "xgboost", "lightgbm", "logistic_regression", "lstm"]

MODEL_DIR = Path("models")


class ModelInfo:
    """Metadata for a trained model."""
    
    def __init__(self, name: ModelName, trained_at: str, params: dict, 
                 score: Optional[float] = None, n_features: Optional[int] = None):
        self.name = name
        self.trained_at = trained_at
        self.params = params
        self.score = score
        self.n_features = n_features
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "trained_at": self.trained_at,
            "params": self.params,
            "score": self.score,
            "n_features": self.n_features,
        }


class ModelRegistry:
    """Registry for managing trained ML models."""
    
    def __init__(self, model_dir: str = str(MODEL_DIR)):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.info: Dict[str, ModelInfo] = {}
    
    def save(self, name: ModelName, model: Any, info: ModelInfo) -> None:
        """Save a trained model to disk."""
        path = self.model_dir / f"{name}.joblib"
        joblib.dump(model, path)
        self.models[name] = model
        self.info[name] = info
    
    def load(self, name: ModelName) -> Any:
        """Load a trained model from disk."""
        path = self.model_dir / f"{name}.joblib"
        if path.exists():
            model = joblib.load(path)
            self.models[name] = model
            return model
        raise FileNotFoundError(f"Model {name} not found at {path}")
    
    def get_info(self, name: ModelName) -> ModelInfo:
        """Get metadata for a model."""
        return self.info.get(name, ModelInfo(name="unknown", trained_at="", params={}))
    
    def list_models(self) -> list[ModelName]:
        """List registered model names."""
        return [name for name in ModelName if name in self.models]