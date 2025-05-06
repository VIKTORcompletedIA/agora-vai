# fetch_multi_asset_data.py

import sys
import os
import json

sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient

client = ApiClient()

ASSETS = {
    "PETR4.SA": "BR",
    "VALE3.SA": "BR",
    "ITUB4.SA": "BR",
    "ETH-USD": "US"
}

SAVE_DIR = "/home/ubuntu/asset_data"
INTERVAL = "1d"
RANGE = "max"

def fetch_and_save(symbol, region):
    """Fetches data for a symbol and saves it to a JSON file."""
    filename = os.path.join(SAVE_DIR, f"{symbol}_data.json")
    print(f"Fetching data for {symbol} (Region: {region})...")
    try:
        data = client.call_api(
            "YahooFinance/get_stock_chart", 
            query={
                "symbol": symbol,
                "region": region,
                "interval": INTERVAL,
                "range": RANGE,
                "includeAdjustedClose": True
            }
        )
        
        # Basic validation of the response structure
        if not data or "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
             print(f"  Error: Invalid or empty data received for {symbol}.")
             # Save an empty structure to indicate failure but allow process to continue
             error_data = {"chart": {"result": None, "error": f"Invalid or empty data received for {symbol}"}}
             with open(filename, "w") as f:
                 json.dump(error_data, f, indent=2)
             return False

        # Check for API-level errors within the valid structure
        # Corrected line 50: Use single quotes for the f-string or escape inner quotes.
        if data["chart"].get("error"):
            print(f'  Error fetching {symbol}: {data["chart"]["error"]}') # Changed outer quotes to single
            with open(filename, "w") as f:
                 json.dump(data, f, indent=2) # Save the error response
            return False

        # Save successful data
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Data for {symbol} saved to {filename}")
        return True
        
    except Exception as e:
        print(f"  Exception occurred while fetching {symbol}: {e}")
        # Save an error structure
        error_data = {"chart": {"result": None, "error": f"Exception: {str(e)}"}}
        try:
            with open(filename, "w") as f:
                json.dump(error_data, f, indent=2)
        except Exception as write_err:
             print(f"  Failed to write error file for {symbol}: {write_err}")
        return False

if __name__ == "__main__":
    os.makedirs(SAVE_DIR, exist_ok=True)
    success_count = 0
    for symbol, region in ASSETS.items():
        if fetch_and_save(symbol, region):
            success_count += 1
    print(f"\nFinished fetching data. {success_count}/{len(ASSETS)} assets fetched successfully.")

