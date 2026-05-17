# Quick Start Guide

## Get Started in 5 Minutes

### Prerequisites

- Python 3.12+ or Docker
- Git

### Option 1: Local Installation (5 min)

```bash
# 1. Clone repository
git clone <repository_url>
cd laughing-couscous

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Jupyter notebook to train model (if needed)
# Skip this if models/ already contains lstm_model.h5, scaler.pkl
jupyter notebook notebooks/fase-4-lstm-model.ipynb
# Run all cells (Kernel → Restart & Run All)

# 5. Start API
python -m uvicorn src.api.app:app --reload

# 6. Open browser
# Visit http://localhost:8000/docs
```

### Option 2: Docker Installation (3 min)

```bash
# 1. Clone repository
git clone <repository_url>
cd laughing-couscous

# 2. Start with Docker Compose
docker-compose up -d

# 3. Check if running
docker-compose ps

# 4. Open browser
# Visit http://localhost:8000/docs
```

---

## First Request

### Using Python

```python
import requests

# Get prediction
response = requests.post('http://localhost:8000/predict', json={
    'symbol': 'AAPL',
    'days_ahead': 1
})

result = response.json()
print(f"Current: ${result['current_price']:.2f}")
print(f"Predicted: ${result['predicted_price']:.2f}")
print(f"Confidence: {result['confidence_level']}")
```

### Using cURL

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "days_ahead": 1}'
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on "POST /predict"
3. Click "Try it out"
4. Modify the example with your stock symbol
5. Click "Execute"

---

## Common Tasks

### Check if API is running

```bash
curl http://localhost:8000/health
```

### Get model information

```bash
curl http://localhost:8000/model/info
```

### Make historical prediction

```bash
curl -X POST http://localhost:8000/predict/historical \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  }'
```

### View API logs

**Local**:
```bash
# Already printing to console
```

**Docker**:
```bash
docker-compose logs -f api
```

### Stop the API

**Local**:
```bash
# Press Ctrl+C in terminal
```

**Docker**:
```bash
docker-compose down
```

---

## Troubleshooting

### Error: "Model not loaded"

**Solution**: Run the Jupyter notebook to generate model files:
```bash
jupyter notebook notebooks/fase-4-lstm-model.ipynb
# Run all cells
```

### Error: "No module named tensorflow"

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Error: "Connection refused"

**Solution**: Make sure API is running:
```bash
# Local
python -m uvicorn src.api.app:app --reload

# Docker
docker-compose up -d
```

### Port 8000 already in use

**Solution**: Change port in startup command:
```bash
python -m uvicorn src.api.app:app --reload --port 8001
```

---

## Next Steps

- 📚 Read [API Documentation](API.md) for all endpoints
- 🚀 Read [Deployment Guide](DEPLOYMENT.md) for production setup
- 📖 Check [README.md](../README.md) for full documentation
- 🔬 Run the [Jupyter Notebook](../notebooks/fase-4-lstm-model.ipynb) to understand the model
- 💻 Explore [Swagger UI](http://localhost:8000/docs) for interactive API testing

---

## Project Structure

```
laughing-couscous/
├── notebooks/
│   └── fase-4-lstm-model.ipynb          ← Run this for model training
├── src/
│   ├── api/app.py                       ← API application
│   ├── data/data_collector.py           ← Data collection
│   └── models/lstm_model.py             ← Model architecture
├── models/
│   ├── lstm_model.h5                    ← Trained model
│   ├── scaler.pkl                       ← Data scaler
│   └── model_info.json                  ← Model metadata
├── requirements.txt                      ← Dependencies
├── Dockerfile                            ← Docker configuration
└── docker-compose.yml                    ← Docker Compose
```

---

## Supported Stock Symbols

Any stock available on Yahoo Finance:
- US: AAPL, GOOGL, MSFT, AMZN, TSLA, META, NVDA, etc.
- International: 0001.HK, TSM, 6758.T, etc.
- ETFs: SPY, QQQ, IVV, VTI, etc.

Try any symbol you want!

---

## Questions?

- Check API documentation at http://localhost:8000/docs
- See [API.md](API.md) for detailed endpoint documentation
- Review [README.md](../README.md) for full project documentation
- Check logs at `logs/app.log` for errors

Happy predicting! 🚀
