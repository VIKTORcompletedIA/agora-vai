# src/routes/trading_routes.py

from flask import Blueprint, request, jsonify
import os
import sys
import traceback

# Adjust path to import from sibling directories (services, backtesting_logic)
project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, project_root_dir)

try:
    # Import the actual backtest runner function
    from src.backtesting_logic.backtest_runner import run_backtest_simulation
    # Import the data loader for chart data
    from src.backtesting_logic.data_loader import load_data_from_json
    # Import the strategy class to pass to the runner
    from src.backtesting_logic.dqn_strategy import DQNStrategy
except ImportError as e:
    print(f"ERROR importing necessary modules in trading_routes: {e}")
    # Define dummy functions if imports fail to avoid crashing Flask app
    def run_backtest_simulation(*args, **kwargs):
        return {"error": "Backtest runner not loaded", "success": False}
    def load_data_from_json(*args, **kwargs):
        return None
    class DQNStrategy: pass

trading_bp = Blueprint("trading", __name__)

# Define data file path relative to project root
DATA_FILE_PATH = os.path.join(project_root_dir, "btc_usd_data.json")
OUTPUT_HTML_FILENAME = "dqn_strategy_backtest.html"
OUTPUT_HTML_PATH = os.path.join(project_root_dir, "src", "static", OUTPUT_HTML_FILENAME)

@trading_bp.route("/start_backtest", methods=["POST"])
def start_backtest_endpoint():
    """Endpoint to start a backtest simulation using DQNStrategy."""
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Extract parameters (though most are handled within DQNStrategy for now)
    asset = data.get("asset", "BTC/USD") # Use asset name for logging/potential future use
    ai_model = data.get("aiModel")
    strategy_param = data.get("strategy")
    # Entry value, target, stop loss might be used later for analysis or strategy adjustment
    entry_value = data.get("entryValue")
    target_value = data.get("targetValue")
    stop_loss = data.get("stopLoss")

    print(f"Received request to start backtest for asset: {asset}")
    print(f"Parameters received: AI={ai_model}, Strategy={strategy_param}, Entry={entry_value}, Target={target_value}, StopLoss={stop_loss}")

    try:
        # Currently, we only have one data file and one strategy
        # In the future, map asset/strategy params to different files/classes
        if asset != "BTC/USD":
             print(f"Warning: Asset 	{asset}	 requested, but only BTC/USD data is currently supported. Running with BTC/USD data.")
             
        # Run the backtest simulation using the imported function and strategy
        result = run_backtest_simulation(
            data_filepath=DATA_FILE_PATH,
            output_html_path=OUTPUT_HTML_PATH,
            strategy_class=DQNStrategy # Pass the actual strategy class
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"Erro durante a simulação de backtest: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Ocorreu um erro interno durante a simulação: {str(e)}"}), 500

@trading_bp.route("/chart-data", methods=["GET"])
def get_chart_data():
    """Endpoint para obter dados históricos OHLCV para o gráfico."""
    asset_key = request.args.get("asset", "BTC/USD") # Default to BTC/USD for now
    print(f"Buscando dados do gráfico para o ativo: {asset_key}")

    # For now, always load the same BTC data file
    # Future: Map asset_key to different data files
    if asset_key != "BTC/USD":
        print(f"Warning: Asset {asset_key} requested, but only BTC/USD data is currently supported for chart.")
        # Optionally return error or default to BTC data
        # return jsonify({"error": "Asset not supported"}), 404

    try:
        df = load_data_from_json(DATA_FILE_PATH)

        if df is not None and not df.empty:
            # Format data for Lightweight Charts: array of {time, open, high, low, close}
            # Ensure index is DateTimeIndex for timestamp conversion
            if not isinstance(df.index, pd.DatetimeIndex):
                 # Attempt conversion if it's not already DatetimeIndex
                 try:
                     df.index = pd.to_datetime(df.index)
                 except Exception as date_err:
                     print(f"Error converting index to DatetimeIndex: {date_err}")
                     return jsonify({"error": "Failed to process data index"}), 500
                     
            # Convert timestamp to UNIX timestamp in seconds (required by Lightweight Charts)
            chart_data = [
                {
                    "time": int(timestamp.timestamp()), # Convert pd.Timestamp to UNIX timestamp (seconds)
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"]
                }
                # Iterate through DataFrame rows, using index for time
                for timestamp, row in df.iterrows()
            ]
            print(f"Retornando {len(chart_data)} pontos de dados para o gráfico ({asset_key})")
            return jsonify(chart_data), 200
        else:
            print(f"Nenhum dado carregado do arquivo: {DATA_FILE_PATH}")
            return jsonify([]), 404 # Return empty array if no data

    except Exception as e:
        print(f"Erro ao buscar ou formatar dados do gráfico: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Erro ao obter dados do gráfico"}), 500

# Remove or comment out unused endpoints like /balance, /reset-balance, /simulate if not needed now
# @trading_bp.route("/balance", methods=["GET"])
# ...
# @trading_bp.route("/reset-balance", methods=["POST"])
# ...

