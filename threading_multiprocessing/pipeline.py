from models import StockData
from readers import StockDataReader
from fetchers import StockDataFetcher

import pandas as pd

from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

class Pipeline:
    def __init__(self,
                 stock_data_fetcher: StockDataFetcher,
                 stock_data_reader: StockDataReader
                 ) -> None:
        self.stock_data_fetcher = stock_data_fetcher
        self.stock_data_reader = stock_data_reader

    def _process_stock_data(
        self,
        stock_data: Optional[pd.DataFrame],
        start_time: pd.Timestamp,
    ) -> Optional[StockData]:
        if stock_data is None or stock_data.empty:
            return None

        ticker = self.stock_data_reader.ticker

        open_price = stock_data.iloc[0][("Open", ticker)]
        close_price = stock_data.iloc[0][("Close", ticker)]

        percentage_change = (
            (close_price - open_price) / open_price
        ) * 100

        return StockData(
            time=start_time,
            ticker=ticker,
            percentage_change=percentage_change,
        )

    def _fetch_and_process(
        self,
        start_time: pd.Timestamp,
    ) -> Optional[StockData]:
        ticker = self.stock_data_reader.ticker

        raw_stock_data = self.stock_data_fetcher.fetch_stock_data(
            start_time,
            ticker,
        )

        return self._process_stock_data(
            raw_stock_data,
            start_time,
        )

    def run(self, workers: int = 8) -> List[StockData]:
        all_results = []

        timestamps = self.stock_data_reader.read_timestamps()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            processed_stock_data = executor.map(
                self._fetch_and_process,
                timestamps,
            )

            all_results.extend(
                stock_data
                for stock_data in processed_stock_data
                if stock_data is not None
            )

        return all_results