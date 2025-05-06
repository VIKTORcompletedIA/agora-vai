# /home/ubuntu/get_yf_data.py
# Script para testar a chamada da API YahooFinance/get_stock_chart

import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json

client = ApiClient()

def fetch_stock_data(symbol, region="US", interval="1d", range="1y"):
    """Busca dados históricos de uma ação usando a API."""
    try:
        print(f"Buscando dados para {symbol} (Region: {region}, Interval: {interval}, Range: {range})...")
        # Ajusta o símbolo para o formato esperado pela API se necessário (ex: PETR4.SA)
        # A API parece usar o símbolo diretamente.
        params = {
            "symbol": symbol,
            "region": region,
            "interval": interval,
            "range": range,
            "includeAdjustedClose": True # Manter True por padrão
        }
        response = client.call_api('YahooFinance/get_stock_chart', query=params)

        if response and response.get("chart") and response["chart"].get("result"):
            print(f"Dados recebidos com sucesso para {symbol}.")
            # Apenas imprime uma parte para confirmação, não o objeto inteiro
            result = response["chart"]["result"][0]
            meta = result.get("meta", {})
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {}).get("quote", [{}])[0]
            # Corrigido: Usar aspas simples dentro das chaves do f-string
            print(f"Meta: {meta.get('symbol')}, Currency: {meta.get('currency')}")
            print(f"Número de timestamps: {len(timestamps)}")
            print(f"Número de registros de Open: {len(indicators.get('open', []))}")
            # Salvar a resposta completa para análise posterior, se necessário
            # with open(f"/home/ubuntu/{symbol}_data.json", "w") as f:
            #     json.dump(response, f, indent=2)
            return response
        elif response and response.get("chart") and response["chart"].get("error"):
            print(f"Erro da API ao buscar {symbol}: {response['chart']['error']}")
            return None
        else:
            print(f"Resposta inesperada ou vazia da API para {symbol}.")
            print(response) # Imprime a resposta completa para depuração
            return None

    except Exception as e:
        print(f"Erro ao chamar a API para {symbol}: {e}")
        return None

# Testes
if __name__ == "__main__":
    print("--- Teste 1: AAPL (US) ---")
    fetch_stock_data(symbol="AAPL", region="US", interval="1d", range="1y")

    print("\n--- Teste 2: PETR4.SA (BR) ---")
    fetch_stock_data(symbol="PETR4.SA", region="BR", interval="1d", range="1y")

    print("\n--- Teste 3: BTC-USD (Cripto) ---")
    # Região pode não ser relevante para cripto, mas a API pode exigir
    fetch_stock_data(symbol="BTC-USD", region="US", interval="1d", range="1y")

    print("\n--- Teste 4: Ativo Inválido ---")
    fetch_stock_data(symbol="INVALID_SYMBOL_XYZ", region="US", interval="1d", range="1y")

