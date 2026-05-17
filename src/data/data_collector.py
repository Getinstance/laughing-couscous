"""
Módulo de coleta de dados de preços de ações usando yfinance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataCollector:
    """Coleta e processa dados de ações do Yahoo Finance."""
    
    def __init__(self, symbol: str, start_date: str = None, end_date: str = None):
        """
        Inicializa o coletor de dados.
        
        Args:
            symbol: Símbolo do ticker da ação (ex: 'AAPL')
            start_date: Data de início no formato 'YYYY-MM-DD' (padrão: -5 anos)
            end_date: Data de término no formato 'YYYY-MM-DD' (padrão: hoje)
        """
        self.symbol = symbol
        
        # Set default dates if not provided
        if end_date is None:
            self.end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.end_date = end_date
            
        if start_date is None:
            self.start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        else:
            self.start_date = start_date
            
        self.df = None
        logger.info(f"StockDataCollector inicializado para {symbol} de {self.start_date} a {self.end_date}")
    
    def download(self) -> pd.DataFrame:
        """
        Baixa dados históricos de ações do Yahoo Finance.
        
        Returns:
            DataFrame com dados OHLCV (Abertura, Máxima, Mínima, Fechamento, Volume, Fechamento Ajustado)
        """
        try:
            logger.info(f"Baixando dados para {self.symbol}...")
            self.df = yf.download(
                self.symbol,
                start=self.start_date,
                end=self.end_date,
                progress=False
            )
            
            if self.df.empty:
                raise ValueError(f"Nenhum dado encontrado para o símbolo {self.symbol}")
                
            logger.info(f"Baixados {len(self.df)} registros")
            return self.df
            
        except Exception as e:
            logger.error(f"Erro ao baixar dados: {str(e)}")
            raise
    
    def get_data(self) -> pd.DataFrame:
        """Obtém o dataframe baixado."""
        if self.df is None:
            self.download()
        return self.df.copy()
    
    def get_info(self) -> dict:
        """Obtém informações básicas sobre a ação."""
        try:
            ticker = yf.Ticker(self.symbol)
            info = {
                'symbol': self.symbol,
                'company_name': ticker.info.get('longName', 'N/A'),
                'sector': ticker.info.get('sector', 'N/A'),
                'market_cap': ticker.info.get('marketCap', 'N/A'),
                'records': len(self.df) if self.df is not None else 0,
                'date_range': f"{self.start_date} to {self.end_date}"
            }
            return info
        except Exception as e:
            logger.error(f"Erro ao obter informações da ação: {str(e)}")
            return {}


class DataPreprocessor:
    """Pré-processa dados de ações para treinamento do modelo."""
    
    def __init__(self, df: pd.DataFrame, lookback: int = 60):
        """
        Inicializa o pré-processador.
        
        Args:
            df: DataFrame com dados de ações
            lookback: Número de dias para olhar para trás para previsões (padrão: 60)
        """
        self.df = df.copy()
        self.lookback = lookback
        self.scaler = None
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None
        self.train_data_len = None
    
    def prepare_data(self, test_size: float = 0.2, val_size: float = 0.1) -> Tuple[dict, dict]:
        """
        Prepara e divide dados para treinamento, validação e teste.
        
        Args:
            test_size: Proporção de dados para teste (padrão: 0,2)
            val_size: Proporção de dados para validação (padrão: 0,1)
            
        Returns:
            Tupla de (dicionário_dados_treinamento, dicionário_info_pre_processamento)
        """
        from sklearn.preprocessing import MinMaxScaler
        
        logger.info("Iniciando processamento de dados...")
        
        # Extrai preços de fechamento
        data = self.df[['Close']].values.astype(float)
        
        # Normaliza dados
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(data)
        
        # Divide em treino, validação, teste
        total_len = len(scaled_data)
        val_len = int(total_len * val_size)
        test_len = int(total_len * test_size)
        train_len = total_len - val_len - test_len
        
        self.train_data_len = train_len
        
        train_data = scaled_data[:train_len]
        val_data = scaled_data[train_len:train_len + val_len]
        test_data = scaled_data[train_len + val_len:]
        
        # Create sequences
        self.X_train, self.y_train = self._create_sequences(train_data, self.lookback)
        self.X_val, self.y_val = self._create_sequences(val_data, self.lookback)
        self.X_test, self.y_test = self._create_sequences(test_data, self.lookback)
        
        logger.info(f"Amostras de treinamento: {len(self.X_train)}")
        logger.info(f"Amostras de validação: {len(self.X_val)}")
        logger.info(f"Amostras de teste: {len(self.X_test)}")
        
        data_dict = {
            'X_train': self.X_train,
            'y_train': self.y_train,
            'X_val': self.X_val,
            'y_val': self.y_val,
            'X_test': self.X_test,
            'y_test': self.y_test
        }
        
        info_dict = {
            'scaler': self.scaler,
            'lookback': self.lookback,
            'train_len': train_len,
            'val_len': val_len,
            'test_len': test_len
        }
        
        return data_dict, info_dict
    
    @staticmethod
    def _create_sequences(data: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cria sequências para treinamento de LSTM.
        
        Args:
            data: Dados escalados
            lookback: Número de passos de tempo para usar como entrada
            
        Returns:
            Tupla de sequências (X, y)
        """
        X, y = [], []
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i, 0])
            y.append(data[i, 0])
        
        return np.array(X), np.array(y)
    
    def get_scaler(self):
        """Obtém o escalador ajustado."""
        return self.scaler
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """Transforma dados normalizados de volta para a escala original."""
        if self.scaler is None:
            raise ValueError("Escalador ainda não foi ajustado")
        return self.scaler.inverse_transform(data.reshape(-1, 1))
