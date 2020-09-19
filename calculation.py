import numpy as np
import time


#this page helping us to re-use functions and variables without writing them more then once

product_type = ["stock", "etf"]

prefix = ["K", "M", "B", "T", "k", "m", "b", "t"]

borsas_index = []

stock_sectors = ["Basic Materials", "CONSUMER_CYCLICAL", "Financial Services", "Realestate", "Consumer Defensive",
                "Healthcare", "Utilities", "Communication Services", "Energy", "Industrials", "Technology"]
bond_sectors = ["US Government", "AAA", "AA", "A", "BBB", "BB", "B", "Below B", "others"]
all_sectors = stock_sectors + bond_sectors

headlines = np.asarray(["symbol", "name", "price", "currency", "type", "main sector", "industry", "leveraged", "5 years yield", "one year yield","dividend in %", "market_cap",
            "profitability", "debt/assents"])

currency = ["USD", ]


def sql_to_show(data):
    return [data[0],
            data[1],
            data[2],
            data[3],
            ("Stock" if data[4] == 0 else "ETF"),
            get_sectors_name(data[5]),
            data[6],
            ("Leveraged" if data[7] else "Not Leveraged"),
            two_point_percentage(data[8]),
            two_point_percentage(data[9]),
            two_point_percentage(data[10]),
            add_prefix(data[11]) ]

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

def add_prefix(number):
    
    multiply = -1
    for i in range(4):
        if(number >= 1000):
            number = number/1000
            multiply += 1
        else: break

    if number >= 100:
        number = (number//10)*10
    elif number >= 10:
        number = int(round(number))
    else:
        number = round(number*10)//10

    return str(number) + prefix[multiply]

   
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

def get_sector_index(sector_name):
    try:
        return all_sectors.index(sector_name)
    except Exception:
        return -1 



def get_benchmark_yield():
    "return QQQ 5 years detailed yield"
    return [1.1003496595751494, 1.0666549243004677, 1.302516102588014, 0.937726452964105, 1.4288811421353493]

def get_benchmark_4y_yield():
    return np.prod(get_benchmark_yield()[1:])

def get_benchmark_dividend():
    "return QQQ 5 years devidends"
    return [0.01067287, 0.01127553, 0.00968813, 0.00822085, 0.00894117, 0.00420541]

def two_point_percentage(number):
    try:
        if hasattr(number, "__len__"):
            #num is a list or a array
            check = number[0]
        else:
            check = number

        if check>1:
            return np.round(number, decimals=2)*100
        if check>0.1:
            return np.round(number, decimals=3)*100
        if check>0.01:
            return np.round(number, decimals=4)*100

    except Exception as e:
        print("calc.twoPoint.num: "+str(number)+"\n"+str(e))




if __name__ == '__main__':
    pass