import requests
import pandas as pd
import time
import json
from pandas.io.json import json_normalize

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


class NseIndiaStockData:
    def __init__(self):
        self.url = 'https://www.nseindia.com'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0'}
        self.session = requests.session()
        self.session.get(self.url, headers=self.headers)
        self.pre_market_base_url = f'https://www.nseindia.com/api/market-data-pre-open?key='
        self.pre_market_key = {
            'Nifty Bank': 'BANKNIFTY',
            'Nifty 50': 'NIFTY',
            'Securities in F&O': 'FO',
            'EMERGE': 'SME',
            'Others': 'OTHERS',
            'All': 'ALL'
        }
        self.live_market_base_url = f'https://www.nseindia.com/api/equity-stockIndices?index='
        self.live_market_key = {
            'Broad Market Indices': ['NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY NEXT 50', 'NIFTY MIDCAP 50',
                                     'NIFTY MIDCAP 100',
                                     'NIFTY MIDCAP 150',
                                     'NIFTY SMALLCAP 50', 'NIFTY SMALLCAP 100', 'NIFTY SMALLCAP 250',
                                     'NIFTY MIDSMALLCAP 250', 'NIFTY500 MULTICAP 50:25:25', 'NIFTY LARGEMIDCAP 250'
                                     ],
            'Sectorial Indices': ['NIFTY AUTO', 'NIFTY BANK', 'NIFTY ENERGY', 'NIFTY FINANCIAL SERVICES',
                                  'NIFTY FINANCIAL SERVICES 25/50',
                                  'NIFTY FMCG', 'NIFTY IT', 'NIFTY MEDIA', 'NIFTY METAL', 'NIFTY PHARMA',
                                  'NIFTY PSU BANK', 'NIFTY REALTY',
                                  'NIFTY PRIVATE BANK', 'NIFTY HEALTHCARE INDEX', 'NIFTY CONSUMER DURABLES',
                                  'NIFTY OIL & GAS'
                                  ],
            'Thematic Indices': ['NIFTY COMMODITIES', 'NIFTY INDIA CONSUMPTION', 'NIFTY CPSE', 'NIFTY INFRASTRUCTURE',
                                 'NIFTY MNC', 'NIFTY GROWTH SECTORS 15', 'NIFTY PSE', 'NIFTY SERVICES SECTOR',
                                 'NIFTY100 LIQUID 15',
                                 'NIFTY MIDCAP LIQUID 15'
                                 ],
            'Strategy Indices': ['NIFTY DIVIDEND OPPORTUNITIES 50', 'NIFTY50 VALUE 20', 'NIFTY100 QUALITY 30',
                                 'NIFTY50 EQUAL WEIGHT',
                                 'NIFTY100 EQUAL WEIGHT', 'NIFTY100 LOW VOLATILITY 30', 'NIFTY ALPHA 50',
                                 'NIFTY200 QUALITY 30',
                                 'NIFTY ALPHA LOW-VOLATILITY 30', 'NIFTY200 MOMENTUM 30'
                                 ],
            'Others': ['Securities in F&O', 'Permitted to Trade']
        }
        self.nse_holiday_base_url = f'https://www.nseindia.com/api/holiday-master?type='
        self.trading_clearing = ['TRADING', 'CLEARING']
        self.market_status_url = f'https://www.nseindia.com/api/marketStatus'
        self.fetch_symbol_url = f'https://www.nseindia.com/api/search/autocomplete?q='
        self.symbol_quote_url = f'https://www.nseindia.com/api/quote-equity?symbol='

    # Fetch the pre market data from NSE
    def nse_pre_market_data(self, key):
        # key = 'Nifty 50'
        if key is not None:
            pre_market_url = f'{self.pre_market_base_url}{self.pre_market_key[key]}'
            pre_market_get_data = self.session.get(pre_market_url, headers=self.headers).json()['data']
            fetch_data = []
            for _ in pre_market_get_data:
                fetch_data.append(_['metadata'])
            pre_market_data_frame = pd.DataFrame(fetch_data)
            return pre_market_data_frame

    # Fetch the live market data from NSE
    def nse_live_market_data(self, indices, key):
        # indices = 'Others'
        # key = 'Permitted to Trade'
        live_market_url = self.live_market_base_url + f'{self.live_market_key[indices][self.live_market_key[indices].index(key)]}'.upper().replace(
            ' ', '%20').replace('&', '%26')

        live_market_get_data = self.session.get(live_market_url, headers=self.headers).json()['data']
        live_market_data_frame = pd.DataFrame(live_market_get_data)

        return live_market_data_frame

    def nse_holidays(self, nse_holiday):
        trading_holiday_url = self.nse_holiday_base_url + nse_holiday
        nse_holiday_get_data = self.session.get(trading_holiday_url, headers=self.headers).json()
        nse_holiday_data_frame = pd.DataFrame(list(nse_holiday_get_data.values())[0])
        return nse_holiday_data_frame

    def ticker(self, ticker_label, root):
        text_width = 150
        ticker_label.config(font=('Helvetica', 10, 'bold'))
        while True:
            blank_val = ' ' * text_width
            market_status_json = self.market_status()
            for cnt in range(0, len(market_status_json)):
                market_status_data = ''
                market_name = f'{market_status_json.iloc[cnt]["index"]} Market : {market_status_json.iloc[cnt]["last"]} ( {round(market_status_json.iloc[cnt]["variation"], 2)} / {market_status_json.iloc[cnt]["percentChange"]}% ) ' if \
                    market_status_json.iloc[cnt][
                        "market"] == 'Capital Market' else f'{market_status_json.iloc[cnt]["market"]}  Market : '
                market_status_data = f'{market_name}   | Market Status : {market_status_json.iloc[cnt]["marketStatus"]}  | Trading Date : {market_status_json.iloc[cnt]["tradeDate"]} | {" " * 30} '
                ticker_troll_text = blank_val + market_status_data
                # To set red / green pattern color for bull / bear run
                if market_status_json.iloc[cnt]["market"] == 'Capital Market':
                    if round(market_status_json.iloc[cnt]["variation"], 2) < 0:
                        ticker_label.configure(fg='coral1')
                    else:
                        ticker_label.configure(fg='forest green')
                else:
                    ticker_label.configure(fg='cornsilk2')

                for k in range(len(ticker_troll_text)):
                    # use string slicing to do the trick
                    ticker_text = ticker_troll_text[k:k + text_width]
                    ticker_label.configure(text=ticker_text)
                    root.update()
                    # delay by 0.22 seconds
                    time.sleep(0.22)

    def market_status(self):
        # This method fetch the market hours details - Trading Date,market status - Open,Last,Variation,percent change
        market_status_get_data = self.session.get(self.market_status_url,
                                                  headers=self.headers).json()['marketState']
        fetch_data = pd.DataFrame(market_status_get_data)
        return fetch_data

    def symbol_filter(self, partially_symbol_text):
        """
            This method to fetch list of symbols from NSE stock market as when the user types the partially text
        """
        if partially_symbol_text != '':
            partially_symbol_text = partially_symbol_text.replace(' ', '%20')
            build_symbol_url = f'{self.fetch_symbol_url}{partially_symbol_text}'
            fetch_symbol_data = self.session.get(build_symbol_url,
                                                 headers=self.headers).json()['symbols']
            fetch_data = pd.DataFrame(fetch_symbol_data)
            return fetch_data
        else:
            return ''

    def stock_quote_details(self, stk_q_symbol, keyval):
        # This method fetch stock quote details for the particular symbol

        symbol_quote_get_data = self.session.get(self.symbol_quote_url + stk_q_symbol,
                                                 headers=self.headers).json()[keyval]

        # Json normalize is used to avoid the keys with different sizes [Error :Pandas and JSON ValueError: arrays must all be same length]
        store_data = json_normalize(symbol_quote_get_data)
        return store_data
