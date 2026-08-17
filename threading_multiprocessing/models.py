import pandas as pd

from dataclasses import dataclass

@dataclass
class StockData:
    time: pd.Timestamp
    ticker: str
    percentage_change: float 

@dataclass
class StockInput:
    file_path: str
    ticker: str