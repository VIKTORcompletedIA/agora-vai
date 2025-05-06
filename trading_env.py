# src/rl_env/trading_env.py

import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces

# Importar função para buscar dados históricos
# Ajuste o caminho se necessário, dependendo da estrutura final
# Supondo que data_service.py esteja em src/services
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.data_service import get_historical_data

class TradingEnv(gym.Env):
    """Ambiente customizado para simulação de trading com Aprendizado por Reforço."""
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, symbol="PETR4.SA", region="BR", interval="1d", range_period="1y", 
                 initial_balance=10000, trade_amount=1000, 
                 target_profit_abs=330, stop_loss_abs=600, 
                 sma_window=20, max_steps=None, render_mode=None):
        super().__init__()

        self.symbol = symbol
        self.region = region
        self.interval = interval
        self.range_period = range_period
        self.initial_balance = initial_balance
        self.trade_amount = trade_amount # Valor fixo por operação (usado repetidamente)
        
        # Metas em valores absolutos (R$)
        self.target_profit_abs = target_profit_abs
        self.stop_loss_abs = stop_loss_abs
        
        self.sma_window = sma_window
        self.render_mode = render_mode

        # Carregar dados históricos
        self.df = self._load_data()
        if self.df is None or self.df.empty:
            raise ValueError("Não foi possível carregar os dados históricos.")
        
        # Calcular SMA
        self._calculate_sma()
        
        # Definir o número máximo de passos (se não fornecido, usa o tamanho dos dados)
        self.max_steps = max_steps if max_steps is not None else len(self.df) - self.sma_window - 1
        if self.max_steps <= 0:
            raise ValueError("Dados insuficientes para o número de passos ou janela SMA.")

        # Espaço de Ação: 0=Manter, 1=Comprar, 2=Vender
        self.action_space = spaces.Discrete(3)

        # Espaço de Observação:
        # [Preço Atual (Close), SMA, Posição Atual (0=nenhuma, 1=comprado), Saldo Normalizado]
        # Normalizar saldo e preço pode ser útil, mas começaremos sem normalização complexa
        # Usaremos Box com limites razoáveis. Ajustar conforme necessário.
        # Limites inferiores: [0, 0, 0, 0]
        # Limites superiores: [Preço Máximo Histórico * 2, Preço Máximo Histórico * 2, 1, Saldo Inicial * 10]
        max_price = self.df["close"].max() * 2
        max_balance = self.initial_balance * 10
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0], dtype=np.float32),
            high=np.array([max_price, max_price, 1, max_balance], dtype=np.float32),
            shape=(4,), dtype=np.float32
        )

        # Estado do ambiente
        self.reset()

    def _load_data(self):
        """Carrega os dados históricos usando o data_service."""
        try:
            df = get_historical_data(self.symbol, self.region, self.interval, self.range_period)
            # Remover linhas com NaN que podem surgir no início
            df.dropna(inplace=True)
            # Resetar índice para garantir acesso numérico
            df.reset_index(inplace=True)
            # Renomear colunas para minúsculas para consistência
            df.columns = [col.lower() for col in df.columns]
            return df
        except Exception as e:
            print(f"Erro ao carregar dados no ambiente: {e}")
            return None

    def _calculate_sma(self):
        """Calcula a Média Móvel Simples (SMA)."""
        if "close" in self.df.columns:
            self.df["sma"] = self.df["close"].rolling(window=self.sma_window).mean()
            # Remover NaNs gerados pelo rolling mean inicial
            self.df.dropna(inplace=True)
            # Resetar índice novamente após dropna
            self.df.reset_index(drop=True, inplace=True)
        else:
            raise ValueError("Coluna 'close' não encontrada nos dados.")

    def _get_observation(self):
        """Retorna a observação atual do ambiente."""
        obs_step = self.current_step # Índice no DataFrame ajustado para SMA
        if obs_step >= len(self.df):
             # Se current_step ultrapassar, usar o último dado válido
             obs_step = len(self.df) - 1
             
        current_price = self.df.loc[obs_step, "close"]
        current_sma = self.df.loc[obs_step, "sma"]
        
        # Normalizar saldo (exemplo simples: dividir pelo saldo inicial)
        normalized_balance = self.balance / self.initial_balance 
        
        # Observação: [Preço, SMA, Posição, Saldo Normalizado]
        # Usar preço e SMA diretamente por enquanto
        observation = np.array([current_price, current_sma, self.position, self.balance], dtype=np.float32)
        
        # Verificar se a observação está dentro dos limites definidos
        if not self.observation_space.contains(observation):
            # Ajustar ou logar o problema
            # print(f"Observação fora dos limites: {observation}")
            # Exemplo de ajuste (clipping): pode não ser o ideal
            observation = np.clip(
                observation, 
                self.observation_space.low, 
                self.observation_space.high
            )
            
        return observation

    def _get_info(self):
        """Retorna informações adicionais sobre o estado."""
        return {
            "step": self.current_step,
            "balance": self.balance,
            "position": self.position,
            "entry_price": self.entry_price,
            "shares_held": self.shares_held,
            "total_profit": self.total_profit,
            "last_trade_profit": self.last_trade_profit,
            "accumulated_profit": self.accumulated_profit,
            "initial_episode_balance": self.initial_episode_balance
        }

    def reset(self, seed=None, options=None):
        """Reseta o ambiente para um novo episódio."""
        super().reset(seed=seed)

        self.balance = self.initial_balance
        self.initial_episode_balance = self.initial_balance  # Saldo no início deste episódio
        self.current_step = 0 # Começa no primeiro ponto de dado VÁLIDO após cálculo da SMA
        self.position = 0
        self.entry_price = 0
        self.shares_held = 0
        self.total_profit = 0
        self.last_trade_profit = 0
        self.accumulated_profit = 0  # Lucro/prejuízo acumulado neste episódio

        observation = self._get_observation()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        """Executa um passo no ambiente com base na ação."""
        self.last_trade_profit = 0 # Reseta o lucro do último trade a cada passo
        current_price = self.df.loc[self.current_step, "close"]
        terminated = False
        truncated = False

        # --- Lógica da Ação ---
        if action == 1: # Comprar
            if self.position == 0 and self.balance >= self.trade_amount:
                self.position = 1
                self.entry_price = current_price
                self.shares_held = self.trade_amount / current_price
                self.balance -= self.trade_amount
                # print(f"Step {self.current_step}: COMPRA @ {current_price:.2f}, Saldo: {self.balance:.2f}")
            # else: Não faz nada se já comprado ou sem saldo
                
        elif action == 2: # Vender
            if self.position == 1:
                profit = (current_price - self.entry_price) * self.shares_held
                self.balance += self.trade_amount + profit # Retorna o valor inicial + lucro/prejuízo
                self.total_profit += profit
                self.last_trade_profit = profit
                self.accumulated_profit += profit  # Atualiza o lucro acumulado neste episódio
                self.position = 0
                self.entry_price = 0
                self.shares_held = 0
                # print(f"Step {self.current_step}: VENDA @ {current_price:.2f}, Lucro/Prejuízo: {profit:.2f}, Saldo: {self.balance:.2f}")
            # else: Não faz nada se não estiver comprado

        # else: action == 0 (Manter) - Nenhuma ação de trade

        # --- Verificar Condições de Término baseadas em valores absolutos ---
        # Verificar se atingiu o lucro alvo em valor absoluto
        if self.accumulated_profit >= self.target_profit_abs:
            terminated = True
            # print(f"Episódio terminado: Meta de lucro atingida (R$ {self.accumulated_profit:.2f})")
            
        # Verificar se atingiu o stop loss em valor absoluto
        elif self.accumulated_profit <= -self.stop_loss_abs:
            terminated = True
            # print(f"Episódio terminado: Stop Loss atingido (R$ {self.accumulated_profit:.2f})")

        # --- Atualizar Valor da Posição ---
        current_portfolio_value = self.balance
        if self.position == 1:
            current_position_value = self.shares_held * current_price
            current_portfolio_value += current_position_value
            
            # Calcular lucro/prejuízo não realizado para informação
            unrealized_profit = (current_price - self.entry_price) * self.shares_held
            unrealized_profit_pct = (current_price - self.entry_price) / self.entry_price

        # --- Calcular Recompensa --- 
        # Recompensa baseada no lucro/prejuízo realizado neste passo
        reward = self.last_trade_profit
            
        # --- Avançar Tempo e Verificar Fim dos Dados ---
        self.current_step += 1
        if self.current_step >= self.max_steps:
            # Se ainda estiver comprado no final, força a venda
            if self.position == 1:
                final_price = self.df.loc[self.current_step -1, "close"]
                profit = (final_price - self.entry_price) * self.shares_held
                self.balance += self.trade_amount + profit
                self.total_profit += profit
                self.last_trade_profit = profit
                self.accumulated_profit += profit  # Atualiza o lucro acumulado
                self.position = 0
            terminated = True # Termina porque acabaram os dados
            truncated = True # Indica que terminou por limite de tempo/dados

        # Obter próxima observação e info
        observation = self._get_observation()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def render(self):
        """Renderiza o ambiente (opcional)."""
        if self.render_mode == "human":
            return self._render_frame()
        else:
            # Modo "rgb_array" poderia retornar um frame como numpy array
            pass 

    def _render_frame(self):
        """Lógica de renderização para modo human (ex: print)."""
        current_price = self.df.loc[self.current_step, "close"] if self.current_step < len(self.df) else "N/A"
        print(f"Passo: {self.current_step}/{self.max_steps}")
        print(f"Preço Atual: {current_price}")
        print(f"Saldo: {self.balance:.2f}")
        print(f"Posição: {'Comprado' if self.position == 1 else 'Nenhuma'}")
        if self.position == 1:
            print(f"  Preço Entrada: {self.entry_price:.2f}")
            print(f"  Ações: {self.shares_held:.4f}")
        print(f"Lucro Total: {self.total_profit:.2f}")
        print(f"Lucro Acumulado neste Episódio: {self.accumulated_profit:.2f}")
        print(f"Meta de Lucro: R$ {self.target_profit_abs:.2f}")
        print(f"Stop Loss: R$ {self.stop_loss_abs:.2f}")
        print("---")

    def close(self):
        """Fecha o ambiente e limpa recursos (opcional)."""
        pass

# --- Bloco para Teste Simples do Ambiente (opcional) ---
if __name__ == "__main__":
    print("Testando o ambiente TradingEnv...")
    try:
        # Usar dados de cripto para teste
        env = TradingEnv(
            symbol="BTC-USD", 
            region="US", 
            range_period="6mo", 
            sma_window=10, 
            trade_amount=1000,
            target_profit_abs=330,  # Meta de lucro em R$
            stop_loss_abs=600,      # Stop loss em R$
            render_mode="human"
        )
        
        # Verificar espaços
        print(f"Espaço de Ação: {env.action_space}")
        print(f"Exemplo Ação: {env.action_space.sample()}")
        print(f"Espaço de Observação: {env.observation_space}")
        print(f"Exemplo Observação (Low): {env.observation_space.low}")
        print(f"Exemplo Observação (High): {env.observation_space.high}")

        # Testar reset
        obs, info = env.reset()
        print("\n--- Reset OK ---")
        print(f"Observação Inicial: {obs}")
        print(f"Info Inicial: {info}")

        # Testar alguns passos com ações aleatórias
        print("\n--- Testando Steps ---")
        terminated = False
        truncated = False
        total_reward = 0
        step_count = 0
        while not terminated and not truncated:
            action = env.action_space.sample() # Ação aleatória
            # action = 1 # Forçar compra
            # action = 2 # Forçar venda
            print(f"\nExecutando Ação: {'Manter' if action == 0 else ('Comprar' if action == 1 else 'Vender')}")
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            step_count += 1
            
            if terminated or truncated:
                print("\n--- Episódio Terminou ---")
                print(f"Motivo: {'Meta/Stop Loss ou Fim dos Dados' if terminated else 'Limite de Passos'}")
                print(f"Passos Totais: {step_count}")
                print(f"Recompensa Total: {total_reward:.2f}")
                print(f"Saldo Final: {info['balance']:.2f}")
                print(f"Lucro Total Final: {info['total_profit']:.2f}")
                print(f"Lucro Acumulado no Episódio: {info['accumulated_profit']:.2f}")
                break
            
            # Limitar passos para teste rápido
            if step_count >= 50:
                print("\n--- Limite de passos de teste atingido ---")
                truncated = True # Força parada para teste

        env.close()
        print("\n--- Teste Concluído --- ")

    except ValueError as ve:
        print(f"\nErro de Valor durante o teste: {ve}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado durante o teste: {e}")
        import traceback
        traceback.print_exc()
