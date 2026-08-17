from models import StockInput
from writers import CsvStockDataWriter
from readers import FileStockDataReader
from fetchers import YahooStockDataFetcher
from pipeline import Pipeline

from concurrent.futures import ThreadPoolExecutor

if __name__ == "__main__":
     stock_input = [StockInput("bitcoin_dates.txt", "BTC-USD"),
                     StockInput("amazon_dates.txt", "AMZN"),
                     StockInput("google_date.txt", "GOOG")]

     stock_data_writer = CsvStockDataWriter()
     stock_data_fetcher = YahooStockDataFetcher()
     stock_data_readers = [FileStockDataReader(file_path=stock.file_path, 
                                               ticker=stock.ticker) 
                         for stock in stock_input]

     with ThreadPoolExecutor(max_workers=3) as executor:
          pipelines = [Pipeline(stock_data_fetcher=stock_data_fetcher,
                                stock_data_reader=stock_data_reader) 
                         for stock_data_reader in stock_data_readers]

          results = executor.map(
               lambda pipeline: pipeline.run(),
               pipelines,
          )

     all_results = []

     for result in results:
          all_results.extend(result)

     stock_data_writer.write(all_results, "output.csv")



 
