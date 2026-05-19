# Tech Challenge Fase 4 - LSTM Stock Price Prediction API

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![TensorFlow 2.14](https://img.shields.io/badge/TensorFlow-2.14-orange)](https://www.tensorflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)

![cuscuz](docs/cuscuz.jpg)

## Link do Video 👇
https://youtu.be/JPnzmOjMK50


## 📋 Descrição do Projeto

Um modelo de predição de preços de ações utilizando **redes neurais LSTM** (Long Short-Term Memory), com API RESTful para servir as previsões. O projeto engloba coleta de dados, preprocessamento, treinamento de modelo, deployment com Docker e monitoramento em produção.

### Empresa Escolhida: Apple (AAPL)

## 🎯 Objetivos

1. ✅ Coletar dados históricos de preços via Yahoo Finance
2. ✅ Pré-processar e normalizar os dados
3. ✅ Construir e treinar um modelo LSTM
4. ✅ Avaliar o modelo com métricas (MAE, RMSE, MAPE)
5. ✅ Salvar o modelo para inferência
6. ✅ Criar API REST com FastAPI
7. ✅ Configurar deployment com Docker
8. ✅ Implementar monitoramento e logging
9. ✅ Documentação completa

## 🏗️ Arquitetura do Projeto

```
laughing-couscous/
├── notebooks/
│   └── fase-4-lstm-model.ipynb          # Notebook completo (coleta, treinamento, avaliação)
├── src/
│   ├── api/
│   │   ├── app.py                       # Aplicação FastAPI principal
│   │   └── monitoring.py                # Monitoramento e logging
│   ├── data/
│   │   └── data_collector.py            # Coleta e preprocessamento de dados
│   └── models/
│       └── lstm_model.py                # Arquitetura do modelo LSTM
├── models/
│   ├── lstm_model.h5                    # Modelo treinado
│   ├── scaler.pkl                       # Scaler para normalização
│   ├── model_info.json                  # Metadados do modelo
│   └── *.png                            # Visualizações
├── requirements.txt                      # Dependências Python
├── Dockerfile                            # Dockerfile para deploy
├── docker-compose.yml                    # Docker Compose para orquestração
├── .dockerignore                         # Arquivos ignorados no Docker
└── README.md                             # Este arquivo
```

## 🔧 Stack Tecnológico

### Backend
- **Python 3.12**: Linguagem de programação
- **TensorFlow/Keras 2.14**: Framework para Deep Learning
- **FastAPI 0.109**: Framework web de alto desempenho
- **Uvicorn**: Servidor ASGI

### Data Science
- **Pandas**: Manipulação de dados
- **NumPy**: Operações numéricas
- **scikit-learn**: Pré-processamento e métricas
- **yfinance**: Coleta de dados de ações

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração de containers

### Monitoramento
- **psutil**: Métricas de sistema
- **logging**: Logging estruturado
- **JSON Lines**: Armazenamento de métricas

## 📊 Modelo LSTM

### Arquitetura

```
Input (60 time steps)
    ↓
LSTM (50 units) + Dropout (20%)
    ↓
LSTM (50 units) + Dropout (20%)
    ↓
LSTM (50 units) + Dropout (20%)
    ↓
Dense (25 units, ReLU)
    ↓
Dense (1 unit) - Output
    ↓
Predicted Price
```

### Hiperparâmetros

| Parâmetro | Valor |
|-----------|-------|
| Lookback Period | 60 dias |
| LSTM Units | 50 |
| Dropout Rate | 0.2 |
| Optimizer | Adam |
| Loss Function | MSE |
| Epochs | 50 |
| Batch Size | 32 |

### Métricas de Performance

- **MAE (Mean Absolute Error)**: Erro absoluto médio
- **RMSE (Root Mean Square Error)**: Raiz do erro quadrático médio
- **MAPE (Mean Absolute Percentage Error)**: Erro percentual absoluto médio

## 🚀 Como Executar

### 1. Requisitos

- Python 3.12+
- pip ou conda
- Docker (opcional)
- Pelo menos 8GB RAM recomendado

### 2. Configuração do Ambiente Local

#### Opção A: Virtual Environment

```bash
# Clonar repositório
git clone <repository_url>
cd laughing-couscous

# Criar virtual environment
python -m venv venv

# Ativar virtual environment
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

#### Opção B: Conda

```bash
conda create -n stock-prediction python=3.12
conda activate stock-prediction
pip install -r requirements.txt
```

### 3. Treinar o Modelo

Execute o notebook Jupyter:

```bash
jupyter notebook notebooks/fase-4-lstm-model.ipynb
```

Ou execute todas as células para gerar:
- `models/lstm_model.h5`: Modelo treinado
- `models/scaler.pkl`: Scaler para normalização
- `models/model_info.json`: Metadados
- Visualizações em `models/*.png`

### 4. Executar a API Localmente

```bash
# Modo desenvolvimento
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Modo produção
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa em: http://localhost:8000/docs

### 5. Deploy com Docker

#### Construir e executar container

```bash
# Construir imagem
docker build -t stock-prediction-api:1.0 .

# Executar container
docker run -p 8000:8000 stock-prediction-api:1.0
```

#### Usar Docker Compose

```bash
# Iniciar serviço
docker-compose up -d

# Parar serviço
docker-compose down

# Visualizar logs
docker-compose logs -f api

# Rebuild
docker-compose up --build
```

## 📡 API Endpoints

### Health Check
```
GET /health
```
Verifica se a API está funcionando.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-05-11T10:30:00.000Z",
  "model_loaded": true
}
```

### Model Information
```
GET /model/info
```
Retorna informações sobre o modelo treinado.

**Resposta:**
```json
{
  "model_name": "LSTM Stock Price Predictor",
  "version": "1.0.0",
  "symbol": "AAPL",
  "lookback_period": 60,
  "lstm_units": 50,
  "dropout_rate": 0.2,
  "training_date": "2024-05-11T08:00:00.000Z",
  "test_metrics": {
    "MAE": 2.1534,
    "RMSE": 3.4521,
    "MAPE": 1.8734
  },
  "epochs_trained": 42
}
```

### Predict Single Price
```
POST /predict
```
Prediz o preço de fechamento para um símbolo específico.

**Request:**
```json
{
  "symbol": "AAPL",
  "days_ahead": 1,
  "historical_data": null
}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "current_price": 182.45,
  "predicted_price": 184.32,
  "prediction_date": "2024-05-12",
  "confidence_level": "High",
  "prediction_timestamp": "2024-05-11T10:30:00.000Z"
}
```

### Predict Historical Period
```
POST /predict/historical
```
Gera previsões para um período histórico.

**Request:**
```json
{
  "symbol": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "lookback": 60
}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "predictions": [
    {
      "date": "2024-01-10",
      "actual": 185.23,
      "predicted": 184.12,
      "error": 1.11
    }
  ],
  "metrics": {
    "MAE": 2.1534,
    "RMSE": 3.4521,
    "MAPE": 1.8734
  },
  "prediction_date": "2024-05-11T10:30:00.000Z"
}
```

## 📈 Exemplos de Uso

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Get model info
response = requests.get(f"{BASE_URL}/model/info")
print(response.json())

# Make prediction
data = {
    "symbol": "AAPL",
    "days_ahead": 1
}
response = requests.post(f"{BASE_URL}/predict", json=data)
prediction = response.json()
print(f"Current: ${prediction['current_price']:.2f}")
print(f"Predicted: ${prediction['predicted_price']:.2f}")
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/model/info

# Predict price
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "days_ahead": 1}'
```

### JavaScript/Node.js

```javascript
const BASE_URL = 'http://localhost:8000';

async function predictPrice(symbol) {
  const response = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      symbol: symbol,
      days_ahead: 1
    })
  });
  
  const data = await response.json();
  console.log(data);
}

predictPrice('AAPL');
```

## 📊 Monitoramento

### Logs

Os logs da aplicação são armazenados em `logs/app.log`:

```
2024-05-11 10:30:15 - StockPredictionAPI - INFO - Request | Endpoint: /predict | Method: POST | Status: 200 | Duration: 0.234s
2024-05-11 10:30:20 - StockPredictionAPI - INFO - Prediction | Symbol: AAPL | Predicted Price: $184.32 | Confidence: High
```

### Métricas de Performance

Armazenadas em `logs/metrics.jsonl`:

```json
{
  "timestamp": "2024-05-11T10:30:15.000Z",
  "system": {
    "cpu_percent": 25.5,
    "memory_mb": 512.4,
    "memory_percent": 12.3,
    "uptime_seconds": 3600.5
  },
  "api": {
    "total_requests": 150,
    "total_errors": 2,
    "error_rate": 1.33,
    "avg_response_time_ms": 245.3,
    "predictions_made": 120
  }
}
```

## 🧪 Testes

### Executar testes unitários

```bash
pytest tests/ -v
```

### Teste de carga

```bash
# Usando Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Usando locust
locust -f tests/locustfile.py
```

## 📝 Variáveis de Ambiente

Criar arquivo `.env`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# Model Configuration
MODEL_PATH=models/lstm_model.h5
SCALER_PATH=models/scaler.pkl

# Data Configuration
STOCK_SYMBOL=AAPL
LOOKBACK_PERIOD=60
```

## 🔍 Troubleshooting

### Problema: Modelo não carrega
**Solução**: Execute o notebook completo em `notebooks/fase-4-lstm-model.ipynb` para gerar os arquivos do modelo.

### Problema: Erro de memória
**Solução**: Aumente o limite de memória do container no `docker-compose.yml`:
```yaml
services:
  api:
    mem_limit: 4g
    memswap_limit: 4g
```

### Problema: Taxa de erro alta
**Solução**: Verifique os logs:
```bash
docker-compose logs api
```

## 📚 Referências

- [TensorFlow LSTM Documentation](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [Docker Documentation](https://docs.docker.com/)

## 📧 Contato

Para dúvidas ou sugestões sobre este projeto, entre em contato.

---

**Desenvolvido para Tech Challenge Fase 4 - POS Tech FIAP**  
**Data de Conclusão**: 11 de Maio de 2024
