# Mapeamento de Componentes da Interface (Baseado nas Imagens)

Este documento detalha os componentes visuais e funcionais identificados nas imagens de referência para a interface da plataforma de trading com IA.

## Layout Geral

*   **Tema:** Escuro (fundo preto/cinza escuro, texto branco/cinza claro, elementos de destaque em verde e vermelho).
*   **Estrutura Principal:** Layout de duas colunas principais:
    *   Coluna Esquerda (Maior): Gráfico de Trading.
    *   Coluna Direita (Menor): Painel de Controle e Status.
*   **Cabeçalho:** Barra superior com logo, nome do usuário e saldo.
*   **Modal:** Janela pop-up para exibir resultados/mensagens importantes.

## Componentes Detalhados

### 1. Cabeçalho
*   **Logo:** "TITAN.IA" (Canto superior esquerdo).
*   **Nome do Usuário:** Ex: "Cesar Bicca Pereira" (Centro/Direita).
*   **Saldo:** Valor monetário (Ex: "R$ 433,58") com um ícone (Canto superior direito, fundo verde).

### 2. Coluna Esquerda (Gráfico)
*   **Seleção de Ativo/Par:** Dropdown mostrando o ativo atual (Ex: "AUD/JPY (OTC)") com ícone. Ao clicar, exibe lista de outros ativos com nome, ícone e "lucratividade" (%).
*   **Seleção de Timeframe:** Dropdown abaixo da seleção de ativo (Ex: "30s") - *Inferido, pode não ser necessário para backtesting inicial.*
*   **Área do Gráfico:**
    *   Tipo: Gráfico de Velas (Candlestick) - Verde para alta, Vermelho para baixa.
    *   Eixos: Eixo Y (Preço), Eixo X (Tempo).
    *   Grid: Linhas horizontais e verticais.
    *   Indicadores Visuais: Possivelmente marcadores de entrada/saída (setas azuis/vermelhas na imagem 1), linha de preço atual.

### 3. Coluna Direita (Painel de Controle e Status)

#### 3.1 Painel de Configuração (Visível na Imagem 2)
*   **Título/Seleção IA:** Dropdown "Inteligência Artificial" (Ex: "GPT 4o Mini").
*   **Seleção Estratégia:** Dropdown "Estratégia" (Ex: "Agressivo").
*   **Input Valor de Entrada:** Campo para definir o valor da operação (Ex: "R$ 5,00").
*   **Input Meta:** Campo para definir a meta de lucro (Ex: "R$ 10,00").
*   **Input Stop Loss:** Campo para definir o limite de perda (Ex: "R$ 200,00").
*   **Botão Iniciar:** Botão verde com ícone de play (Ex: "▷ INICIAR").
*   **Opção Configurar Automático:** Checkbox/Toggle (funcionalidade a definir).
*   **Display de Lucro/Prejuízo Atual:** Mostra o resultado da operação atual (Ex: "R$ 0,00" antes de iniciar, "+R$ 12,84" após finalizar na imagem 3).

#### 3.2 Painel de Status (Visível na Imagem 1)
*   **Botão Parar:** Botão vermelho (Ex: "◎ PARAR").
*   **Alerta:** Mensagem de aviso (Ex: "⚠ Não minimize ou deixe a tela desligar durante a operação!").
*   **Informações da Operação Ativa:**
    *   Ativo (Ex: "CAD/CHF (OTC)").
    *   Modelo IA (Ex: "GPT 4o Mini").
    *   Estratégia (Ex: "Agressivo").
    *   Meta e Stop Loss definidos.
    *   Lucro/Prejuízo Atual (grande, verde/vermelho com seta, Ex: "+ R$ 3,70 ▲").
    *   Indicador de Progresso/Status:
        *   Linha vertical com pontos.
        *   Ponto 1 (Verde): Entrada realizada (com valor, Ex: "R$ 5,00").
        *   Ponto 2 (Laranja): Aguardando saída (com timer, Ex: "00:03").

### 4. Modal de Resultado (Visível na Imagem 3)
*   **Título/Ícone:** Ícone de gráfico/tendência.
*   **Mensagem:** Texto informativo (Ex: "Parabéns, você atingiu sua meta! A operação da IA foi finalizada, mas você pode retornar quando quiser.").
*   **Botão OK:** Botão para fechar o modal.

## Funcionalidades Implícitas/Necessárias

*   **Carregamento de Dados:** Obter dados históricos (OHLCV) para o ativo selecionado.
*   **Comunicação com Backend:**
    *   Enviar parâmetros de configuração (ativo, IA, estratégia, valores) para iniciar o backtest/operação.
    *   Receber status da operação em andamento (lucro/prejuízo, tempo restante, etc.).
    *   Receber resultados finais do backtest/operação.
    *   Receber dados para atualizar o gráfico.
*   **Atualização da Interface:** Refletir dinamicamente o status da operação, lucro/prejuízo, gráfico, etc.
*   **Gerenciamento de Estado:** Manter o estado da aplicação (operação ativa/inativa, parâmetros selecionados, etc.).

## Adaptações para Backtesting

*   A seleção de "Ativo" pode ser mapeada para diferentes arquivos de dados históricos (como o `btc_usd_data.json`).
*   Os parâmetros de "IA" e "Estratégia" podem ser mapeados para diferentes configurações ou até mesmo diferentes classes de estratégia no `Backtesting.py` (inicialmente, usaremos a `DQNStrategy`).
*   O painel de status "em tempo real" será simulado com base nos resultados do backtest.
*   O gráfico exibirá os dados históricos e os trades executados pelo backtest.
*   "Valor de Entrada", "Meta" e "Stop Loss" podem ser usados como parâmetros para a lógica da estratégia ou para análise pós-backtest, mas a `DQNStrategy` atual não os utiliza diretamente para tomar decisões (ela decide comprar/vender/manter com base no estado e Q-values).

Este mapeamento servirá como base para a estruturação do HTML, CSS e JavaScript.
