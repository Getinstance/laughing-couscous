"""
FastAPI application for serving LSTM stock price predictions.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import pickle
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tensorflow as tf
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Price Prediction API",
    description="LSTM-based API for predicting stock closing prices",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and scaler
model = None
scaler = None
model_info = None
lookback_period = 60


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Request model for price prediction."""
    symbol: str = Field(..., example="AAPL", description="Stock ticker symbol")
    days_ahead: int = Field(default=1, ge=1, le=30, description="Number of days to predict ahead")
    historical_data: Optional[List[float]] = Field(
        default=None, 
        description="Optional historical prices to use instead of downloading"
    )


class PredictionResponse(BaseModel):
    """Response model for price prediction."""
    symbol: str
    current_price: float
    predicted_price: float
    prediction_date: str
    confidence_level: str
    prediction_timestamp: str


class HistoricalPredictionRequest(BaseModel):
    """Request model for historical data predictions."""
    symbol: str
    start_date: str = Field(..., example="2024-01-01", description="Start date for historical data")
    end_date: Optional[str] = Field(
        default=None,
        example="2024-12-31",
        description="End date for historical data (default: today)"
    )
    lookback: int = Field(default=60, ge=30, le=120, description="Lookback period for LSTM")


class HistoricalPredictionResponse(BaseModel):
    """Response model for historical predictions."""
    symbol: str
    predictions: List[Dict[str, float]]
    metrics: Dict[str, float]
    prediction_date: str


class ModelInfoResponse(BaseModel):
    """Response model for model information."""
    model_name: str
    version: str
    symbol: str
    lookback_period: int
    lstm_units: int
    dropout_rate: float
    training_date: str
    test_metrics: Dict[str, float]
    epochs_trained: int


def load_model_and_artifacts():
    """Load the pre-trained model and associated artifacts."""
    global model, scaler, model_info, lookback_period
    
    try:
        # Load model
        model_path = '/home/raulg/dev/laughing-couscous/models/lstm_model.h5'
        model = tf.keras.models.load_model(model_path)
        logger.info(f"✓ Model loaded from {model_path}")
        
        # Load scaler
        scaler_path = '/home/raulg/dev/laughing-couscous/models/scaler.pkl'
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        logger.info(f"✓ Scaler loaded from {scaler_path}")
        
        # Load model info
        model_info_path = '/home/raulg/dev/laughing-couscous/models/model_info.json'
        with open(model_info_path, 'r') as f:
            model_info = json.load(f)
        logger.info(f"✓ Model info loaded from {model_info_path}")
        
        lookback_period = model_info['lookback_period']
        logger.info(f"✓ Lookback period set to {lookback_period}")
        
    except Exception as e:
        logger.error(f"Error loading model artifacts: {str(e)}")
        raise


def get_stock_data(symbol: str, days: int = 365) -> np.ndarray:
    """
    Download historical stock data.
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days of historical data to download
        
    Returns:
        Array of closing prices
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = yf.download(
            symbol,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False
        )
        
        return df['Close'].values
    except Exception as e:
        logger.error(f"Error downloading stock data: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error downloading data: {str(e)}")


def prepare_sequences(data: np.ndarray, lookback: int) -> np.ndarray:
    """
    Prepare sequences for LSTM model.
    
    Args:
        data: Input data array
        lookback: Number of time steps
        
    Returns:
        Reshaped data for LSTM
    """
    # Normalize data
    scaled_data = scaler.transform(data.reshape(-1, 1))
    
    # Take the last 'lookback' values
    sequence = scaled_data[-lookback:].flatten()
    sequence = sequence.reshape(1, lookback, 1)
    
    return sequence, scaled_data


def predict_price(sequence: np.ndarray) -> float:
    """
    Make prediction using the LSTM model.
    
    Args:
        sequence: Prepared sequence data
        
    Returns:
        Predicted price
    """
    prediction = model.predict(sequence, verbose=0)
    predicted_price = scaler.inverse_transform(prediction)
    return predicted_price[0][0]


@app.on_event("startup")
async def startup_event():
    """Load model on application startup."""
    logger.info("Starting up application...")
    load_model_and_artifacts()
    logger.info("✓ Application startup completed!")


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Check API health status.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None
    }


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info() -> Dict:
    """
    Get information about the trained model.
    
    Returns:
        Model configuration and metrics
    """
    if model_info is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return ModelInfoResponse(
        model_name="LSTM Stock Price Predictor",
        version="1.0.0",
        symbol=model_info.get('symbol', 'AAPL'),
        lookback_period=model_info.get('lookback_period', 60),
        lstm_units=model_info.get('lstm_units', 50),
        dropout_rate=model_info.get('dropout_rate', 0.2),
        training_date=model_info.get('training_date', ''),
        test_metrics=model_info.get('test_metrics', {}),
        epochs_trained=model_info.get('epochs_trained', 0)
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_stock_price(request: PredictionRequest) -> Dict:
    """
    Predict stock closing price.
    
    Args:
        request: Prediction request with stock symbol
        
    Returns:
        Predicted price and metadata
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Get current price
        stock = yf.Ticker(request.symbol)
        current_data = stock.history(period='1d')
        if current_data.empty:
            raise HTTPException(status_code=400, detail=f"No data found for symbol {request.symbol}")
        
        current_price = float(current_data['Close'].iloc[-1])
        
        # Get historical data
        if request.historical_data:
            historical_prices = np.array(request.historical_data)
        else:
            # Download last 2 years of data to ensure we have enough
            historical_prices = get_stock_data(request.symbol, days=730)
        
        # Prepare sequences and predict
        sequence, _ = prepare_sequences(historical_prices, lookback_period)
        predicted_price = predict_price(sequence)
        
        # Calculate confidence level
        price_change = abs(predicted_price - current_price) / current_price * 100
        if price_change < 2:
            confidence = "High"
        elif price_change < 5:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        # Calculate prediction date
        prediction_date = (datetime.now() + timedelta(days=request.days_ahead)).strftime('%Y-%m-%d')
        
        logger.info(f"Prediction for {request.symbol}: {predicted_price:.2f} ({confidence} confidence)")
        
        return PredictionResponse(
            symbol=request.symbol,
            current_price=current_price,
            predicted_price=float(predicted_price),
            prediction_date=prediction_date,
            confidence_level=confidence,
            prediction_timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict/historical", response_model=HistoricalPredictionResponse, tags=["Predictions"])
async def predict_historical(request: HistoricalPredictionRequest) -> Dict:
    """
    Generate predictions for historical period.
    
    Args:
        request: Historical prediction request
        
    Returns:
        List of predictions with metrics
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Get data
        end_date = request.end_date or datetime.now().strftime('%Y-%m-%d')
        df = yf.download(
            request.symbol,
            start=request.start_date,
            end=end_date,
            progress=False
        )
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data found for the specified date range")
        
        # Make predictions for each day
        predictions = []
        prices = df['Close'].values
        
        for i in range(request.lookback, len(prices)):
            # Use data up to day i
            historical = prices[:i]
            sequence, _ = prepare_sequences(historical, request.lookback)
            pred_price = predict_price(sequence)
            
            predictions.append({
                'date': df.index[i].strftime('%Y-%m-%d'),
                'actual': float(prices[i]),
                'predicted': float(pred_price),
                'error': float(prices[i] - pred_price)
            })
        
        # Calculate metrics
        actual_prices = np.array([p['actual'] for p in predictions])
        predicted_prices = np.array([p['predicted'] for p in predictions])
        
        mae = np.mean(np.abs(actual_prices - predicted_prices))
        rmse = np.sqrt(np.mean((actual_prices - predicted_prices) ** 2))
        mape = np.mean(np.abs((actual_prices - predicted_prices) / actual_prices)) * 100
        
        logger.info(f"Historical predictions for {request.symbol}: MAE={mae:.4f}, RMSE={rmse:.4f}, MAPE={mape:.2f}%")
        
        return HistoricalPredictionResponse(
            symbol=request.symbol,
            predictions=predictions[-100:],  # Return last 100 for API efficiency
            metrics={
                'MAE': float(mae),
                'RMSE': float(rmse),
                'MAPE': float(mape)
            },
            prediction_date=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Historical prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Historical prediction error: {str(e)}")


@app.get("/", tags=["Root"])
async def read_root() -> Dict:
    """
    Root endpoint with API documentation.
    
    Returns:
        Welcome message and available endpoints
    """
    return {
        "message": "Stock Price Prediction API",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "model_info": "/model/info",
            "predict": "/predict",
            "predict_historical": "/predict/historical"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
