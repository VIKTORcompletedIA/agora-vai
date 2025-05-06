# Documentação do Fluxo de Aprendizado e Orientações para Evolução

Este documento descreve o fluxo de aprendizado proposto para a IA Trader, o estado atual do protótipo implementado e as orientações para os próximos passos de desenvolvimento.

## 1. Fluxo de Aprendizado Proposto (Aprendizado por Reforço)

A abordagem central é o Aprendizado por Reforço (RL), onde um agente (a IA) aprende a tomar decisões de trading (comprar, vender, manter) interagindo com um ambiente simulado que replica o mercado financeiro.

1.  **Ambiente (`TradingEnv`):** Um ambiente customizado, compatível com a interface `gymnasium.Env`, foi criado (`src/rl_env/trading_env.py`). Ele utiliza dados históricos reais (OHLCV) fornecidos pelo `Data Service`.
2.  **Estado (Observação):** O agente observa o estado atual do mercado. No protótipo atual, o espaço de observação está definido, mas a lógica para preenchê-lo com dados relevantes (ex: janela de preços/indicadores recentes, posição atual) ainda precisa ser implementada (`_get_observation`).
3.  **Ação:** Com base na observação, o agente escolhe uma ação (0: Manter, 1: Comprar, 2: Vender), conforme definido no `action_space` (`spaces.Discrete(3)`).
4.  **Transição e Recompensa:** O ambiente executa a ação no passo de tempo atual (candle). A lógica de execução da ação (atualização de saldo, posição, cálculo de comissões) e o cálculo da recompensa (baseada no lucro/perda ou outra métrica) ainda precisam ser implementados nos métodos `step` e `_calculate_reward`.
5.  **Aprendizado:** O agente (a ser treinado com `stable-baselines3`, como PPO) utiliza a sequência de observações, ações e recompensas para aprender uma política ótima que maximize a recompensa acumulada ao longo do tempo.

## 2. Estado Atual do Protótipo (Fase 1 e Início da Fase 2 do Plano)

*   **Integração de Dados Reais:** O `Data Service` (`src/services/data_service.py`) busca dados históricos reais da API `YahooFinance/get_stock_chart` e os fornece ao backend.
*   **Frontend:** O gráfico na interface (`index.html`) agora exibe dados históricos reais (ex: PETR4.SA, BTC-USD) via endpoint `/api/chart-data`.
*   **Ambiente RL (`TradingEnv`):**
    *   A estrutura básica do ambiente compatível com `gymnasium` está criada.
    *   Recebe o DataFrame com dados históricos na inicialização.
    *   O método `reset` foi implementado.
    *   O método `step` avança no tempo, mas a lógica de execução de ordens e cálculo de recompensa são placeholders.
    *   O método `_get_observation` retorna um placeholder.
    *   O método `_calculate_reward` retorna um placeholder (0.0).
    *   Testes básicos (`python -m src.rl_env.trading_env`) confirmam que o ambiente pode ser instanciado e iterado com ações aleatórias, utilizando os dados reais carregados pelo `Data Service`.

## 3. Limitações Atuais

*   **Lógica de Trading Incompleta:** O ambiente `TradingEnv` ainda não implementa a lógica real de compra/venda, cálculo de custos (comissão), atualização de saldo ou valor do portfólio.
*   **Observação Simplista:** O estado (observação) fornecido ao agente é apenas um placeholder e não contém informações úteis do mercado.
*   **Recompensa Inexistente:** A função de recompensa ainda não foi definida ou implementada.
*   **Treinamento Não Iniciado:** Nenhum agente RL foi treinado ainda.
*   **Integração da Simulação RL Pendente:** O endpoint `/api/simulate` ainda utiliza a simulação básica (`run_basic_simulation`) e não o agente RL treinado.

## 4. Orientações para Evolução (Próximos Passos)

Conforme o Plano de Prototipação Incremental (`006_plano_prototipacao_ia.md`):

1.  **Completar `TradingEnv` (Fase 2):**
    *   Implementar a lógica de execução de ordens no método `step`, considerando o preço atual, saldo disponível, comissões e atualização da posição (`shares_held`, `current_position`).
    *   Implementar `_get_observation` para construir um vetor de estado significativo (ex: últimos N preços OHLC, volume, indicadores técnicos básicos calculados pelo `Data Service`, posição atual).
    *   Implementar `_calculate_reward` com uma métrica inicial (ex: lucro/perda realizado ao fechar uma posição, ou variação do net worth).
    *   Refinar `observation_space` com base na observação definida.
    *   Testar exaustivamente o ambiente completo.
2.  **Treinar Agente RL (Fase 3):**
    *   Criar o script `train_agent.py`.
    *   Utilizar `stable-baselines3` (ex: PPO) para treinar um agente no `TradingEnv` completo.
    *   Experimentar com diferentes hiperparâmetros, observações e funções de recompensa.
    *   Salvar o modelo treinado.
3.  **Integrar Agente à Simulação (Fase 4):**
    *   Modificar `Simulation Service` para carregar o modelo treinado.
    *   Implementar `run_rl_simulation` que utiliza o modelo para tomar decisões passo a passo no ambiente.
    *   Atualizar o endpoint `/api/simulate` para chamar `run_rl_simulation`.
    *   Validar a simulação ponta a ponta a partir do frontend.
4.  **Refinamentos Futuros:**
    *   Adicionar mais indicadores técnicos.
    *   Explorar diferentes algoritmos de RL.
    *   Melhorar a função de recompensa (ex: considerar risco).
    *   Implementar backtesting mais robusto.
    *   Considerar dados em tempo real e execução real (muito mais complexo).
