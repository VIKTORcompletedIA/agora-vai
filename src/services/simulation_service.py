# src/services/simulation_service.py

import random
import time
from src.services import balance_manager # Import the balance manager

def run_basic_simulation(asset, mode, entry_value, take_profit, stop_loss):
    """Executa uma simulação de trading básica com dados mockados e gerenciamento de saldo."""
    print(f"Iniciando simulação: Ativo={asset}, Modo={mode}, Entrada={entry_value}, TP={take_profit}%, SL={stop_loss}%")

    try:
        entry_value = float(entry_value)
        take_profit_pct = float(take_profit)
        stop_loss_pct = float(stop_loss)
        if entry_value <= 0 or take_profit_pct <= 0 or stop_loss_pct <= 0:
            raise ValueError("Valores de entrada, TP e SL devem ser positivos.")
    except (ValueError, TypeError) as e:
        error_msg = f"Erro nos parâmetros: {e}"
        print(error_msg)
        return {"status": "erro", "resultado": error_msg}

    # 1. Tentar debitar o valor de entrada do saldo virtual
    if not balance_manager.debit_entry_value(entry_value):
        error_msg = "Saldo insuficiente para iniciar a operação."
        print(error_msg)
        return {"status": "erro", "resultado": error_msg}

    # Simula algum processamento/espera
    time.sleep(1)

    # Lógica de simulação extremamente simplificada (usando dados mock)
    # Em fases futuras, isso usará dados reais/históricos e lógica de IA
    preco_entrada_simulado = 100.0 # Preço de entrada fixo para o mock
    preco_atual = preco_entrada_simulado
    resultado_final = ""
    profit_loss_value = 0

    # Simula algumas variações de preço
    print("Simulando variações de preço...")
    for i in range(15): # Simula 15 passos de tempo
        variacao = random.uniform(-1.5, 1.6) # Pequena variação aleatória
        preco_atual += variacao
        preco_atual = max(0.1, preco_atual) # Evita preço zero ou negativo
        print(f"  Passo {i+1}: Preço atual = {preco_atual:.2f}")

        # Calcula lucro/perda atual baseado no valor de entrada e variação percentual
        variacao_percentual = (preco_atual - preco_entrada_simulado) / preco_entrada_simulado
        profit_loss_atual = entry_value * variacao_percentual

        # Verifica Take Profit (baseado na % sobre o valor de entrada)
        meta_lucro_valor = entry_value * (take_profit_pct / 100.0)
        if profit_loss_atual >= meta_lucro_valor:
            resultado_final = f"Take Profit atingido em {preco_atual:.2f}. Lucro: {meta_lucro_valor:.2f}"
            profit_loss_value = meta_lucro_valor # Garante o valor exato do TP
            print(resultado_final)
            break

        # Verifica Stop Loss (baseado na % sobre o valor de entrada)
        limite_perda_valor = -abs(entry_value * (stop_loss_pct / 100.0))
        if profit_loss_atual <= limite_perda_valor:
            resultado_final = f"Stop Loss atingido em {preco_atual:.2f}. Perda: {limite_perda_valor:.2f}"
            profit_loss_value = limite_perda_valor # Garante o valor exato do SL
            print(resultado_final)
            break

        time.sleep(0.15) # Pequena pausa para simular tempo passando

    # Se não atingiu TP ou SL após os passos
    if not resultado_final:
        variacao_percentual_final = (preco_atual - preco_entrada_simulado) / preco_entrada_simulado
        profit_loss_value = entry_value * variacao_percentual_final
        resultado_final = f"Simulação concluída por tempo. Preço final: {preco_atual:.2f}. Resultado: {profit_loss_value:.2f}"
        print(resultado_final)

    # 2. Atualizar o saldo com o resultado da operação (lucro ou perda)
    # Adiciona de volta o valor de entrada + lucro/perda
    balance_manager.update_balance_after_trade(entry_value + profit_loss_value)

    return {"status": "concluído", "resultado": resultado_final}

