from backtesting import Backtest
from data_loader import load_data_from_json
from simple_strategy import SimpleMovingAverageStrategy
import os

# Definir o diretório de trabalho e o caminho do arquivo de dados
WORK_DIR = "/home/ubuntu/projeto_ia_trading"
DATA_FILE = os.path.join(WORK_DIR, "btc_usd_data.json")
OUTPUT_HTML = os.path.join(WORK_DIR, "simple_strategy_backtest.html")

def run_simple_backtest():
    """Carrega os dados, executa um backtest com a estratégia simples e salva o gráfico."""
    print(f"Carregando dados de {DATA_FILE}...")
    data = load_data_from_json(DATA_FILE)

    if data is None or data.empty:
        print("Falha ao carregar dados. Abortando backtest.")
        return

    print("Dados carregados. Iniciando backtest com SimpleMovingAverageStrategy...")
    # Instanciar o Backtest
    # Usar um valor de caixa inicial razoável e comissão simulada
    bt = Backtest(data, SimpleMovingAverageStrategy, cash=10000, commission=.002)

    # Executar o backtest
    stats = bt.run()

    print("\nEstatísticas do Backtest:")
    print(stats)

    # Salvar o gráfico interativo
    try:
        print(f"Salvando gráfico do backtest em {OUTPUT_HTML}...")
        bt.plot(filename=OUTPUT_HTML, open_browser=False)
        print("Gráfico salvo com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar o gráfico: {e}")
        print("As estatísticas foram impressas acima.")

if __name__ == "__main__":
    run_simple_backtest()

