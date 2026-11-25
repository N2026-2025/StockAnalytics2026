"""LSTM model for the quantitative trading platform."""

from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TF = True
except ImportError:
    HAS_TF = False


def _prepare_lstm_data(X: pd.DataFrame, y: pd.Series, lookback: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare X and y data for LSTM: shape (samples, timesteps, features)."""
    if isinstance(X, pd.DataFrame):
        X_array = X.values
    else:
        X_array = X
    
    n_samples = len(X_array) - lookback
    if n_samples <= 0:
        raise ValueError(f"Not enough data for lookback={lookback}, have {len(X_array)} samples")
    
    X_lstm = np.zeros((n_samples, lookback, X_array.shape[1] if len(X_array.shape) > 1 else 1))
    y_lstm = y.values[n_samples:] if isinstance(y, pd.Series) else y[n_samples:]
    
    for i in range(n_samples):
        X_lstm[i, :, :] = X_array[i:i+lookback, :]
    
    return X_lstm, y_lstm


class LSTMModel:
    """LSTM (Long Short-Term Memory) model for time series forecasting or classification."""
    
    def __init__(self, lookback: int = 20, n_features: int = 1,
                 units: int = 50, n_layers: int = 1, 
                 epochs: int = 20, batch_size: int = 32,
                 random_state: int = 42):
        self.lookback = lookback
        self.n_features = n_features
        self.units = units
        self.n_layers = n_layers
        self.epochs = epochs
        self.batch_size = batch_size
        self.random_state = random_state
        self.model: Optional[Any] = None
        self.trained_at: Optional[str] = None
        self.score: Optional[float] = None
        self.history = None
    
    def build_model(self, input_shape: Tuple[int, int]) -> Any:
        """Build the LSTM neural network model."""
        if not HAS_TF:
            raise ImportError("TensorFlow/Keras is not installed. Install with: pip install tensorflow")
        
        model = keras.Sequential()
        
        # First LSTM layer with return_sequences if multiple layers
        for i in range(self.n_layers):
            return_seq = True if i < self.n_layers - 1 else False
            model.add(layers.LSTM(
                self.units, 
                return_sequences=return_seq,
                input_shape=input_shape if i == 0 else (input_shape[0], self.units)
            ))
            model.add(layers.Dropout(0.2))
        
        # Output layer
        model.add(layers.Dense(1))
        
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "LSTMModel":
        """Fit the LSTM model."""
        if not HAS_TF:
            raise ImportError("TensorFlow/Keras is not installed")
        
        # Prepare data
        X_lstm, y_lstm = _prepare_lstm_data(X, y, self.lookback)
        
        # Build model
        input_shape = (self.lookback, X.shape[1] if isinstance(X, pd.DataFrame) and X.shape[1] > 1 else 1)
        self.model = self.build_model(input_shape)
        
        # Train
        self.history = self.model.fit(
            X_lstm, y_lstm,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=0.2,
            verbose=0
        )
        
        self.trained_at = pd.Timestamp.now().isoformat()
        # Evaluate on training data
        if self.model is not None:
            self.score = self.model.evaluate(X_lstm, y_lstm, verbose=0)
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using the fitted LSTM model."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        
        X_lstm, _ = _prepare_lstm_data(X, pd.Series(0, index=range(len(X))), self.lookback)
        predictions = self.model.predict(X_lstm, verbose=0).flatten()
        return predictions
    
    def predict_direction(self, X: pd.DataFrame) -> np.ndarray:
        """Predict direction (up/down) based on LSTM output."""
        preds = self.predict(X)
        return (preds > 0).astype(int)  # 1 if positive, 0 if negative/zero
    
    def feature_importances(self) -> Optional[pd.DataFrame]:
        """LSTM doesn't have traditional feature importances; return None."""
        return None


def train_lstm(X: pd.DataFrame, y: pd.Series,
               model_name: ModelName = "lstm",
               **kwargs) -> tuple[LSTMModel, dict]:
    """Train an LSTM model and return the model + training history."""
    model = LSTMModel(**kwargs)
    model.fit(X, y)
    
    return model, model.history.history if model.history else {}