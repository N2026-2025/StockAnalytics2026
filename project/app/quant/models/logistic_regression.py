"""Logistic Regression model for the quantitative trading platform."""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (roc_auc_score, accuracy_score, 
                             precision_score, recall_score, f1_score)

from app.quant.models.registry import ModelInfo, ModelRegistry, ModelName


class LogisticRegressionModel:
    """Logistic Regression model for binary classification on financial time series."""
    
    def __init__(self, C: float = 1.0, penalty: str = "l2",
                 solver: str = "lbfgs", max_iter: int = 1000,
                 random_state: int = 42):
        self.C = C
        self.penalty = penalty
        self.solver = solver
        self.max_iter = max_iter
        self.random_state = random_state
        self.model: Optional[LogisticRegression] = None
        self.trained_at: Optional[str] = None
        self.score: Optional[float] = None
        self.n_features: Optional[int] = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "LogisticRegressionModel":
        """Fit the Logistic Regression model."""
        self.model = LogisticRegression(
            C=self.C,
            penalty=self.penalty,
            solver=self.solver,
            max_iter=self.max_iter,
            random_state=self.random_state,
        )
        self.model.fit(X, y)
        self.trained_at = pd.Timestamp.now().isoformat()
        self.n_features = X.shape[1]
        self.score = self.model.score(X, y) if self.model is not None else None
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class labels."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> Optional[np.ndarray]:
        """Predict class probabilities."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        return None
    
    def feature_importances(self) -> Optional[pd.DataFrame]:
        """Return feature importances (coefficients) as DataFrame."""
        if self.model is None:
            return None
        coefficients = self.model.coef_[0]
        feature_names = getattr(self, 'feature_names_', None)
        if feature_names is None:
            feature_names = [f"feat_{i}" for i in range(len(coefficients))]
        imp_df = pd.DataFrame({
            "feature": feature_names,
            "coefficient": coefficients
        }).abs().sort_values("coefficient", ascending=False)
        return imp_df


def train_logistic_regression(X: pd.DataFrame, y: pd.Series,
                              model_name: ModelName = "logistic_regression",
                              **kwargs) -> tuple[LogisticRegressionModel, ModelInfo]:
    """Train a Logistic Regression model and return the model + info."""
    model = LogisticRegressionModel(**kwargs)
    model.fit(X, y)
    
    info = ModelInfo(
        name=model_name,
        trained_at=model.trained_at or pd.Timestamp.now().isoformat(),
        params=model.__dict__,
        score=model.score,
        n_features=model.n_features,
    )
    
    return model, info