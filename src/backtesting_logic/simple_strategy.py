#!/usr/bin/env python
# coding: utf-8

from backtesting import Strategy
from backtesting.lib import crossover

# Exemplo de uma estratégia simples para Backtesting.py
# Esta estratégia usa médias móveis como exemplo.
# Posteriormente, adaptaremos o agente DQN para interagir aqui.

class SimpleMovingAverageStrategy(Strategy):
    """ Uma estratégia simples baseada no cruzamento de médias móveis. """
    # Definir os períodos das duas médias móveis
    n1 = 10  # Média curta
    n2 = 20  # Média longa

    def init(self):
        # Pré-calcular as médias móveis
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)

    def next(self):
        # Se a média curta cruzar acima da média longa, comprar
        if crossover(self.sma1, self.sma2):
            self.buy()

        # Se a média curta cruzar abaixo da média longa, vender
        elif crossover(self.sma2, self.sma1):
            self.sell()

# Import necessário para o cálculo dentro da estratégia
import pandas as pd

