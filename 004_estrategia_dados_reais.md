# Estratégia para Utilização de Dados Históricos Reais

Este documento descreve a estratégia para incorporar dados históricos reais de ativos no sistema IA Trader Pessoal, substituindo os dados mock utilizados anteriormente. O objetivo é fornecer um ambiente de simulação e treinamento mais realista para a IA, utilizando a API `YahooFinance/get_stock_chart`.

## 1. Fonte de Dados: API YahooFinance/get_stock_chart

Utilizaremos a API `YahooFinance/get_stock_chart` para buscar dados históricos de OHLCV (Open, High, Low, Close, Volume).

*   **Vantagens:** Ampla cobertura de ativos (ações, potencialmente cripto via símbolos específicos como "BTC-USD"), dados históricos acessíveis, granularidades diversas.
*   **Parâmetros Chave a Utilizar:**
    *   `symbol`: O ticker do ativo (ex: "AAPL", "MSFT", "BTC-USD"). Inicialmente, usaremos os exemplos já presentes no dropdown ("EXMPL3" será mapeado para um ativo real como "AAPL" ou "PETR4.SA" e "BTC" para "BTC-USD").
    *   `interval`: A granularidade dos dados (ex: "1d" para diário, "1h" para horário, "5m" para 5 minutos). Começaremos com "1d" para visualização e simulação inicial.
    *   `range`: O período histórico a ser buscado (ex: "1y" para 1 ano, "6mo" para 6 meses). Começaremos com "1y" para ter um histórico razoável.
    *   `includeAdjustedClose`: Manter `True` (padrão) para obter preços ajustados, importantes para análises de longo prazo.

## 2. Integração no Sistema

### 2.1. Backend (Flask)

*   **Modificação do Endpoint `/api/chart-data` (`src/routes/trading_routes.py`):**
    1.  Receber o `asset` selecionado pelo usuário como parâmetro (já implementado).
    2.  Mapear o valor do `asset` (ex: "acao_exemplo") para um símbolo real do Yahoo Finance (ex: "AAPL" ou "PETR4.SA").
    3.  Chamar a API `YahooFinance/get_stock_chart` usando um script Python (via `ApiClient`), passando o símbolo mapeado, `interval="1d"` e `range="1y"`.
    4.  Processar a resposta da API:
        *   Extrair os arrays `timestamp`, `open`, `high`, `low`, `close` do objeto `result[0].indicators.quote[0]`.
        *   Verificar se os arrays não estão vazios e têm o mesmo tamanho.
        *   Formatar os dados no formato esperado pela biblioteca Plotly.js (array de objetos com `time`, `open`, `high`, `low`, `close`, onde `time` é o timestamp em segundos).
    5.  Retornar os dados formatados como JSON.
    6.  Implementar tratamento de erros para falhas na API ou dados inválidos.
*   **Adaptação do Serviço de Simulação (`src/services/simulation_service.py`):**
    *   Em uma fase futura (implementação da IA), este serviço precisará receber os dados históricos (ou um ponteiro para eles) para que o agente de RL possa observar o estado do mercado e simular a passagem do tempo candle a candle.
    *   Inicialmente, a simulação ainda pode usar uma lógica simplificada, mas o endpoint `/api/chart-data` já fornecerá os dados reais para o gráfico.

### 2.2. Frontend (`src/static/index.html`)

*   Nenhuma modificação significativa é necessária no frontend, pois ele já está configurado para buscar dados de `/api/chart-data` e passá-los para o Plotly.js.
*   A mudança será transparente para o usuário, que passará a ver dados reais no gráfico.

## 3. Mapeamento de Ativos (Inicial)

*   `acao_exemplo` (EXMPL3) -> Mapear para `PETR4.SA` (Petrobras PN no Bovespa) ou `AAPL` (Apple na NASDAQ).
*   `cripto_exemplo` (BTC) -> Mapear para `BTC-USD` (Bitcoin em Dólar Americano).

*Nota:* Usar `PETR4.SA` requer especificar `region="BR"` na chamada da API.

## 4. Limitações e Considerações

*   **Limites da API:** APIs gratuitas como a do Yahoo Finance podem ter limites de requisições. Devemos implementar caching ou buscar dados com menos frequência se necessário.
*   **Disponibilidade de Dados:** Nem todos os ativos ou granularidades podem estar disponíveis.
*   **Ajustes de Preços:** Usar preços ajustados (`adjclose`) é crucial para backtesting de longo prazo, mas para simulação intradiária ou de curto prazo, os preços não ajustados (`close`) podem ser mais relevantes. A API fornece ambos.
*   **Fuso Horário:** Os timestamps retornados pela API são em UTC. O frontend (Plotly.js) geralmente lida bem com isso, mas é preciso atenção.

## 5. Próximos Passos Imediatos

1.  Criar um script Python (`/home/ubuntu/get_yf_data.py`) para testar a chamada à API `YahooFinance/get_stock_chart` com `ApiClient`.
2.  Integrar a chamada da API no endpoint `/api/chart-data` em `src/routes/trading_routes.py`, substituindo a geração de dados mock.
3.  Testar a exibição dos dados reais no gráfico da interface.
