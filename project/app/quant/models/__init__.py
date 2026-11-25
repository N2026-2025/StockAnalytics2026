"""Models for the quantitative trading platform.

ML models: Random Forest, XGBoost, LightGBM, Logistic Regression, LSTM.
Each model follows the same fit/predict/save interface.
"""

from .random_forest import RandomForestModel, train_random_forest
from .xgboost import XGBoostModel, train_xgboost
from .lightgbm import LightGBMModel, train_lightgbm
from .logistic_regression import LogisticRegressionModel, train_logistic_regression
from .lstm import LSTMModel, train_lstm
from .registry import ModelRegistry, ModelInfo, ModelName

__all__ = [
    "RandomForestModel", "train_random_forest",
    "XGBoostModel", "train_xgboost",
    "LightGBMModel", "train_lightgbm",
    "LogisticRegressionModel", "train_logistic_regression",
    "LSTMModel", "train_lstm",
    "ModelRegistry", "ModelInfo", "ModelName"
]