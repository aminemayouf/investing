import pandas as pd
import time
import datetime
import numpy as np
import os
import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .income_statement import IncomeStatement
from .balance_sheet import BalanceSheet
from .cash_flow import CashFlow
from .ratios import Ratios

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-extensions")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)

def click_annual():
    annual_btn = driver.find_element_by_link_text("Annual")
    driver.execute_script("arguments[0].click();", annual_btn)
    time.sleep(0.33)

class Equity:
    url = None

    def __init__(self, ISIN):
        ISIN = ISIN.upper()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        csv_path = f"{dir_path}/equities/{ISIN[0:2]}.csv"
        if not os.path.exists(csv_path):
            raise Exception("Equities in this country are not supported yet")
        equities = pd.read_csv(csv_path)
        for index, equity in equities.iterrows():
            if equity.ISIN == ISIN:
                self.url = equity.Url
                break
        if not self.url:
            raise Exception("ISIN not found")

        self.income_statement = self.__income_statement()
        self.balance_sheet = self.__balance_sheet()
        self.cash_flow = self.__cash_flow()
        self.ratios = self.__ratios()

    def __income_statement(self):
        driver.get(f"{self.url}-income-statement")

        # get name
        self.name = driver.find_elements_by_xpath("//section[@id='leftColumn']/div[@class='instrumentHead']/h1")[0].text
        # get price
        self.price = float(driver.find_element_by_id("last_last").text)

        click_annual()

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        div = soup.select_one("div#rrtable")
        table = pd.read_html(str(div))[0]
        # rename colums
        for i in range(1, len(table.columns)):
            column_name = table.columns[i]
            table = table.rename(columns={column_name: datetime.datetime.strptime(column_name, "%Y%d/%m").strftime("%d/%m/%Y")})
        # use first column values as index
        table.index = table.iloc[:, 0]
        table.index.name = ""
        # remove first column
        table = table.drop(columns=["Period Ending:"])
        # set non numeric values to NaN
        table = table.apply(pd.to_numeric, errors="coerce")
        # drop rows when all cells are set to NaN
        table = table.dropna(how="all")
        # values are actually in millions
        table *= 1e6
        return IncomeStatement(table)

    def __balance_sheet(self):
        driver.get(f"{self.url}-balance-sheet")

        click_annual()

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        div = soup.select_one("div#rrtable")
        table = pd.read_html(str(div))[0]
        # rename colums
        for i in range(1, len(table.columns)):
            column_name = table.columns[i]
            table = table.rename(columns={column_name: datetime.datetime.strptime(column_name, "%Y%d/%m").strftime("%d/%m/%Y")})
        # use first column values as index
        table.index = table.iloc[:, 0]
        table.index.name = ""
        # remove first column
        table = table.drop(columns=["Period Ending:"])
        # set non numeric values to NaN
        table = table.apply(pd.to_numeric, errors="coerce")
        # drop rows when all cells are set to NaN
        table = table.dropna(how="all")
        # values are actually in millions
        table *= 1e6
        return BalanceSheet(table)

    def __cash_flow(self):
        driver.get(f"{self.url}-cash-flow")

        click_annual()

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        div = soup.select_one("div#rrtable")
        table = pd.read_html(str(div))[0]
        # rename colums
        for i in range(1, len(table.columns)):
            column_name = table.columns[i][0]
            table = table.rename(columns={column_name: datetime.datetime.strptime(column_name, "%Y%d/%m").strftime("%d/%m/%Y")})
        # use first column values as index
        table.index = table.iloc[:, 0]
        table.index.name = ""
        # remove first column
        table = table.drop(columns=["Period Ending:"])
        # set non numeric values to NaN
        table = table.apply(pd.to_numeric, errors="coerce")
        # drop rows when all cells are set to NaN
        table = table.dropna(how="all")
        # values are actually in millions
        table *= 1e6
        return CashFlow(table)

    def __ratios(self):
        driver.get(f"{self.url}-ratios")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        div = soup.select_one("table#rrTable")
        table = pd.read_html(str(div))[0]
        # use first column values as index
        table.index = table.iloc[:, 0]
        table.index.name = ""
        # remove first column
        table = table.drop(columns=["Name"])
        # drop rows when all cells are set to NaN
        table = table.dropna(how="all")
        return Ratios(table)

    def market_cap(self):
        return self.balance_sheet.total_common_shares_outstanding()[0] * self.price
