# General imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
# Company financials import
import simfin as sf
from simfin.names import *

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
def get_stock_historical_data(stock_client, symbol, timeframe, start=None, end=None):
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=timeframe,
        start=start,
        end=end
    )

    bars = stock_client.get_stock_bars(request_params)
    bars_df = bars.df
    return bars_df.loc[symbol]

'''
Parameters:
    stock_index: name of the stock index
    start: datetime start
Return:
    None
Writes the daily stock data for every company in the index to individual csv files.
Data is from the entered start day until now.
'''
def write_stock_data_to_files(stock_index, start, timeframe):
    stock_client = StockHistoricalDataClient(config.API_KEY,  config.SECRET_KEY)
    with open(f'data/{stock_index}.csv') as f:
        qqq_holdings = f.readlines()
    symbols = [holding.split(',')[2].strip() for holding in qqq_holdings[1:]]
    print(timeframe)
    for symbol in symbols:
        # gets data frame of stock data
        df = get_stock_historical_data(stock_client, symbol, timeframe, start)
        # add technical indicators to data frame
        sma = btalib.sma(df, period = 30)
        rsi = btalib.rsi(df)
        macd = btalib.macd(df)
        df['30sma'] = sma.df
        df['rsi'] = rsi.df
        df['macd'] = macd.df['macd']
        df['signal'] = macd.df['signal']
        df['histogram'] = macd.df['histogram']
        # write data to file
        filename = f'data/{stock_index}/{timeframe}/{symbol}_{timeframe}.txt'
        with open(filename, 'w') as f:
            f.write(df.to_csv())


def main():
    stock_index = 'qqq'
    timeframe = TimeFrame.Day 
    start = datetime.datetime(2022,1,1)
    # write_stock_data_to_files(stock_index=stock_index, start=start, timeframe=timeframe)
    
    # account.get_account_info(config.KEYS)

    symbol = 'AAPL'
    df = pd.read_csv(f'data/qqq/1Day/{symbol}_1Day.txt', parse_dates=True, index_col='timestamp')
    # print(df)

    # Getting fundamental data
    sf.set_data_dir('data/simfin/')
    sf.set_api_key(api_key=config.SIMFIN_KEY)
    df_income = sf.load(dataset='income', variant='annual', market='us', index=[TICKER, REPORT_DATE],
              parse_dates=[REPORT_DATE, PUBLISH_DATE, RESTATED_DATE], refresh_days=1)
    df_balance = sf.load(dataset='balance', variant='annual', market='us', index=[TICKER, REPORT_DATE],
              parse_dates=[REPORT_DATE, PUBLISH_DATE, RESTATED_DATE], refresh_days=1)
    df_cashflow = sf.load(dataset='cashflow', variant='annual', market='us', index=[TICKER, REPORT_DATE],
              parse_dates=[REPORT_DATE, PUBLISH_DATE, RESTATED_DATE], refresh_days=1)
    df_derived = sf.load(dataset='derived', variant='annual', market='us', index=[TICKER, REPORT_DATE],
              parse_dates=[REPORT_DATE, PUBLISH_DATE, RESTATED_DATE], refresh_days=1)
    ticker = 'AAPL'
    cols = [REVENUE, NET_INCOME]
    print(df_income.loc[ticker][cols])
    # print(df_balance.loc[ticker])
    # print(df_cashflow.loc[ticker][[NET_CASH_OPS, NET_CASH_INV, NET_CASH_FIN, NET_CHG_CASH]])
    # print(df_derived.loc[ticker])
        

if __name__ == '__main__':
    main()