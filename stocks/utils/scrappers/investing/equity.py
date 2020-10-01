import pandas as pd
import requests
import datetime
import numpy as np

from .income_statement import IncomeStatement
from .balance_sheet import BalanceSheet
from .ratios import Ratios

symbols = {
    "BIG":      "bigben-interactive",
    "BOI":      "boiron",
    "MSFT":     "microsoft-corp",
    "NACON":    "nacon-sa",
    "KPSN":     "kinepolis-group",
    "VMX":      "inside-secure-sa"
}

http_headers = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

class Equity:
    cached_income_statement = None
    cached_balance_sheet = None
    cached_ratios = None

    def __init__(self, symbol):
        symbol = symbol.upper().split(".")[0]
        if not symbol in symbols.keys():
            raise Exception("Symbol not found in dict")
        self.url = f"https://www.investing.com/equities/{symbols[symbol]}"

    def income_statement(self):
        if not self.cached_income_statement:
            request = requests.get(self.url + "-income-statement", headers=http_headers)
            dfs = pd.read_html(request.text)
            index = 0
            for i in range(len(dfs)):
                if len(dfs[i].index) == 53:
                    index = i
                    break
            columns = np.squeeze(dfs[index].tail(1).values.tolist())
            columns = columns[1:]
            for i in range(len(columns)):
                columns[i] = datetime.datetime.strptime(columns[i], "%Y%d/%m").strftime("%d/%m/%Y")
            pretty = dfs[index][:-1]
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
            self.cached_income_statement = IncomeStatement(pretty)
        return self.cached_income_statement

    def balance_sheet(self):
        if not self.cached_balance_sheet:
            request = requests.get(self.url + "-balance-sheet", headers=http_headers)
            dfs = pd.read_html(request.text)
            index = 0
            for i in range(len(dfs)):
                if len(dfs[i].index) == 53:
                    index = i
                    break
            columns = np.squeeze(dfs[index].tail(1).values.tolist())
            columns = columns[1:]
            for i in range(len(columns)):
                columns[i] = datetime.datetime.strptime(columns[i], "%Y%d/%m").strftime("%d/%m/%Y")
            # remove the last row as it will be used as column name
            pretty = dfs[index][:-1]
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
            self.cached_balance_sheet = BalanceSheet(pretty)
        return self.cached_balance_sheet

    def ratios(self):
        if not self.cached_ratios:
            request = requests.get(self.url + "-ratios", headers=http_headers)
            dfs = pd.read_html(request.text)
            pretty = pd.DataFrame(dfs[1].values, columns=["Name", "Company", "Industry"])
            # use first column values as index
            pretty.index = pretty.iloc[:, 0]
            # remove first column
            pretty = pretty.drop(columns=["Name"])
            self.cached_ratios = Ratios(pretty)
        return self.cached_ratios
