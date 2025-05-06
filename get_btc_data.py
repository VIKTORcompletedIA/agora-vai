
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json

client = ApiClient()

# Fetch historical data for BTC-USD
try:
    # Get maximum available daily data
    btc_data = client.call_api('YahooFinance/get_stock_chart', query={
        'symbol': 'BTC-USD',
        'interval': '1d',
        'range': 'max',
        'includeAdjustedClose': True
    })

    # Save the data to a JSON file
    with open('/home/ubuntu/btc_usd_data.json', 'w') as f:
        json.dump(btc_data, f, indent=2)

    print("Dados históricos de BTC-USD (diário, máximo) salvos em /home/ubuntu/btc_usd_data.json")

except Exception as e:
    print(f"Erro ao buscar ou salvar dados: {e}")


