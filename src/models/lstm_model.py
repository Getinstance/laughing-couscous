"""
LSTM model for stock price prediction.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import logging
from typing import Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LSTMModel:
    """LSTM-based model for time series prediction."""
    
    def __init__(self, lookback: int = 60, units: int = 50, dropout: float = 0.2):
        """
        Initialize LSTM model architecture.
        
        Args:
            lookback: Number of input time steps
            units: Number of LSTM units
            dropout: Dropout rate
        """
        self.lookback = lookback
        self.units = units
        self.dropout = dropout
        self.model = None
        self.history = None
        logger.info(f"Initialized LSTM Model with lookback={lookback}, units={units}, dropout={dropout}")
    
    def build(self) -> models.Sequential:
        """
        Build the LSTM model architecture.
        
        Returns:
            Compiled Sequential model
        """
        try:
            self.model = models.Sequential([
                # First LSTM layer
                layers.LSTM(
                    units=self.units,
                    return_sequences=True,
                    input_shape=(self.lookback, 1)
                ),
                layers.Dropout(self.dropout),
                
                # Second LSTM layer
                layers.LSTM(
                    units=self.units,
                    return_sequences=True
                ),
                layers.Dropout(self.dropout),
                
                # Third LSTM layer
                layers.LSTM(
                    units=self.units,
                    return_sequences=False
                ),
                layers.Dropout(self.dropout),
                
                # Dense layers
                layers.Dense(units=25, activation='relu'),
                layers.Dense(units=1)
            ])
            
            # Compile model
            self.model.compile(
                optimizer='adam',
                loss='mean_squared_error',
                metrics=['mae']
            )
            
            logger.info("LSTM model built successfully")
            self.model.summary()
            return self.model
            
        except Exception as e:
            logger.error(f"Error building model: {str(e)}")
            raise
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        epochs: int = 50,
        batch_size: int = 32,
        verbose: int = 1
    ) -> Dict:
        """
        Train the LSTM model.
        
        Args:
            X_train: Training input data
            y_train: Training target data
            X_val: Validation input data
            X_val: Validation target data
            epochs: Number of epochs
            batch_size: Batch size
            verbose: Verbosity level
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build()
        
        try:
            # Reshape data for LSTM (samples, timesteps, features)
            X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
            if X_val is not None:
                X_val = X_val.reshape((X_val.shape[0], X_val.shape[1], 1))
            
            # Callbacks
            early_stopping = EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            )
            
            reduce_lr = ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            )
            
            # Train model
            validation_data = (X_val, y_val) if X_val is not None else None
            
            self.history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=validation_data,
                callbacks=[early_stopping, reduce_lr],
                verbose=verbose
            )
            
            logger.info("Model training completed")
            return self.history.history
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the trained model.
        
        Args:
            X: Input data
            
        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not built yet")
        
        X = X.reshape((X.shape[0], X.shape[1], 1))
        predictions = self.model.predict(X, verbose=0)
        return predictions
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        scaler=None
    ) -> Dict[str, float]:
        """
        Evaluate model performance on test data.
        
        Args:
            X_test: Test input data
            y_test: Test target data
            scaler: MinMaxScaler object for inverse transformation
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            # Make predictions
            predictions = self.predict(X_test)
            
            # Inverse transform if scaler provided
            if scaler is not None:
                predictions = scaler.inverse_transform(predictions)
                y_test_scaled = scaler.inverse_transform(y_test.reshape(-1, 1))
            else:
                y_test_scaled = y_test.reshape(-1, 1)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test_scaled, predictions)
            rmse = np.sqrt(mean_squared_error(y_test_scaled, predictions))
            mape = mean_absolute_percentage_error(y_test_scaled, predictions)
            
            metrics = {
                'MAE': mae,
                'RMSE': rmse,
                'MAPE': mape
            }
            
            logger.info(f"Evaluation Metrics - MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            raise
    
    def save(self, filepath: str):
        """Save the trained model."""
        if self.model is None:
            raise ValueError("Model not built yet")
        
        try:
            self.model.save(filepath)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load(self, filepath: str):
        """Load a trained model."""
        try:
            self.model = keras.models.load_model(filepath)
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
