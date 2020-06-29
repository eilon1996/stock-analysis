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


class FinanceProduct:

    def __init__(self, symbol=None):
        self.symbol = symbol
        self.stocks_wrong = []
        """
        self.full_name
        self.age
        self.trade_value
        self.price_history
        self.yearly_yield
        self.yealy_dividend
        self.yealy_dividend_per_share
        """
    """
    def check_if_exist(self, symbol):
        try:
            dr.data.get_data_yahoo(stock, start="2020-1-1", end="2020-2-1")
            return True
        except:
            # TODO check why the internat fail every time
            return False
          """

    def check_if_exist(self, symbol):
        try:
            dr.data.get_data_yahoo(symbol, start="2020-1-1", end="2020-2-1")
            return True
        except Exception as e:
            self.stocks_wrong.append([symbol, e])
            return False


    def create_all_symbols(self):
        """
        :return: all the possible stocks symbols up to 4 letters
        :rtype: nested list
        """
        s = time.time()
        # 1 letter
        a = []
        a1 = []
        for i in range(26):
            symbol = chr(65 + i)
            a.append([symbol])
            if self.check_if_exist(symbol):
                a1.append(symbol)
        print("1 letter, ", time.time()-s)


        # 2 letter
        b = np.full((26, 26), "AA")
        b1 = []
        for j in range(26):
            b1.append([])
            for i in range(26):
                symbol = str(a[j][0] + a[i][0])
                b[j, i] = symbol
                if self.check_if_exist(symbol):
                    b1.append(symbol)

        print("2 letter, ", time.time()-s)

        # 3 letter
        c = np.full((26, 26 * 26), "AAA")
        c1 = []
        for j in range(26):
            for i in range(26):
                c1.append([])
                for k in range(26):
                    symbol = str(b[j][i] + a[k][0])
                    c[j, i * 26 + k] = symbol
                    if self.check_if_exist(symbol):
                        c1.append(symbol)

        print("3 letter, ", time.time()-s)

        # 4 letter
        d = np.full((26, 26 ** 3), "AAAA")
        d1 = []
        for j in range(26):


            for i in range(26 ** 2):
                d1.append([])
                for k in range(26):
                    t = str(c[j][i] + a[k][0])
                    d[j, i * 26 + k] = t
                    if self.check_if_exist(symbol):
                        d1.append(symbol)

            print("4 letter: ", j, " ,", time.time()-s)
        return [a1, b1, c1, d1]

    def get_stocks_symbols_to_xlsx(self, file_name, info):
        # info should be nested list with the stocks symbols divided acording to the first letter
        # saving file with existing file name will run-over the old one
        workbook = xlsxwriter.Workbook("C:\\Users\\Uriya\\Desktop\\all stocks symbols.xlsx")
        index = 0
        s = time.time()
        for i in info:
            print(index, time.time() - s)
            worksheet = workbook.add_worksheet()
            for col, stocks_per_letter in enumerate(i):
                for row, symbol in enumerate(stocks_per_letter):
                    worksheet.write(row, col, symbol)
        workbook.close()

        workbook = xlsxwriter.Workbook("C:\\Users\\Uriya\\Desktop\\not stocks symbols.xlsx")
        worksheet = workbook.add_worksheet()
        for index, value in self.stocks_wrong:
            worksheet.write((index)%100, 2*index//100, value[0])
            worksheet.write((index)%100, 2*index//100+1, value[1])




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

    def get_dividends(self, symbol, length=5):
        """
        :param symbol: stock symbol
        :type symbol: str
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
                "path": symbol + "/history?period1=" + str(start) + "&period2=" + str(
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

    # TODO: return price for every month
    # TODO: handling diffrent ways for geting time
    def get_stock_price_data(self, stock, time_length=5, end_time=[]):
        """end time need to be list or tuple for instence [2018,5,28]
        the def return a list of the value of the stock in 1 year gaps
                    incase the stock exist less then the years expected it
                    will return only the years in which its exist"""
        temp = get_relevant_dates(time_length, end_time)
        dates = [temp[-1][0], temp[0][0]]
        df = dr.data.get_data_yahoo(stock, start=dates[0], end=dates[1])
        values = df["Close"].values
        res = []
        for i in range((len(values) - 1) // 250 + 1)[::-1]:
            res.append(float(values[i * 250]))
        return res

    def stock_graph_matplotlib(self, stock):
        df = dr.DataReader(stock, 'yahoo')
        plt.plot_date(df.index, df.Close, '-')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Interesting Graph')
        plt.legend()
        plt.show()

    def show_precise_graph(self, stock, start_date='2015-3-1', end_date='2020-3-1'):
        # YYYY-M-D
        df = dr.data.get_data_yahoo(stock, start=start_date, end=end_date)
        close_price = df["Close"]
        # return close_price

        print(max(close_price), ", ", min(close_price))
        print(df.info())  # let you see the structure of the information

        # figzise adjust the size of the hight and the width
        # if you want to show only one graph, you dont need the second []
        df[["Close", "Open"]].plot(figsize=(5, 5))
        plt.show()

    def get_yearly_yield(self, stock_symbol, time_length=5, end_time=[]):
        date_start_end = translate_date_to_string(time_length, end_time)
        # TODO

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
        for i in range(
                time_length + 1):  # the +1 is for the loop to incloud today end exactly time_length since the end date
            res.append([(str(end_time[0] - i) + "-" + str(end_time[1]) + "-" + str(end_time[2])),
                        (str(end_time[0] - i) + "-" + str(end_time[1]) + "-" + str(end_time[2] + add))])

        return res

fp = FinanceProduct()
info = fp.create_all_symbols()
fp.get_stocks_symbols_to_xlsx("", info)