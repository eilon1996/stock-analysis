from urllib.error import HTTPError

import lxml
import matplotlib.pyplot as plt
import time
import pandas as pd
import requests
import csv
import numpy as np
import pandas_datareader as dr
from pandas.io.html import read_html
from bs4 import BeautifulSoup
from lxml import html
from pandas.util.testing import assert_frame_equal
import xlsxwriter

def get_relevant_dates(time_length, end_time):
    """return a list of pers of lists dates in string for the relevent time
        example: [[2020-3-10, 2020-3-5], [2019-3-10, 2019-3-5], [2018-3-10, 2018-3-5], [2017-3-10, 2017-3-5], [2016-3-10, 2016-3-5]]
     """
    if len(end_time) == 0:
        end_time = time.localtime(time.time())[:3]
    add = 5
    if end_time[2]>24:
        end_time = (end_time[0], end_time[1], end_time[2]-5)
    res = []
    for i in range(time_length+1):     # the +1 is for the loop to incloud today end exactly time_length since the end date
        res.append([(str(end_time[0] - i) + "-" + str(end_time[1]) + "-" + str(end_time[2])), (str(end_time[0] - i) + "-" + str(end_time[1]) + "-" + str(end_time[2]+add))])

    return res


def translate_date_to_string(time_length=5, end_time=[]):
    if len(end_time) == 0:
        end_time = time.localtime(time.time())[:3]
    end_date_str = "-".join(str(x) for x in end_time)
    start_date_str = str(end_time[0] - time_length) + "-" + str(end_time[1]) + "-" + str(end_time[2])
    return [start_date_str, end_date_str]


def convert_string_to_number(number):
    """"for dealing with representing that inclouds ','  like  10,000 """
    try:
        minus = False
        if number[0] == "-":
            minus = True
            number = number[1:]

        divided_number = number.split(",")
        res = 0
        for i in divided_number:
            res = res*1000+float(i)
        if minus: res = -1*res
        return res
    except ValueError:
        return -1

def get_dividends(symbol, length=5):
    """
    :param symbol: stock symbol
    :type symbol: str
    :param length: int
    :type length: how many years you want to check
    :return: nested list contain every year dividend
    :rtype: list
    """
    year_start = int(time.mktime((time.localtime()[0],1,1,1,1,1,1,1,1)))
    one_year = year_start - int(time.mktime((time.localtime()[0]-1,1,1,1,1,1,1,1,1)))
    start = year_start - length*one_year
    end = year_start
   # to get dividends not in full years
   # now = time.localtime()
   # start = int(time.mktime((now[0]-length,) + now[1:]))
   # end = int(time.mktime(now))

    hdrs = {"authority": "finance.yahoo.com",
            "method": "GET",
            "path": symbol+"/history?period1="+str(start)+"&period2="+str(end)+ "&interval=div%7Csplit&filter=div&frequency=1d",
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
        div_per_year = [[float(dividends['Dividends'][len(dividends["Date"])-2].replace(' Dividend', ''))]]
    except (IndexError, KeyError):
        return None

    index = 0
    for i in range(1, len(dividends["Date"])-1)[::-1]:
        if dividends["Date"][i][-4:] != dividends["Date"][i-1][-4:]:
            index += 1
            div_per_year.append([])
        div_per_year[index].append(float(dividends['Dividends'][i-1].replace(' Dividend', '')))
    #print(div_per_year)
    return div_per_year

def get_stock_price_data(stock, time_length=5, end_time=[]):
    """end time need to be list or tuple for instence [2018,5,28]
    the def return a list of the value of the stock in 1 year gaps
                incase the stock exist less then the years expected it will return only the years in which its exist
    adventage faster becouse its enter the internet only 1 time"""
    temp = get_relevant_dates(time_length, end_time)
    dates = [temp[-1][0], temp[0][0]]
    df = dr.data.get_data_yahoo(stock, start=dates[0], end=dates[1])
    values = df["Close"].values
    res = []
    for i in range((len(values)-1)//250+1)[::-1]:
        res.append(float(values[i*250]))
    return res

a = get_stock_price_data("g")


def get_stock_price_data2(stock, time_length=5, end_time=[]):
    """end time need to be list or tuple for instence [2018,5,28]
    the def return a list of the value of the stock in 1 year gaps
                incase the stock exist less then the years expected it will return only the years in which its exist
    a dis-adventage is that the def get the internt for every year"""
    dates = get_relevant_dates(time_length, end_time)
    res = []
    for i in range(time_length+1):
        try:
            df = dr.data.get_data_yahoo(stock, start=dates[i][0], end=dates[i][1])
            res.append(df["Close"].values[0])
        except:
            print("failed")
            break
    return res


def get_revenue_n_net_income(stock_symbol):
    """"get the stock name and return 2 diamention list with the last 4 years data"""

    url = "https://finance.yahoo.com/quote/"+stock_symbol+"/financials?p="+stock_symbol
    html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
    soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
    data = soup.find("div", attrs={"class": "D(tbrg)"})
    data_content_revenue_income = [data.contents[0], data.contents[10]]
    revenue = data_content_revenue_income[0].contents[0].contents
    revenue_value = [convert_string_to_number(x.string) for x in revenue[2:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-201
    income_net = data_content_revenue_income[1].contents[0].contents
    income_net_value = [convert_string_to_number(x.string) for x in income_net[2:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-2016
    # print(revenue_value, income_net_value)
    return [revenue_value, income_net_value]



def get_assent_n_debt(stock_symbol):
    """"get the stock name and return 2 diamention list with the last 4 years data"""

    url = "https://finance.yahoo.com/quote/"+stock_symbol+"/balance-sheet?p="+stock_symbol
    html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
    soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
    data = soup.find("div", attrs={"class": "D(tbrg)"})
    data_content_assent_debt = [data.contents[0], data.contents[11]]
    assent = data_content_assent_debt[0].contents[0].contents
    assent_value = [convert_string_to_number(x.string) for x in assent[1:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-201
    debt = data_content_assent_debt[1].contents[0].contents
    debt_value = [convert_string_to_number(x.string) for x in debt[1:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-2016
    return [assent_value, debt_value]


def get_free_cash(stock_symbol):
    """"get the stock name and return 2 diamention list with the last 4 years data"""
    url = "https://finance.yahoo.com/quote/"+stock_symbol+"/cash-flow?p="+stock_symbol
    html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
    soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
    data = soup.find("div", attrs={"class": "D(tbrg)"}).contents[14].contents[0].contents[2:]
    free_cash_value = [convert_string_to_number(x.text) for x in data]
    return free_cash_value


def get_holdings(etf_symbol):
    """"get the stock name and return avg' volume, PE ratio, yearly dividend"""

    url = "https://finance.yahoo.com/quote/"+etf_symbol+"/holdings?p="+etf_symbol
    html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
    soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
    data = soup.find("section", attrs={"class": "Pb(20px) smartphone_Px(20px) smartphone_Mt(20px)"})

    stocks_share = convert_string_to_number(data.contents[0].contents[0].contents[1].contents[0].contents[1].text[:-1])

    bond_share = convert_string_to_number(data.contents[0].contents[0].contents[1].contents[1].contents[1].text[:-1])

    if bond_share>10:
        bond_sectors_data = data.contents[1].contents[1].contents[1].contents
        bond_sectors = [convert_string_to_number(x.contents[1].text[:-1]) for x in bond_sectors_data[1:]]

    sectors_share_data = data.contents[0].contents[1].contents[1].contents
    sectors_share = [convert_string_to_number(x.contents[2].text[:-1]) for x in sectors_share_data[1:]]

    top_holdings_data = data.contents[3].contents[1].contents[1].contents
    # top holding example [[microsoft corp, MSFT, 11.76], [apple inc, AAPL, 11.09] ... ]
    top_holdings = [[x.contents[0].text, x.contents[1].text, convert_string_to_number(x.contents[2].text[:-1])]for x in top_holdings_data]

    return 1


def get_basic_data(stock_symbol):
    """"get the stock name and return avg' volume, PE ratio, yearly dividend"""

    url = "https://finance.yahoo.com/quote/"+stock_symbol+"/"
    html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
    soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
    data = soup.find("div", attrs={"id": "quote-summary"})
    avg_volume = convert_string_to_number(data.contents[0].contents[0].contents[0].contents[7].contents[1].text)
    pe_ratio = convert_string_to_number(data.contents[1].contents[0].contents[0].contents[2].contents[1].text)
    yearly_dividend = 0
    if "Dividend" in data.contents[1].contents[0].contents[0].contents[5].contents[0].text: # only stocks has "dividend in it"
        yearly_dividend = convert_string_to_number(data.contents[1].contents[0].contents[0].contents[5].contents[1].text.split("(")[1][:-2])
    else:
        get_holdings(stock_symbol)

    # print([avg_volume, pe_ratio, yearly_dividend])
    return [avg_volume, pe_ratio, yearly_dividend]


get_basic_data("lqd")

def stock_graph_matplotlib(stock):
    df = dr.DataReader(stock, 'yahoo')
    plt.plot_date(df.index, df.Close, '-')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Interesting Graph')
    plt.legend()
    plt.show()



def get_holdings(stock_symbol): # TODO everything
    """"get the stock name and return 2 diamention list with the last 4 years data"""
    url = "https://finance.yahoo.com/quote/"+stock_symbol+"/holdings?p="+stock_symbol
    html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
    soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
    data = soup.find("div", attrs={"class": "D(tbrg)"}).contents[14].contents[0].contents[2:]
    free_cash_value = [convert_string_to_number(x.text) for x in data]
    return free_cash_value




def get_etf_profile(etf_symbol): # TODO everything
    """"get the stock name and return 2 diamention list with the last 4 years data"""
    url = "https://etfdb.com/etf/"+etf_symbol+"/#etf-ticker-profile"
    soup = BeautifulSoup(requests.get(url).text, "lxml")      # Parse the html content ( # Make a GET request to fetch the raw HTML content , )
    data = soup.find("div", attrs={"class": "D(tbrg)"}).contents[14].contents[0].contents[2:]
    free_cash_value = [convert_string_to_number(x.text) for x in data]
    return free_cash_value


def stock_graph_panda(stock, start_date='2015-3-1', end_date='2020-3-1'):
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

def get_yearly_yield(stock_symbol, time_length=5, end_time=[]):
    date_start_end = translate_date_to_string(time_length, end_time)
    # TODO

# half work
# print all 2 letters , and all 1 letter in diff list, for 3 its open anther un nesesery nested list
def get_all_available_stocks_symbols(symbol = "", length = 2):
    if length <=0:
        try:
            #get_stock_price_data(symbol)
            return symbol
        except:
            return None

    stocks = []
    for i in range(ord("a"), ord("z")+1):
        temp = get_all_available_stocks_symbols(symbol+chr(i), length-1)
        if temp is not None:
            stocks.append(temp)
    # for shorter stocks' symbols
    if len(symbol) == 0:
        stocks.append(get_all_available_stocks_symbols(symbol, length-1))
    return stocks


def get_all_available_stocks_symbols_fast(symbol = "", length = 2):
    if length <=0:
        try:
           # dr.data.get_data_yahoo(stock, start="2020-1-1", end="2020-2-1")
            return symbol
        except:
            return None

    try:
   #     dr.data.get_data_yahoo(stock, start="2020-1-1", end="2020-2-1")
        stocks.append(symbol)
    except:
        pass
    stocks = []
    for i in range(ord("a"), ord("z")+1):
        temp = get_all_available_stocks_symbols_fast(symbol+chr(i), length-1)
        if type(temp) == list:
            stocks.extend(temp)
        elif temp is not None:
            stocks.append(temp)
    # for shorter stocks' symbols
    if len(symbol) == 0:
        temp = get_all_available_stocks_symbols_fast(symbol+chr(i), length-1)
        if type(temp) == list:
            stocks.extend(temp)
        elif temp is not None and len(temp)>0:
            stocks.append(temp)
    return stocks

def get_all_stocks(length):
    if 0 >= length:
        return
    global lst
    if length == 1:
        for i, l in enumerate(range(ord("a"), ord("z")+1)):
            lst[i] = chr(l)

    for i, l in enumerate(range(ord("a"), ord("z")+1)):
        the_rest = get_all_stocks(lst, length-1)
        lst[i] = [chr(l)+t for t in the_rest]
    return lst


def get_stocks_symbols_to_xlsx(file_name, info):
    # info should be nested list with the stocks symbols divided acording to the first letter
    # saving file with existing file name will run-over the old one
    workbook = xlsxwriter.Workbook(file_name+'\\all stocks symbols.xlsx')
    worksheet = workbook.workbooks[supplier].add_worksheet('Sheet1')
    worksheet.right_to_left()
    for col, stocks_per_letter in enumerate(info):
        for row, symbol in enumerate(stocks_per_letter):
            worksheet.write(row, col, symbol)
    workbook.close()



a = get_all_available_stocks_symbols("", 2)
print(a)
get_stocks_symbols_to_xlsx("desktop", a)