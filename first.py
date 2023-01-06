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
    
    stock_index = 'qqq'
    with open(f'data/{stock_index}.csv') as f:
        qqq_holdings = f.readlines()
    
    symbols = [holding.split(',')[2].strip() for holding in qqq_holdings[1:]]
    timeframe = TimeFrame.Day
    start = datetime.datetime(2022,1,1)
    for symbol in symbols:
        df = get_stock_historical_data(stock_client, symbol, timeframe, start)

        # technical indicators
        sma = btalib.sma(df, period = 30)
        rsi = btalib.rsi(df)
        macd = btalib.macd(df)
        df['30sma'] = sma.df
        df['rsi'] = rsi.df
        df['macd'] = macd.df['macd']
        df['signal'] = macd.df['signal']
        df['histogram'] = macd.df['histogram']

        filename = f'data/daily/{symbol}.txt'
        with open(filename, 'w') as f:
            f.write(df.loc[symbol].to_csv())
        
    
    df = pd.read_csv('data/daily/AAPL.txt', parse_dates=True, index_col='timestamp')
    print(df)

    # Getting financial data
    # sf.set_data_dir('data/simfin/')
    # sf.set_api_key(api_key=config.SIMFIN_KEY)
    # df_income = sf.load_income(variant='annual', market='us')
    # print(df_income.loc['AAPL'])
        

if __name__ == '__main__':
    main()