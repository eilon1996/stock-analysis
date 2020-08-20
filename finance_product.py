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
        self.full_name, self.borsa, self.price = self.get_stock_name_N_borsa()
        self.price_history, self.age = self.get_stock_price_data_and_age()
        self.yield_1y, self.yield_5y = self.get_last_and_full_yield()
        self.yearly_dividend = self.get_dividends()
        self.yearly_dividend_per_share = self.div_in_pecentage()
        try:
            self.last_div = self.yearly_dividend[-1]
        except IndexError:
            print("ERROR: FinanceProduct - __init__ IndexError")
            self.last_div = 0

        basic_data = self.get_basic_data()
        self.avg_volume = basic_data["avg_volume"]
        self.pe_ratio = basic_data["pe_ratio"]
        if basic_data["expense_ratio"] == -1: # thats mean its a stock not etf
            self.product = stock.Stock(symbol, basic_data["market_cap"])
        else:
            self.product = etf.Etf(symbol, basic_data["expense_ratio"])
        self.analyst_score = -1.0  # TODO


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
            div_growth = sumed_div[-1, 0] / sumed_div[0, 0]
            start = len(sumed_div)
            bench_yield = 1
            for i in bench_growth[start:]:
                bench_yield = bench_yield*i
            ratio = div_growth/bench_yield
            estimate_div = []
            for i in bench[:-start]:
                estimate_div.append(i*ratio)
            # need to be check

        total_growth = self.yearly_dividend*(sumed_div+1)

        if type(self.product) == etf.Etf:
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
            res = [sumed_div[i]/self.price_history[i, 0]
                for i in range(min(len(self.price_history[:-1]), len(sumed_div[:-1])))[::-1]]
            res = np.asarray(res[::-1])
        res[np.isinf(res)] = 0
        res[np.isnan(res)] = 0
        np.seterr(divide="raise")
        return res


    def get_stock_name_N_borsa(self, get_price=True):
        url = "https://finance.yahoo.com/quote/"+self.symbol+"/"
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"id": "quote-header-info"})
        name = data.contents[1].contents[0].contents[0].contents[0].text

        #removing the symbol from the name
        try:
            index_s = name.index("(")
            index_e = name.index(")")
            name = name[:index_s]
            name += name[index_e+1:]
        except Exception as e:
            print("ERROR: FinanceProduct - get_stock_name_N_borsa "+ e)
            pass

        borsa = data.contents[1].contents[0].contents[1].contents[0].text
        borsa = str.split(borsa, " ")[0]
        if get_price:
            return name, borsa, self.get_corrent_price(data)

        return name, borsa



    def get_corrent_price(self, data=None):
        if data is None:
            url = "https://finance.yahoo.com/quote/"+self.symbol+"/"
            html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
            soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
            data = soup.find("div", attrs={"id": "quote-header-info"})

        return calculation.convert_string_to_number(data.contents[2].contents[0].contents[0].contents[0].text)


    # also detarmain if its a stock or etf
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
            res["market_cap"] = calculation.convert_string_to_number(res["market_cap"])
            pass

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
        except (IndexError, KeyError) as e:
            print("ERROR: FinanceProduct - get_dividends "+ e)
            return None # TODO: find better solution how to handle no dividends

        index = 0
        for i in range(1, len(dividends["Date"]) - 1)[::-1]:
            if dividends["Date"][i][-4:] != dividends["Date"][i - 1][-4:]:
                index += 1
                div_per_year.append([])
            try:
                div_per_year[index].append(float(dividends['Dividends'][i - 1].replace(' Dividend', '')))
            except ValueError:  
                print("ERROR: FinanceProduct - get_dividends ValueError")
                pass
        # create a full rectangle array by puting 0 in the missing parts
        return np.array(list(itertools.zip_longest(*div_per_year, fillvalue=0))).T


    def get_stock_price_data_and_age(self, time_length=5, end_time=[]):
        """end time need to be list or tuple for instence [2018,5,28]
        the def return a list of the value of the stock in 1 year gaps
                    incase the stock exist less then the years expected it
                    will return only the years in which its exist
        
        start, end = calculation.get_relevant_dates(time_length, end_time)
        df = dr.data.get_data_yahoo(self.symbol, start=start, end=end)
        
        """
        try:
            
            df = dr.data.get_data_yahoo(self.symbol)
        except Exception:
            return [-1,-1,-1,-1,-1], -1
        values = df["Close"].values
        age = round((len(values)/250)*10)/10
        prices = np.zeros((int(np.ceil(age)), 4))
        for i in range(len(prices)):
            for j in range(4):
                try:
                    prices[i, j] = float(values[i * 250 + j*(250-1)//4])
                except IndexError:
                    print("ERROR: FinanceProduct - get_stock_price_data_and_age IndexError")
                    break
        return prices, age


    def show_precise_graph(self, length=5, start_date=None, end_date=None):
        if length==5 and start_date is None and end_date is None:
            df = dr.DataReader(self.symbol, 'yahoo')
        else:
            start_date, end_date = calculation.get_relevant_dates(length, start_date,  end_date)
            df = dr.data.get_data_yahoo(self.symbol, start=start_date, end=end_date)

        # plt is the import of matplotlib
        # plot_date is a method that show the date as the X axe
        plt.plot_date(df.index, df.Close, '-')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(self.symbol)
        # legend more useful when you have several graphs togather
        # it write on each graph line what it represent
        plt.legend()
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
            print("ERROR: FinanceProduct - get_detailed_yield IndexError")
            return None, None

        if len(self.price_history)>=6:
            yield_5y = self.price_history[-1, index] / self.price_history[-6, index]
            return last_yield, yield_5y
        else:
            # in case the prudact is less then 5 years we are going to estimate his yield
            # we compare it's yield to the QQQ and use this ratio to estimate the yield in the missing years
            benchmark = calculation.get_benchmark_yield()
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
    pass