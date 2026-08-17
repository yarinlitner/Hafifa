import yfinance
import pandas as pd

from typing import Protocol, Optional

class StockDataFetcher(Protocol):
    def fetch_stock_data(self, start_time: pd.Timestamp, ticker: str) -> Optional[pd.DataFrame]:
        ...

class YahooStockDataFetcher:
    def fetch_stock_data(self, start_time: pd.Timestamp, ticker: str) -> Optional[pd.DataFrame]:
        try:
            stock_data = yfinance.download(
                    ticker,
                    start = start_time,
                    end = start_time + pd.Timedelta(hours=1),
                    interval="1h",
                    progress=False,
                )

            return stock_data

        except Exception as e:
            print(f"Error retrieving stock data: {e}")

            return None
