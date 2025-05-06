import json
import pandas as pd

def load_data_from_json(filepath):
    """Loads historical data from the specific JSON format and converts it to a DataFrame.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        pandas.DataFrame: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume'] 
                          and datetime index, or None if loading fails.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Navigate the JSON structure
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        indicators = result['indicators']['quote'][0]
        
        # Ensure all required indicator lists exist and have the same length as timestamps
        required_keys = ['open', 'high', 'low', 'close', 'volume']
        if not all(key in indicators for key in required_keys):
            print(f"Erro: Faltando uma ou mais chaves de indicadores {required_keys} no JSON.")
            return None
            
        if not all(len(indicators[key]) == len(timestamps) for key in required_keys):
            print("Erro: Inconsistência no comprimento das listas de indicadores e timestamps.")
            # Attempt to truncate lists to the minimum common length if possible
            min_len = min(len(timestamps), min(len(indicators[key]) for key in required_keys))
            if min_len > 0:
                print(f"Truncando listas para o comprimento mínimo comum: {min_len}")
                timestamps = timestamps[:min_len]
                for key in required_keys:
                    indicators[key] = indicators[key][:min_len]
            else:
                 return None

        # Create DataFrame
        df = pd.DataFrame({
            'Open': indicators['open'],
            'High': indicators['high'],
            'Low': indicators['low'],
            'Close': indicators['close'],
            'Volume': indicators['volume']
        }, index=pd.to_datetime(timestamps, unit='s'))

        # Convert columns to numeric, coercing errors
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
             df[col] = pd.to_numeric(df[col], errors='coerce')

        # Handle potential missing values (e.g., forward fill)
        df.ffill(inplace=True)
        df.bfill(inplace=True) # Backfill any remaining NaNs at the beginning
        df.dropna(inplace=True) # Drop rows if any NaNs persist (shouldn't happen with ffill/bfill)

        # Ensure OHLC are positive
        df = df[(df['Open'] > 0) & (df['High'] > 0) & (df['Low'] > 0) & (df['Close'] > 0)]

        print(f"Dados carregados com sucesso. Shape: {df.shape}")
        return df

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {filepath}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        print(f"Erro ao processar a estrutura do JSON: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
        return None

# Example usage (for testing)
if __name__ == "__main__":
    btc_data = load_data_from_json('btc_usd_data.json')
    if btc_data is not None:
        print("\nCabeçalho do DataFrame:")
        print(btc_data.head())
        print("\nInformações do DataFrame:")
        print(btc_data.info())
        print("\nEstatísticas Descritivas:")
        print(btc_data.describe())

