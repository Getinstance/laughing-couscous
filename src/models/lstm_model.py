"""
Modelo LSTM para previsão de preços de ações.
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
    """Modelo baseado em LSTM para previsão de séries temporais."""
    
    def __init__(self, lookback: int = 60, units: int = 50, dropout: float = 0.2):
        """
        Inicializar arquitetura do modelo LSTM.
        
        Args:
            lookback: Número de passos de tempo de entrada
            units: Número de unidades LSTM
            dropout: Taxa de dropout
        """
        self.lookback = lookback
        self.units = units
        self.dropout = dropout
        self.model = None
        self.history = None
        logger.info(f"Modelo LSTM inicializado com lookback={lookback}, units={units}, dropout={dropout}")
    
    def build(self) -> models.Sequential:
        """
        Construir a arquitetura do modelo LSTM.
        
        Returns:
            Modelo Sequential compilado
        """
        try:
            self.model = models.Sequential([
                # Primeira camada LSTM
                layers.LSTM(
                    units=self.units,
                    return_sequences=True,
                    input_shape=(self.lookback, 1)
                ),
                layers.Dropout(self.dropout),
                
                # Segunda camada LSTM
                layers.LSTM(
                    units=self.units,
                    return_sequences=True
                ),
                layers.Dropout(self.dropout),
                
                # Terceira camada LSTM
                layers.LSTM(
                    units=self.units,
                    return_sequences=False
                ),
                layers.Dropout(self.dropout),
                
                # Camadas densas
                layers.Dense(units=25, activation='relu'),
                layers.Dense(units=1)
            ])
            
            # Compilar modelo
            self.model.compile(
                optimizer='adam',
                loss='mean_squared_error',
                metrics=['mae']
            )
            
            logger.info("Modelo LSTM construído com sucesso")
            self.model.summary()
            return self.model
            
        except Exception as e:
            logger.error(f"Erro ao construir modelo: {str(e)}")
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
        Treinar o modelo LSTM.
        
        Args:
            X_train: Dados de entrada de treinamento
            y_train: Dados alvo de treinamento
            X_val: Dados de entrada de validação
            X_val: Dados alvo de validação
            epochs: Número de épocas
            batch_size: Tamanho do lote
            verbose: Nível de verbosidade
            
        Returns:
            Histórico de treinamento
        """
        if self.model is None:
            self.build()
        
        try:
            # Redimensionar dados para LSTM (amostras, passos de tempo, características)
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
            
            # Treinar modelo
            validation_data = (X_val, y_val) if X_val is not None else None
            
            self.history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=validation_data,
                callbacks=[early_stopping, reduce_lr],
                verbose=verbose
            )
            
            logger.info("Treinamento do modelo concluído")
            return self.history.history
            
        except Exception as e:
            logger.error(f"Erro durante o treinamento: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Fazer previsões usando o modelo treinado.
        
        Args:
            X: Dados de entrada
            
        Returns:
            Previsões
        """
        if self.model is None:
            raise ValueError("Modelo não construído ainda")
        
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
        Avaliar desempenho do modelo em dados de teste.
        
        Args:
            X_test: Dados de entrada de teste
            y_test: Dados alvo de teste
            scaler: Objeto MinMaxScaler para transformação inversa
            
        Returns:
            Dicionário com métricas de avaliação
        """
        try:
            # Fazer previsões
            predictions = self.predict(X_test)
            
            # Transformação inversa se dimensionador fornecido
            if scaler is not None:
                predictions = scaler.inverse_transform(predictions)
                y_test_scaled = scaler.inverse_transform(y_test.reshape(-1, 1))
            else:
                y_test_scaled = y_test.reshape(-1, 1)
            
            # Calcular métricas
            mae = mean_absolute_error(y_test_scaled, predictions)
            rmse = np.sqrt(mean_squared_error(y_test_scaled, predictions))
            mape = mean_absolute_percentage_error(y_test_scaled, predictions)
            
            metrics = {
                'MAE': mae,
                'RMSE': rmse,
                'MAPE': mape
            }
            
            logger.info(f"Métricas de Avaliação - MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Erro durante a avaliação: {str(e)}")
            raise
    
    def save(self, filepath: str):
        """Salvar o modelo treinado."""
        if self.model is None:
            raise ValueError("Modelo não construído ainda")
        
        try:
            self.model.save(filepath)
            logger.info(f"Modelo salvo em {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {str(e)}")
            raise
    
    def load(self, filepath: str):
        """Carregar um modelo treinado."""
        try:
            self.model = keras.models.load_model(filepath)
            logger.info(f"Modelo carregado de {filepath}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            raise
