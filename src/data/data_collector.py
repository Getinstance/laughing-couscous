"""
Data collection module for stock price data using yfinance.
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
    """Collects and preprocesses stock data from Yahoo Finance."""
    
    def __init__(self, symbol: str, start_date: str = None, end_date: str = None):
        """
        Initialize the data collector.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            start_date: Start date in format 'YYYY-MM-DD' (default: 5 years ago)
            end_date: End date in format 'YYYY-MM-DD' (default: today)
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
        logger.info(f"Initialized StockDataCollector for {symbol} from {self.start_date} to {self.end_date}")
    
    def download(self) -> pd.DataFrame:
        """
        Download historical stock data from Yahoo Finance.
        
        Returns:
            DataFrame with OHLCV data (Open, High, Low, Close, Volume, Adj Close)
        """
        try:
            logger.info(f"Downloading data for {self.symbol}...")
            self.df = yf.download(
                self.symbol,
                start=self.start_date,
                end=self.end_date,
                progress=False
            )
            
            if self.df.empty:
                raise ValueError(f"No data found for symbol {self.symbol}")
                
            logger.info(f"Downloaded {len(self.df)} records")
            return self.df
            
        except Exception as e:
            logger.error(f"Error downloading data: {str(e)}")
            raise
    
    def get_data(self) -> pd.DataFrame:
        """Get the downloaded dataframe."""
        if self.df is None:
            self.download()
        return self.df.copy()
    
    def get_info(self) -> dict:
        """Get basic info about the stock."""
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
            logger.error(f"Error getting stock info: {str(e)}")
            return {}


class DataPreprocessor:
    """Preprocesses stock data for model training."""
    
    def __init__(self, df: pd.DataFrame, lookback: int = 60):
        """
        Initialize preprocessor.
        
        Args:
            df: DataFrame with stock data
            lookback: Number of days to look back for predictions (default: 60)
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
        Prepare and split data for training, validation, and testing.
        
        Args:
            test_size: Proportion of data for testing (default: 0.2)
            val_size: Proportion of data for validation (default: 0.1)
            
        Returns:
            Tuple of (training_data_dict, preprocessing_info_dict)
        """
        from sklearn.preprocessing import MinMaxScaler
        
        logger.info("Starting data preprocessing...")
        
        # Extract Close prices
        data = self.df[['Close']].values.astype(float)
        
        # Normalize data
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(data)
        
        # Split into train, val, test
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
        
        logger.info(f"Training samples: {len(self.X_train)}")
        logger.info(f"Validation samples: {len(self.X_val)}")
        logger.info(f"Test samples: {len(self.X_test)}")
        
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
        Create sequences for LSTM training.
        
        Args:
            data: Scaled data
            lookback: Number of time steps to use as input
            
        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i, 0])
            y.append(data[i, 0])
        
        return np.array(X), np.array(y)
    
    def get_scaler(self):
        """Get the fitted scaler."""
        return self.scaler
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """Inverse transform normalized data back to original scale."""
        if self.scaler is None:
            raise ValueError("Scaler not fitted yet")
        return self.scaler.inverse_transform(data.reshape(-1, 1))
