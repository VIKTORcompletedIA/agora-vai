# Arquitetura de Aprendizado e Fluxo de Dados da IA Trader

Este documento detalha a arquitetura proposta para o módulo de inteligência artificial (IA) baseado em Aprendizado por Reforço (RL) e o fluxo de dados associado, visando a integração com o sistema IA Trader Pessoal existente.

## 1. Arquitetura Geral

A arquitetura será centrada em um **Ambiente de Trading** customizado, compatível com a interface padrão do `gymnasium` (sucessor do OpenAI Gym), e um **Agente de RL** treinado usando a biblioteca `stable-baselines3`.

```mermaid
graph TD
    subgraph Backend Flask
        API(API Endpoints: /simulate, /chart-data, /balance)
        SS(Simulation Service)
        BM(Balance Manager)
        DS(Data Service: Busca e Prepara Dados)
        IA_Module(Módulo IA: Treinamento/Inferência)
    end

    subgraph IA_Module
        Env(Ambiente de Trading Gymnasium)
        Agent(Agente RL - Stable Baselines3: PPO)
        Trainer(Lógica de Treinamento)
        Model(Modelo Treinado)
    end

    subgraph Data Flow
        YF_API(Yahoo Finance API)
        HistData(Dados Históricos OHLCV)
        Indicators(Indicadores Técnicos)
        State(Estado do Ambiente)
        Action(Ação: Comprar/Vender/Manter)
        Reward(Recompensa: Lucro/Perda)
    end

    YF_API --> DS
    DS --> HistData
    HistData --> Env
    DS -- Calcula --> Indicators
    Indicators --> Env
    BM -- Saldo --> Env
    SS -- Posição --> Env
    Env -- Monta --> State
    State --> Agent
    Agent -- Decide --> Action
    Action --> Env
    Env -- Executa via --> SS
    SS -- Atualiza --> BM
    SS -- Calcula --> Reward
    Reward --> Agent
    Agent -- Aprende/Atualiza --> Model
    Trainer -- Orquestra --> Agent
    Trainer -- Orquestra --> Env
    API -- Dispara Simulação --> SS
    SS -- Usa --> Model # Durante inferência/simulação
```

## 2. Componentes Detalhados

### 2.1. Data Service (Expansão)

*   **Responsabilidade:** Buscar dados históricos da API `YahooFinance/get_stock_chart`, limpar/validar os dados, calcular indicadores técnicos selecionados (usando `pandas_ta` ou `TA-Lib`) e fornecer os dados brutos (OHLCV) e os indicadores calculados para o Ambiente de Trading.
*   **Implementação:** Será um módulo Python dentro de `src/services/`. Poderá ter funções como `get_historical_data(symbol, interval, range)` que retorna um DataFrame pandas com OHLCV e indicadores.
*   **Integração:** O endpoint `/api/chart-data` usará este serviço. O Ambiente de Trading também o utilizará para obter os dados necessários para construir o estado.

### 2.2. Ambiente de Trading (`TradingEnv`)

*   **Interface:** Herdará de `gymnasium.Env`.
*   **Responsabilidade:** Simular o processo de trading passo a passo (candle a candle) usando os dados históricos e indicadores fornecidos pelo `Data Service`. Manter o estado atual da simulação (posição, saldo - via `BalanceManager`, dados recentes) e calcular a recompensa após cada ação do agente.
*   **Métodos Principais:**
    *   `__init__(self, df, initial_balance, ...)`: Recebe o DataFrame com dados históricos e indicadores, saldo inicial, etc.
    *   `reset(self)`: Reinicia o ambiente para o início dos dados históricos, retorna a observação inicial.
    *   `step(self, action)`: Executa a ação do agente (comprar, vender, manter) no candle atual, atualiza a posição e o saldo (via `BalanceManager`), avança para o próximo candle, calcula a recompensa e retorna a nova observação, recompensa, se terminou (terminated), se truncou (truncated) e informações adicionais (info).
    *   `_get_observation(self)`: Constrói o vetor/matriz que representa o estado atual do ambiente para o agente (ex: janela de preços/indicadores recentes, posição atual).
    *   `_calculate_reward(self)`: Calcula a recompensa com base na ação tomada e na variação do portfólio/lucro.
*   **Estado (Observation Space):** Definido usando `gymnasium.spaces`. Inicialmente, pode ser um `Box` (vetor contínuo) contendo N últimos valores de preços (OHLC) e indicadores.
*   **Ações (Action Space):** Definido usando `gymnasium.spaces`. Inicialmente, um `Discrete(3)` representando [Manter, Comprar, Vender].

### 2.3. Agente RL (`Agent`)

*   **Biblioteca:** `stable-baselines3`.
*   **Algoritmo:** PPO (Proximal Policy Optimization) é um bom ponto de partida, pois funciona bem com espaços de ação discretos e contínuos e é robusto.
*   **Treinamento:** Um script Python separado (`train_agent.py`) será criado. Ele instanciará o `Data Service` para buscar dados, criará o `TradingEnv` com esses dados e usará `stable-baselines3` para treinar o agente PPO no ambiente (`model = PPO(...)`, `model.learn(total_timesteps=...)`).
*   **Modelo Treinado (`Model`):** O agente treinado será salvo em um arquivo (ex: `ppo_trader.zip`).
*   **Inferência/Simulação:** O `Simulation Service` será modificado. Ao receber uma solicitação via API `/simulate`, ele carregará o modelo treinado (`model = PPO.load(
