import numpy as np
import time

# @staticmethod # consider adding to other methods
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

def get_relevant_dates(time_length, end_time):
    """
        :param end_time: tuple or list in the form (d,m,yyyy)
        :param time_length: int
        return a list with the end time given or current date if not,
         and start date is the 1-1-YYYY at the end tea minus the time_length
         example: [1-1-2015, 14-5-2020]
     """
    if len(end_time) == 0:
        end_time = time.localtime(time.time())[:3]

    start_time = (str(end_time[0]-time_length)+"-1-1")
    end_time = str(end_time[0])+"-"+str(end_time[1])+"-"+str(end_time[2])

    return [start_time, end_time]


def get_bond_sectors():
    return ["US Government", "AAA", "AA", "A", "BBB", "BB", "B", "Below B", "Others"]


def get_stock_sectors():
    return ["Basic Materials", "CONSUMER_CYCLICAL", "Financial Services", "Realestate", "Consumer Defensive",
            "Healthcare", "Utilities", "Communication Services", "Energy", "Industrials", "Technology"]

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