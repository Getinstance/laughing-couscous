# Documentação da API

## Visão Geral

Uma API de Previsão de Preços de Ações que usa redes neurais LSTM (Long Short-Term Memory) para prever preços de fechamento de ações. A API fornece endpoints para previsões únicas, previsões históricas e informações do modelo.

## URL Base

- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: `https://api.example.com` (quando implementada) (Na verdade não deu tempo.)

## Autenticação

Atualmente, a API não requer autenticação. Em produção, considere implementar:
- Autenticação por chave de API
- OAuth 2.0
- Tokens JWT

## Formato de Requisição/Resposta

Todas as requisições e respostas estão em formato JSON.

### Respostas de Erro

Todas as respostas de erro seguem este formato:

```json
{
  "detail": "Mensagem de erro descrevendo o que deu errado"
}
```

## Endpoints

### 1. Verificação de Saúde

**Endpoint**: `GET /health`

**Descrição**: Verifica se a API está rodando e se o modelo foi carregado.

**Parâmetros**: Nenhum

**Resposta (200)**:
```json
{
  "status": "saudável",
  "timestamp": "2024-05-11T10:30:00.123456Z",
  "model_loaded": true
}
```

**Resposta (503)**:
```json
{
  "detail": "Modelo não carregado"
}
```

---

### 2. Obter Informações do Modelo

**Endpoint**: `GET /model/info`

**Descrição**: Recupera informações detalhadas sobre o modelo LSTM treinado.

**Parâmetros**: Nenhum

**Resposta (200)**:
```json
{
  "model_name": "Preditor de Preços de Ações LSTM",
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

**Campos**:
- `model_name`: Nome do modelo
- `version`: Versão da API
- `symbol`: Símbolo da ação em que o modelo foi treinado
- `lookback_period`: Número de dias históricos usados para previsões
- `lstm_units`: Número de unidades LSTM na rede
- `dropout_rate`: Taxa de dropout usada durante o treinamento
- `training_date`: Timestamp ISO 8601 do treinamento
- `test_metrics`: Métricas de avaliação no conjunto de teste
- `epochs_trained`: Número de épocas em que o modelo foi treinado

---

### 3. Prever Preço Único de Ação

**Endpoint**: `POST /predict`

**Descrição**: Prevê o preço de fechamento de um símbolo de ação.

**Corpo da Requisição**:
```json
{
  "symbol": "AAPL",
  "days_ahead": 1,
  "historical_data": null
}
```

**Parâmetros**:
- `symbol` (string, obrigatório): Símbolo do ticker da ação (ex: "AAPL", "GOOGL", "MSFT")
- `days_ahead` (inteiro, opcional): Dias futuros para prever (1-30, padrão: 1)
- `historical_data` (array de floats, opcional): Preços históricos customizados para usar em vez de fazer download

**Resposta (200)**:
```json
{
  "symbol": "AAPL",
  "current_price": 182.45,
  "predicted_price": 184.32,
  "prediction_date": "2024-05-12",
  "confidence_level": "Alta",
  "prediction_timestamp": "2024-05-11T10:30:00.123456Z"
}
```

**Campos**:
- `symbol`: Símbolo da ação
- `current_price`: Último preço de fechamento
- `predicted_price`: Preço de fechamento previsto
- `prediction_date`: Data da previsão
- `confidence_level`: "Alta" (< 2% de variação), "Média" (2-5% de variação) ou "Baixa" (> 5% de variação)
- `prediction_timestamp`: Quando a previsão foi feita

**Resposta de Erro (400)**:
```json
{
  "detail": "Erro ao baixar dados: Símbolo inválido"
}
```

**Resposta de Erro (503)**:
```json
{
  "detail": "Modelo não carregado"
}
```

---

### 4. Prever Período Histórico

**Endpoint**: `POST /predict/historical`

**Descrição**: Gera previsões para um intervalo de datas históricas.

**Corpo da Requisição**:
```json
{
  "symbol": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "lookback": 60
}
```

**Parâmetros**:
- `symbol` (string, obrigatório): Símbolo do ticker da ação
- `start_date` (string, obrigatório): Data de início no formato "YYYY-MM-DD"
- `end_date` (string, opcional): Data de término no formato "YYYY-MM-DD" (padrão: hoje)
- `lookback` (inteiro, opcional): Período de retrospectiva para LSTM (30-120, padrão: 60)

**Resposta (200)**:
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

**Campos**:
- `symbol`: Símbolo da ação
- `predictions`: Array de objetos de previsão
  - `date`: Data da previsão
  - `actual`: Preço de fechamento real
  - `predicted`: Preço de fechamento previsto
  - `error`: Erro de previsão (real - previsto)
- `metrics`: Métricas de avaliação
  - `MAE`: Erro Médio Absoluto
  - `RMSE`: Raiz do Erro Quadrático Médio
  - `MAPE`: Erro Percentual Médio Absoluto (%)
- `prediction_date`: Quando as previsões foram geradas

**Resposta de Erro (400)**:
```json
{
  "detail": "Nenhum dado encontrado para o intervalo de datas especificado"
}
```

---

## Exemplos de Uso

### Python (biblioteca requests)

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Verificação de saúde
response = requests.get(f"{BASE_URL}/health")
print("Saúde:", response.json())

# 2. Obter informações do modelo
response = requests.get(f"{BASE_URL}/model/info")
model_info = response.json()
print("Informações do Modelo:", model_info)

# 3. Fazer previsão única
prediction_data = {
    "symbol": "AAPL",
    "days_ahead": 1
}
response = requests.post(f"{BASE_URL}/predict", json=prediction_data)
prediction = response.json()
print(f"Atual: ${prediction['current_price']:.2f}")
print(f"Previsto: ${prediction['predicted_price']:.2f}")

# 4. Previsões históricas
historical_data = {
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
}
response = requests.post(f"{BASE_URL}/predict/historical", json=historical_data)
historical = response.json()
print(f"Previsões históricas - MAE: {historical['metrics']['MAE']:.4f}")
```

### cURL

```bash
# Verificação de saúde
curl http://localhost:8000/health

# Obter informações do modelo
curl http://localhost:8000/model/info

# Fazer previsão
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "days_ahead": 1
  }'

# Previsões históricas
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

// Prever preço
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
      throw new Error(`Erro HTTP! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`Atual: $${data.current_price.toFixed(2)}`);
    console.log(`Previsto: $${data.predicted_price.toFixed(2)}`);
    console.log(`Confiança: ${data.confidence_level}`);
  } catch (error) {
    console.error('Erro:', error);
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
    console.error('Erro:', error.message);
  }
}

getPrediction('AAPL');
```

## Limite de Taxa

Atualmente, não há limitação de taxa implementada. Para implantação em produção, considere implementar:
- Limitação de taxa por endereço IP
- Limitação de taxa por chave de API do usuário
- Tratamento de solicitações em rajada

## Tempos de Resposta

Tempos de resposta esperados:
- Verificação de saúde: < 10ms
- Informações do modelo: < 10ms
- Previsão única: 100-500ms
- Previsões históricas: 500-2000ms (dependendo do intervalo de datas)

## Símbolos de Ações Suportados

A API suporta qualquer símbolo de ação disponível no Yahoo Finance, incluindo:
- Ações dos EUA: AAPL, GOOGL, MSFT, AMZN, TSLA, etc.
- Internacionais: 0001.HK (Hong Kong), 1398.HK, etc.
- ETFs: SPY, QQQ, IVV, etc.

## Limitações do Modelo

- **Período de Retrospectiva**: O modelo usa 60 dias de dados históricos para previsões
- **Treinado em**: Dados de AAPL de 2019-2024
- **Horizonte de Previsão**: Otimizado para previsões de 1 dia à frente
- **Intervalos de Mercado**: Lida com finais de semana e feriados de mercado

## Melhores Práticas

1. **Cache de Previsões**: Armazene em cache previsões do mesmo símbolo para reduzir a carga da API
2. **Tratamento de Erros**: Sempre implemente tratamento de erros para falhas de rede
3. **Validação de Entrada**: Valide símbolos de ações antes de enviar requisições
4. **Limite de Taxa**: Implemente limitação de taxa no lado do cliente
5. **Monitoramento**: Acompanhe a precisão das previsões ao longo do tempo

## Melhorias Futuras

- [ ] Suporte para múltiplos símbolos de ações em uma única requisição
- [ ] Intervalos de confiança para previsões
- [ ] Endpoint de resultados de backtesting
- [ ] Capacidades de retreinamento do modelo
- [ ] Suporte WebSocket para previsões em tempo real
- [ ] Versionamento de API (v1, v2, etc.)

## Suporte

Para dúvidas ou problemas:
- Verifique os logs em `logs/app.log`
- Revise a documentação da API em `/docs` (Swagger UI)
- Verifique `/redoc` para visualização alternativa da documentação
