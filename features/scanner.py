from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd


class Scanners:
    def __init__(self):
        self.today_date = datetime.today().strftime('%d-%m-%Y')

    def chartink_eng(self, cond):
        url = "https://chartink.com/screener/process"

        conditions = {"scan_clause": cond}

        with requests.session() as s:
            r_data = s.get(url)
            soup = bs(r_data.content, "lxml")
            meta = soup.find_all("meta", {"name": "csrf-token"})[0]["content"]
            header = {"x-csrf-token": meta}
            data = s.post(url, headers=header, data=conditions).json()
            scan = pd.DataFrame(data["data"])
            return scan

    def get_stocks(self):
        # short term
        cond = "( {57960} ( weekly ema ( weekly close , 21 ) >= weekly ema ( weekly close , 50 ) and weekly ema ( close,10 ) / weekly ema ( close,21 ) <= 1.03 and weekly ema ( close,10 ) / weekly ema ( close,21 ) > 1 and weekly ema ( close,21 ) / weekly ema ( close,30 ) <= 1.03 and weekly ema ( close,21 ) / weekly ema ( close,30 ) > 1 and weekly ema ( close,30 ) / weekly ema ( close,50 ) <= 1.03 and weekly ema ( close,30 ) / weekly ema ( close,50 ) > 1 and latest close > 30 and latest sma ( latest volume , 50 ) > 10000 and market cap >= 300 and latest volume > latest sma ( latest volume , 20 ) ) ) "
        df1 = pd.DataFrame(self.chartink_eng(cond=cond))['nsecode']

        # mid
        cond = "( {cash} ( latest ema ( latest close , 20 ) >= latest ema ( latest close , 50 ) and latest ema ( latest close , 50 ) >= latest ema ( latest close , 75 ) and latest ema ( latest close , 75 ) >= latest ema ( latest close , 100 ) and latest ema ( latest close , 100 ) >= latest ema ( latest close , 200 ) and latest ema ( close,20 ) / latest ema ( close,50 ) < 1.03 and latest ema ( close,20 ) / latest ema ( close,50 ) > 1 and latest ema ( close,50 ) / latest ema ( close,75 ) < 1.03 and latest ema ( close,50 ) / latest ema ( close,75 ) > 1 and latest ema ( close,75 ) / latest ema ( close,100 ) < 1.03 and latest ema ( close,75 ) / latest ema ( close,100 ) > 1 and latest close > 30 and latest sma ( latest volume , 50 ) > 10000 and market cap >= 300 and latest close > 30 and weekly ema ( weekly close , 50 ) >= weekly ema ( weekly close , 100 ) and quarterly indian public percentage <= 1 quarter ago indian public percentage ) ) "
        df2 = pd.DataFrame(self.chartink_eng(cond=cond))['nsecode']

        # weekly
        cond = "( {57960} ( latest ema ( latest close , 21 ) >= latest ema ( latest close , 50 ) and latest ema ( close,10 ) / latest ema ( close,21 ) <= 1.03 and latest ema ( close,10 ) / latest ema ( close,21 ) > 1 and latest ema ( close,21 ) / latest ema ( close,30 ) <= 1.03 and latest ema ( close,21 ) / latest ema ( close,30 ) > 1 and latest ema ( close,30 ) / latest ema ( close,50 ) <= 1.03 and latest ema ( close,30 ) / latest ema ( close,50 ) > 1 and latest close >= weekly max ( 52 , weekly high ) * 0.75 and latest close >= weekly max ( 52 , weekly low ) * 1 and latest sma ( latest volume , 50 ) > 1000 and weekly ema ( weekly close , 50 ) >= weekly ema ( weekly close , 100 ) ) ) "
        df3 = pd.DataFrame(self.chartink_eng(cond=cond))['nsecode']
        # Convert Series to DataFrame
        df1 = df1.to_frame()
        df2 = df2.to_frame()
        df3 = df3.to_frame()

        # Reset index to make the current index a column and create a proper index
        df1.reset_index(drop=True, inplace=True)
        df2.reset_index(drop=True, inplace=True)
        df3.reset_index(drop=True, inplace=True)

        # Add 'Cat' column
        df1['Cat'] = "S"
        df2['Cat'] = "M"
        df3['Cat'] = "L"

        # Concatenate DataFrames vertically
        df = pd.concat([df1, df2, df3], axis=0)

        return df

    def FII_buying(self):
        cond = "( {cash} ( latest ema ( latest close , 20 ) >= latest ema ( latest close , 50 ) and latest ema ( latest close , 50 ) >= latest ema ( latest close , 75 ) and latest ema ( latest close , 75 ) >= latest ema ( latest close , 100 ) and latest ema ( latest close , 100 ) >= latest ema ( latest close , 200 ) and latest ema ( close,20 ) / latest ema ( close,50 ) < 1.03 and latest ema ( close,20 ) / latest ema ( close,50 ) > 1 and latest ema ( close,50 ) / latest ema ( close,75 ) < 1.03 and latest ema ( close,50 ) / latest ema ( close,75 ) > 1 and latest ema ( close,75 ) / latest ema ( close,100 ) < 1.03 and latest ema ( close,75 ) / latest ema ( close,100 ) > 1 and market cap >= 300 and quarterly foreign institutional investors percentage > 1 quarter ago foreign institutional investors percentage and quarterly foreign institutional investors percentage > quarterly indian public percentage ) ) "
        df1 = pd.DataFrame(self.chartink_eng(cond=cond))['nsecode']

        df1 = df1.to_frame()

        df1.reset_index(drop=True, inplace=True)
        return df1

    def darvas_stocks(self):
        cond = "( {cash} ( latest close > latest ema ( latest close , 21 ) and latest close > latest ema ( latest close , 50 ) and latest ema ( latest close , 21 ) > latest ema ( latest close , 50 ) and latest ema ( latest volume , 50 ) >= 100000 and latest close >= 10 and weekly high < 1 week ago high and weekly low > 1 week ago low and weekly high < 2 weeks ago high and weekly low > 2 weeks ago low and ( {cash} ( latest ema ( latest close , 20 ) >= latest ema ( latest close , 50 ) and latest ema ( latest close , 50 ) >= latest ema ( latest close , 75 ) and latest ema ( latest close , 75 ) >= latest ema ( latest close , 100 ) and latest ema ( latest close , 100 ) >= latest ema ( latest close , 200 ) and latest ema ( close,20 ) / latest ema ( close,50 ) < 1.03 and latest ema ( close,20 ) / latest ema ( close,50 ) > 1 and latest ema ( close,50 ) / latest ema ( close,75 ) < 1.03 and latest ema ( close,50 ) / latest ema ( close,75 ) > 1 and latest ema ( close,75 ) / latest ema ( close,100 ) < 1.03 and latest ema ( close,75 ) / latest ema ( close,100 ) > 1 and market cap >= 300 ) ) ) ) "
        df1 = pd.DataFrame(self.chartink_eng(cond=cond))['nsecode']

        df1 = df1.to_frame()

        df1.reset_index(drop=True, inplace=True)
        return df1

    def up_20p(self):
        cond = """( {57960} ( weekly "close - 1 candle ago close / 1 candle ago close * 100" > 10 ) ) """
        df1 = pd.DataFrame(self.chartink_eng(cond=cond))['nsecode']

        df1 = df1.to_frame()

        df1.reset_index(drop=True, inplace=True)
        return df1
