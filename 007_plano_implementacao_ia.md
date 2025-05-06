# Plano de Implementação da Lógica de IA Autônoma

Este documento detalha o plano para implementar a lógica de Inteligência Artificial (IA) autônoma no sistema IA Trader Pessoal, focando na análise de dados de mercado, gráficos e tomada de decisões de trade (compra/venda) baseadas em aprendizado por reforço (Reinforcement Learning - RL).

## 1. Objetivos

*   Desenvolver um agente de RL capaz de aprender estratégias de trading.
*   Integrar o agente ao ambiente de simulação (`TradingEnv`) já criado.
*   Utilizar os dados históricos reais (obtidos via `data_service.py`) para treinamento e simulação.
*   Permitir que a IA opere com base nos parâmetros definidos pelo usuário (Valor da Operação, Meta de Lucro, Stop Loss) dentro do saldo virtual.
*   Fornecer feedback sobre as decisões e o desempenho da IA ao usuário.

## 2. Abordagem Proposta (Aprendizado por Reforço)

Utilizaremos Aprendizado por Reforço (RL) como a técnica principal para a IA. A ideia é que o agente aprenda por tentativa e erro, interagindo com o ambiente de simulação (`TradingEnv`).

*   **Ambiente (`TradingEnv`):** Já iniciado, precisa ser completado. Ele fornecerá o estado atual do mercado (preços, indicadores técnicos básicos), receberá as ações do agente (comprar, vender, manter) e calculará a recompensa (lucro/prejuízo) e o próximo estado.
*   **Agente:** Implementaremos um agente de RL (por exemplo, usando bibliotecas como Stable Baselines3 ou TF-Agents). O agente observará o estado do ambiente e decidirá a próxima ação para maximizar a recompensa acumulada.
*   **Estado:** O estado incluirá informações relevantes do mercado, como preços recentes (OHLC), volume e, potencialmente, indicadores técnicos simples (Médias Móveis, RSI) calculados a partir dos dados históricos.
*   **Ações:** As ações possíveis para o agente serão:
    *   0: Manter (não fazer nada)
    *   1: Comprar (abrir uma posição comprada com o valor definido pelo usuário)
    *   2: Vender (fechar a posição atual, se houver)
*   **Recompensa:** A recompensa será baseada no lucro ou prejuízo realizado ao fechar uma posição, ou na variação do valor da posição em aberto a cada passo, incentivando o agente a buscar lucro e evitar perdas, respeitando o Stop Loss e Take Profit definidos.

## 3. Etapas Incrementais

1.  **Completar `TradingEnv`:**
    *   Implementar a lógica de `step()`: processar ação do agente, atualizar estado, calcular recompensa, verificar condições de término (Stop Loss, Take Profit, fim dos dados).
    *   Implementar `reset()`: reiniciar o ambiente para um novo episódio de simulação/treinamento.
    *   Definir claramente os espaços de observação e ação.
    *   Integrar o cálculo de indicadores técnicos básicos (ex: Média Móvel Simples) no estado.
2.  **Selecionar e Implementar Agente RL:**
    *   Escolher uma biblioteca de RL (ex: Stable Baselines3).
    *   Selecionar um algoritmo de RL adequado (ex: PPO, A2C, DQN).
    *   Implementar o agente básico usando a biblioteca escolhida.
3.  **Treinamento Inicial:**
    *   Utilizar os dados históricos (ex: 1 ano de dados diários de PETR4.SA) para treinar o agente.
    *   Monitorar o processo de treinamento (recompensas, convergência).
    *   Salvar o modelo treinado.
4.  **Integração com Backend Flask:**
    *   Modificar a rota `/api/simulate` para carregar o modelo treinado e usar o agente para tomar decisões dentro do `TradingEnv`, em vez da simulação básica atual.
    *   Passar os parâmetros do usuário (valor, TP, SL) para o ambiente.
    *   Retornar o resultado da operação realizada pela IA.
5.  **Testes e Validação:**
    *   Testar o fluxo completo: usuário define parâmetros, clica em simular, IA opera, resultado é exibido, saldo é atualizado.
    *   Validar com o usuário se o comportamento inicial da IA (mesmo que simples) faz sentido.

## 4. Tecnologias e Bibliotecas

*   **Python:** Linguagem principal.
*   **Flask:** Framework web backend.
*   **Gymnasium:** Para criar o ambiente de RL.
*   **Pandas:** Para manipulação de dados históricos.
*   **Stable Baselines3 (ou similar):** Para implementar e treinar o agente RL.
*   **YahooFinance API (via `data_api`):** Para obter dados históricos.

## 5. Próximos Passos Imediatos

*   Iniciar a implementação detalhada do `TradingEnv.step()` e `TradingEnv.reset()`.
*   Instalar a biblioteca Stable Baselines3.
*   Implementar o cálculo de uma Média Móvel Simples para incluir no estado.

