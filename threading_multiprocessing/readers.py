import pandas as pd

from typing import Protocol, List

class StockDataReader(Protocol):
    ticker: str

    def read_timestamps(self) -> List[pd.Timestamp]:
        ...

class FileStockDataReader:
    def __init__(self, file_path: str, ticker: str):
        self.file_path = file_path
        self.ticker = ticker

    def read_timestamps(self) -> List[pd.Timestamp]:
        with open(self.file_path) as file:
            return [pd.to_datetime(line.strip()).floor("h") 
                    for line in file if line.strip()]
