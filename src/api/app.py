"""
Aplicação FastAPI para servir previsões de preços de ações LSTM.
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
from typing import List, Dict, Optional, Any
import tensorflow as tf
import yfinance as yf

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar aplicação FastAPI
app = FastAPI(
    title="API de Previsão de Preços de Ações",
    description="API baseada em LSTM para prever preços de fechamento de ações",
    version="1.0.0"
)

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis globais para modelo e escalador
model = None
scaler = None
model_info = None
lookback_period = 60


# Modelos Pydantic para requisição/resposta
class PredictionRequest(BaseModel):
    """Modelo de requisição para previsão de preço."""
    symbol: str = Field(..., example="AAPL", description="Símbolo do ticker da ação")
    days_ahead: int = Field(default=1, ge=1, le=30, description="Número de dias para prever adiante")
    historical_data: Optional[List[float]] = Field(
        default=None,
        description="Preços históricos opcionais para usar ao invés de baixar"
    )


class PredictionResponse(BaseModel):
    """Modelo de resposta para previsão de preço."""
    symbol: str
    current_price: float
    predicted_price: float
    prediction_date: str
    confidence_level: str
    prediction_timestamp: str


class HistoricalPredictionRequest(BaseModel):
    """Modelo de requisição para previsões de dados históricos."""
    symbol: str
    start_date: str = Field(..., example="2024-01-01", description="Data de início para dados históricos")
    end_date: Optional[str] = Field(
        default=None,
        example="2024-12-31",
        description="Data de término para dados históricos (padrão: hoje)"
    )
    lookback: int = Field(default=60, ge=30, le=120, description="Período de retrospectiva para LSTM")


class HistoricalPredictionResponse(BaseModel):
    """Modelo de resposta para previsões históricas."""
    symbol: str
    predictions: List[Dict[str, Any]]
    metrics: Dict[str, float]
    prediction_date: str


class ModelInfoResponse(BaseModel):
    """Modelo de resposta para informações do modelo."""
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
    """Carrega o modelo pré-treinado e artefatos associados."""
    global model, scaler, model_info, lookback_period
    
    try:
        # Carregar modelo
        model_path = 'models/lstm_model.h5'
        model = tf.keras.models.load_model(model_path)
        logger.info(f"✓ Modelo carregado de {model_path}")
        
        # Carregar escalador
        scaler_path = 'models/scaler.pkl'
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        logger.info(f"✓ Escalador carregado de {scaler_path}")
        
        # Carregar informações do modelo
        model_info_path = 'models/model_info.json'
        with open(model_info_path, 'r') as f:
            model_info = json.load(f)
        logger.info(f"✓ Informações do modelo carregadas de {model_info_path}")
        
        lookback_period = model_info['lookback_period']
        logger.info(f"✓ Período de retrospectiva definido para {lookback_period}")
        
    except Exception as e:
        logger.error(f"Erro ao carregar artefatos do modelo: {str(e)}")
        raise


def get_stock_data(symbol: str, days: int = 365) -> np.ndarray:
    """
    Baixar dados históricos de ações.
    
    Args:
        symbol: Símbolo do ticker da ação
        days: Número de dias de dados históricos para baixar
        
    Returns:
        Array de preços de fechamento
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
        logger.error(f"Erro ao baixar dados de ações: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao baixar dados: {str(e)}")


def prepare_sequences(data: np.ndarray, lookback: int) -> np.ndarray:
    """
    Preparar sequências para o modelo LSTM.
    
    Args:
        data: Array de dados de entrada
        lookback: Número de passos de tempo
        
    Returns:
        Dados redimensionados para LSTM
    """
    # Normalizar dados
    scaled_data = scaler.transform(data.reshape(-1, 1))
    
    # Pegar os últimos 'lookback' valores
    sequence = scaled_data[-lookback:].flatten()
    sequence = sequence.reshape(1, lookback, 1)
    
    return sequence, scaled_data


def predict_price(sequence: np.ndarray) -> float:
    """
    Fazer previsão usando o modelo LSTM.
    
    Args:
        sequence: Dados de sequência preparados
        
    Returns:
        Preço previsto
    """
    prediction = model.predict(sequence, verbose=0)
    predicted_price = scaler.inverse_transform(prediction)
    return predicted_price[0][0]


@app.on_event("startup")
async def startup_event():
    """Carregar modelo na inicialização da aplicação."""
    logger.info("Iniciando aplicação...")
    load_model_and_artifacts()
    logger.info("✓ Inicialização da aplicação concluída!")


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Verificar status de saúde da API.
    
    Returns:
        Status de saúde
    """
    return {
        "status": "saudável",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None
    }


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info() -> Dict:
    """
    Obter informações sobre o modelo treinado.
    
    Returns:
        Configuração e métricas do modelo
    """
    if model_info is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")
    
    return ModelInfoResponse(
        model_name="Preditor de Preços de Ações LSTM",
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
    Prever preço de fechamento de ação.
    
    Args:
        request: Requisição de previsão com símbolo da ação
        
    Returns:
        Preço previsto e metadados
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")
    
    try:
        # Obter preço atual
        stock = yf.Ticker(request.symbol)
        current_data = stock.history(period='1d')
        if current_data.empty:
            raise HTTPException(status_code=400, detail=f"Nenhum dado encontrado para o símbolo {request.symbol}")
        
        current_price = float(current_data['Close'].iloc[-1])
        
        # Obter dados históricos
        if request.historical_data:
            historical_prices = np.array(request.historical_data)
        else:
            # Baixar últimos 2 anos de dados para garantir que temos o suficiente
            historical_prices = get_stock_data(request.symbol, days=730)
        
        # Preparar sequências e prever
        sequence, _ = prepare_sequences(historical_prices, lookback_period)
        predicted_price = predict_price(sequence)
        
        # Calcular nível de confiança
        price_change = abs(predicted_price - current_price) / current_price * 100
        if price_change < 2:
            confidence = "Alta"
        elif price_change < 5:
            confidence = "Média"
        else:
            confidence = "Baixa"
        
        # Calcular data de previsão
        prediction_date = (datetime.now() + timedelta(days=request.days_ahead)).strftime('%Y-%m-%d')
        
        logger.info(f"Previsão para {request.symbol}: {predicted_price:.2f} (confiança {confidence})")
        
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
        logger.error(f"Erro de previsão: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro de previsão: {str(e)}")


@app.post("/predict/historical", response_model=HistoricalPredictionResponse, tags=["Predictions"])
async def predict_historical(request: HistoricalPredictionRequest) -> Dict:
    """
    Gerar previsões para período histórico.
    
    Args:
        request: Requisição de previsão histórica
        
    Returns:
        Lista de previsões com métricas
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")
    
    try:
        # Obter dados
        end_date = request.end_date or datetime.now().strftime('%Y-%m-%d')
        df = yf.download(
            request.symbol,
            start=request.start_date,
            end=end_date,
            progress=False
        )
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Nenhum dado encontrado para o intervalo de datas especificado")
        
        # Fazer previsões para cada dia
        predictions = []
        prices = df['Close'].values
        
        for i in range(request.lookback, len(prices)):
            # Usar dados até o dia i
            historical = prices[:i]
            sequence, _ = prepare_sequences(historical, request.lookback)
            pred_price = predict_price(sequence)
            
            predictions.append({
                'date': df.index[i].strftime('%Y-%m-%d'),
                'actual': float(prices[i].item()),
                'predicted': float(pred_price),
                'error': float(prices[i].item() - pred_price)
            })
        
        # Calcular métricas
        actual_prices = np.array([p['actual'] for p in predictions])
        predicted_prices = np.array([p['predicted'] for p in predictions])
        
        mae = np.mean(np.abs(actual_prices - predicted_prices))
        rmse = np.sqrt(np.mean((actual_prices - predicted_prices) ** 2))
        mape = np.mean(np.abs((actual_prices - predicted_prices) / actual_prices)) * 100
        
        logger.info(f"Previsões históricas para {request.symbol}: MAE={mae:.4f}, RMSE={rmse:.4f}, MAPE={mape:.2f}%")
        
        return HistoricalPredictionResponse(
            symbol=request.symbol,
            predictions=predictions[-100:],  # Retornar últimas 100 para eficiência da API
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
        logger.error(f"Erro de previsão histórica: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro de previsão histórica: {str(e)}")


@app.get("/", tags=["Root"])
async def read_root() -> Dict:
    """
    Endpoint raiz com documentação da API.
    
    Returns:
        Mensagem de boas-vindas e endpoints disponíveis
    """
    return {
        "message": "API de Previsão de Preços de Ações",
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
    
    # Executar a aplicação
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
