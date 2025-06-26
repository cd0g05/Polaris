from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import requests
import json


@dataclass
class Stock:
    name:str
    amount:int
    price:float
    # def __init__(self, name:str, amount:int, price:float):
    #     self.name = name
    #     self.amount = amount
    #     self.price = price

    def __str__(self):
        return f"{self.name}: {self.amount} shares at ${self.price}"

    def total_value(self):
        return self.amount * self.price

    def stock_price_diff(self, new_price: float):
        return new_price - self.price

    def perc_price_diff(self, new_price: float):
        return ((new_price - self.price)/self.price) * 100

    def total_amount_diff(self, new_price: float):
        return (self.amount * new_price) - (self.amount * self.price)

class StockPriceRetriever(metaclass=ABCMeta):
    @abstractmethod
    def get_stock_price(self, symbol:str ) -> float:
        pass

class StubStockPriceRetriever(StockPriceRetriever):

    def get_stock_price(self, symbol: str) -> float:
        return 123.45

class AlphavantageStockRetriever(StockPriceRetriever):

    def get_stock_price(self, symbol: str) -> float:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=2QKVQ00THSAN95I6'
        r = requests.get(url)
        data = r.json()

        # most_recent_date = max(data["Time Series (Daily)"].keys())
        dates:list = sorted(list(data["Time Series (Daily)"].keys()))
        most_recent_date = dates[-1]
        latest_price = float(data["Time Series (Daily)"][most_recent_date]["4. close"])
        return latest_price


class StockItToMe:


    def __init__(self, stockservice:StockPriceRetriever) -> None:
        super().__init__()
        self.service = stockservice

    def service_user(self, user:str) -> str:
        pass
        #load user
        #feed through command line
        #get portfolio (via csv)
        stocks = []

        with open('/Users/cartercripe/dev/code/projects/stockittome/working/user.txt', 'r') as file:
            for line in file:
                name, amount, price = line.strip().split()
                # Convert string values to appropriate types and create Stock object
                stock = Stock(name, int(amount), float(price))
                stocks.append(stock)

        #call alpha api

        for stock in stocks:
            latest_price = self.service.get_stock_price(stock.name)

            #calculate changes
            with open('/Users/cartercripe/dev/code/projects/stockittome/working/output.txt', 'a') as file:
                file.write(f"\nStock: {stock.name}\n")
                file.write(f"Yesterday's Price: {stock.price:0.2f}\n")
                file.write(f"Current Price: {latest_price:0.2f}\n")
                file.write(f"Price Difference: {stock.stock_price_diff(latest_price):0.2f}\n")
                file.write(f"Percent Difference: {stock.perc_price_diff(latest_price):0.2f}\n")
                file.write(f"Total Difference: {stock.total_amount_diff(latest_price):0.2f}\n")

            stock.price = latest_price





    #feed data to llm
        #return results



# if __name__ == '__main__':
#
#
#     runner = StockItToMe(service)
#     runner.service_user("carter")