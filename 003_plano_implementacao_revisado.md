# Plano de Implementação Incremental (Revisão Pós-Feedback)

Com a arquitetura e o design revisados para incorporar seu feedback, detalhamos agora o plano para implementar as novas funcionalidades e os ajustes visuais de forma incremental. A prioridade será reestruturar a interface para se assemelhar à plataforma Rico, integrar o gráfico de candles e implementar o gerenciamento de saldo virtual, estabelecendo a base para futuras evoluções da IA.

## Fase 1: Reestruturação Visual e Integração do Gráfico de Candles

O foco desta fase é transformar a experiência visual e introduzir o elemento central: o gráfico.

1.  **Refatoração do Layout (Frontend):** Modificaremos o arquivo `/home/ubuntu/ia_trader_app/src/static/index.html` e seus estilos CSS associados. O layout será reorganizado para apresentar uma área principal destinada ao gráfico de candles. O dropdown de seleção de ativos será posicionado acima desta área. Os controles (valor de entrada, take profit, stop loss, botão iniciar/parar) serão agrupados em um painel lateral ou inferior, buscando clareza e simplicidade visual. Uma nova área será designada para exibir o saldo virtual.
2.  **Seleção e Integração da Biblioteca de Gráficos:** Escolheremos uma biblioteca JavaScript adequada para gráficos financeiros (ex: Lightweight Charts, Plotly.js). A biblioteca será integrada ao `index.html`.
3.  **Adaptação do Serviço de Dados (Backend):** O `src/services/data_service.py` (a ser criado ou adaptado) será responsável por fornecer dados no formato OHLCV. Inicialmente, utilizaremos dados históricos fixos ou gerados proceduralmente para testes.
4.  **Novo Endpoint para Gráfico (Backend):** Criaremos um novo endpoint na API Flask (em `src/routes/trading_routes.py` ou um novo arquivo de rotas) que servirá os dados OHLCV formatados para a biblioteca de gráficos.
5.  **Conexão Gráfico-Backend (Frontend):** O JavaScript no `index.html` será atualizado para fazer requisições a este novo endpoint e alimentar a biblioteca de gráficos, exibindo os candles na interface.

*Objetivo ao final da Fase 1:* Ter uma interface visualmente reestruturada com um gráfico de candles exibindo dados estáticos ou históricos simples, e os controles reposicionados.

## Fase 2: Implementação do Saldo Virtual e Valor de Entrada

Esta fase introduz a lógica de gerenciamento de capital simulado.

1.  **Criação do Gerenciador de Saldo (Backend):** Implementaremos um novo módulo, `src/services/balance_manager.py`, com funções para inicializar, consultar, debitar (valor de entrada) e creditar/debitar (resultado da operação) o saldo virtual. Inicialmente, o saldo pode ser mantido em memória ou em um arquivo simples para persistência básica entre reinicializações do servidor.
2.  **Integração do Saldo na Simulação (Backend):** O `src/services/simulation_service.py` será modificado para:
    *   Receber o `valor_entrada` como parâmetro.
    *   Chamar o `BalanceManager` para verificar se há saldo suficiente e para debitar o `valor_entrada` no início da operação simulada.
    *   Calcular o lucro/perda com base no `valor_entrada`.
    *   Chamar o `BalanceManager` para atualizar o saldo com o resultado ao final da operação.
3.  **Atualização da API (Backend):** O endpoint `/api/simulate` será atualizado para lidar com o `valor_entrada` e interagir com o `BalanceManager`. Novos endpoints podem ser criados para consultar o saldo atual.
4.  **Exibição e Interação do Saldo (Frontend):** O `index.html` será modificado para:
    *   Exibir o saldo virtual atual (buscando via API ao carregar a página e após cada simulação).
    *   Garantir que o campo `valor_entrada` seja enviado corretamente na requisição para `/api/simulate`.
    *   Atualizar a exibição do resultado da simulação para incluir o impacto no saldo.

*Objetivo ao final da Fase 2:* Ter o gerenciamento de saldo fictício funcional, com operações simuladas utilizando um valor de entrada definido pelo usuário e refletindo o resultado no saldo exibido na interface.

## Fase 3: Refinamento da Interface e Validação Inicial

Nesta fase, polimos a experiência do usuário e preparamos para validação.

1.  **Melhorias no Gráfico:** Adicionar funcionalidades básicas de interação ao gráfico, como zoom e rolagem no tempo, se suportado pela biblioteca escolhida.
2.  **Feedback Visual Aprimorado:** Melhorar a forma como o status da simulação (aguardando, ativa, concluída), os resultados e as atualizações de saldo são comunicados ao usuário na interface.
3.  **Testes Integrados:** Realizar testes completos do fluxo: carregar página -> ver gráfico e saldo -> selecionar ativo -> definir parâmetros (entrada, TP, SL) -> iniciar simulação -> observar atualização do painel de resultados e do saldo.
4.  **Preparação para Validação:** Organizar o código, garantir que o servidor Flask esteja estável e preparar o ambiente para que você possa testar a nova versão.

*Objetivo ao final da Fase 3:* Ter um protótipo funcional com as principais melhorias visuais e funcionais implementadas (gráfico básico, gerenciamento de saldo, valor de entrada), pronto para sua avaliação.

## Fases Subsequentes (Planejamento Contínuo)

Após a validação da Fase 3, continuaremos com as etapas planejadas anteriormente, agora enriquecidas com os novos requisitos:
*   Integração de dados em tempo real (para gráfico e simulação).
*   Desenvolvimento e integração de modelos de IA mais sofisticados e do módulo de aprendizado.
*   Implementação de persistência robusta com banco de dados.
*   Adição de mais ativos, indicadores no gráfico, etc.

Este plano revisado foca em entregar as mudanças visuais e funcionais mais impactantes primeiro, permitindo validações frequentes e garantindo que o desenvolvimento permaneça alinhado com sua visão.
