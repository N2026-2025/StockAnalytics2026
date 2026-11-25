"""Random Forest model for the quantitative trading platform."""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (roc_auc_score, accuracy_score, 
                             precision_score, recall_score, f1_score)

from app.quant.models.registry import ModelInfo, ModelRegistry, ModelName


class RandomForestModel:
    """Random Forest model for classification/regression on financial time series."""
    
    def __init__(self, n_estimators: int = 100, max_depth: Optional[int] = None,
                 min_samples_split: int = 2, min_samples_leaf: int = 1,
                 random_state: int = 42, model_type: str = "classifier"):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.model_type = model_type
        self.model: Optional[Any] = None
        self.trained_at: Optional[str] = None
        self.score: Optional[float] = None
        self.n_features: Optional[int] = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RandomForestModel":
        """Fit the Random Forest model."""
        if self.model_type == "classifier":
            self.model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.random_state,
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.random_state,
            )
        
        self.model.fit(X, y)
        self.trained_at = pd.Timestamp.now().isoformat()
        self.n_features = X.shape[1]
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
    
    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """Return the model score (R^2 for regression, accuracy for classification)."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        return self.model.score(X, y)
    
    def feature_importances(self) -> Optional[pd.DataFrame]:
        """Return feature importances as DataFrame."""
        if self.model is None:
            return None
        importances = self.model.feature_importances_
        feature_names = getattr(self, 'feature_names_', None)
        if feature_names is None:
            feature_names = [f"feat_{i}" for i in range(len(importances))]
        return pd.DataFrame({
            "feature": feature_names,
            "importance": importances
        }).sort_values("importance", ascending=False)


def train_random_forest(X: pd.DataFrame, y: pd.Series, 
                        model_name: ModelName = "random_forest",
                        **kwargs) -> tuple[RandomForestModel, ModelInfo]:
    """Train a Random Forest model and return the model + info."""
    model = RandomForestModel(**kwargs)
    model.fit(X, y)
    
    info = ModelInfo(
        name=model_name,
        trained_at=model.trained_at or pd.Timestamp.now().isoformat(),
        params=model.__dict__,
        score=model.score(X, y) if model.model is not None else None,
        n_features=model.n_features,
    )
    
    return model, info