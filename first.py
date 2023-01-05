import pandas as pd
import numpy as np
import datetime

import config
from account import get_account_info

# Market Data imports
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data import CryptoDataStream, StockDataStream
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest

get_account_info(config.KEYS)

#test