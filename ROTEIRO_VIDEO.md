# 🎬 Roteiro de Vídeo - LSTM Stock Price Prediction API
**Duração Total: ~10 minutos**

---

## 📌 ESTRUTURA DO VÍDEO

### Bloco 1: Introdução (1:00 min)
**Duração**: 60 segundos

**O que mostrar:**
- Tela: Abrir o repositório do projeto no navegador
- Mostrar a estrutura de pastas no VS Code

**Script:**
> "Olá! Este é o **Tech Challenge Fase 4** - um projeto completo de Machine Learning para previsão de preços de ações usando redes neurais LSTM.
>
> O que você vai ver neste vídeo:
> - A arquitetura do projeto
> - Como funciona o modelo de IA
> - A API REST para servir as previsões
> - Como fazer deployment com Docker
>
> Tudo isso pronto para produção, com monitoramento, logging e documentação completa!"

---

### Bloco 2: O Problema e a Solução (1:30 min)
**Duração**: 90 segundos

**O que mostrar:**
- Tela: README.md com objetivos do projeto
- Gráfico conceitual (ou desenhar com setas no keynote/powerpoint)

**Script:**
> "**O Desafio**: Prever preços de ações do futuro usando dados históricos.
>
> **Por que LSTM?** Porque os preços de ações são uma série temporal - cada dia depende dos dias anteriores. LSTM (Long Short-Term Memory) é perfeita para isso, pois consegue aprender padrões de longo prazo nos dados.
>
> **A Solução**: Um pipeline completo que:
> 1. Coleta dados históricos da ação (escolhemos Apple - AAPL)
> 2. Pré-processa e normaliza os dados
> 3. Treina um modelo neural LSTM
> 4. Expõe as previsões através de uma API REST
> 5. Deploy automático com Docker"

---

### Bloco 3: A Arquitetura do Modelo LSTM (2:00 min)
**Duração**: 120 segundos

**O que mostrar:**
- Tela: Diagrama da rede neural (do README.md ou desenhar)
- Abrir o arquivo `src/models/lstm_model.py` para mostrar a implementação

**Script:**
> "**Vamos ver como a rede neural é construída:**
>
> A entrada recebe 60 dias de dados históricos de preço.
>
> Depois passa por **3 camadas LSTM**, cada uma com 50 unidades. Isso permite que a rede 'memorize' padrões complexos ao longo do tempo.
>
> Entre cada camada, usamos **Dropout de 20%** - isso é uma técnica para evitar overfitting, ou seja, que o modelo decora os dados em vez de aprender padrões reais.
>
> Depois temos uma camada **Dense com 25 unidades** usando ativação ReLU para fazer uma transformação não-linear.
>
> Por fim, uma camada **Dense final com 1 unidade** - é o nosso output: o preço previsto.
>
> Tudo isso resulta em **~80 mil parâmetros** que foram ajustados durante o treinamento para minimizar o erro de previsão."

---

### Bloco 4: Os Dados e o Treinamento (1:30 min)
**Duração**: 90 segundos

**O que mostrar:**
- Tela: Notebook Jupyter com gráficos de treinamento
- Mostrar as métricas (MAE, RMSE, MAPE)

**Script:**
> "**De onde vêm os dados?**
>
> Usamos o Yahoo Finance para baixar 5 anos de dados históricos da Apple (AAPL). Isso nos dá aproximadamente 1.200 dias de dados reais.
>
> **Pré-processamento:**
> Normalizamos os dados usando MinMax Scaler - isso transforma os preços para uma escala de 0 a 1, o que ajuda a rede neural a convergir mais rápido.
>
> **Treinamento:**
> Dividimos os dados em: 70% treino, 15% validação, 15% teste.
> O modelo foi treinado por 50 épocas com callbacks inteligentes - **Early Stopping** para parar quando o modelo não melhora mais.
>
> **Resultados:**
> - MAE (Erro Médio Absoluto): $2.15 - em média, o modelo erra $2.15 no preço
> - RMSE: $3.45 - penaliza mais os erros maiores
> - MAPE: 1.87% - erro percentual muito baixo!"

---

### Bloco 5: A API REST (1:45 min)
**Duração**: 105 segundos

**O que mostrar:**
- Tela: Abrir API no navegador (http://localhost:8000/docs)
- Mostrar o Swagger UI interativo
- Testar um endpoint em tempo real
- Mostrar o código de `src/api/app.py`

**Script:**
> "**A API REST**: Usamos FastAPI, um framework Python moderno e super rápido.
>
> Temos 4 endpoints principais:
>
> **1. GET /health** - Verifica se a API está rodando e se o modelo foi carregado. Resposta simples: status 'saudável'.
>
> **2. GET /model/info** - Retorna todas as informações sobre o modelo: version, métricas de teste, data de treinamento, arquitetura.
>
> **3. POST /predict** - **O mais importante!** Você envia o símbolo da ação e quantos dias no futuro quer prever. A API retorna: preço atual, preço previsto, nível de confiança e intervalo de confiança.
>
> **4. POST /predict/historical** - Se você quer prever múltiplos dias, esse endpoint faz previsões para um intervalo inteiro.
>
> Todos os dados são validados usando **Pydantic** - se você enviar um JSON malformado, a API rejeita e explica o erro.
>
> E temos **logging estruturado** - toda requisição é registrada com timestamp, endpoint, tempo de resposta."

---

### Bloco 6: Monitoramento em Produção (1:00 min)
**Duração**: 60 segundos

**O que mostrar:**
- Tela: Arquivo `src/api/monitoring.py`
- Mostrar exemplo de logs (se houver arquivo)

**Script:**
> "**Monitoramento**: Quando você coloca isso em produção, você precisa saber o que está acontecendo.
>
> Implementamos:
>
> **ProductionLogger** - Logs estruturados em JSON Lines. Cada linha é um evento completo: timestamp, tipo de evento, dados relevantes.
>
> **PerformanceMonitor** - Rastreia tempo de resposta, CPU, memória, número de requisições. Isso te ajuda a identificar gargalos.
>
> **MetricsCollector** - Coleta estatísticas: quantas previsões foram feitas, qual a acurácia média, erros que ocorreram.
>
> Tudo isso é salvo em arquivos que podem ser analisados depois ou enviados para ferramentas de monitoring como DataDog ou CloudWatch."

---

### Bloco 7: Docker e Deployment (1:15 min)
**Duração**: 75 segundos

**O que mostrar:**
- Tela: Mostrar `Dockerfile` e `docker-compose.yml`
- Se possível, executar `docker-compose up` e mostrar containers rodando

**Script:**
> "**Deploy com Docker**: Nosso projeto é pronto para produção com containerização.
>
> No arquivo **docker-compose.yml**, definimos um container com:
> - Python 3.12 slim (imagem leve)
> - Todas as dependências instaladas automaticamente
> - Health checks para monitorar se a API está saudável
> - Volumes para persistir o modelo e os logs
> - Reinício automático em caso de falha
>
> **Para fazer deploy**, é literalmente 3 comandos:
>
> ```bash
> git clone <repo>
> cd laughing-couscous
> docker-compose up -d
> ```
>
> E pronto! Sua API está rodando em http://localhost:8000
>
> Isso funciona em **qualquer cloud provider**: AWS EC2, Google Cloud Run, Azure Container Instances, ou até em um Raspberry Pi."

---

### Bloco 8: Exemplo de Uso Prático (1:15 min)
**Duração**: 75 segundos

**O que mostrar:**
- Tela: Terminal/Python rodando exemplo real
- Mostrar uma previsão sendo feita
- Exibir o resultado em JSON formatado

**Script:**
> "**Vamos fazer uma previsão de verdade:**
>
> [Executar código Python]
> ```python
> import requests
> response = requests.post('http://localhost:8000/predict', 
>   json={'symbol': 'AAPL', 'days_ahead': 1})
> 
> result = response.json()
> print(f\"Preço Atual: ${result['current_price']:.2f}\")
> print(f\"Preço Previsto: ${result['predicted_price']:.2f}\")
> ```
>
> [Mostrar output]
> ```
> Preço Atual: $182.50
> Preço Previsto: $184.23
> ```
>
> A API responde em **~50ms**.
>
> Note que a resposta inclui um **intervalo de confiança** - porque não sabemos o futuro com certeza. Nosso modelo diz: 'Tem 95% de chance do preço estar entre $182 e $186'.
>
> Você pode integrar isso em: bots de trading automático, dashboards de decisão, sistemas de alertas, etc."

---

### Bloco 9: Stack Tecnológico Resumido (0:45 min)
**Duração**: 45 segundos

**O que mostrar:**
- Tela: badges e logos dos tecnologias usadas

**Script:**
> "**Stack Tecnológico:**
>
> **Backend**: Python 3.12, FastAPI, Uvicorn
>
> **Machine Learning**: TensorFlow 2.14, Keras, scikit-learn
>
> **Data**: Pandas, NumPy, yfinance (coleta de dados)
>
> **DevOps**: Docker, Docker Compose
>
> **Monitoramento**: psutil, logging estruturado
>
> Tudo open-source, bem documentado, e pronto para produção."

---

### Bloco 10: Resumo e Call-to-Action (0:40 min)
**Duração**: 40 segundos

**O que mostrar:**
- Tela: Repositório GitHub / Links importantes

**Script:**
> "**Resumindo:**
>
> ✅ Modelo LSTM treinado com dados reais
> ✅ API REST com 4 endpoints
> ✅ Pronto para produção (Docker, monitoramento, logging)
> ✅ Documentação completa
> ✅ Exemplos de uso
>
> Você pode usar este projeto como base para:
> - Um produto de análise de ações
> - Um sistema de alertas de preços
> - Uma ferramenta educacional
> - Um portfólio impressionante 😎
>
> **Todo o código está no repositório:** [Link]
>
> **Documentação completa:** veja QUICKSTART.md para começar em 5 minutos.
>
> Obrigado por assistir!"

---

## 📊 RESUMO VISUAL

| Segmento | Tempo | Ação |
|----------|-------|------|
| 1. Introdução | 0:00-1:00 | Apresentação geral |
| 2. Problema & Solução | 1:00-2:30 | Explicar o "por quê" |
| 3. Arquitetura LSTM | 2:30-4:30 | Deep dive técnico |
| 4. Dados & Treinamento | 4:30-6:00 | Mostrar notebook |
| 5. API REST | 6:00-7:45 | Testar endpoints |
| 6. Monitoramento | 7:45-8:45 | Produção ready |
| 7. Docker | 8:45-10:00 | Deploy |
| 8. Exemplo Prático | 10:00-11:15 | Demo ao vivo |
| 9. Stack Tecnológico | 11:15-12:00 | Tecnologias |
| 10. Resumo | 12:00-12:40 | Conclusão |

**Tempo Total: 12:40** (deixa margem para cortes e pausas naturais)

---

## 🎥 DICAS PARA GRAVAÇÃO

### Antes de Gravar:
- ✅ Teste todos os endpoints da API
- ✅ Faça ao menos 2-3 previsões para ter casos de sucesso
- ✅ Verifique que Docker está rodando
- ✅ Abra todos os arquivos que vai mostrar em abas diferentes
- ✅ Aumente o zoom do terminal para 120-150%
- ✅ Feche notificações e aplicações desnecessárias

### Enquanto Grava:
- ✅ Fale devagar e com clareza (não é corrida)
- ✅ Pause entre parágrafos para respirar
- ✅ Mostre o código enquanto explica (não só fale)
- ✅ Use diferentes ângulos: tela inteira, zoom em seção específica
- ✅ Deixe 2-3 segundos de silêncio antes de mudar de cena

### Recursos Visuais Recomendados:
- 📊 Gráficos do notebook (já temos em PNG)
- 📐 Diagrama da arquitetura LSTM (desenhar ou baixar)
- 🔗 Links em texto/overlay para os arquivos
- 🎬 Transições suaves entre abas

### Pós-Produção (Edição):
- Cortar pausas muito longas
- Adicionar legendas/subtítulos
- Highlighting de código importante
- Música de fundo leve durante intros/outros
- Zoom em partes críticas (métricas, outputs)

---

## 📁 RECURSOS JÁ DISPONÍVEIS NO PROJETO

Para facilitar a gravação, você pode usar:

1. **Notebooks**: `notebooks/fase-4-lstm-model.ipynb`
   - Gráficos de treinamento
   - Visualizações de dados
   - Resultados das métricas

2. **Modelos treinados**: `models/lstm_model.h5`
   - Pronto para usar - não precisa retreinar

3. **Documentação**:
   - `README.md` - Visão geral
   - `docs/API.md` - Detalhes dos endpoints
   - `docs/DEPLOYMENT.md` - Deploy em cloud

4. **Código-fonte**:
   - `src/api/app.py` - Endpoints para demonstrar
   - `src/models/lstm_model.py` - Arquitetura LSTM
   - `src/data/data_collector.py` - Coleta de dados

---

## 🎬 TEMPLATE PARA TRANSIÇÕES

Usar entre blocos para manter a narrativa fluida:

> "Agora que entendemos o desafio, vamos ver..."
> "Com os dados preparados, chegou a hora de..."
> "A API é onde tudo se junta..."
> "Mas em produção, precisamos de..."

---

## 💡 VARIAÇÕES POSSÍVEIS

Caso queira versões mais curtas/longas:

**Versão Curta (5 min)**: Blocos 1, 2, 3 (problema), 5 (API), 10 (resumo)

**Versão Média (10 min)**: Este roteiro completo

**Versão Longa (15-20 min)**: Adicionar deep-dive em notebooks, exemplos adicionais, troubleshooting

