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


#import stock
#import etf
#import partfolio
#import database_handler

class FinanceProduct:

    def __init__(self, symbol):
        self.symbol = symbol
        self.full_name = self.get_stock_name()
   #     self.age
   #     self.trade_value
        self.price_history = self.get_stock_price_data()
        self.yearly_yield = self.get_yearly_yield()
        self.yearly_dividend = self.get_dividends()


        # fix so the dividend will match the price
        # option - run on the div and from there which price you need
        #self.yealy_dividend_per_share = [self.yearly_dividend[round(i*dividends_per_quorter)]/self.price_history[i]\
        #                                        for i in range(len(self.yearly_dividend))]
        basic_data = self.get_basic_data()
        self.average_value = basic_data["avg_value"]
        self.pe_ratio = basic_data["pe_ratio"]
        if basic_data["expense_ratio"] == -1: # its a stock not etf
            # TODO: check if its necesery to write stock.Stock or just Stock will do
            self.product = stock.Stock(symbol, basic_data[market_cap])
        else:
            self.product = etf.Etf(symbol, basic_data["expense_ratio"])

    def get_stock_name(self):
        url = "https://finance.yahoo.com/quote/"+self.symbol+"/"
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"id": "quote-header-info"})

        return data.contents[1].contents[0].contents[0].contents[0].text


    # also detarmain if its a stock or etf
    # TODO: extract the stock name
    def get_basic_data(self):
        """"get the stock name and return avg' volume, PE ratio, yearly dividend"""
        res = {}

        url = "https://finance.yahoo.com/quote/"+self.symbol+"/"
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"id": "quote-summary"})
        res["avg_volume"] = self.convert_string_to_number(data.contents[0].contents[0].contents[0].contents[7].contents[1].text)
        res["pe_ratio"] = self.convert_string_to_number(data.contents[1].contents[0].contents[0].contents[2].contents[1].text)
        res["expense_ratio"] = -1

        if "Expense" in data.contents[1].contents[0].contents[0].contents[6].contents[0].text: # only stocks has "dividend in it"
            res["expense_ratio"] = self.convert_string_to_number(data.contents[1].contents[0].contents[0].contents[5].contents[1].text.split("(")[1][:-2])
        else:
            res["market_cap"] = data.contents[1].contents[0].contents[0].contents[0].contents[1].text
            # TODO extract the number and check the letter (b - billion, ...)

        return res

    def check_if_exist(self):
        try:
            dr.data.get_data_yahoo(self.symbol, start="2020-1-1", end="2020-2-1")
            return True
        except Exception as e:
            self.stocks_wrong.append([self.symbol, e])
            return False


    @staticmethod # consider adding to other methods
    def convert_string_to_number(number):
        """"for dealing with representing that inclouds ','  like  10,000
            relevent for extarcting data from HTML"""
        try:
            minus = False
            if number[0] == "-":
                minus = True
                number = number[1:]

            divided_number = number.split(",")
            res = 0
            for i in divided_number:
                res = res * 1000 + float(i)
            if minus: res = -1 * res
            return res
        except ValueError:
            return -1

    def get_dividends(self, length=5):
        """
        :param length: int
        :type length: how many years you want to check
        :return: nested list contain every year dividend
        :rtype: list
        """
        year_start = int(time.mktime((time.localtime()[0], 1, 1, 1, 1, 1, 1, 1, 1)))
        one_year = year_start - int(time.mktime((time.localtime()[0] - 1, 1, 1, 1, 1, 1, 1, 1, 1)))
        start = year_start - length * one_year
        end = year_start
        # to get dividends not in full years
        # now = time.localtime()
        # start = int(time.mktime((now[0]-length,) + now[1:]))
        # end = int(time.mktime(now))

        hdrs = {"authority": "finance.yahoo.com",
                "method": "GET",
                "path": self.symbol + "/history?period1=" + str(start) + "&period2=" + str(
                    end) + "&interval=div%7Csplit&filter=div&frequency=1d",
                "scheme": "https",
                "accept": "text/html,application/xhtml+xml",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "cookie": "cookies",
                "dnt": "1",
                "pragma": "no-cache",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": '?1',
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0"}

        url = "https://finance.yahoo.com/quote/" + hdrs["path"]
        # scrape the dividend history table from Yahoo Finance
        table = html.fromstring(requests.get(url, headers=hdrs).content).xpath('//table')
        dividends = pd.read_html(lxml.etree.tostring(table[0], method='xml'))[0]
        # clean the dividend history table
        try:
            div_per_year = [[float(dividends['Dividends'][len(dividends["Date"]) - 2].replace(' Dividend', ''))]]
        except (IndexError, KeyError):
            return None

        index = 0
        for i in range(1, len(dividends["Date"]) - 1)[::-1]:
            if dividends["Date"][i][-4:] != dividends["Date"][i - 1][-4:]:
                index += 1
                div_per_year.append([])
            div_per_year[index].append(float(dividends['Dividends'][i - 1].replace(' Dividend', '')))
        # print(div_per_year)
        return div_per_year

    # TODO: return price for every qourter (per year and not just 4 month earlier
    # TODO: handling diffrent ways for geting time
    def get_stock_price_data(self, time_length=5, end_time=[]):
        """end time need to be list or tuple for instence [2018,5,28]
        the def return a list of the value of the stock in 1 year gaps
                    incase the stock exist less then the years expected it
                    will return only the years in which its exist"""
        temp = self.get_relevant_dates(time_length, end_time)
        dates = [temp[-1][0], temp[0][0]]
        df = dr.data.get_data_yahoo(self.symbol, start=dates[0], end=dates[1])
        values = df["Close"].values
        res = []
        for i in range((len(values) - 1) // 250)[::-1]:
            res.append([])
            for j in range(4):
                res[i].append(float(values[i * 250 + j*250//4]))
        return res

    def stock_graph_matplotlib(self, stock):
        df = dr.DataReader(stock, 'yahoo')
        plt.plot_date(df.index, df.Close, '-')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Interesting Graph')
        plt.legend()
        plt.show()

    # need extra check
    def show_precise_graph(self, start_date='2015-3-1', end_date='2020-3-1'):
        # YYYY-M-D
        df = dr.data.get_data_yahoo(self.symbol, start=start_date, end=end_date)
        close_price = df["Close"]
        # return close_price

        print(max(close_price), ", ", min(close_price))
        print(df.info())  # let you see the structure of the information

        # figzise adjust the size of the hight and the width
        # if you want to show only one graph, you dont need the second []
        df[["Close", "Open"]].plot(figsize=(5, 5))
        plt.show()

    def get_yearly_yield(self):
        """will return the averge yeild, 5 years yeild, yeild comper to the qqq, is the yeild rising or not"""
        # TODO
        growth = [self.price_history[i+1]/self.price_history[i] for i in range(len(self.price_history)-1)]
        return growth


    def get_relevant_dates(self, time_length, end_time):
        """return a list of pers of lists dates in string for the relevent time
            example: [[2020-3-10, 2020-3-5], [2019-3-10, 2019-3-5], [2018-3-10, 2018-3-5], [2017-3-10, 2017-3-5], [2016-3-10, 2016-3-5]]
         """
        if len(end_time) == 0:
            end_time = time.localtime(time.time())[:3]
        add = 5
        if end_time[2] > 24:
            end_time = (end_time[0], end_time[1], end_time[2] - 5)
        res = []
        for i in range(time_length + 1):  # the +1 is for the loop to incloud today end exactly time_length since the end date
            res.append([(str(end_time[0] - i) + "-" + str(end_time[1]) + "-" + str(end_time[2])),
                        (str(end_time[0] - i) + "-" + str(end_time[1]) + "-" + str(end_time[2] + add))])

        return res

fp = FinanceProduct("MA")

#info = fp.create_all_symbols()
#fp.get_stocks_symbols_to_xlsx("", info)