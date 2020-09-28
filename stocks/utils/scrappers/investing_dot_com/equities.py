import pandas as pd
import requests
import datetime
import numpy as np

symbols = {
    "MSFT": "microsoft-corp",
    "KPSN": "kinepolis-group"
}

http_headers = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

url_prefix = "https://www.investing.com/equities/"

class base:
    url = ""
    data = None

    def __init__(self, symbol, url_suffix):
        symbol = symbol.upper().split('.')[0]
        if not symbol in symbols.keys():
            raise Exception("Symbol not found in dict")
        self.url = f"{url_prefix}{symbols[symbol]}{url_suffix}"

class income_statement(base):
    request = None
    data = None

    def __init__(self, symbol):
        super().__init__(symbol, "-income-statement")
        request = requests.get(self.url, headers=http_headers)
        dfs = pd.read_html(request.text)
        columns = np.squeeze(dfs[1].tail(1).values.tolist())
        for i in range(1,len(columns)):
            columns[i] = datetime.datetime.strptime(columns[i], '%Y%d/%m').strftime('%d/%m/%Y')
        pretty = dfs[1][:-1]
        pretty.columns = columns
        pretty = pretty.drop(1).drop(7)
        self.data = pretty.reset_index(drop=True)

class balance_sheet(base):
    request = None
    data = None

    def __init__(self, symbol):
        super().__init__(symbol, "-balance-sheet")
        request = requests.get(self.url, headers=http_headers)
        dfs = pd.read_html(request.text)
        columns = np.squeeze(dfs[1].tail(1).values.tolist())
        for i in range(1,len(columns)):
            columns[i] = datetime.datetime.strptime(columns[i], '%Y%d/%m').strftime('%d/%m/%Y')
        pretty = dfs[1][:-1]
        pretty.columns = columns
        pretty = pretty.drop(1).drop(12).drop(23).drop(31).drop(39)
        self.data = pretty.reset_index(drop=True)

    def total_common_shares_outstanding(self):
        return int(float(self.data.iat[45, 1])*1e6)

class ratios(base):

    def __init__(self, symbol):
        super().__init__(symbol, "-ratios")
        request = requests.get(self.url, headers=http_headers)
        dfs = pd.read_html(request.text)
        dfs[3] = dfs[3][1:]
        dfs[5] = dfs[5][1:]
        self.data = pd.DataFrame(pd.concat(dfs[2:10]).values, columns=['Name', 'Compagny', 'Industry'])
