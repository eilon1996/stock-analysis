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


class Stock:

    def __init__(self, symbol, market_cap):
        self.symbol = symbol
        self.market_cap = int(market_cap)
        data = self.get_revenue_n_net_income()
        self.revenue = data[0]#is relevant?
        self.income = data[1]#is relevant?
        # check zero division
        self.profitability = calculation.two_point_percentage(self.revenue[-1]/self.income[-1])
        data = self.get_assent_n_debt()
        self.assents = data[0]#is relevant?
        self.debt = data[1]#is relevant?
        self.debt_percentage = calculation.two_point_percentage(self.debt[-1]/self.assents[-1])
        self.free_cash = self.get_free_cash()#is relevant?
        self.main_sector = self.get_main_sector()

    def get_revenue_n_net_income(self):
        """"get the stock name and return 2 diamention list with the last 4 years data"""

        url = "https://finance.yahoo.com/quote/"+self.symbol+"/financials?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"class": "D(tbrg)"})
        data_content_revenue_income = [data.contents[0], data.contents[10]]
        revenue = data_content_revenue_income[0].contents[0].contents
        revenue_value = [calculation.convert_string_to_number(x.string) for x in revenue[2:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-201
        income_net = data_content_revenue_income[1].contents[0].contents
        income_net_value = [calculation.convert_string_to_number(x.string) for x in income_net[2:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-2016
        # print(revenue_value, income_net_value)
        return [revenue_value, income_net_value]


    def get_assent_n_debt(self):
        """"get the stock name and return 2 diamention list with the last 4 years data"""

        url = "https://finance.yahoo.com/quote/"+self.symbol+"/balance-sheet?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"class": "D(tbrg)"})
        data_content_assent_debt = [data.contents[0], data.contents[11]]
        assent = data_content_assent_debt[0].contents[0].contents
        assent_value = [calculation.convert_string_to_number(x.string) for x in assent[1:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-201
        debt = data_content_assent_debt[1].contents[0].contents
        debt_value = [calculation.convert_string_to_number(x.string) for x in debt[1:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-2016
        return [assent_value, debt_value]

    def get_free_cash(self):
        """"get the stock name and return 2 diamention list with the last 4 years data"""
        url = "https://finance.yahoo.com/quote/"+self.symbol+"/cash-flow?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"class": "D(tbrg)"}).contents[14].contents[0].contents[2:]
        free_cash_value = [calculation.convert_string_to_number(x.text) for x in data]
        return free_cash_value

    def get_main_sector(self):
        
        url = "https://finance.yahoo.com/quote/"+self.symbol+"/profile?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"class": "qsp-2col-profile Pt(10px) smartphone_Pt(20px) Lh(1.7)"})
        sector = data.contents[1].contents[1].contents[4].text
        return calculation.get_sectors_index(sector)