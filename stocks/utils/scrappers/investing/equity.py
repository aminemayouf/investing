import pandas as pd
import requests
import datetime
import numpy as np

from .income_statement import IncomeStatement
from .balance_sheet import BalanceSheet
from .ratios import Ratios

symbols = {
    "MSFT": "microsoft-corp",
    "KPSN": "kinepolis-group"
}

http_headers = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

class Equity:
    def __init__(self, symbol):
        symbol = symbol.upper().split(".")[0]
        if not symbol in symbols.keys():
            raise Exception("Symbol not found in dict")
        self.url = f"https://www.investing.com/equities/{symbols[symbol]}"

    def income_statement(self):
        request = requests.get(self.url + "-income-statement", headers=http_headers)
        dfs = pd.read_html(request.text)
        columns = np.squeeze(dfs[1].tail(1).values.tolist())
        columns = columns[1:]
        for i in range(len(columns)):
            columns[i] = datetime.datetime.strptime(columns[i], "%Y%d/%m").strftime("%d/%m/%Y")
        pretty = dfs[1][:-1]
        # use first column values as index
        pretty.index = pretty.iloc[:, 0]
        pretty.index.name = ""
        # remove first column
        pretty = pretty.drop(columns=[0])
        pretty.columns = columns
        # set non numeric values to NaN
        pretty = pretty.apply(pd.to_numeric, errors="coerce")
        # drop rows when all cells are set to NaN
        pretty = pretty.dropna(how="all")
        # values are actually in millions
        pretty *= 1e6
        return IncomeStatement(pretty)

    def balance_sheet(self):
        request = requests.get(self.url + "-balance-sheet", headers=http_headers)
        dfs = pd.read_html(request.text)
        columns = np.squeeze(dfs[1].tail(1).values.tolist())
        columns = columns[1:]
        for i in range(len(columns)):
            columns[i] = datetime.datetime.strptime(columns[i], "%Y%d/%m").strftime("%d/%m/%Y")
        # remove the last row as it will be used as column name
        pretty = dfs[1][:-1]
        # use first column values as index
        pretty.index = pretty.iloc[:, 0]
        pretty.index.name = ""
        # remove first column
        pretty = pretty.drop(columns=[0])
        pretty.columns = columns
        # set non numeric values to NaN
        pretty = pretty.apply(pd.to_numeric, errors="coerce")
        # drop rows when all cells are set to NaN
        pretty = pretty.dropna(how="all")
        # values are actually in millions
        pretty *= 1e6
        return BalanceSheet(pretty)

    def ratios(self):
        request = requests.get(self.url + "-ratios", headers=http_headers)
        dfs = pd.read_html(request.text)
        dfs[3] = dfs[3][1:]
        dfs[5] = dfs[5][1:]
        pretty = pd.DataFrame(pd.concat(dfs[2:10]).values, columns=["Name", "Company", "Industry"])
        # use first column values as index
        pretty.index = pretty.iloc[:, 0]
        # remove first column
        pretty = pretty.drop(columns=["Name"])
        return Ratios(pretty)
