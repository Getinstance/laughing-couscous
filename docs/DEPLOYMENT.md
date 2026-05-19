# Guia de Deploy

## Visão Geral

Este guia fornece instruções passo a passo para implantar a API de Previsão de Preços de Ações em diferentes ambientes.

## Índice

1. [Desenvolvimento Local](#desenvolvimento-local)
2. [Docker Local](#docker-local)
3. [Deploy em Nuvem](#deploy-em-nuvem)
4. [Configuração de Produção](#configuração-de-produção)
5. [Monitoramento e Logging](#monitoramento-e-logging)

---

## Desenvolvimento Local

### Pré-requisitos

- Python 3.12+
- pip ou conda
- Git

### Instalação

1. **Clone o repositório**:
```bash
git clone <repository_url>
cd laughing-couscous
```

2. **Crie um ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Verifique se os arquivos do modelo existem**:
```bash
ls -la models/
# Deve mostrar: lstm_model.h5, scaler.pkl, model_info.json
```

Se os arquivos não existirem, execute o notebook Jupyter:
```bash
jupyter notebook notebooks/fase-4-lstm-model.ipynb
```

5. **Inicie a API**:
```bash
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

6. **Acesse a API**:
- Documentação da API: http://localhost:8000/docs
- Documentação Alternativa: http://localhost:8000/redoc
- Verificação de Saúde: http://localhost:8000/health

---

## Docker Local

### Pré-requisitos

- Docker instalado
- Docker Compose (opcional mas recomendado)

### Início Rápido com Docker Compose

1. **Construa e inicie os serviços**:
```bash
docker-compose up -d
```

2. **Verifique se o container está rodando**:
```bash
docker-compose ps
```

3. **Verifique os logs**:
```bash
docker-compose logs -f api
```

4. **Pare os serviços**:
```bash
docker-compose down
```

### Construção Manual do Docker

1. **Construa a imagem**:
```bash
docker build -t stock-prediction-api:1.0 .
```

2. **Execute o container**:
```bash
docker run -d \
  --name stock-api \
  -p 8000:8000 \
  -e LOG_LEVEL=info \
  stock-prediction-api:1.0
```

3. **Veja os logs**:
```bash
docker logs -f stock-api
```

4. **Pare o container**:
```bash
docker stop stock-api
```

---

## Deploy em Nuvem

### AWS EC2

1. **Inicie uma instância EC2**:
   - AMI: Ubuntu 20.04 LTS
   - Tipo de instância: t3.medium (mínimo)
   - Armazenamento: 20GB
   - Grupo de segurança: Permita portas 80, 443, 8000

2. **Conecte-se à instância**:
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Instale Docker**:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
```

4. **Clone o repositório**:
```bash
git clone <repository_url>
cd laughing-couscous
```

5. **Deploy com Docker Compose**:
```bash
docker-compose up -d
```

6. **Configure o proxy reverso Nginx**:
```bash
sudo apt install -y nginx
```

Crie `/etc/nginx/sites-available/default`:
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

Reinicie o Nginx:
```bash
sudo systemctl restart nginx
```

### Google Cloud Run

1. **Configure Google Cloud CLI**:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **Construa e envie a imagem para o Container Registry**:
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/stock-prediction-api:latest .
docker push gcr.io/YOUR_PROJECT_ID/stock-prediction-api:latest
```

3. **Deploy para Cloud Run**:
```bash
gcloud run deploy stock-prediction-api \
  --image gcr.io/YOUR_PROJECT_ID/stock-prediction-api:latest \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --memory 2Gi \
  --cpu 2
```

4. **Acesse o serviço implementado**:
```bash
gcloud run services describe stock-prediction-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### Azure Container Instances

1. **Faça login no Azure**:
```bash
az login
```

2. **Crie um grupo de recursos**:
```bash
az group create --name stock-prediction --location eastus
```

3. **Construa e envie a imagem**:
```bash
az acr build --registry YOUR_REGISTRY --image stock-prediction-api:latest .
```

4. **Implante o container**:
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

## Configuração de Produção

### Variáveis de Ambiente

Crie arquivo `.env`:

```env
# Configuração da API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
DEBUG=false

# Segurança
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=api.example.com

# Configuração do Modelo
MODEL_PATH=models/lstm_model.h5
SCALER_PATH=models/scaler.pkl

# Banco de Dados (opcional)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Monitoramento
SENTRY_DSN=https://your-sentry-url

# Cache (opcional)
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Configuração do Gunicorn

Crie `gunicorn_config.py`:

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

Inicie com:
```bash
gunicorn src.api.app:app --config gunicorn_config.py
```

### Certificado SSL/TLS

Usando Let's Encrypt com Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.example.com
```

Atualize a configuração do Nginx para usar certificados.

---

## Monitoramento e Logging

### Integração com Prometheus

1. **Instale Prometheus**:
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

3. **Execute Prometheus**:
```bash
docker run -p 9090:9090 \
  -v /etc/prometheus:/etc/prometheus \
  prom/prometheus
```

### ELK Stack para Logging

1. **Docker Compose com ELK**:

Veja template `docker-compose.elk.yml`.

2. **Configure envio de logs**:
```python
# Na aplicação
import logging
from pythonjsonlogger import jsonlogger

handler = logging.FileHandler("logs/app.json")
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Verificações de Saúde

Configure verificações de saúde em sua plataforma de orquestração:

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

## Solução de Problemas

### Container não inicia

```bash
# Verifique os logs
docker logs stock-api

# Verifique arquivos do modelo
docker exec stock-api ls -la models/

# Verifique o uso de memória
docker stats stock-api
```

### Latência alta

1. Verifique recursos do sistema (CPU, Memória, Disco I/O)
2. Aumente o número de workers
3. Ative cache para requisições repetidas
4. Considere balanceamento de carga

### Erros ao carregar modelo

```bash
# Reconstrua o container
docker-compose build --no-cache

# Verifique instalação do TensorFlow
docker exec stock-api python -c "import tensorflow; print(tensorflow.__version__)"
```

---

## Backup e Recuperação

### Backup do modelo

```bash
# Crie um backup
tar -czf backup_$(date +%Y%m%d).tar.gz models/

# Armazene no S3
aws s3 cp backup_*.tar.gz s3://your-bucket/backups/
```

### Backups automáticos

Crie um cron job:

```bash
0 2 * * * cd /path/to/app && tar -czf backup_$(date +\%Y\%m\%d).tar.gz models/ && aws s3 cp backup_*.tar.gz s3://your-bucket/backups/
```

---

## Escalabilidade

### Escalabilidade Horizontal

Use balanceador de carga (Nginx, HAProxy, AWS ELB):

```bash
# Execute múltiplas instâncias
docker-compose -f docker-compose.yml up -d --scale api=3
```

### Escalabilidade Vertical

Aumente recursos em `docker-compose.yml`:

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

## Dicas de Performance

1. **Use CDN** para conteúdo estático
2. **Ative cache** para requisições repetidas
3. **Use balanceamento de carga** para múltiplas instâncias
4. **Monitore o uso de recursos** e escale conforme necessário
5. **Otimize consultas ao banco de dados** se usando banco de dados
6. **Use pool de conexões** para conexões de banco de dados
