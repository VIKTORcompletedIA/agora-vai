# src/services/balance_manager.py

import os
import json

# Simple file-based persistence for the virtual balance
BALANCE_FILE = "/home/ubuntu/ia_trader_app/data/virtual_balance.json"
INITIAL_BALANCE = 10000.0 # Saldo inicial fictício

def _ensure_data_dir():
    """Ensures the data directory exists."""
    data_dir = os.path.dirname(BALANCE_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

def _read_balance():
    """Reads the current balance from the file or returns initial balance."""
    _ensure_data_dir()
    try:
        with open(BALANCE_FILE, 'r') as f:
            data = json.load(f)
            return float(data.get('balance', INITIAL_BALANCE))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        # If file doesn't exist, is empty, invalid, or balance is not a number, reset
        _write_balance(INITIAL_BALANCE)
        return INITIAL_BALANCE

def _write_balance(new_balance):
    """Writes the new balance to the file."""
    _ensure_data_dir()
    try:
        with open(BALANCE_FILE, 'w') as f:
            json.dump({'balance': float(new_balance)}, f)
    except (IOError, TypeError) as e:
        print(f"Error writing balance file: {e}")
        # Handle error appropriately in a real application (e.g., logging)

def get_current_balance():
    """Returns the current virtual balance."""
    return _read_balance()

def check_funds(amount_needed):
    """Checks if there are sufficient funds in the balance."""
    amount_needed = float(amount_needed)
    current_balance = get_current_balance()
    return current_balance >= amount_needed

def debit_entry_value(entry_value):
    """Debits the entry value from the balance when a trade starts.

    Returns True if successful, False otherwise (e.g., insufficient funds).
    """
    try:
        entry_value = float(entry_value)
        if entry_value <= 0:
            print("Error: Entry value must be positive.")
            return False

        current_balance = get_current_balance()
        if current_balance >= entry_value:
            new_balance = current_balance - entry_value
            _write_balance(new_balance)
            print(f"Debited {entry_value}. New balance: {new_balance}")
            return True
        else:
            print(f"Insufficient funds. Needed: {entry_value}, Available: {current_balance}")
            return False
    except (ValueError, TypeError) as e:
        print(f"Error processing debit: Invalid entry value. {e}")
        return False

def update_balance_after_trade(profit_or_loss):
    """Updates the balance with the profit or loss from a completed trade."""
    try:
        profit_or_loss = float(profit_or_loss)
        current_balance = get_current_balance()
        new_balance = current_balance + profit_or_loss
        _write_balance(new_balance)
        print(f"Updated balance by {profit_or_loss}. New balance: {new_balance}")
    except (ValueError, TypeError) as e:
        print(f"Error updating balance: Invalid profit/loss value. {e}")

def reset_balance():
    """Resets the balance to the initial value."""
    _write_balance(INITIAL_BALANCE)
    print(f"Balance reset to {INITIAL_BALANCE}")
    return INITIAL_BALANCE

# Initialize balance file if it doesn't exist on module load
if not os.path.exists(BALANCE_FILE):
    reset_balance()

