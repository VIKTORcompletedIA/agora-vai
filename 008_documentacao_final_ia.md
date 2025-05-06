# Documentação Final - VIKTOR IA

## Visão Geral

A VIKTOR IA é uma plataforma de trading autônomo que utiliza técnicas de aprendizado por reforço para tomar decisões de compra e venda de ativos financeiros. A plataforma foi projetada para operar de forma contínua até atingir metas de lucro ou limites de perda definidos pelo usuário, utilizando valores fixos para cada operação.

## Arquitetura do Sistema

A plataforma é composta pelos seguintes componentes principais:

1. **Interface Web (Frontend)**
   - Implementada em HTML, CSS e JavaScript
   - Utiliza Plotly.js para visualização de gráficos de candles
   - Suporta temas claro e escuro
   - Exibe saldo virtual, controles de operação e resultados detalhados

2. **Servidor Backend (Flask)**
   - Gerencia requisições da interface web
   - Fornece dados históricos de ativos
   - Controla o saldo virtual
   - Coordena simulações e treinamentos da IA

3. **Ambiente de Trading (TradingEnv)**
   - Implementa a interface Gymnasium para aprendizado por reforço
   - Gerencia o estado do mercado, ações possíveis e recompensas
   - Suporta múltiplas operações sequenciais
   - Implementa metas acumuladas em valores absolutos (R$)

4. **Agente de IA (DQN)**
   - Utiliza Deep Q-Network para aprendizado
   - Toma decisões de compra, venda ou espera
   - Aprende através de tentativa e erro
   - Melhora com o tempo através de treinamento contínuo

5. **Serviço de IA (AIService)**
   - Gerencia treinamento e simulação da IA
   - Armazena e carrega modelos treinados
   - Coordena múltiplas instâncias de agentes para diferentes ativos

## Fluxo de Operação

1. **Configuração Inicial**
   - Usuário seleciona o ativo desejado (ex: BTC-USD)
   - Define o valor de cada operação (ex: R$ 1.000)
   - Estabelece meta de lucro acumulado (ex: R$ 330)
   - Define limite de perda acumulada (ex: R$ 600)

2. **Simulação/Operação**
   - A IA analisa os dados históricos e o estado atual do mercado
   - Toma decisões sequenciais de compra, venda ou espera
   - Utiliza o valor definido para cada operação
   - Continua operando até atingir a meta de lucro ou o limite de perda
   - Atualiza o saldo virtual conforme os resultados

3. **Análise de Resultados**
   - Exibe resumo da simulação (saldo inicial, final, lucro/prejuízo)
   - Mostra gráfico de evolução do saldo
   - Apresenta histórico detalhado de todas as operações
   - Permite análise do desempenho da IA

## Funcionalidades Implementadas

- **Tema Claro/Escuro**: Alternância entre temas visuais
- **Dados Reais**: Integração com Yahoo Finance para dados históricos
- **Saldo Virtual**: Gerenciamento de saldo para simulações
- **Múltiplas Operações**: Capacidade de realizar várias operações sequenciais
- **Metas em Valores Absolutos**: Definição de metas de lucro e stop loss em reais (R$)
- **Aprendizado Autônomo**: IA que aprende através de tentativa e erro
- **Resultados Detalhados**: Visualização completa do histórico de operações

## Uso da Plataforma

### Configuração de Operação

1. Selecione o ativo desejado no menu suspenso
2. Defina o valor de cada operação individual (ex: R$ 1.000)
3. Estabeleça a meta de lucro acumulado em reais (ex: R$ 330)
4. Defina o limite de perda acumulada em reais (ex: R$ 600)
5. Clique em "Iniciar Simulação"

### Interpretação dos Resultados

- **Saldo Virtual**: Exibido no cabeçalho, representa seu capital disponível
- **Painel de Status**: Mostra o status atual da simulação
- **Modal de Resultados**: Exibe detalhes completos após a simulação
  - Resumo financeiro (saldo inicial, final, lucro/prejuízo)
  - Gráfico de evolução do saldo
  - Tabela com histórico de todas as operações

## Personalização e Extensão

### Adição de Novos Ativos

Para adicionar novos ativos à plataforma:

1. Modifique o arquivo `src/static/index.html` para incluir novas opções no seletor de ativos
2. Atualize o serviço `data_service.py` para suportar a busca de dados do novo ativo
3. Teste a integração para garantir que os dados são exibidos corretamente

### Ajuste de Parâmetros da IA

Os principais parâmetros da IA podem ser ajustados em `src/rl_agent/trainer.py`:

- `learning_rate`: Taxa de aprendizado do modelo
- `gamma`: Fator de desconto para recompensas futuras
- `exploration_fraction`: Controla a exploração vs. exploração
- `train_freq`: Frequência de atualização do modelo durante treinamento

### Implementação de Novos Indicadores

Para adicionar novos indicadores técnicos:

1. Modifique `src/rl_env/trading_env.py` para calcular e incluir os novos indicadores
2. Atualize o método `_get_observation()` para incluir os novos valores no estado
3. Ajuste a dimensão do espaço de observação conforme necessário

## Próximos Passos

### Treinamento Avançado

Para melhorar o desempenho da IA:

1. Execute treinamentos mais longos (1000+ episódios)
2. Experimente diferentes configurações de hiperparâmetros
3. Utilize dados históricos mais extensos
4. Implemente técnicas de validação cruzada temporal

### Integração com APIs de Corretoras

Para operações com dados em tempo real:

1. Implemente conectores para APIs de corretoras (Binance, XP, etc.)
2. Adicione autenticação e gerenciamento de chaves de API
3. Desenvolva modo de operação em papel (paper trading)
4. Implemente salvaguardas para operações reais

### Análise de Desempenho

Para avaliar e melhorar a estratégia:

1. Implemente métricas adicionais (Sharpe ratio, drawdown máximo, etc.)
2. Adicione comparações com estratégias de referência (benchmark)
3. Desenvolva visualizações de desempenho por período
4. Implemente backtesting com diferentes janelas temporais

## Considerações Finais

A VIKTOR IA representa uma abordagem moderna para trading automatizado, utilizando técnicas de aprendizado por reforço para tomar decisões de investimento. A plataforma foi projetada para ser extensível e personalizável, permitindo adaptação a diferentes estratégias e mercados.

O sistema atual funciona como uma prova de conceito robusta, demonstrando a viabilidade da abordagem e fornecendo uma base sólida para desenvolvimentos futuros. Com treinamento adequado e refinamentos adicionais, a VIKTOR IA tem o potencial de se tornar uma ferramenta valiosa para traders que buscam automatizar suas estratégias de investimento.
