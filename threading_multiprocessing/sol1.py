import yfinance as yf
import pandas as pd

from concurrent.futures import ThreadPoolExecutor
from typing import Protocol
from dataclasses import dataclass

@dataclass
class StockData:
    time: pd.Timestamp
    ticker: str
    percentage_change: float 

class StockDataFetcher(Protocol):
    def fetch_stock_data(self, start_time: pd.Timestamp, ticker: str) -> pd.DataFrame | None:
        ...

class YahooStockDataFetcher:
    def fetch_stock_data(self, start_time: pd.Timestamp, ticker: str) -> pd.DataFrame | None:
        try:
            stock_data = yf.download(
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

def process_stock_data(stock_data: pd.DataFrame | None,
                       start_time: pd.Timestamp,
                       ticker: str) -> StockData | None:  
    if stock_data is None or stock_data.empty:
        return None

    open_price = stock_data.iloc[0][("Open", ticker)]
    close_price = stock_data.iloc[0][("Close", ticker)]

    percentage_change = ((close_price - open_price) / open_price) * 100

    return StockData(
        time=start_time,
        ticker=ticker,
        percentage_change=percentage_change
    )

def fetch_and_process(fetcher: StockDataFetcher, 
                      start_time: pd.Timestamp,
                      ticker: str) -> StockData | None:
    raw_stock_data = fetcher.fetch_stock_data(start_time, ticker)

    return process_stock_data(raw_stock_data, start_time, ticker)

class StockDataWriter(Protocol):
    def write(self, stock_data_list: list[StockData]) -> None:
        ...

class CsvStockDataWriter:
    def __init__(self, output_filepath: str):
        self.output_filepath = output_filepath

    def write(self, stock_data_list: list[StockData]) -> None:
        df = pd.DataFrame(stock_data_list)
        df.to_csv(self.output_filepath, index=False)

class StockDataReader(Protocol):
    ticker: str

    def read_timestamps(self) -> list[pd.Timestamp]:
        ...

class FileStockDataReader:
    def __init__(self, file_path: str, ticker: str):
        self.file_path = file_path
        self.ticker = ticker

    def read_timestamps(self) -> list[pd.Timestamp]:
        with open(self.file_path) as file:
            return [pd.to_datetime(line.strip()).floor("h") 
                    for line in file if line.strip()]

class Pipeline:
    def __init__(self, 
                 stock_data_writer: StockDataWriter,
                 stock_data_fetcher: StockDataFetcher,
                 stock_data_readers: list[StockDataReader]
                 ) -> None:
        self.stock_data_writer = stock_data_writer
        self.stock_data_fetcher = stock_data_fetcher
        self.stock_data_readers = stock_data_readers

    def run(self, workers: int = 8) -> None:
        all_results = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            for reader in self.stock_data_readers:
                timestamps = reader.read_timestamps()

                processed_stock_data = executor.map(
                    lambda timestamp: fetch_and_process(
                        fetcher=self.stock_data_fetcher,
                        start_time=timestamp,
                        ticker=reader.ticker
                    ),
                    timestamps
                )

                all_results.extend(
                    stock_data
                    for stock_data in processed_stock_data
                    if stock_data is not None
                )

        self.stock_data_writer.write(all_results)

if __name__ == "__main__":
     input_params = [("bitcoin_dates.txt", "BTC-USD"),
                     ("amazon_dates.txt", "AMZN"),
                     ("google_date.txt", "GOOG")]

     stock_data_writer = CsvStockDataWriter("output.csv")
     stock_data_fetcher = YahooStockDataFetcher()
     stock_data_readers = [FileStockDataReader(file_path=param[0], 
                                             ticker=param[1]) 
                         for param in input_params]

     pipeline = Pipeline(stock_data_writer=stock_data_writer,
                         stock_data_fetcher=stock_data_fetcher,
                         stock_data_readers=stock_data_readers)
     pipeline.run()

 
