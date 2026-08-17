from models import StockData

import pandas as pd

from typing import Protocol, List

class StockDataWriter(Protocol):
    def write(self, stock_data_list: List[StockData], filepath: str) -> None:
        ...

class CsvStockDataWriter:
    def write(self, stock_data_list: List[StockData], filepath: str) -> None:
        df = pd.DataFrame(stock_data_list)
        df.to_csv(filepath, index=False)
