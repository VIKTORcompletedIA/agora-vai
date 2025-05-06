from backtesting import Backtest
import os
import traceback
import sys
import pandas as pd
import numpy as np # Import numpy for np.isfinite

# Correct path adjustment: Add the project root directory (parent of src) to sys.path
project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, project_root_dir)

try:
    # Now imports starting from 'src' should work when running this script directly
    from src.backtesting_logic.data_loader import load_data_from_json
    from src.backtesting_logic.dqn_strategy import DQNStrategy
except ImportError as e:
    print(f"Erro ao importar módulos de backtesting_logic: {e}")
    # Define dummy functions/classes if import fails
    def load_data_from_json(*args, **kwargs):
        print("Erro: Função load_data_from_json não encontrada.")
        return None
    class DQNStrategy:
        def __init__(self, *args, **kwargs): pass

# Definir o diretório de trabalho e o caminho do arquivo de dados
WORK_DIR = project_root_dir # Use the calculated project root
DATA_FILE = os.path.join(WORK_DIR, "btc_usd_data.json")
OUTPUT_HTML_FILENAME = "dqn_strategy_backtest.html"
# Ensure output path is within src/static for Flask access
OUTPUT_HTML_PATH = os.path.join(WORK_DIR, "src", "static", OUTPUT_HTML_FILENAME)

def run_backtest_simulation(data_filepath=DATA_FILE, output_html_path=OUTPUT_HTML_PATH, strategy_class=DQNStrategy):
    """Carrega os dados, executa um backtest com a estratégia especificada e retorna estatísticas/caminho do gráfico.

    Args:
        data_filepath (str): Caminho para o arquivo de dados JSON.
        output_html_path (str): Caminho completo para salvar o arquivo HTML do gráfico.
        strategy_class (Type[Strategy]): A classe da estratégia a ser usada no backtest.

    Returns:
        dict: Um dicionário contendo estatísticas e o caminho relativo do gráfico em caso de sucesso,
              ou uma mensagem de erro em caso de falha.
    """
    plot_path_relative = None # Initialize plot path as None
    plot_error_message = None # Initialize plot error message
    try:
        print(f"Carregando dados de {data_filepath}...")
        data = load_data_from_json(data_filepath)

        if data is None or data.empty:
            print("Falha ao carregar dados.")
            return {"error": "Falha ao carregar dados do arquivo.", "success": False}

        # Ensure data has standard OHLCV column names expected by Backtesting.py
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in data.columns for col in required_cols):
             return {"error": f"Dados carregados não contêm as colunas OHLCV necessárias: {required_cols}", "success": False}

        print(f"Dados carregados. Iniciando backtest com {strategy_class.__name__}...")
        # Certificar que o diretório de saída existe
        output_dir = os.path.dirname(output_html_path)
        os.makedirs(output_dir, exist_ok=True)

        # Instanciar o Backtest
        bt = Backtest(data, strategy_class, cash=10000, commission=.002)

        # Executar o backtest
        stats = bt.run()

        print("\nEstatísticas do Backtest:")
        print(stats)

        # Salvar o gráfico interativo - Wrap in try-except and disable superimpose
        try:
            print(f"Salvando gráfico do backtest em {output_html_path}...")
            # Disable superimpose to avoid the upsampling error
            bt.plot(filename=output_html_path, open_browser=False, superimpose=False)
            print("Gráfico salvo com sucesso.")
            plot_path_relative = f"/static/{OUTPUT_HTML_FILENAME}" # Set relative path if plot succeeds
        except ValueError as ve:
            # Catch potential plotting errors (though superimpose=False should help)
            plot_error_message = f"Erro ao gerar gráfico: {ve}. As estatísticas ainda estão disponíveis."
            print(f"\n{plot_error_message}\n")
        except Exception as plot_e:
            # Catch other potential plotting errors
            plot_error_message = f"Erro inesperado ao gerar gráfico: {plot_e}. As estatísticas ainda estão disponíveis."
            print(f"\n{plot_error_message}\n")

        # Preparar o resultado para retornar (converter o que não for serializável)
        strategy_instance = stats._strategy
        episode_rewards = getattr(strategy_instance, 'episode_rewards', [])

        stats_serializable = stats.to_dict()
        stats_serializable.pop("_strategy", None)
        stats_serializable.pop("_equity_curve", None)
        stats_serializable.pop("_trades", None)

        # Converter tipos numpy/pandas para tipos Python nativos
        for key, value in stats_serializable.items():
            if hasattr(value, 'item'): # Numpy types
                stats_serializable[key] = value.item()
            elif isinstance(value, pd.Timestamp):
                 stats_serializable[key] = value.isoformat()
            # Add handling for Timedelta
            elif isinstance(value, pd.Timedelta):
                 stats_serializable[key] = str(value) # Convert Timedelta to string
            # Use np.isfinite instead of pd.isfinite
            elif isinstance(value, float) and (pd.isna(value) or not np.isfinite(value)):
                 stats_serializable[key] = None # Convert NaN/inf to None

        result_dict = {
            "success": True,
            "message": f"Backtest com {strategy_class.__name__} concluído.",
            "stats": stats_serializable,
            "plot_path": plot_path_relative, # Use the variable which might be None
            "episode_rewards": episode_rewards
        }
        if plot_error_message:
            result_dict["plot_warning"] = plot_error_message # Add warning if plot failed

        return result_dict

    except Exception as e:
        print(f"Erro durante o backtest: {e}")
        print(traceback.format_exc())
        return {"error": f"Erro durante a execução do backtest: {str(e)}", "success": False}

# Bloco principal para teste direto do script
if __name__ == "__main__":
    results = run_backtest_simulation()
    print("\nResultado da simulação:")
    import json
    print(json.dumps(results, indent=2))

