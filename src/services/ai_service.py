# src/services/ai_service.py

import os
import json
import threading
import time
from datetime import datetime
import numpy as np
from src.rl_agent.trainer import TradingTrainer

class AIService:
    """Serviço para gerenciar a IA de trading."""
    
    def __init__(self, model_dir="/home/ubuntu/ia_trader_app/models"):
        """
        Inicializa o serviço de IA.
        
        Args:
            model_dir: Diretório para salvar/carregar modelos
        """
        self.model_dir = model_dir
        self.trainers = {}  # Dicionário de treinadores por símbolo
        self.training_threads = {}  # Threads de treinamento em andamento
        self.simulation_results = {}  # Resultados de simulações recentes
        
        # Criar diretório de modelos se não existir
        os.makedirs(self.model_dir, exist_ok=True)
    
    def get_trainer(self, symbol, region="US", create_if_missing=True):
        """
        Obtém um treinador para um símbolo específico.
        
        Args:
            symbol: Símbolo do ativo
            region: Região do mercado
            create_if_missing: Se True, cria um novo treinador se não existir
            
        Returns:
            Instância de TradingTrainer
        """
        trainer_key = f"{symbol}_{region}"
        
        if trainer_key not in self.trainers and create_if_missing:
            # Criar novo treinador
            trainer = TradingTrainer(
                symbol=symbol,
                region=region,
                interval="1d",  # Padrão: diário
                range_period="1y",  # Padrão: 1 ano
                initial_balance=10000,  # Padrão: R$ 10.000
                trade_amount=1000,  # Padrão: R$ 1.000 por operação
                target_profit_abs=330,  # Padrão: R$ 330 de lucro
                stop_loss_abs=600,  # Padrão: R$ 600 de prejuízo
                sma_window=20,  # Padrão: SMA de 20 períodos
                model_dir=self.model_dir
            )
            
            # Tentar carregar modelo existente
            model_files = [f for f in os.listdir(self.model_dir) 
                          if f.startswith(symbol) and f.endswith(".pth")]
            
            if model_files:
                # Carregar o modelo mais recente
                latest_model = sorted(model_files)[-1].replace(".pth", "")
                try:
                    trainer.load_model(latest_model)
                    print(f"Modelo carregado: {latest_model}")
                except Exception as e:
                    print(f"Erro ao carregar modelo {latest_model}: {e}")
            
            self.trainers[trainer_key] = trainer
        
        return self.trainers.get(trainer_key)
    
    def start_training(self, symbol, region="US", episodes=100, 
                      initial_balance=10000, trade_amount=1000,
                      target_profit_abs=330, stop_loss_abs=600):
        """
        Inicia o treinamento da IA em uma thread separada.
        
        Args:
            symbol: Símbolo do ativo
            region: Região do mercado
            episodes: Número de episódios de treinamento
            initial_balance: Saldo inicial
            trade_amount: Valor de cada operação
            target_profit_abs: Meta de lucro em valor absoluto (R$)
            stop_loss_abs: Stop loss em valor absoluto (R$)
            
        Returns:
            ID do treinamento
        """
        trainer_key = f"{symbol}_{region}"
        
        # Verificar se já existe um treinamento em andamento
        if trainer_key in self.training_threads and self.training_threads[trainer_key].is_alive():
            return {"status": "error", "message": "Já existe um treinamento em andamento para este ativo."}
        
        # Obter ou criar treinador
        trainer = self.get_trainer(symbol, region)
        
        # Atualizar parâmetros
        trainer.initial_balance = initial_balance
        trainer.trade_amount = trade_amount
        trainer.target_profit_abs = target_profit_abs
        trainer.stop_loss_abs = stop_loss_abs
        
        # Recriar ambiente com os novos parâmetros
        trainer.env = trainer.env.__class__(
            symbol=symbol,
            region=region,
            interval=trainer.interval,
            range_period=trainer.range_period,
            initial_balance=initial_balance,
            trade_amount=trade_amount,
            target_profit_abs=target_profit_abs,
            stop_loss_abs=stop_loss_abs,
            sma_window=trainer.sma_window,
            max_steps=trainer.max_steps
        )
        
        # Criar thread de treinamento
        training_id = f"{symbol}_{region}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def training_thread():
            try:
                print(f"Iniciando treinamento {training_id}...")
                trainer.train(episodes=episodes)
                print(f"Treinamento {training_id} concluído.")
            except Exception as e:
                print(f"Erro no treinamento {training_id}: {e}")
        
        thread = threading.Thread(target=training_thread)
        thread.daemon = True  # Thread será encerrada quando o programa principal terminar
        thread.start()
        
        self.training_threads[trainer_key] = thread
        
        return {
            "status": "success", 
            "training_id": training_id,
            "message": f"Treinamento iniciado com {episodes} episódios."
        }
    
    def get_training_status(self, symbol, region="US"):
        """
        Verifica o status de um treinamento em andamento.
        
        Args:
            symbol: Símbolo do ativo
            region: Região do mercado
            
        Returns:
            Status do treinamento
        """
        trainer_key = f"{symbol}_{region}"
        
        if trainer_key in self.training_threads and self.training_threads[trainer_key].is_alive():
            return {"status": "running", "message": "Treinamento em andamento."}
        elif trainer_key in self.trainers:
            return {
                "status": "completed", 
                "message": "Treinamento concluído.",
                "history": self.trainers[trainer_key].training_history
            }
        else:
            return {"status": "not_found", "message": "Nenhum treinamento encontrado para este ativo."}
    
    def run_simulation(self, symbol, region="US", 
                      trade_amount=1000, target_profit_abs=330, stop_loss_abs=600):
        """
        Executa uma simulação com a IA treinada.
        
        Args:
            symbol: Símbolo do ativo
            region: Região do mercado
            trade_amount: Valor de cada operação
            target_profit_abs: Meta de lucro em valor absoluto (R$)
            stop_loss_abs: Stop loss em valor absoluto (R$)
            
        Returns:
            Resultados da simulação
        """
        # Obter treinador
        trainer = self.get_trainer(symbol, region, create_if_missing=False)
        
        if trainer is None:
            return {
                "status": "error", 
                "message": "Nenhum modelo treinado encontrado para este ativo."
            }
        
        try:
            # Executar simulação
            results = trainer.run_simulation(
                trade_amount=trade_amount,
                target_profit_abs=target_profit_abs,
                stop_loss_abs=stop_loss_abs,
                verbose=False
            )
            
            # Armazenar resultados
            simulation_id = f"{symbol}_{region}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.simulation_results[simulation_id] = results
            
            # Adicionar informações adicionais
            results["simulation_id"] = simulation_id
            results["status"] = "success"
            results["message"] = "Simulação concluída com sucesso."
            
            return results
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao executar simulação: {str(e)}"
            }
    
    def get_available_models(self):
        """
        Obtém a lista de modelos disponíveis.
        
        Returns:
            Lista de modelos disponíveis
        """
        models = []
        
        if os.path.exists(self.model_dir):
            model_files = [f for f in os.listdir(self.model_dir) if f.endswith(".pth")]
            
            for model_file in model_files:
                model_name = model_file.replace(".pth", "")
                
                # Tentar extrair símbolo e data
                parts = model_name.split("_")
                if len(parts) >= 2:
                    symbol = parts[0]
                    
                    # Verificar se há arquivo de parâmetros
                    params_file = os.path.join(self.model_dir, f"{model_name}_params.json")
                    params = {}
                    
                    if os.path.exists(params_file):
                        try:
                            with open(params_file, "r") as f:
                                params = json.load(f)
                        except:
                            pass
                    
                    models.append({
                        "name": model_name,
                        "symbol": symbol,
                        "file": model_file,
                        "params": params
                    })
        
        return models

# Instância global do serviço
ai_service = AIService()

# Exemplo de uso
if __name__ == "__main__":
    print("Testando o serviço de IA...")
    
    # Obter treinador para BTC-USD
    trainer = ai_service.get_trainer("BTC-USD")
    print(f"Treinador criado para BTC-USD")
    
    # Iniciar treinamento rápido
    print("Iniciando treinamento rápido (2 episódios)...")
    result = ai_service.start_training("BTC-USD", episodes=2)
    print(f"Resultado: {result}")
    
    # Aguardar conclusão
    print("Aguardando conclusão do treinamento...")
    while ai_service.get_training_status("BTC-USD")["status"] == "running":
        time.sleep(1)
    
    # Executar simulação
    print("Executando simulação...")
    sim_result = ai_service.run_simulation("BTC-USD")
    print(f"Resultado da simulação: {sim_result['status']}")
    
    if sim_result["status"] == "success":
        print(f"Lucro: R$ {sim_result['accumulated_profit']:.2f}")
        print(f"Operações: {sim_result['trades']}")
    
    print("Teste concluído!")
