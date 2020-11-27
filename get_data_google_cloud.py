import requests
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup
import json
import time

prefix = ["K", "M", "B", "T", "k", "m", "b", "t"]

stock_sectors = ["Basic Materials", "CONSUMER_CYCLICAL", "Financial Services", "Realestate", "Consumer Defensive",
                 "Healthcare", "Utilities", "Communication Services", "Energy", "Industrials", "Technology"]
bond_sectors = ["US Government", "AAA", "AA", "A", "BBB", "BB", "B", "Below B", "others"]
all_sectors = stock_sectors + bond_sectors


def two_point_percentage(number):
    try:
        if hasattr(number, "__len__"):
            # num is a list or a array
            check = number[0]
        else:
            check = number

        if check > 1:
            return np.round(number * 100, decimals=2)
        if check > 0.1:
            return np.round(number * 100, decimals=3)
        if check > 0.01:
            return np.round(number * 100, decimals=4)
        return 0
    except Exception as e:
        print("calc.twoPoint.num: " + str(number) + "\n" + str(e))


def two_point_num(number):
    try:
        if hasattr(number, "__len__"):
            # num is a list or a array
            check = number[0]
        else:
            check = number

        if check > 1:
            return np.round(number, decimals=2)
        if check > 0.1:
            return np.round(number, decimals=3)
        if check > 0.01:
            return np.round(number, decimals=4)
        return 0
    except Exception as e:
        print("calc.twoPoint.num: " + str(number) + "\n" + str(e))


def get_benchmark_yield():
    "return QQQ 5 years detailed yield"
    return [1.1003496595751494, 1.0666549243004677, 1.302516102588014, 0.937726452964105, 1.4288811421353493]


def get_benchmark_4y_yield():
    return np.prod(get_benchmark_yield()[1:])


def get_sectors_name(sector_index):
    try:
        return all_sectors[sector_index]
    except Exception:
        return "index error"


# @staticmethod # consider adding to other methods
def convert_string_to_number(number):
    """"for dealing with representing like  -15,010.3M
            relevent for extarcting data from HTML"""
    try:
        minus = False
        if number[0] == "-":
            minus = True
            number = number[1:]

        # if the number have one of those prefix we will turn it to the full number
        try:
            multiply = prefix.index(number[-1])
            if multiply != -1:
                multiply = 10 ** ((multiply % 4 + 1) * 3)
                number = number[:-1]
        except:
            multiply = 1

        divided_number = number.split(",")
        res = 0
        for i in divided_number:
            res = res * 1000 + float(i)

        if minus: res = -1 * res

        return res * multiply
    except ValueError:
        return -1


def create_product(symbol):
    try:
        ticker = yf.Ticker(symbol)
        ###### get stock info ######
        info = ticker.info

    except:
        # some times its not working on the first time becouse of internet connection
        time.sleep(3.5)
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
        except:
            return "cant get ticker for " + symbol

    # assigning defualt values
    name = symbol
    symbol = symbol.upper()
    product = {}
    product_type = ""
    sector = ""
    industry = ""
    profitability = -1
    debt_to_assent = -1
    leveraged = False
    price_history = []
    yearly_dividend = np.zeros(5)
    div_per_price = []
    last_full_year_div = 0
    yield_1y = 0
    yield_5y = 0
    error = ""

    #### set name ####

    try:
        s_name = info['shortName']
    except:
        s_name = ""
    try:
        l_name = info['longName']
    except:
        l_name = ""
    if s_name != "" and l_name != "":
        if len(s_name) > len(l_name):
            name = l_name
        else:
            name = s_name
    elif s_name == "" and l_name != "":
        name = l_name
    elif s_name != "" and l_name == "":
        name = s_name

    ##### determine product TYPE and more... #####
    try:

        if info['quoteType'] is not None and info['quoteType'] == "ETF":
            product_type = "ETF"

            ###### get sectors ########
            url = "https://finance.yahoo.com/quote/" + symbol + "/holdings?p=" + symbol
            html_content = requests.get(url).text  # Make a GET request to fetch the raw HTML content
            soup = BeautifulSoup(html_content, "lxml")  # Parse the html content
            data = soup.find("section", attrs={"class": "Pb(20px) smartphone_Px(20px) smartphone_Mt(20px)"})
            sectors = {}

            bond_share = convert_string_to_number(
                data.contents[0].contents[0].contents[1].contents[1].contents[1].text[:-1])

            if bond_share >= 50:
                sector = "Bonds etf"
                sectors_data = data.contents[1].contents[1].contents[1].contents
            else:
                sector = "Stocks etf"
                sectors_data = data.contents[0].contents[1].contents[1].contents

            sectors = [convert_string_to_number(x.contents[2].text[:-1]) for x in sectors_data[1:]]
            max1 = max(sectors)
            max1_index = sectors.index(max1)
            industry = get_sectors_name(max1_index) + " " + str(max1) + "%"

            if max1 < 90:
                sectors[max1_index] = 0
                max2 = max(sectors)
                max2_index = sectors.index(max2)
                industry += "\n" + get_sectors_name(max2_index) + " " + str(max2) + "%"

            # ETF dont have profitability or debt_to_assent


        else:
            if info['quoteType'] is not None:
                product_type = info['quoteType']
            else:
                product_type = "Stock"

            sector = info["sector"]
            industry = info["industry"]

            ###### get stock profitability ######

            url = "https://finance.yahoo.com/quote/" + symbol + "/financials?p=" + symbol
            html_content = requests.get(url).text  # Make a GET request to fetch the raw HTML content
            soup = BeautifulSoup(html_content, "lxml")  # Parse the html content
            data = soup.find("div", attrs={"class": "D(tbrg)"})

            revenue = convert_string_to_number(data.contents[0].contents[0].contents[2].string)
            income = convert_string_to_number(data.contents[10].contents[0].contents[2].string)
            profitability = two_point_percentage(revenue / income)

            ###### get stock debt/assent ######

            url = "https://finance.yahoo.com/quote/" + symbol + "/balance-sheet?p=" + symbol
            html_content = requests.get(url).text  # Make a GET request to fetch the raw HTML content
            soup = BeautifulSoup(html_content, "lxml")  # Parse the html content
            data = soup.find("div", attrs={"class": "D(tbrg)"})

            assent = convert_string_to_number(data.contents[0].contents[0].contents[1].string)
            debt = convert_string_to_number(data.contents[11].contents[0].contents[1].string)
            debt_to_assent = two_point_percentage(debt / assent)


    except Exception as e:
        error += "get sector: " + str(e)

    ###### get stock Leveraged ######

    try:
        if info['category'] is not None:
            "Leveraged" in info['category']
            leveraged = True
    except:
        pass
        # leveraged is false by defualt

    ###### get historical market data ######
    try:
        history = ticker.history(
            period="5y",
            interval="3mo",
            group_by='ticker')
        price_history = history.Open.values[:-1]  # the last one is today price
        not_nan = price_history == price_history
        price_history = price_history[not_nan]

        dates = np.array([[history.index.day[i], history.index.month[i], history.index.year[i]]
                          for i in range(len(history.index) - 1)])
        dates = dates[not_nan].tolist

    except Exception as e:
        error += "get historical: " + str(e)

    ###### extract dividends ######
    try:
        dividends = ticker.dividends
        dividends, dates = dividends.values, list(dividends.index.year)
        first_year = dates[-1] - 4
        start_index = dates.index(first_year)

        count_last_year = 0
        count_previes_year = 0
        for (div, y) in zip(dividends[start_index:], dates[start_index:]):
            yearly_dividend[y - first_year] += div

            if y - first_year == 3: count_previes_year += 1
            if y - first_year == 4: count_last_year += 1
        if count_previes_year == count_last_year:
            # this is a full year dividend
            astimate_last_div = yearly_dividend[-1]
            last_full_year_div = sum(yearly_dividend[-4:-1])
        else:
            # this is not a full year dividend
            ### estimate for full year
            ### we asume that there will be the same amount of dividend as last year
            ### and that the rimaining dividens are like the last one
            astimate_last_div = yearly_dividend[-1] + dividends[-1] * (count_previes_year - count_last_year)
            last_full_year_div = sum(yearly_dividend[-4 - count_last_year:-1 - count_last_year])
        two_point_num(last_full_year_div)


    except Exception as e:
        error += "get dividends: " + str(e)

    ###### extract dividends -- in % to price ######
    try:
        dates = np.asarray([history.index.year[i] for i in range(len(history.index) - 1)])
        dates = dates[not_nan]
        start_index = np.where(dates == first_year)[0][0]

        sum_price = np.zeros(5)

        count_last_year = 0
        for (p, y) in zip(price_history[start_index:], dates[start_index:]):
            sum_price[y - first_year] += p

            if y - first_year == 4: count_last_year += 1

        last_full_year_sum_price = sum_price[-1] + price_history[-1] * (4 - count_previes_year)

        div_per_price = (yearly_dividend[:-1] / (sum_price[:-1] / 4))
        div_per_price += astimate_last_div / (last_full_year_sum_price / 4)

    except Exception as e:
        error += "get dividends in %: " + str(e)

    ##### calculate div and price yield #####
    try:
        yield_1y = two_point_percentage(price_history[-1] / price_history[-5] - 1)
        if len(price_history) >= 21:
            # we have full data of 5 years
            yield_5y = price_history[-1] / price_history[0] - 1
        elif len(price_history) < 17:
            # not enough details to astimate for 5 years
            yield_5y = -1
        else:
            # estimating the remaining yield based on the benchmark yield at the time
            yield_4y = price_history[-1] / price_history[-17]
            ratio = yield_4y / get_benchmark_4y_yield()
            yeild_missing_year = get_benchmark_yield()[0] * ratio
            yield_5y = yeild_missing_year * yield_4y - 1

        yield_5y = two_point_percentage(yield_5y)

    except Exception as e:
        error += "get yeald: " + str(e)

    price_history = list(price_history)
    yearly_dividend = list(yearly_dividend)
    div_per_price = list(div_per_price)

    try:
        currency = info["currency"]
    except:
        currency = "error"
    try:
        trailingPE = info["trailingPE"]
    except:
        trailingPE = "error"
    try:
        marketCap = info["marketCap"]
    except:
        marketCap = "error"
    try:
        averageVolume = info["averageVolume"]
    except:
        averageVolume = "error"
    try:
        previousClose = info["previousClose"]
    except:
        previousClose = "error"

    product = {symbol: {
        "name": name,
        "currency": currency,
        "trailingPe": trailingPE,
        "marketCap": marketCap,
        "averageValume": averageVolume,
        "previousClose": previousClose,
        "product_type": product_type,
        "sector": sector,
        "industry": industry,
        "profitability": profitability,
        "debt_to_assent": debt_to_assent,
        "leveraged": leveraged,
        "price_history": price_history,
        "yearly_dividend": yearly_dividend,
        "last_full_year_div": last_full_year_div,
        "yield_1y": yield_1y,
        "yield_5y": yield_5y
    }}

    url = "https://stocks-etf.firebaseio.com/.json"

    data = json.dumps(product)

    response = requests.patch(url, data)
    return "done"


def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    try:
        j = request.json

        s = j.index(':')
        e = j.index('}')

        symbol = j[s + 3:e - 1]
        # return j #work' geting '{"symb":"value"}'
        # return j["symbol"]
        a = create_product(symbol)
        return a
    except Exception as e:
        return "main function exception: " + str(e) + "/n\n request is: " + str(request.json)

    return f'Hello World!'

