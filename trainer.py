# src/rl_agent/trainer.py

import os
import numpy as np
import torch
import json
import time
from datetime import datetime
from src.rl_env.trading_env import TradingEnv
from src.rl_agent.dqn_agent import DQNAgent

class TradingTrainer:
    """Classe para treinar e executar o agente de IA no ambiente de trading."""
    
    def __init__(self, symbol="BTC-USD", region="US", interval="1d", range_period="1y",
                 initial_balance=10000, trade_amount=1000, 
                 target_profit_abs=330, stop_loss_abs=600,
                 sma_window=20, max_steps=None,
                 model_dir="/home/ubuntu/ia_trader_app/models"):
        """
        Inicializa o treinador com parâmetros para o ambiente e o agente.
        
        Args:
            symbol: Símbolo do ativo (ex: "BTC-USD", "PETR4.SA")
            region: Região do mercado (ex: "US", "BR")
            interval: Intervalo dos dados (ex: "1d", "1h")
            range_period: Período dos dados (ex: "1y", "6mo")
            initial_balance: Saldo inicial para simulação
            trade_amount: Valor de cada operação individual
            target_profit_abs: Meta de lucro em valor absoluto (R$)
            stop_loss_abs: Stop loss em valor absoluto (R$)
            sma_window: Janela para cálculo da média móvel simples
            max_steps: Número máximo de passos por episódio
            model_dir: Diretório para salvar/carregar modelos
        """
        self.symbol = symbol
        self.region = region
        self.interval = interval
        self.range_period = range_period
        self.initial_balance = initial_balance
        self.trade_amount = trade_amount
        self.target_profit_abs = target_profit_abs
        self.stop_loss_abs = stop_loss_abs
        self.sma_window = sma_window
        self.max_steps = max_steps
        self.model_dir = model_dir
        
        # Criar diretório de modelos se não existir
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Inicializar ambiente
        self.env = TradingEnv(
            symbol=self.symbol,
            region=self.region,
            interval=self.interval,
            range_period=self.range_period,
            initial_balance=self.initial_balance,
            trade_amount=self.trade_amount,
            target_profit_abs=self.target_profit_abs,
            stop_loss_abs=self.stop_loss_abs,
            sma_window=self.sma_window,
            max_steps=self.max_steps
        )
        
        # Inicializar agente
        state_size = self.env.observation_space.shape[0]
        action_size = self.env.action_space.n
        self.agent = DQNAgent(
            state_size=state_size,
            action_size=action_size,
            learning_rate=0.001,
            gamma=0.99,
            epsilon=1.0,
            epsilon_min=0.01,
            epsilon_decay=0.995,
            memory_size=10000,
            batch_size=64,
            target_update=10
        )
        
        # Histórico de treinamento
        self.training_history = {
            "episodes": [],
            "rewards": [],
            "balances": [],
            "profits": [],
            "steps": [],
            "epsilon": []
        }
        
    def train(self, episodes=100, batch_size=64, save_interval=10, verbose=True):
        """
        Treina o agente no ambiente de trading.
        
        Args:
            episodes: Número de episódios de treinamento
            batch_size: Tamanho do lote para treinamento
            save_interval: Intervalo para salvar o modelo
            verbose: Se True, exibe informações durante o treinamento
            
        Returns:
            Histórico de treinamento
        """
        start_time = time.time()
        
        for episode in range(1, episodes + 1):
            state, info = self.env.reset()
            total_reward = 0
            step_count = 0
            done = False
            
            while not done:
                # Escolher ação
                action = self.agent.act(state)
                
                # Executar ação
                next_state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                
                # Armazenar experiência
                self.agent.remember(state, action, reward, next_state, done)
                
                # Treinar agente (experience replay)
                self.agent.replay()
                
                # Atualizar estado e contadores
                state = next_state
                total_reward += reward
                step_count += 1
            
            # Registrar resultados do episódio
            self.training_history["episodes"].append(episode)
            self.training_history["rewards"].append(total_reward)
            self.training_history["balances"].append(info["balance"])
            self.training_history["profits"].append(info["accumulated_profit"])
            self.training_history["steps"].append(step_count)
            self.training_history["epsilon"].append(self.agent.epsilon)
            
            # Exibir progresso
            if verbose and (episode % 10 == 0 or episode == 1):
                elapsed = time.time() - start_time
                print(f"Episódio {episode}/{episodes} | Recompensa: {total_reward:.2f} | "
                      f"Saldo: {info['balance']:.2f} | Lucro: {info['accumulated_profit']:.2f} | "
                      f"Passos: {step_count} | Epsilon: {self.agent.epsilon:.4f} | "
                      f"Tempo: {elapsed:.2f}s")
            
            # Salvar modelo periodicamente
            if episode % save_interval == 0:
                self.save_model(f"{self.symbol}_{episode}")
        
        # Salvar modelo final
        self.save_model(f"{self.symbol}_final")
        
        # Salvar histórico de treinamento
        self.save_training_history()
        
        return self.training_history
    
    def test(self, episodes=10, render=False, verbose=True):
        """
        Testa o agente treinado no ambiente de trading.
        
        Args:
            episodes: Número de episódios de teste
            render: Se True, renderiza o ambiente durante o teste
            verbose: Se True, exibe informações durante o teste
            
        Returns:
            Resultados do teste
        """
        test_results = {
            "episodes": [],
            "rewards": [],
            "balances": [],
            "profits": [],
            "steps": [],
            "success_rate": 0
        }
        
        successful_episodes = 0
        
        for episode in range(1, episodes + 1):
            state, info = self.env.reset()
            total_reward = 0
            step_count = 0
            done = False
            
            while not done:
                # Escolher ação (sem exploração durante teste)
                action = self.agent.act(state, training=False)
                
                # Executar ação
                next_state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                
                # Renderizar se solicitado
                if render:
                    self.env.render()
                
                # Atualizar estado e contadores
                state = next_state
                total_reward += reward
                step_count += 1
            
            # Registrar resultados do episódio
            test_results["episodes"].append(episode)
            test_results["rewards"].append(total_reward)
            test_results["balances"].append(info["balance"])
            test_results["profits"].append(info["accumulated_profit"])
            test_results["steps"].append(step_count)
            
            # Verificar se o episódio foi bem-sucedido (lucro positivo)
            if info["accumulated_profit"] > 0:
                successful_episodes += 1
            
            # Exibir progresso
            if verbose:
                print(f"Teste {episode}/{episodes} | Recompensa: {total_reward:.2f} | "
                      f"Saldo: {info['balance']:.2f} | Lucro: {info['accumulated_profit']:.2f} | "
                      f"Passos: {step_count}")
        
        # Calcular taxa de sucesso
        test_results["success_rate"] = successful_episodes / episodes
        
        if verbose:
            print(f"\nResultados do Teste:")
            print(f"Taxa de Sucesso: {test_results['success_rate'] * 100:.2f}%")
            print(f"Lucro Médio: {np.mean(test_results['profits']):.2f}")
            print(f"Recompensa Média: {np.mean(test_results['rewards']):.2f}")
            print(f"Passos Médios: {np.mean(test_results['steps']):.2f}")
        
        return test_results
    
    def run_simulation(self, trade_amount, target_profit_abs, stop_loss_abs, verbose=True):
        """
        Executa uma simulação com o agente treinado usando parâmetros específicos.
        
        Args:
            trade_amount: Valor de cada operação individual
            target_profit_abs: Meta de lucro em valor absoluto (R$)
            stop_loss_abs: Stop loss em valor absoluto (R$)
            verbose: Se True, exibe informações durante a simulação
            
        Returns:
            Resultados da simulação
        """
        # Criar ambiente específico para esta simulação
        sim_env = TradingEnv(
            symbol=self.symbol,
            region=self.region,
            interval=self.interval,
            range_period=self.range_period,
            initial_balance=self.initial_balance,
            trade_amount=trade_amount,
            target_profit_abs=target_profit_abs,
            stop_loss_abs=stop_loss_abs,
            sma_window=self.sma_window,
            max_steps=self.max_steps
        )
        
        # Executar simulação
        state, info = sim_env.reset()
        total_reward = 0
        step_count = 0
        done = False
        
        # Histórico de operações
        trades_history = []
        
        while not done:
            # Escolher ação (sem exploração durante simulação)
            action = self.agent.act(state, training=False)
            
            # Registrar estado antes da ação
            pre_action_info = sim_env._get_info()
            
            # Executar ação
            next_state, reward, terminated, truncated, info = sim_env.step(action)
            done = terminated or truncated
            
            # Registrar operação se houve compra ou venda
            if action == 1:  # Compra
                if pre_action_info["position"] == 0 and info["position"] == 1:
                    trades_history.append({
                        "step": step_count,
                        "type": "BUY",
                        "price": sim_env.entry_price,
                        "amount": trade_amount,
                        "balance": info["balance"]
                    })
            elif action == 2:  # Venda
                if pre_action_info["position"] == 1 and info["position"] == 0:
                    trades_history.append({
                        "step": step_count,
                        "type": "SELL",
                        "price": sim_env.df.loc[sim_env.current_step-1, "close"],
                        "profit": info["last_trade_profit"],
                        "balance": info["balance"]
                    })
            
            # Atualizar estado e contadores
            state = next_state
            total_reward += reward
            step_count += 1
            
            # Exibir progresso
            if verbose and step_count % 10 == 0:
                print(f"Passo {step_count} | Ação: {action} | Recompensa: {reward:.2f} | "
                      f"Saldo: {info['balance']:.2f} | Lucro Acumulado: {info['accumulated_profit']:.2f}")
        
        # Resultados da simulação
        simulation_results = {
            "initial_balance": self.initial_balance,
            "final_balance": info["balance"],
            "accumulated_profit": info["accumulated_profit"],
            "total_reward": total_reward,
            "steps": step_count,
            "trades": len(trades_history),
            "trades_history": trades_history,
            "success": info["accumulated_profit"] > 0,
            "target_reached": info["accumulated_profit"] >= target_profit_abs,
            "stop_loss_reached": info["accumulated_profit"] <= -stop_loss_abs,
            "params": {
                "trade_amount": trade_amount,
                "target_profit_abs": target_profit_abs,
                "stop_loss_abs": stop_loss_abs
            }
        }
        
        if verbose:
            print(f"\nResultados da Simulação:")
            print(f"Saldo Inicial: R$ {self.initial_balance:.2f}")
            print(f"Saldo Final: R$ {info['balance']:.2f}")
            print(f"Lucro Acumulado: R$ {info['accumulated_profit']:.2f}")
            print(f"Operações Realizadas: {len(trades_history)}")
            print(f"Passos Totais: {step_count}")
            if simulation_results["target_reached"]:
                print(f"Meta de Lucro Atingida: R$ {target_profit_abs:.2f}")
            elif simulation_results["stop_loss_reached"]:
                print(f"Stop Loss Atingido: R$ {stop_loss_abs:.2f}")
            else:
                print("Simulação encerrada por limite de dados/tempo")
        
        return simulation_results
    
    def save_model(self, name=None):
        """
        Salva o modelo do agente.
        
        Args:
            name: Nome do arquivo (sem extensão)
        """
        if name is None:
            name = f"{self.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = os.path.join(self.model_dir, f"{name}.pth")
        self.agent.save(filepath)
        
        # Salvar também os parâmetros do ambiente
        params = {
            "symbol": self.symbol,
            "region": self.region,
            "interval": self.interval,
            "range_period": self.range_period,
            "initial_balance": self.initial_balance,
            "trade_amount": self.trade_amount,
            "target_profit_abs": self.target_profit_abs,
            "stop_loss_abs": self.stop_loss_abs,
            "sma_window": self.sma_window,
            "max_steps": self.max_steps
        }
        
        params_filepath = os.path.join(self.model_dir, f"{name}_params.json")
        with open(params_filepath, "w") as f:
            json.dump(params, f, indent=4)
        
        return filepath
    
    def load_model(self, name):
        """
        Carrega um modelo salvo.
        
        Args:
            name: Nome do arquivo (sem extensão)
        """
        filepath = os.path.join(self.model_dir, f"{name}.pth")
        self.agent.load(filepath)
        
        # Carregar também os parâmetros do ambiente
        params_filepath = os.path.join(self.model_dir, f"{name}_params.json")
        if os.path.exists(params_filepath):
            with open(params_filepath, "r") as f:
                params = json.load(f)
            
            # Atualizar parâmetros
            self.symbol = params.get("symbol", self.symbol)
            self.region = params.get("region", self.region)
            self.interval = params.get("interval", self.interval)
            self.range_period = params.get("range_period", self.range_period)
            self.initial_balance = params.get("initial_balance", self.initial_balance)
            self.trade_amount = params.get("trade_amount", self.trade_amount)
            self.target_profit_abs = params.get("target_profit_abs", self.target_profit_abs)
            self.stop_loss_abs = params.get("stop_loss_abs", self.stop_loss_abs)
            self.sma_window = params.get("sma_window", self.sma_window)
            self.max_steps = params.get("max_steps", self.max_steps)
            
            # Recriar ambiente com os parâmetros carr
(Content truncated due to size limit. Use line ranges to read in chunks)