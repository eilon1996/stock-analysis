from urllib.error import HTTPError
from pandas.io.html import read_html
from bs4 import BeautifulSoup
from lxml import html
from pandas.util.testing import assert_frame_equal
import lxml
import matplotlib.pyplot as plt
import time
import pandas as pd
import requests
import csv
import numpy as np
import pandas_datareader as dr
import xlsxwriter
import itertools

import calculation


class Etf:

    def __init__(self, symbol, expense_ratio):
        self.symbol = symbol
        self.expense_ratio = expense_ratio
        data = self.get_holdings()
        self.top_holdings = data["top holdings"]
        self.stocks_share = data["stocks share"]
        self.stock_sectors = data["stock sectors"]
        self.bonds_share = data["bond share"]
        self.bond_sectors = data["bond sectors"]
        self.main_sector = self.get_main_sector()  #TODO combine 2 sectors

    def get_etf_profile(self):  # TODO everything
        """"get the stock name and return 2 diamention list with the last 4 years data"""
        url = "https://etfdb.com/etf/" + self.symbol + "/#etf-ticker-profile"
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        data = soup.find("div", attrs={"class": "D(tbrg)"}).contents[14].contents[0].contents[2:]
        free_cash_value = [calculation.convert_string_to_number(x.text) for x in data]
        return free_cash_value

    def get_holdings(self):
        """"get the stock name and return avg' volume, PE ratio, yearly dividend"""

        url = "https://finance.yahoo.com/quote/" + self.symbol + "/holdings?p=" + self.symbol
        html_content = requests.get(url).text  # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")  # Parse the html content
        data = soup.find("section", attrs={"class": "Pb(20px) smartphone_Px(20px) smartphone_Mt(20px)"})
        res = {}

        res["bond share"] = calculation.convert_string_to_number(
            data.contents[0].contents[0].contents[1].contents[1].contents[1].text[:-1])

        if res["bond share"] > 0:
            bond_sectors_data = data.contents[1].contents[1].contents[1].contents
            res["bond sectors"] = [calculation.convert_string_to_number(x.contents[1].text[:-1]) for x in bond_sectors_data[1:]]
        else:
            res["bond sectors"] = []

        res["stocks share"] = calculation.convert_string_to_number(
            data.contents[0].contents[0].contents[1].contents[0].contents[1].text[:-1])

        if res["stocks share"] > 0:
            sectors_share_data = data.contents[0].contents[1].contents[1].contents
            res["stock sectors"] = [calculation.convert_string_to_number(x.contents[2].text[:-1]) for x in sectors_share_data[1:]]
        else:
            res["stock sectors"] = []

        top_holdings_data = data.contents[3].contents[1].contents[1].contents
        # top holding example [[microsoft corp, MSFT, 11.76], [apple inc, AAPL, 11.09] ... ]
        res["top holdings"] = [[x.contents[0].text, x.contents[1].text, calculation.convert_string_to_number(x.contents[2].text[:-1])]
            for x in top_holdings_data]

        return res

    def get_main_sector(self):
        if self.bonds_share > self.stocks_share:
            # for easier saving and navigation in the sectors, we index the bonds after the stocks and not in parallel 
            # for better understanding look at all_sectors in calculation
            return self.bond_sectors.index(max(self.bond_sectors)) + len(calculation.stock_sectors)
        return self.stock_sectors.index(max(self.stock_sectors))
            