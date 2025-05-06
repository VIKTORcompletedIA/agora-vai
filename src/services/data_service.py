# src/services/data_service.py

import sys
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient
import pandas as pd
from datetime import datetime
import time # Para caching simples

client = ApiClient()

# Cache simples em memória para evitar chamadas repetidas à API
_data_cache = {}
_CACHE_EXPIRY_SECONDS = 3600 # 1 hora

def _get_cached_data(cache_key):
    """Retorna dados do cache se existirem e não estiverem expirados."""
    if cache_key in _data_cache:
        data, timestamp = _data_cache[cache_key]
        if time.time() - timestamp < _CACHE_EXPIRY_SECONDS:
            print(f"Retornando dados do cache para {cache_key}")
            return data
        else:
            print(f"Cache expirado para {cache_key}")
            del _data_cache[cache_key]
    return None

def _set_cached_data(cache_key, data):
    """Armazena dados no cache com timestamp."""
    _data_cache[cache_key] = (data, time.time())
    print(f"Dados armazenados no cache para {cache_key}")

def get_historical_data(symbol, region="US", interval="1d", range="1y"):
    """Busca dados históricos OHLCV, processa e retorna como DataFrame pandas."""
    cache_key = f"{symbol}_{region}_{interval}_{range}"
    cached_data = _get_cached_data(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        print(f"Buscando dados da API para {symbol} (Region: {region}, Interval: {interval}, Range: {range})...")
        params = {
            "symbol": symbol,
            "region": region,
            "interval": interval,
            "range": range,
            "includeAdjustedClose": True
        }
        response = client.call_api("YahooFinance/get_stock_chart", query=params)

        if response and response.get("chart") and response["chart"].get("result"):
            result = response["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {}).get("quote", [{}])[0]
            adjclose_data = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])

            if not timestamps or not indicators.get("open"):
                print(f"Dados recebidos mas incompletos para {symbol}.")
                return None

            # Verifica consistência dos tamanhos
            required_keys = ["open", "high", "low", "close", "volume"]
            lengths = {k: len(indicators.get(k, [])) for k in required_keys}
            lengths["timestamp"] = len(timestamps)
            lengths["adjclose"] = len(adjclose_data)

            if len(set(lengths.values())) > 1:
                print(f"Inconsistência nos tamanhos dos dados recebidos para {symbol}: {lengths}")
                return None

            df = pd.DataFrame({
                "timestamp": timestamps,
                "open": indicators.get("open"),
                "high": indicators.get("high"),
                "low": indicators.get("low"),
                "close": indicators.get("close"),
                "volume": indicators.get("volume"),
                "adjclose": adjclose_data
            })

            # Converte timestamp para datetime (opcional, mas útil)
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
            df = df.set_index("datetime")

            # Remove linhas com valores NaN (importante para RL)
            df.dropna(inplace=True)

            if df.empty:
                print(f"DataFrame vazio após processamento para {symbol}.")
                return None

            print(f"Dados processados com sucesso para {symbol}. Shape: {df.shape}")
            _set_cached_data(cache_key, df)
            return df

        elif response and response.get("chart") and response["chart"].get("error"):
            # Corrigido: Usar aspas simples para chaves dentro do f-string
            print(f"Erro da API ao buscar {symbol}: {response['chart']['error']}")
            return None
        else:
            print(f"Resposta inesperada ou vazia da API para {symbol}.")
            return None

    except Exception as e:
        print(f"Erro ao buscar ou processar dados para {symbol}: {e}")
        import traceback
        traceback.print_exc() # Imprime traceback completo para depuração
        return None

# Exemplo de uso (pode ser removido ou comentado depois)
if __name__ == "__main__":
    print("\n--- Testando Data Service ---")
    df_aapl = get_historical_data("AAPL", range="6mo")
    if df_aapl is not None:
        print("AAPL Data (primeiras 5 linhas):")
        print(df_aapl.head())

    df_petr4 = get_historical_data("PETR4.SA", region="BR", range="6mo")
    if df_petr4 is not None:
        print("\nPETR4.SA Data (primeiras 5 linhas):")
        print(df_petr4.head())

    df_btc = get_historical_data("BTC-USD", range="6mo")
    if df_btc is not None:
        print("\nBTC-USD Data (primeiras 5 linhas):")
        print(df_btc.head())

    # Teste de cache
    print("\n--- Testando Cache (AAPL) ---")
    df_aapl_cached = get_historical_data("AAPL", range="6mo")
    if df_aapl_cached is not None:
        print("Cache funcionou.")

