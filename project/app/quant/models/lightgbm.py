"""LightGBM model for the quantitative trading platform."""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

try:
    import lightgbm as lgb
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

from app.quant.models.registry import ModelInfo, ModelRegistry, ModelName


class LightGBMModel:
    """LightGBM model for classification/regression on financial time series."""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = -1,
                 learning_rate: float = 0.1, random_state: int = 42,
                 model_type: str = "classifier"):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model_type = model_type
        self.model: Optional[Any] = None
        self.trained_at: Optional[str] = None
        self.score: Optional[float] = None
        self.n_features: Optional[int] = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "LightGBMModel":
        """Fit the LightGBM model."""
        if not HAS_LGBM:
            raise ImportError("lightgbm is not installed. Install with: pip install lightgbm")
        
        if self.model_type == "classifier":
            self.model = lgb.LGBMClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state,
            )
        else:
            self.model = lgb.LGBMRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state,
            )
        
        self.model.fit(X, y)
        self.trained_at = pd.Timestamp.now().isoformat()
        self.n_features = X.shape[1]
        self.score = self.model.score(X, y) if hasattr(self.model, "score") else None
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using the fitted model."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> Optional[np.ndarray]:
        """Predict class probabilities if available."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        return None
    
    def feature_importances(self) -> Optional[pd.DataFrame]:
        """Return feature importances as DataFrame."""
        if self.model is None or not hasattr(self.model, "feature_importances_"):
            return None
        importances = self.model.feature_importances_
        feature_names = getattr(self, 'feature_names_', None)
        if feature_names is None:
            feature_names = [f"feat_{i}" for i in range(len(importances))]
        return pd.DataFrame({
            "feature": feature_names,
            "importance": importances
        }).sort_values("importance", ascending=False)


def train_lightgbm(X: pd.DataFrame, y: pd.Series,
                   model_name: ModelName = "lightgbm",
                   **kwargs) -> tuple[LightGBMModel, ModelInfo]:
    """Train a LightGBM model and return the model + info."""
    model = LightGBMModel(**kwargs)
    model.fit(X, y)
    
    info = ModelInfo(
        name=model_name,
        trained_at=model.trained_at or pd.Timestamp.now().isoformat(),
        params=model.__dict__,
        score=model.score,
        n_features=model.n_features,
    )
    
    return model, info