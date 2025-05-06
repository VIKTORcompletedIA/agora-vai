# train_viktor_ia.py

import sys
import os
import numpy as np

# Adicionar o diretório src ao path para importar módulos locais
sys.path.append(os.path.join(os.path.dirname(__file__), 'ia_trader_app', 'src'))

from rl_env.trading_env import TradingEnv
from rl_agent.dqn_agent import DQNAgent

# --- Parâmetros de Treinamento ---
DATA_FILEPATH = "/home/ubuntu/btc_usd_data.json"
MODEL_SAVE_PATH = "/home/ubuntu/viktor_ia_dqn_model.pth"
NUM_EPISODES = 100 # Número de episódios para treinar (ajustar conforme necessário)
INITIAL_BALANCE = 10000
TRADE_AMOUNT = 1000
TARGET_PROFIT_ABS = 500 # Meta de lucro em $ por episódio
STOP_LOSS_ABS = 300   # Stop loss em $ por episódio
SMA_WINDOW = 15

# Parâmetros do Agente DQN
LEARNING_RATE = 0.001
GAMMA = 0.95
EPSILON = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
MEMORY_SIZE = 50000
BATCH_SIZE = 64
TARGET_UPDATE = 10 # Frequência de atualização da rede alvo

# --- Inicialização ---
try:
    # Inicializar Ambiente
    env = TradingEnv(
        data_filepath=DATA_FILEPATH,
        initial_balance=INITIAL_BALANCE,
        trade_amount=TRADE_AMOUNT,
        target_profit_abs=TARGET_PROFIT_ABS,
        stop_loss_abs=STOP_LOSS_ABS,
        sma_window=SMA_WINDOW,
        render_mode="none" # Sem renderização durante o treino para velocidade
    )
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    # Inicializar Agente
    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        learning_rate=LEARNING_RATE,
        gamma=GAMMA,
        epsilon=EPSILON,
        epsilon_min=EPSILON_MIN,
        epsilon_decay=EPSILON_DECAY,
        memory_size=MEMORY_SIZE,
        batch_size=BATCH_SIZE,
        target_update=TARGET_UPDATE
    )

    # Carregar modelo se existir (opcional)
    # if os.path.exists(MODEL_SAVE_PATH):
    #     print(f"Carregando modelo pré-treinado de {MODEL_SAVE_PATH}")
    #     agent.load(MODEL_SAVE_PATH)

    print(f"Iniciando treinamento por {NUM_EPISODES} episódios...")
    print(f"Ambiente: {DATA_FILEPATH}, Saldo Inicial: {INITIAL_BALANCE}, Trade: {TRADE_AMOUNT}")
    print(f"Metas: Lucro R$ {TARGET_PROFIT_ABS}, Loss R$ {STOP_LOSS_ABS}")
    print(f"Agente: LR={LEARNING_RATE}, Gamma={GAMMA}, Epsilon Decay={EPSILON_DECAY}")

    # --- Loop de Treinamento ---
    episode_rewards = []
    episode_profits = []

    for e in range(NUM_EPISODES):
        state, info = env.reset()
        # state = np.reshape(state, [1, state_size]) # Desnecessário se o agente já lida com isso
        total_reward = 0
        steps = 0
        terminated = False
        truncated = False

        while not terminated and not truncated:
            # 1. Escolher ação
            action = agent.act(state, training=True)
            
            # 2. Executar ação no ambiente
            next_state, reward, terminated, truncated, info = env.step(action)
            # next_state = np.reshape(next_state, [1, state_size]) # Desnecessário
            
            # 3. Armazenar experiência
            done = terminated or truncated
            agent.remember(state, action, reward, next_state, done)
            
            # 4. Atualizar estado
            state = next_state
            total_reward += reward
            steps += 1
            
            # 5. Treinar o agente (replay)
            agent.replay()

            # Limitar passos por episódio se necessário (evitar loops infinitos em cenários ruins)
            # if steps > env.max_steps * 1.1: # Um pouco mais que o máximo de dados
            #    truncated = True

        # Fim do episódio
        accumulated_profit = info['accumulated_profit']
        episode_rewards.append(total_reward)
        episode_profits.append(accumulated_profit)
        
        print(f"Episódio: {e+1}/{NUM_EPISODES}, Passos: {steps}, Recompensa Total: {total_reward:.2f}, Lucro Acumulado: {accumulated_profit:.2f}, Epsilon: {agent.epsilon:.4f}")

        # Salvar modelo periodicamente (ex: a cada 10 episódios)
        if (e + 1) % 10 == 0:
            agent.save(MODEL_SAVE_PATH)
            print(f"Modelo salvo em {MODEL_SAVE_PATH} no episódio {e+1}")

    # --- Fim do Treinamento ---
    print("\nTreinamento concluído!")
    agent.save(MODEL_SAVE_PATH) # Salvar modelo final
    print(f"Modelo final salvo em {MODEL_SAVE_PATH}")

    # Exibir algumas estatísticas
    print(f"\nMédia de Recompensa por Episódio: {np.mean(episode_rewards):.2f}")
    print(f"Média de Lucro Acumulado por Episódio: {np.mean(episode_profits):.2f}")

except FileNotFoundError as fnf:
    print(f"\nErro Crítico: Arquivo de dados não encontrado. Verifique o caminho: {DATA_FILEPATH}")
except ValueError as ve:
    print(f"\nErro Crítico de Valor na inicialização ou treino: {ve}")
except Exception as ex:
    print(f"\nOcorreu um erro inesperado durante o treinamento: {ex}")
    import traceback
    traceback.print_exc()

finally:
    if 'env' in locals() and env is not None:
        env.close()
        print("Ambiente fechado.")


