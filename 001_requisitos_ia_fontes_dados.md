# Análise de Requisitos da IA Autônoma e Fontes de Dados

Este documento detalha os requisitos para o desenvolvimento da inteligência artificial (IA) do Trader Pessoal, com base nas suas diretrizes: aprendizado autônomo por tentativa e erro, análise de mercado e análise gráfica.

## 1. Requisitos Funcionais da IA

### 1.1. Aprendizado Autônomo (Tentativa e Erro)

*   **Abordagem Sugerida:** Aprendizado por Reforço (Reinforcement Learning - RL). A IA (agente) aprenderá interagindo com um ambiente de mercado simulado.
*   **Ciclo de Aprendizado:**
    1.  **Observação do Estado:** A IA observa o estado atual do mercado (preços, indicadores, posição atual, saldo).
    2.  **Tomada de Decisão (Ação):** Com base no estado observado e em sua política aprendida, a IA decide uma ação (comprar, vender, manter, definir volume/percentual).
    3.  **Execução e Feedback:** A ação é executada no ambiente simulado. A IA recebe um feedback (recompensa ou punição) baseado no resultado financeiro da ação (lucro/perda realizado ou não realizado).
    4.  **Atualização da Política:** A IA utiliza o feedback para ajustar sua política interna, visando maximizar a recompensa acumulada ao longo do tempo.
*   **Componentes Chave do RL a Definir:**
    *   **Representação do Estado (State):** Quais informações definem o estado do mercado para a IA? Inicialmente, pode incluir:
        *   Janela de dados OHLCV recentes (ex: últimos 60 períodos).
        *   Valores de indicadores técnicos calculados sobre esses dados.
        *   Posição atual (comprado/vendido/neutro, quantidade).
        *   Saldo virtual disponível.
    *   **Espaço de Ações (Action Space):** Quais ações a IA pode realizar?
        *   *Discreto:* Comprar, Vender, Manter.
        *   *Contínuo (mais complexo):* Comprar X%, Vender Y%, Manter. (Pode ser simplificado inicialmente).
        *   *Consideração futura:* Definir Stop Loss/Take Profit dinamicamente.
    *   **Função de Recompensa (Reward Function):** Como medir o sucesso?
        *   Lucro/Perda por operação fechada.
        *   Variação do valor do portfólio (incluindo posições abertas).
        *   Métricas ajustadas ao risco (ex: Sharpe Ratio).
        *   *Inicialmente:* Lucro/perda simples por trade pode ser um bom começo.
    *   **Algoritmo de RL:** Qual algoritmo usar? (Ex: DQN para ações discretas, PPO para ações contínuas/discretas - PPO é popular em finanças).

### 1.2. Análise de Mercado

*   **Dados Essenciais:** Dados históricos e, futuramente, em tempo real de OHLCV (Open, High, Low, Close, Volume) para os ativos selecionados (ações, criptomoedas).
*   **Granularidade:** Definir os timeframes (ex: 1 minuto, 5 minutos, 1 hora, 1 dia) a serem utilizados para análise e operação. Diferentes granularidades podem ser usadas simultaneamente.
*   **Fontes de Dados (ver seção 2):** APIs de provedores de dados financeiros.
*   **Considerações Futuras:** Incorporar notícias (análise de sentimento), dados macroeconômicos, dados de order book.

### 1.3. Análise Gráfica (Técnica)

*   **Cálculo de Indicadores:** A IA deve ser capaz de calcular e utilizar indicadores técnicos como parte de sua observação do estado.
*   **Indicadores Iniciais Sugeridos:**
    *   Médias Móveis (Simples - SMA, Exponencial - EMA).
    *   Índice de Força Relativa (RSI).
    *   MACD (Moving Average Convergence Divergence).
    *   Bandas de Bollinger.
*   **Bibliotecas:** Utilizar bibliotecas Python como `TA-Lib` ou `pandas_ta` para facilitar o cálculo.

### 1.4. Integração com Sistema Existente

*   O módulo da IA deverá ser integrado ao backend Flask.
*   Receberá dados de mercado pré-processados (OHLCV, indicadores) do serviço de dados.
*   Receberá o estado atual da simulação (saldo, posição) do `BalanceManager` e `SimulationService`.
*   Enviará decisões (ações) para o `SimulationService`.
*   Receberá o resultado (recompensa) do `SimulationService` para o loop de aprendizado.

## 2. Fontes de Dados Potenciais

### 2.1. Dados Históricos (Para Treinamento e Backtesting)

*   **Yahoo Finance:** Acessível via bibliotecas como `yfinance`. Boa cobertura de ações, dados gratuitos com algumas limitações de frequência de acesso.
*   **Alpha Vantage:** API com plano gratuito limitado (requer chave de API). Cobertura de ações, forex, cripto.
*   **Polygon.io:** Foco em dados de mercado dos EUA (ações, opções, forex, cripto). Possui planos gratuitos e pagos.
*   **Binance API / CCXT:** Para dados históricos de criptomoedas. A biblioteca `ccxt` unifica o acesso a várias exchanges.
*   **Arquivos CSV:** Possibilidade de usar arquivos de dados baixados manualmente para desenvolvimento inicial.

### 2.2. Dados em Tempo Real (Para Operação Futura)

*   Muitos dos provedores acima oferecem APIs de streaming (geralmente pagas).
*   WebSockets são comuns para dados de baixa latência.

## 3. Bibliotecas e Ferramentas Potenciais

*   **Busca de Dados:** `yfinance`, `alpha_vantage`, `ccxt`.
*   **Manipulação de Dados:** `pandas`, `numpy`.
*   **Análise Técnica:** `TA-Lib` (requer instalação cuidadosa), `pandas_ta`.
*   **Aprendizado por Reforço:** `stable-baselines3` (popular e bem documentado), `Ray RLlib` (mais escalável para pesquisa e produção).
*   **Ambiente de Simulação:** Será necessário criar ou adaptar um ambiente compatível com RL (seguindo a interface do `gymnasium`/`gym`) que utilize os serviços existentes (`SimulationService`, `BalanceManager`, `DataService`).

## 4. Próximos Passos Imediatos

1.  Pesquisar projetos open source que utilizem RL para trading para identificar abordagens e desafios comuns.
2.  Avaliar as APIs de dados (limitações dos planos gratuitos, facilidade de uso).
3.  Selecionar um conjunto inicial de indicadores técnicos.
4.  Escolher um framework de RL (provavelmente `stable-baselines3` para começar).
5.  Definir a estrutura inicial do ambiente de simulação para RL.
