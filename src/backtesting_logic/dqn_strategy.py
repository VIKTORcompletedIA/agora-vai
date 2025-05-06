#!/usr/bin/env python
# coding: utf-8

import numpy as np
import torch
from backtesting import Strategy
from backtesting.lib import crossover # Might be useful later, keeping import
import pandas as pd
import sys
import os

# Adjust path to import DQNAgent from the correct location
# Assuming dqn_agent.py is now in src/services or similar based on restructuring
# Let's assume it was moved to src/services/ai_service.py or kept as dqn_agent.py in root
# Trying to import from root first, then adjust if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, project_root) # Add project root to path

try:
    # Assuming dqn_agent.py might be in src/services after restructuring
    # Let's try importing directly first, assuming it's accessible
    from dqn_agent import DQNAgent # Check if dqn_agent.py is in the root or accessible path
except ImportError:
    print("Failed to import DQNAgent directly. Trying from src/services...")
    try:
        # Adjust based on actual final location after restructuring
        from src.services.dqn_agent import DQNAgent 
    except ImportError:
         print("ERROR: Could not find DQNAgent. Ensure dqn_agent.py is in the correct path (e.g., src/services) and accessible.")
         # Define a dummy class to avoid crashing if import fails
         class DQNAgent:
             def __init__(self, *args, **kwargs): pass
             def act(self, *args, **kwargs): return 0 # Default to Hold
             def remember(self, *args, **kwargs): pass
             def replay(self, *args, **kwargs): pass
             def save(self, *args, **kwargs): pass
             def load(self, *args, **kwargs): pass

class DQNStrategy(Strategy):
    """ A trading strategy using a Deep Q-Network agent. """
    
    # --- Parameters --- 
    state_window_size = 10  # Number of past closing prices to use as state
    action_size = 3         # 0: Hold, 1: Buy, 2: Sell
    initial_epsilon = 1.0
    epsilon_decay = 0.995
    epsilon_min = 0.01
    learning_rate = 0.001
    gamma = 0.95
    memory_size = 2000
    batch_size = 32
    target_update = 10      # Update target network every 10 steps
    model_save_path = os.path.join(project_root, "viktor_ia_dqn_model_bt.pth") # Save in project root
    load_model = False      # Set to True to load a pre-trained model
    train_mode = True       # Set to False for evaluation only (no exploration, no training)
    
    # --- Internal State --- 
    agent = None
    last_state = None
    last_action = None
    last_portfolio_value = None
    episode_rewards = []
    current_episode_reward = 0
    step_count = 0

    def init(self):
        print(f"Initializing DQNStrategy... State window: {self.state_window_size}, Actions: {self.action_size}")
        # Ensure data length is sufficient for the state window
        if len(self.data.Close) <= self.state_window_size:
            raise ValueError("Data length must be greater than state_window_size")

        # Initialize the DQN agent
        self.agent = DQNAgent(
            state_size=self.state_window_size,
            action_size=self.action_size,
            learning_rate=self.learning_rate,
            gamma=self.gamma,
            epsilon=self.initial_epsilon if self.train_mode else 0.0, # No exploration if not training
            epsilon_min=self.epsilon_min,
            epsilon_decay=self.epsilon_decay,
            memory_size=self.memory_size,
            batch_size=self.batch_size,
            target_update=self.target_update
        )

        # Load pre-trained model if specified
        if self.load_model and os.path.exists(self.model_save_path):
            try:
                print(f"Loading pre-trained model from {self.model_save_path}")
                self.agent.load(self.model_save_path)
                if not self.train_mode:
                    self.agent.epsilon = 0.0 # Ensure no exploration in eval mode
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}. Starting with a new model.")
        elif self.load_model:
            print(f"Model file not found at {self.model_save_path}. Starting with a new model.")

        # Initial portfolio value
        self.last_portfolio_value = self.equity # self.equity is provided by Backtesting.py
        self.step_count = 0
        print("DQNStrategy initialized.")

    def get_state(self, index):
        """ Returns the state representation at a given index. """
        if index < self.state_window_size -1:
             # Not enough data for a full state window, return zeros or handle appropriately
             # For simplicity, returning zeros. A better approach might be padding or skipping.
             print(f"Warning: Not enough data at index {index} for state window {self.state_window_size}. Returning zeros.")
             return np.zeros(self.state_window_size)
             
        # Get the last `state_window_size` closing prices up to the current index
        start_index = index - (self.state_window_size - 1)
        state_data = self.data.Close[start_index : index + 1]
        
        # Normalize the state (e.g., percentage change relative to the first element)
        # Simple normalization: divide by the first price in the window
        # Avoid division by zero if the first price is 0 (unlikely for price data)
        first_price = state_data[0]
        if first_price != 0:
             normalized_state = (state_data / first_price) - 1
        else:
             normalized_state = np.zeros(self.state_window_size) # Or handle differently
             
        return normalized_state

    def next(self):
        """ Called at each data point (bar/tick). """
        current_index = len(self.data.Close) - 1
        # Need at least state_window_size steps to form the first state
        if current_index < self.state_window_size -1:
            # print(f"Skipping step {current_index}, not enough data for state.")
            return
            
        # 1. Get current state
        current_state = self.get_state(current_index)
        
        # 2. Decide action using the agent
        action = self.agent.act(current_state, training=self.train_mode)
        
        # --- Store experience from the *previous* step --- 
        # We need the outcome (reward, next_state) of the previous action
        if self.last_state is not None and self.last_action is not None:
            # Calculate reward: Change in portfolio value since the last step
            reward = self.equity - self.last_portfolio_value
            self.current_episode_reward += reward
            
            # Check if done (end of data)
            # Backtesting.py runs until the end, so 'done' is true only on the very last step
            done = (current_index == len(self.data.Close) - 1) 

            # Remember the experience (state, action, reward, next_state, done)
            if self.train_mode:
                self.agent.remember(self.last_state, self.last_action, reward, current_state, done)
                
                # Train the agent using experience replay
                self.agent.replay()

            # If done, record episode reward and reset
            if done:
                self.episode_rewards.append(self.current_episode_reward)
                print(f"End of data reached. Total Reward: {self.current_episode_reward:.2f}, Epsilon: {self.agent.epsilon:.4f}")
                # Optionally save the model at the end
                if self.train_mode:
                    try:
                        self.agent.save(self.model_save_path)
                        print(f"Model saved to {self.model_save_path}")
                    except Exception as e:
                        print(f"Error saving model: {e}")
                # Reset for potential next run (though Backtesting.py usually runs once)
                self.current_episode_reward = 0 

        # --- Execute the chosen action --- 
        # Action: 0=Hold, 1=Buy, 2=Sell
        if action == 1: # Buy
            # Simple logic: close existing short, buy if not already long
            if self.position.is_short:
                self.position.close()
            if not self.position.is_long:
                 self.buy()
        elif action == 2: # Sell
            # Simple logic: close existing long, sell if not already short
            if self.position.is_long:
                self.position.close()
            if not self.position.is_short:
                 self.sell()
        # else action == 0: Hold (do nothing)

        # --- Update state for the next iteration --- 
        self.last_state = current_state
        self.last_action = action
        self.last_portfolio_value = self.equity
        self.step_count += 1

# Example of how to potentially use indicators later:
# from backtesting.lib import SMA
# self.sma = self.I(SMA, self.data.Close, 20)
# state could include self.sma[-1]

