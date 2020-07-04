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
import stock
import etf


class FinanceProduct:


    def __init__(self, symbol):
        self.symbol = symbol.upper()
        # will raise an error if not exist (which one?)
        data = self.get_stock_name()
        self.full_name = data[0]
        self.price = data[1]
        self.price_history, self.age = self.get_stock_price_data_and_age()
        self.yield_1y, self.yield_5y = self.get_last_and_full_yield()
        self.yearly_dividend = self.get_dividends()
        self.yearly_dividend_per_share = self.div_in_pecentage()
        try:
            self.last_div = self.yearly_dividend[-1]
        except IndexError:
            self.last_div = 0

        basic_data = self.get_basic_data()
        self.avg_volume = basic_data["avg_volume"]
        self.pe_ratio = basic_data["pe_ratio"]
        if basic_data["expense_ratio"] == -1: # its a stock not etf
            # TODO: check if its necesery to write stock.Stock or just Stock will do
            self.product = stock.Stock(symbol, basic_data["market_cap"])
        else:
            self.product = etf.Etf(symbol, basic_data["expense_ratio"])
        self.country = "-"  # TODO
        self.analyst_score = -1.0  # TODO


    def show_data(self):

        col_label = ["yield", "dividend", "dividend in %"]
        col_label_stock = ["revenue", "income",  "assents", "free cash", "debt"]
        col_label_etf = ["top holdings", "stocks share",  "bond share", "sectors"]

        row_lable_stock= ["5 years yield", "profitability", "debt/assents", "market_cap", "top_sector", "country",
                          "pe ratio",  "avg volume", "analyst score"]
        """
        data = []
        row_lable = []
        for s in symbols:
            tmp = self.mydb.get_product_by_symbol(s.upper())
            if len(tmp) > 0:
                row = tmp[0]
            else:
                try:
                    self.mydb.insert_product(fp.FinanceProduct(s.upper()))
                except:
                    print("a problem occurred will loading ", s.upper())
                    continue
                row = self.mydb.get_product_by_symbol(s.upper())[0]
            for index in range(max(0, len(row[1]) // 2 - 2), len(row[1]) - 1):
                if row[1][index] == " ":
                    row_lable.append(row[1][:index] + "\n" + row[1][index + 1:])
                    break
                data.append(list(row))

        fig, ax = plt.subplots(2, 1)
        # hide axes
        fig.patch.set_visible(False)

        # full screen
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')

        ax[1].axis('off')
        ax[1].axis('tight')

        data = np.asarray(data)[:, 2:]
        df = pd.DataFrame(data, columns=self.headlines[2:])
        table = ax[1].table(cellText=df.values, colLabels=df.columns, rowLabels=row_lable, cellLoc='center')
        fig.tight_layout()
        table.auto_set_font_size(False)
        table.set_fontsize(10)

        ###############
        for s in symbols:
            df = dr.DataReader(s, 'yahoo')
            ax[0].plot_date(df.index, df.Close, '-')
            plt.plot_date([], [], label=s)

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('  VS  '.join(symbols))
        plt.legend()

        plt.show()
        """

    def total_yield(self):
        # in case it is not a full year we estimate the dividend to be like in the beginning
        sumed_div = self.yearly_dividend_per_share.sum(axis=1)
        index = 3 # check case with less then 4 div a year
        while self.yearly_dividend_per_share[-1, index] == 0:
            index -= 1
        sumed_div[-1] = sumed_div[-1]*len(sumed_div[0])/(1+index)

        if len(sumed_div) < 6:
            bench = calculation.get_benchmark_dividend()
            bench[-1] = bench[-1]*len(bench[0])/(1+index)

            # in case the prudact is less then 5 years we are going to estimate his yield
            # we compare it's yield to the QQQ and use this ratio to estimate the yield in the missing years
            bench_growth = [bench[i+1]/bench[i] for i in range(len(bench)-1)]
            div_growth = self.sumed_div[-1, 0] / self.sumed_div[0, 0]
            start = len(self.sumed_div)
            bench_yield = 1
            for i in bench_growth[start:]:
                bench_yield = bench_yield*i
            ratio = div_growth/bench_yield
            estimate_div = []
            for i in bench[:-start]:
                estimate_div.append(i*ratio)
            # need to be check

        total_growth = self.yearly_dividend*(sumed_div+1)

        if type(self.product) == Etf:
            total_growth = total_growth*(1-self.product.expense_ratio)

        # find a better way to do it
        res = 1
        for i in total_growth:
            res = res*i
        return calculation.two_point_percentage(res)

    def div_in_pecentage(self):
        np.seterr(divide="ignore")
        try:
            res = self.yearly_dividend/self.price_history
        except ValueError:
            sumed_div = self.yearly_dividend.sum(axis=1)
            res = [sumed_div[i]/self.price_history[i,0]
                for i in range(min(len(self.price_history[:-1]), len(sumed_div[:-1])))[::-1]]
            res = np.asarray(res[::-1])
        res[np.isinf(res)] = 0
        res[np.isnan(res)] = 0
        np.seterr(divide="raise")
        return res


    def get_stock_name(self, get_price=True):
        url = "https://finance.yahoo.com/quote/"+self.symbol+"/"
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"id": "quote-header-info"})
        name = data.contents[1].contents[0].contents[0].contents[0].text
        if get_price:
            return name, self.get_corrent_price(data)

        return name



    def get_corrent_price(self, data=None):
        if data is None:
            url = "https://finance.yahoo.com/quote/"+self.symbol+"/"
            html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
            soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
            data = soup.find("div", attrs={"id": "quote-header-info"})

        return calculation.convert_string_to_number(data.contents[2].contents[0].contents[0].text)


    # also detarmain if its a stock or etf
    # TODO: extract the stock name
    def get_basic_data(self):
        """"get the stock name and return avg' volume, PE ratio, yearly dividend"""
        res = {}

        url = "https://finance.yahoo.com/quote/"+self.symbol+"/"
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"id": "quote-summary"})
        res["avg_volume"] = int(calculation.convert_string_to_number(data.contents[0].contents[0].contents[0].contents[7].contents[1].text))
        res["pe_ratio"] = calculation.convert_string_to_number(data.contents[1].contents[0].contents[0].contents[2].contents[1].text)
        res["expense_ratio"] = -1

        if "Expense" in data.contents[1].contents[0].contents[0].contents[6].contents[0].text: # only stocks has "dividend in it"
            res["expense_ratio"] = calculation.convert_string_to_number(data.contents[1].contents[0].contents[0].contents[5].contents[1].text)
        else:
            res["market_cap"] = data.contents[1].contents[0].contents[0].contents[0].contents[1].text
            # TODO extract the number and check the letter (b - billion, ...)

        return res


    def get_dividends(self, length=5):
        """
        :param length: int
        :type length: how many years you want to check
        :return: nested list contain every year dividend
        :rtype: array
        """

        #perhapse move this part to calculation
        now = time.localtime()
        year_start = int(time.mktime((now[0], 1, 1, 1, 1, 1, 1, 1, 1)))
        one_year_in_seconds = 31536000
        start = year_start - length * one_year_in_seconds
        end = int(time.mktime(now))

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
            return None # TODO: find better solution how to handle no dividends

        index = 0
        for i in range(1, len(dividends["Date"]) - 1)[::-1]:
            if dividends["Date"][i][-4:] != dividends["Date"][i - 1][-4:]:
                index += 1
                div_per_year.append([])
            try:
                div_per_year[index].append(float(dividends['Dividends'][i - 1].replace(' Dividend', '')))
            except ValueError:
                pass
        # create a full rectangle array by puting 0 in the missing parts
        return np.array(list(itertools.zip_longest(*div_per_year, fillvalue=0))).T

    # TODO: return price for every qourter (per year and not just 4 month earlier
    # TODO: handling diffrent ways for geting time
    def get_stock_price_data_and_age(self, time_length=5, end_time=[]):
        """end time need to be list or tuple for instence [2018,5,28]
        the def return a list of the value of the stock in 1 year gaps
                    incase the stock exist less then the years expected it
                    will return only the years in which its exist"""
        dates = calculation.get_relevant_dates(time_length, end_time)
        df = dr.data.get_data_yahoo(self.symbol, start=dates[0], end=dates[1])
        values = df["Close"].values
        age = round((len(values)/250)*10)/10
        prices = np.zeros((int(np.ceil(age)), 4))
        for i in range(len(prices)):
            for j in range(4):
                try:
                    prices[i, j] = float(values[i * 250 + j*(250-1)//4])
                except IndexError:
                    break
        return prices, age

    def show_precise_graph(self):
        df = dr.DataReader(self.symbol, 'yahoo')
        plot = plt.subplots(2, 1)[1]
        plot[0].plot_date(df.index, df.Close, '-')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Interesting Graph')
        plt.legend()
        plt.show()

    def show_precise_graph2(self):
        df = dr.DataReader(self.symbol, 'yahoo')
        plt.plot_date(df.index, df.Close, '-')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Interesting Graph')
        plt.legend()
        plt.show()


    # need extra check
    def show_precise_graph1(self, start_date='2015-3-1', end_date='2020-3-1'):
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

    def get_detailed_yield(self):
        """will return the averge yeild, 5 years yeild, yeild comper to the qqq, is the yeild rising or not"""
        # TODO
        growth = [self.price_history[i+1][0]/self.price_history[i][0] for i in range(len(self.price_history)-1)]
        return growth

    def get_last_and_full_yield(self):
        index = 3
        while self.price_history[-1,index] == 0:
            index -= 1
        try:
            last_yield = self.price_history[-1, index] / self.price_history[-2, index]
        except IndexError:
            return None, None

        if len(self.price_history)>=6:
            yield_5y = self.price_history[-1, index] / self.price_history[-6, index]
            return last_yield, yield_5y
        else:
            # in case the prudact is less then 5 years we are going to estimate his yield
            # we compare it's yield to the QQQ and use this ratio to estimate the yield in the missing years
            benchmark = calculation.get_banchmark_yield()
            my_yield = self.price_history[-1, 0] / self.price_history[0, 0]
            start = len(self.price_history)
            bench_yield = 1
            for i in benchmark[start:]:
                bench_yield = bench_yield*i
            ratio = my_yield/bench_yield
            estimate_yield = my_yield
            for i in benchmark[:-start]:
                estimate_yield = estimate_yield*i*ratio

            return last_yield, estimate_yield




if __name__ == '__main__':
    a = FinanceProduct("qqq")
    a.show_precise_graph()
    pass
