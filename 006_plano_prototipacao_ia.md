# Plano de Prototipação Incremental da IA e Integração

Este documento detalha o plano para desenvolver e integrar o módulo de inteligência artificial (IA) baseado em Aprendizado por Reforço (RL) de forma incremental no sistema IA Trader Pessoal.

## Fases do Desenvolvimento

### Fase 1: Integração de Dados Reais e Ambiente Base (Gymnasium)

*   **Objetivo:** Substituir os dados mock por dados históricos reais no gráfico e criar a estrutura inicial do ambiente de simulação para RL.
*   **Tarefas:**
    1.  **Implementar `Data Service`:** Criar `src/services/data_service.py` com funções para:
        *   Chamar a API `YahooFinance/get_stock_chart` (usando `ApiClient` e o script de teste `get_yf_data.py` como base).
        *   Receber símbolo (mapeado), intervalo (`1d`), range (`1y`).
        *   Processar a resposta e retornar um DataFrame pandas com OHLCV.
        *   *Opcional (adiado para Fase 2):* Calcular indicadores técnicos básicos (ex: SMA) usando `pandas_ta`.
    2.  **Integrar ao Backend:** Modificar `/api/chart-data` em `src/routes/trading_routes.py` para usar o `Data Service` e retornar dados formatados para Plotly.
    3.  **Criar Estrutura `TradingEnv`:** Criar `src/rl_env/trading_env.py` com a classe `TradingEnv` herdando de `gymnasium.Env`.
        *   Implementar `__init__` para receber o DataFrame de dados.
        *   Implementar `reset` básico.
        *   Definir `observation_space` e `action_space` (inicialmente podem ser placeholders ou simplificados).
    4.  **Testar e Validar:**
        *   Verificar se o gráfico no frontend exibe corretamente os dados históricos reais para os ativos mapeados (ex: PETR4.SA, BTC-USD).
        *   Testar a instanciação básica do `TradingEnv`.
*   **Entregável:** Interface exibindo gráfico com dados reais; Estrutura inicial do `TradingEnv`.

### Fase 2: Implementação Completa do Ambiente de Simulação (Gymnasium)

*   **Objetivo:** Tornar o `TradingEnv` funcional, capaz de simular o processo de trading passo a passo e calcular recompensas.
*   **Tarefas:**
    1.  **Implementar `step()`:**
        *   Receber a ação (0: Manter, 1: Comprar, 2: Vender).
        *   Simular a execução da ordem no preço de fechamento do candle atual (simplificado).
        *   Atualizar a posição mantida pelo ambiente (comprado/vendido/neutro, quantidade/valor).
        *   Calcular o lucro/perda da operação se fechada.
        *   *Integração Pendente:* Chamar `BalanceManager` para atualizar saldo (adiado para garantir foco no ambiente RL primeiro).
        *   Avançar para o próximo candle/timestamp.
    2.  **Implementar `_get_observation()`:** Definir e implementar a lógica para construir o vetor de observação (ex: últimos N candles OHLC, indicadores básicos como SMA).
    3.  **Implementar `_calculate_reward()`:** Definir e implementar a função de recompensa (ex: lucro/perda da última operação fechada, ou variação percentual do valor do portfólio no passo).
    4.  **Refinar `observation_space` e `action_space`:** Definir os espaços corretamente usando `gymnasium.spaces.Box` e `gymnasium.spaces.Discrete`.
    5.  **Testar Ambiente:** Criar um script simples (`test_env.py`) para interagir com o ambiente usando ações aleatórias e verificar se o estado, recompensa e fluxo funcionam.
*   **Entregável:** `TradingEnv` funcional e testado isoladamente.

### Fase 3: Treinamento do Primeiro Agente RL (PPO)

*   **Objetivo:** Treinar um agente de RL básico usando o ambiente criado.
*   **Tarefas:**
    1.  **Adicionar Dependências:** Incluir `stable-baselines3` e `torch` (ou `tensorflow`) em `requirements.txt` e instalar no venv.
    2.  **Criar Script de Treinamento (`train_agent.py`):**
        *   Importar `TradingEnv`, `Data Service`, `PPO` de `stable_baselines3`.
        *   Instanciar `Data Service` para buscar dados (ex: 1 ano de dados diários de PETR4.SA).
        *   Instanciar `TradingEnv` com os dados.
        *   *Opcional:* Envolver o ambiente com `DummyVecEnv` ou `SubprocVecEnv` se necessário.
        *   Instanciar o modelo PPO (`model = PPO("MlpPolicy", env, verbose=1)`).
        *   Treinar o modelo (`model.learn(total_timesteps=10000)` - número baixo inicialmente para teste).
        *   Salvar o modelo treinado (`model.save("ppo_trader_v1")`).
    3.  **Validar Treinamento:** Observar o output do treinamento (verbose=1) para verificar se as recompensas médias tendem a melhorar (mesmo que pouco inicialmente).
*   **Entregável:** Script de treinamento funcional; Primeiro modelo RL treinado (`ppo_trader_v1.zip`).

### Fase 4: Integração do Agente Treinado à Simulação via API

*   **Objetivo:** Permitir que o usuário inicie uma simulação no frontend que utilize o agente RL treinado para tomar decisões.
*   **Tarefas:**
    1.  **Modificar `Simulation Service` (`src/services/simulation_service.py`):**
        *   Criar uma função `run_rl_simulation(asset, entry_value, take_profit, stop_loss)`.
        *   Carregar o modelo PPO treinado (`model = PPO.load("ppo_trader_v1")`).
        *   Instanciar `Data Service` para buscar os dados do `asset`.
        *   Instanciar `TradingEnv` com os dados.
        *   Executar um loop de inferência:
            *   Obter a observação inicial (`obs, _ = env.reset()`).
            *   Iterar pelos passos do ambiente:
                *   Obter a ação do modelo (`action, _ = model.predict(obs, deterministic=True)`).
                *   Executar a ação no ambiente (`obs, reward, terminated, truncated, info = env.step(action)`).
                *   Registrar as ações, recompensas, estado do portfólio.
                *   Parar se `terminated` ou `truncated`.
        *   Retornar um resumo dos resultados da simulação (lucro/perda total, número de trades, etc.).
    2.  **Modificar Endpoint `/api/simulate` (`src/routes/trading_routes.py`):**
        *   Chamar a nova função `run_rl_simulation` do `Simulation Service`.
        *   Retornar o resultado formatado para o frontend.
    3.  **Testar Integração:** Usar o frontend para iniciar a simulação e verificar se:
        *   A simulação executa usando o agente RL.
        *   O resultado é exibido corretamente no painel de status.
*   **Entregável:** Backend capaz de executar simulações guiadas pelo agente RL treinado, acionadas pelo frontend.

## Cronograma e Checkpoints

*   Cada fase representa um marco principal.
*   Ao final de cada fase, o progresso será validado (testes, demonstração se aplicável) antes de iniciar a próxima.
*   O `todo_ia_dev.md` será atualizado após a conclusão de cada fase.

Este plano permite um desenvolvimento iterativo, com entregas funcionais parciais, facilitando a validação e o ajuste de curso conforme necessário.
