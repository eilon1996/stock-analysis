import numpy as np
import time

product_type = ["stock", "etf"]

prefix = ["K", "M", "B", "T", "k", "m", "b", "t"]

borsas_index = []

stock_sectors = ["Basic Materials", "CONSUMER_CYCLICAL", "Financial Services", "Realestate", "Consumer Defensive",
                "Healthcare", "Utilities", "Communication Services", "Energy", "Industrials", "Technology"]
bond_sectors = ["US Government", "AAA", "AA", "A", "BBB", "BB", "B", "Below B", "others"]
all_sectors = stock_sectors + bond_sectors

headlines = np.asarray(["symbol", "name", "type", "price", "5 years yield", "one years yield","dividend in %", "pe ratio",
            "profitability", "debt/assents", "market cap", "main sector", "borsa", "average volume", "analyst score"])

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
                multiply = 10**((multiply%4+1)*3) 
                number = number[:-1]
        except: multiply = 1

        divided_number = number.split(",")
        res = 0
        for i in divided_number:
            res = res * 1000 + float(i)

        if minus: res = -1 * res
    
        return res*multiply
    except ValueError:
        return -1

def get_relevant_dates(time_length=5, start_time=None, end_time=None):
    """
        :param time_length: int
        :param start_time: tuple or list in the form (d,m,yyyy)
        :param end_time: tuple or list in the form (d,m,yyyy)
         the function complite the missing params and
        :return start time & end time in form of 'd-m-yyyy' 
     """
    
    if end_time is None:
        end_time = time.localtime()[:3][::-1]
    if start_time is None:
        start_time = end_time.copy()
        start_time[2] = start_time[2]-time_length

    start_time = "-".join([str(t) for t in start_time])
    end_time = "-".join([str(t) for t in end_time])
    return start_time, end_time



def get_sectors_name(sector_index):
    try:
        return all_sectors[sector_index]
    except Exception:
        return "index error"

def get_sectors_index(sector_name):
    try:
        return all_sectors.index(sector_name)
    except Exception:
        return -1 



def get_benchmark_yield():
    "return QQQ 5 years detailed yield"
    return [1.1003496595751494, 1.0666549243004677, 1.302516102588014, 0.937726452964105, 1.4288811421353493]


def get_benchmark_dividend():
    "return QQQ 5 years devidends"
    return [0.01067287, 0.01127553, 0.00968813, 0.00822085, 0.00894117, 0.00420541]

def two_point_percentage(number):
    try:
        return float(np.round(number*10000)/100)
    except:
        print(number)

if __name__=="main":
    pass