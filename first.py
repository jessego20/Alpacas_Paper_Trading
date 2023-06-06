# General imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
import json
import datetime
import os
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
        index_holdings = f.readlines()
    symbols = [holding.split(',')[2].strip() for holding in index_holdings[1:]]
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

'''
Time Series Momentum Correlation Analysis
Parameters:
    df: dataframe of stock prices
Returns: a dataframe where rows are lookback, hold_days tuples
         and columns are [correlation coefficient, p-value]
'''
def TSM_correlation(df, using_simfin=True):
    if using_simfin:
        open_prices = df[OPEN]
        close_prices  = df[CLOSE]
    else:
        open_prices = df['open']
        close_prices = df['close']

    dict = {}
    for lookback in [1, 5, 10, 25, 60, 120, 250]:
        for hold_days in [1, 5, 10, 25, 60, 120, 250]:
            step = hold_days
            if lookback < hold_days:
                step = lookback
            lookback_returns = [100*(close_prices[i]-open_prices[i-lookback+1])/open_prices[i-lookback+1] for i in range(lookback-1,len(close_prices)-hold_days,step)]
            hold_days_returns = [100*(close_prices[i]-open_prices[i-hold_days+1])/open_prices[i-hold_days+1] for i in range(lookback+hold_days-1,len(close_prices),step)]
            cc_pv = scipy.stats.pearsonr(lookback_returns, hold_days_returns)
            dict[(lookback, hold_days)] = (round(cc_pv[0], 4), round(cc_pv[1], 4))
    return pd.DataFrame.from_dict(dict, orient='index', columns=['Correlation Coefficient', 'p-value'])


def main():
    # account.get_account_info(config.KEYS)

    # Gets stock data for each stock in the given index
    '''
    stock_index = 'qqq'
    timeframe = TimeFrame.Day 
    start = datetime.datetime(2016,1,1)
    write_stock_data_to_files(stock_index=stock_index, start=start, timeframe=timeframe)
    '''

    # Uses simfin's daily stock prices data to perform Time Series Momentum correlation analysis
    '''
    sf.set_data_dir('data/simfin/')
    sf.set_api_key(api_key=config.SIMFIN_KEY)
    qqq_tickers = [ticker.strip() for ticker in pd.read_csv('data/qqq.csv')['Holding Ticker']
                    if ticker.strip() not in ['GOOGL','ASML', 'PDD', 'AZN', 'GFS', 'WBD']]
    df_shares = sf.load(dataset='shareprices', variant='daily', market='us', index=[TICKER, DATE], refresh_days=1)
    df_qqq_shares = df_shares.loc[qqq_tickers]

    # Time Series Momentum correlation analysis
    ticker = 'AAPL'
    df_corr = TSM_correlation(df_qqq_shares.loc[ticker])
    print(df_corr)
    '''
    
    # Getting fundamental data
    '''
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

    income_cols = [REVENUE, NET_INCOME]
    # print(df_income.loc[ticker][income_cols])

    # print(df_balance.loc[ticker])

    cashflow_cols = [NET_CASH_OPS, NET_CASH_INV, NET_CASH_FIN, NET_CHG_CASH]
    # print(df_cashflow.loc[ticker][cashflow_cols])

    derived_cols = [EBITDA, FCF, EPS_BASIC, EPS_DILUTED]
    print(df_derived.loc[ticker][derived_cols])
    '''
    



if __name__ == '__main__':
    main()
