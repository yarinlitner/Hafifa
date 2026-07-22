import yfinance as yf
import pandas as pd
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

output_file = "output.csv"

input_params = [("bitcoin_dates.txt", "BTC-USD"), ("amazon_dates.txt", "AMZN"), ("google_date.txt", "GOOG")]
all_results = []

def fetch_hour(t, ticker):
    try:
        btc = yf.download(
                ticker,
                start = t,
                end = t + pd.Timedelta(hours=1),
                interval="1h",
                progress=False,
            )
        if btc.empty:
            return None
        else:
            open_price = btc.iloc[0][("Open", ticker)]
            close_price = btc.iloc[0][("Close", ticker)]

            pct_change = ((close_price - open_price) / open_price) * 100

            return {
                "hour": t,
                "stock type": ticker,
                "percentage change": pct_change,
            }
    except Exception as e:
        print(f"Error processing {t}: {e}")
        return None
 
with ThreadPoolExecutor(max_workers=8) as executor:
    for (file, ticker) in input_params:
        with open(file) as f:
            timestamps = [pd.to_datetime(line.strip()).floor("h") for line in f if line.strip()]  
    
            results = list(executor.map(fetch_hour, timestamps, [ticker] * len(timestamps)))
            all_results.extend(r for r in results if r is not None)

    df = pd.DataFrame(all_results)
    df.to_csv(output_file, index=False)