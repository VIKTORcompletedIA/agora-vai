# src/rl_agent/dqn_agent.py

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

# Rede Neural para o DQN
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# Agente DQN
class DQNAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, gamma=0.99, 
                 epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, 
                 memory_size=10000, batch_size=64, target_update=10):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.batch_size = batch_size
        self.gamma = gamma  # Fator de desconto
        self.epsilon = epsilon  # Exploração vs. Exploitação
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.target_update = target_update
        self.update_counter = 0
        
        # Dispositivo (CPU ou GPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Redes neural principal e alvo
        self.model = DQN(state_size, action_size).to(self.device)
        self.target_model = DQN(state_size, action_size).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()  # Modo de avaliação (não treina)
        
        # Otimizador
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
    def remember(self, state, action, reward, next_state, done):
        """Armazena experiência na memória"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, training=True):
        """Escolhe ação com base no estado atual"""
        # Exploração: ação aleatória
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        # Exploitação: melhor ação segundo o modelo
        state = torch.FloatTensor(state).to(self.device)
        self.model.eval()
        with torch.no_grad():
            action_values = self.model(state)
        self.model.train()
        return np.argmax(action_values.cpu().data.numpy())
    
    def replay(self):
        """Treina o modelo com experiências passadas (experience replay)"""
        if len(self.memory) < self.batch_size:
            return
        
        # Amostra aleatória da memória
        minibatch = random.sample(self.memory, self.batch_size)
        
        states = torch.FloatTensor([i[0] for i in minibatch]).to(self.device)
        actions = torch.LongTensor([[i[1]] for i in minibatch]).to(self.device)
        rewards = torch.FloatTensor([[i[2]] for i in minibatch]).to(self.device)
        next_states = torch.FloatTensor([i[3] for i in minibatch]).to(self.device)
        dones = torch.FloatTensor([[i[4]] for i in minibatch]).to(self.device)
        
        # Valores Q atuais (Q(s,a)) para as ações tomadas
        curr_q = self.model(states).gather(1, actions)
        
        # Valores Q futuros (Q(s',a')) usando a rede alvo
        with torch.no_grad():
            next_q = self.target_model(next_states).detach().max(1)[0].unsqueeze(1)
        
        # Valores Q alvo
        target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # Calcula a perda
        loss = self.criterion(curr_q, target_q)
        
        # Otimiza o modelo
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Atualiza epsilon (reduz exploração gradualmente)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        # Atualiza a rede alvo periodicamente
        self.update_counter += 1
        if self.update_counter % self.target_update == 0:
            self.target_model.load_state_dict(self.model.state_dict())
            
    def save(self, filepath):
        """Salva o modelo treinado"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, filepath)
        
    def load(self, filepath):
        """Carrega um modelo treinado"""
        if torch.cuda.is_available():
            checkpoint = torch.load(filepath)
        else:
            checkpoint = torch.load(filepath, map_location=torch.device('cpu'))
            
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if 'epsilon' in checkpoint:
            self.epsilon = checkpoint['epsilon']
            print(f"Epsilon loaded from checkpoint: {self.epsilon}")
        else:
            # Se epsilon não estiver no checkpoint (modelos mais antigos),
            # usa o epsilon_min definido na inicialização do agente.
            # A lógica na DQNStrategy irá sobrescrever para 0.0 se train_mode for False.
            self.epsilon = self.epsilon_min 
            print(f"Aviso: 'epsilon' não encontrado no checkpoint. Usando epsilon_min: {self.epsilon_min}")
