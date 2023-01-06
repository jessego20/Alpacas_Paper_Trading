# General imports
import pandas as pd
import numpy as np
import datetime
# My file imports
import config
import account
# Alpacas Market Data imports
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data import CryptoDataStream, StockDataStream
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
# Technical Analysis import
import btalib

'''
Parameters: 
    stock_client = alpacas stock client object
    symbols = list of stock symbols
    timeframe = alpacas timeframe object, 
    start = datetime object
    end = datetime object
Returns:
    pandas dataframe with stock data
'''
def get_stock_historical_data(stock_client, symbols, timeframe, start=None, end=None):
    request_params = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=timeframe,
        start=start,
        end=end
    )

    bars = stock_client.get_stock_bars(request_params)
    bars_df = bars.df
    return bars_df

def main():
    account.get_account_info(config.KEYS)

    stock_client = StockHistoricalDataClient(config.API_KEY,  config.SECRET_KEY)

    with open('data/qqq.csv') as f:
        qqq_holdings = f.readlines()
    
    symbols = [holding.split(',')[2].strip() for holding in qqq_holdings[1:]]
    timeframe = TimeFrame.Day
    start = datetime.datetime(2022,1,1)
    end = datetime.datetime(2022,12,31)
    df = get_stock_historical_data(stock_client, symbols, timeframe, start, end)
    print(df)

    sma = btalib.sma(df, period = 30)
    print(sma.df)

if __name__ == '__main__':
    main()