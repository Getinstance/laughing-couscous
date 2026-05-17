# Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Stock Price Prediction API in different environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Local](#docker-local)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Configuration](#production-configuration)
5. [Monitoring & Logging](#monitoring--logging)

---

## Local Development

### Prerequisites

- Python 3.12+
- pip or conda
- Git

### Installation

1. **Clone the repository**:
```bash
git clone <repository_url>
cd laughing-couscous
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Verify model files exist**:
```bash
ls -la models/
# Should show: lstm_model.h5, scaler.pkl, model_info.json
```

If files don't exist, run the Jupyter notebook:
```bash
jupyter notebook notebooks/fase-4-lstm-model.ipynb
```

5. **Start the API**:
```bash
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API**:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## Docker Local

### Prerequisites

- Docker installed
- Docker Compose (optional but recommended)

### Quick Start with Docker Compose

1. **Build and start services**:
```bash
docker-compose up -d
```

2. **Verify container is running**:
```bash
docker-compose ps
```

3. **Check logs**:
```bash
docker-compose logs -f api
```

4. **Stop services**:
```bash
docker-compose down
```

### Manual Docker Build

1. **Build the image**:
```bash
docker build -t stock-prediction-api:1.0 .
```

2. **Run the container**:
```bash
docker run -d \
  --name stock-api \
  -p 8000:8000 \
  -e LOG_LEVEL=info \
  stock-prediction-api:1.0
```

3. **View logs**:
```bash
docker logs -f stock-api
```

4. **Stop the container**:
```bash
docker stop stock-api
```

---

## Cloud Deployment

### AWS EC2

1. **Launch EC2 instance**:
   - AMI: Ubuntu 20.04 LTS
   - Instance type: t3.medium (minimum)
   - Storage: 20GB
   - Security Group: Allow ports 80, 443, 8000

2. **Connect to instance**:
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install Docker**:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
```

4. **Clone repository**:
```bash
git clone <repository_url>
cd laughing-couscous
```

5. **Deploy with Docker Compose**:
```bash
docker-compose up -d
```

6. **Setup Nginx reverse proxy**:
```bash
sudo apt install -y nginx
```

Create `/etc/nginx/sites-available/default`:
```nginx
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

### Google Cloud Run

1. **Setup Google Cloud CLI**:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **Build and push image to Container Registry**:
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/stock-prediction-api:latest .
docker push gcr.io/YOUR_PROJECT_ID/stock-prediction-api:latest
```

3. **Deploy to Cloud Run**:
```bash
gcloud run deploy stock-prediction-api \
  --image gcr.io/YOUR_PROJECT_ID/stock-prediction-api:latest \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --memory 2Gi \
  --cpu 2
```

4. **Access the deployed service**:
```bash
gcloud run services describe stock-prediction-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### Azure Container Instances

1. **Login to Azure**:
```bash
az login
```

2. **Create resource group**:
```bash
az group create --name stock-prediction --location eastus
```

3. **Build and push image**:
```bash
az acr build --registry YOUR_REGISTRY --image stock-prediction-api:latest .
```

4. **Deploy container**:
```bash
az container create \
  --resource-group stock-prediction \
  --name stock-api \
  --image YOUR_REGISTRY.azurecr.io/stock-prediction-api:latest \
  --port 8000 \
  --cpu 2 \
  --memory 2 \
  --ip-address public
```

---

## Production Configuration

### Environment Variables

Create `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
DEBUG=false

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=api.example.com

# Model Configuration
MODEL_PATH=models/lstm_model.h5
SCALER_PATH=models/scaler.pkl

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Monitoring
SENTRY_DSN=https://your-sentry-url

# Cache (optional)
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Gunicorn Configuration

Create `gunicorn_config.py`:

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 60
keepalive = 5
```

Start with:
```bash
gunicorn src.api.app:app --config gunicorn_config.py
```

### SSL/TLS Certificate

Using Let's Encrypt with Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.example.com
```

Update Nginx configuration to use certificates.

---

## Monitoring & Logging

### Prometheus Integration

1. **Install Prometheus**:
```bash
docker pull prom/prometheus
```

2. **Configure `/etc/prometheus/prometheus.yml`**:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'stock-api'
    static_configs:
      - targets: ['localhost:8000']
```

3. **Run Prometheus**:
```bash
docker run -p 9090:9090 \
  -v /etc/prometheus:/etc/prometheus \
  prom/prometheus
```

### ELK Stack for Logging

1. **Docker Compose with ELK**:

See `docker-compose.elk.yml` template.

2. **Configure log shipping**:
```python
# In app
import logging
from pythonjsonlogger import jsonlogger

handler = logging.FileHandler("logs/app.json")
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Health Checks

Configure health checks in your orchestration platform:

- **Kubernetes**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

- **Docker Compose**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs stock-api

# Verify model files
docker exec stock-api ls -la models/

# Check memory usage
docker stats stock-api
```

### High latency

1. Check system resources (CPU, Memory, Disk I/O)
2. Increase number of workers
3. Enable caching for repeated requests
4. Consider load balancing

### Model loading errors

```bash
# Rebuild container
docker-compose build --no-cache

# Verify TensorFlow installation
docker exec stock-api python -c "import tensorflow; print(tensorflow.__version__)"
```

---

## Backup & Recovery

### Backup model

```bash
# Create backup
tar -czf backup_$(date +%Y%m%d).tar.gz models/

# Store in S3
aws s3 cp backup_*.tar.gz s3://your-bucket/backups/
```

### Automated backups

Create a cron job:

```bash
0 2 * * * cd /path/to/app && tar -czf backup_$(date +\%Y\%m\%d).tar.gz models/ && aws s3 cp backup_*.tar.gz s3://your-bucket/backups/
```

---

## Scaling

### Horizontal Scaling

Use load balancer (Nginx, HAProxy, AWS ELB):

```bash
# Run multiple instances
docker-compose -f docker-compose.yml up -d --scale api=3
```

### Vertical Scaling

Increase resources in `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## Performance Tips

1. **Use CDN** for static content
2. **Enable caching** for repeated requests
3. **Use load balancing** for multiple instances
4. **Monitor resource usage** and scale accordingly
5. **Optimize database queries** if using database
6. **Use connection pooling** for database connections
