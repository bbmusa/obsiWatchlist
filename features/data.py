from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from features.scanner import Scanners

def nifty500():
    nse_ticker = pd.read_csv('features/tickers/ind_nifty500list.csv')
    nse_ticker['yahoo_symbol'] = nse_ticker['Symbol'] + '.NS'
    return nse_ticker


def get_date_range(days=252):
    now = datetime.now()
    date_to = now.strftime("%Y-%m-%d")
    date_from = (now - timedelta(days=252)).strftime("%Y-%m-%d")
    return date_from, date_to


class GetData:
    def __init__(self):
        self.ticker = nifty500()
        self.scans = Scanners()

    def get_piles(self):
        sand_df = self.scans.get_stocks()
        darvas_df = self.scans.darvas_stocks()
        up_df = self.scans.up_20p()
        return sand_df, darvas_df, up_df
