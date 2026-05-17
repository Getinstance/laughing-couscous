# API Documentation

## Overview

A Stock Price Prediction API that uses LSTM (Long Short-Term Memory) neural networks to predict stock closing prices. The API provides endpoints for single predictions, historical predictions, and model information.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.example.com` (quando deployada)

## Authentication

Currently, the API does not require authentication. In production, consider implementing:
- API Key authentication
- OAuth 2.0
- JWT tokens

## Request/Response Format

All requests and responses are in JSON format.

### Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

**Description**: Checks if the API is running and model is loaded.

**Parameters**: None

**Response (200)**:
```json
{
  "status": "healthy",
  "timestamp": "2024-05-11T10:30:00.123456Z",
  "model_loaded": true
}
```

**Response (503)**:
```json
{
  "detail": "Model not loaded"
}
```

---

### 2. Get Model Information

**Endpoint**: `GET /model/info`

**Description**: Retrieves detailed information about the trained LSTM model.

**Parameters**: None

**Response (200)**:
```json
{
  "model_name": "LSTM Stock Price Predictor",
  "version": "1.0.0",
  "symbol": "AAPL",
  "lookback_period": 60,
  "lstm_units": 50,
  "dropout_rate": 0.2,
  "training_date": "2024-05-11T08:00:00Z",
  "test_metrics": {
    "MAE": 2.1534,
    "RMSE": 3.4521,
    "MAPE": 1.8734
  },
  "epochs_trained": 42
}
```

**Fields**:
- `model_name`: Name of the model
- `version`: API version
- `symbol`: Stock ticker the model was trained on
- `lookback_period`: Number of historical days used for predictions
- `lstm_units`: Number of LSTM units in the network
- `dropout_rate`: Dropout rate used during training
- `training_date`: ISO 8601 timestamp of training
- `test_metrics`: Evaluation metrics on test set
- `epochs_trained`: Number of epochs model was trained

---

### 3. Predict Single Stock Price

**Endpoint**: `POST /predict`

**Description**: Predicts the closing price for a stock symbol.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "days_ahead": 1,
  "historical_data": null
}
```

**Parameters**:
- `symbol` (string, required): Stock ticker symbol (e.g., "AAPL", "GOOGL", "MSFT")
- `days_ahead` (integer, optional): Days ahead to predict (1-30, default: 1)
- `historical_data` (array of floats, optional): Custom historical prices to use instead of downloading

**Response (200)**:
```json
{
  "symbol": "AAPL",
  "current_price": 182.45,
  "predicted_price": 184.32,
  "prediction_date": "2024-05-12",
  "confidence_level": "High",
  "prediction_timestamp": "2024-05-11T10:30:00.123456Z"
}
```

**Fields**:
- `symbol`: The stock symbol
- `current_price`: Latest closing price
- `predicted_price`: Predicted closing price
- `prediction_date`: Date for the prediction
- `confidence_level`: "High" (< 2% change), "Medium" (2-5% change), or "Low" (> 5% change)
- `prediction_timestamp`: When the prediction was made

**Error Response (400)**:
```json
{
  "detail": "Error downloading data: Invalid symbol"
}
```

**Error Response (503)**:
```json
{
  "detail": "Model not loaded"
}
```

---

### 4. Predict Historical Period

**Endpoint**: `POST /predict/historical`

**Description**: Generates predictions for a historical date range.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "lookback": 60
}
```

**Parameters**:
- `symbol` (string, required): Stock ticker symbol
- `start_date` (string, required): Start date in format "YYYY-MM-DD"
- `end_date` (string, optional): End date in format "YYYY-MM-DD" (default: today)
- `lookback` (integer, optional): Lookback period for LSTM (30-120, default: 60)

**Response (200)**:
```json
{
  "symbol": "AAPL",
  "predictions": [
    {
      "date": "2024-01-10",
      "actual": 185.23,
      "predicted": 184.12,
      "error": 1.11
    },
    {
      "date": "2024-01-11",
      "actual": 186.45,
      "predicted": 185.98,
      "error": 0.47
    }
  ],
  "metrics": {
    "MAE": 2.1534,
    "RMSE": 3.4521,
    "MAPE": 1.8734
  },
  "prediction_date": "2024-05-11T10:30:00.123456Z"
}
```

**Fields**:
- `symbol`: The stock symbol
- `predictions`: Array of prediction objects
  - `date`: Prediction date
  - `actual`: Actual closing price
  - `predicted`: Predicted closing price
  - `error`: Prediction error (actual - predicted)
- `metrics`: Evaluation metrics
  - `MAE`: Mean Absolute Error
  - `RMSE`: Root Mean Square Error
  - `MAPE`: Mean Absolute Percentage Error (%)
- `prediction_date`: When predictions were generated

**Error Response (400)**:
```json
{
  "detail": "No data found for the specified date range"
}
```

---

## Usage Examples

### Python (requests library)

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# 2. Get model info
response = requests.get(f"{BASE_URL}/model/info")
model_info = response.json()
print("Model Info:", model_info)

# 3. Make single prediction
prediction_data = {
    "symbol": "AAPL",
    "days_ahead": 1
}
response = requests.post(f"{BASE_URL}/predict", json=prediction_data)
prediction = response.json()
print(f"Current: ${prediction['current_price']:.2f}")
print(f"Predicted: ${prediction['predicted_price']:.2f}")

# 4. Historical predictions
historical_data = {
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
}
response = requests.post(f"{BASE_URL}/predict/historical", json=historical_data)
historical = response.json()
print(f"Historical predictions - MAE: {historical['metrics']['MAE']:.4f}")
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Get model info
curl http://localhost:8000/model/info

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "days_ahead": 1
  }'

# Historical predictions
curl -X POST http://localhost:8000/predict/historical \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  }'
```

### JavaScript/Fetch API

```javascript
const BASE_URL = 'http://localhost:8000';

// Predict price
async function predictPrice(symbol) {
  try {
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
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`Current: $${data.current_price.toFixed(2)}`);
    console.log(`Predicted: $${data.predicted_price.toFixed(2)}`);
    console.log(`Confidence: ${data.confidence_level}`);
  } catch (error) {
    console.error('Error:', error);
  }
}

predictPrice('AAPL');
```

### Node.js (axios)

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function getPrediction(symbol) {
  try {
    const response = await axios.post(`${BASE_URL}/predict`, {
      symbol: symbol,
      days_ahead: 1
    });
    
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

getPrediction('AAPL');
```

## Rate Limiting

Currently, there is no rate limiting in place. For production deployment, consider implementing:
- Rate limiting per IP address
- Per-user API key rate limiting
- Burst request handling

## Response Times

Expected response times:
- Health check: < 10ms
- Model info: < 10ms
- Single prediction: 100-500ms
- Historical predictions: 500-2000ms (depending on date range)

## Supported Stock Symbols

The API supports any stock symbol available on Yahoo Finance, including:
- US Stocks: AAPL, GOOGL, MSFT, AMZN, TSLA, etc.
- International: 0001.HK (Hong Kong), 1398.HK, etc.
- ETFs: SPY, QQQ, IVV, etc.

## Model Limitations

- **Lookback Period**: The model uses 60 days of historical data for predictions
- **Trained on**: AAPL data from 2019-2024
- **Prediction Horizon**: Optimized for 1-day ahead predictions
- **Market Gaps**: Handles weekends and market holidays

## Best Practices

1. **Cache Predictions**: Cache predictions for the same symbol to reduce API load
2. **Error Handling**: Always implement error handling for network failures
3. **Input Validation**: Validate stock symbols before sending requests
4. **Rate Limiting**: Implement client-side rate limiting
5. **Monitoring**: Track prediction accuracy over time

## Future Enhancements

- [ ] Support for multiple stock symbols in single request
- [ ] Confidence intervals for predictions
- [ ] Backtesting results endpoint
- [ ] Model retraining capabilities
- [ ] WebSocket support for real-time predictions
- [ ] API versioning (v1, v2, etc.)

## Support

For issues or questions:
- Check logs at `logs/app.log`
- Review API documentation at `/docs` (Swagger UI)
- Check `/redoc` for alternative documentation view
