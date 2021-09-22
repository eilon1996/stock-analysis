import numpy as np
import time
import pandas as pd
import xlsxwriter
import os
pd.options.mode.chained_assignment = None  # default='warn'

#this page helping us to re-use functions and variables without writing them more then once

product_type = ["stock", "etf"]

prefix = ["", "K", "M", "B", "T", "k", "m", "b", "t"]

borsas_index = []

stock_sectors = ["Basic Materials", "CONSUMER_CYCLICAL", "Financial Services", "Realestate", "Consumer Defensive",
                "Healthcare", "Utilities", "Communication Services", "Energy", "Industrials", "Technology"]
bond_sectors = ["US Government", "AAA", "AA", "A", "BBB", "BB", "B", "Below B", "others"]
all_sectors = stock_sectors + bond_sectors



headlines = np.asarray([
    "Symbol",
    "Average Volume",
    "Currency",
    "Debt/Assent",
    "Industry",
    "Dividend 1y",
    "Leveraged",
    "Market Cap",
    "previousClose",
    "Product Type",
    "Profitability",
    "Sector",
    "Trailing PE",
    "Yield 1y",
    "Yield 5y"
])

currency = ["USD", ]


default_values = {
    "Symbol": "-1",
    "Average Volume": -1,
    "Currency": "-1",
    "Debt/Assent": -1,
    "Industry": "-1",
    "Dividend 1y": -1,
    "Leveraged": False,
    "Market Cap": -1,
    "Name": "Name",
    "previousClose": -1,
    "price_history": [],
    "Product Type": "-1",
    "Profitability": -1,
    "Sector": "-1",
    "Trailing PE": -1,
    "yearly_dividend": [],
    "Yield 1y": -1,
    "Yield 5y": -1
}

fields = [
    "Symbol",
    "Average Volume",
    "Currency",
    "Debt/Assent",
    "Industry",
    "Dividend 1y",
    "Leveraged",
    "Market Cap",
    "Name",
    "previousClose",
    "price_history",
    "Product Type",
    "Profitability",
    "Sector",
    "Trailing PE",
    "yearly_dividend",
    "Yield 1y",
    "Yield 5y"
]

def leng(x):
    return len(str(x))


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
            add_prefix(data[11])]

# @staticmethod # consider adding to other methods
def convert_string_to_number(number):
    """"for dealing with representing like  -15,010.3M
            relevent for extarcting data from HTML"""
    if isinstance(number, float) or isinstance(number, int):
        return number
    try:
        # if the number have one of those prefix we will turn it to the full number
        try:
            multiply = prefix.index(number[-1])
            if multiply != -1:
                multiply = 10**((multiply%4+1)*3) 
                number = number[:-1]
        except: multiply = 1

        res = float("".join(number.split(",")))
        return res*multiply
    except ValueError:
        return -1

def add_prefix(number):
    try:
        number = float(number)
    except:
        return "-"
    multiply = 0
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

def two_point_percentage(number, percentage=False):
    try:
        if not isinstance(number, str):
            number = str(number)
        if not number.isnumeric or number == "-1" or number == "-":
            return "-"

        i = number.find(".")
        if i + 2 < len(number)-2: number = number[:i+2]
        if percentage: number = number + "%"
        return number

    except Exception as e:
        #print("calc.twoPoint.num: "+str(number)+"\n"+str(e))
        return "-"


def find_closest(arr, target, start, end, above):
    """
    @above: true if you want to get the target or the closest above it,
            false if you want to get the target or the closest below it
    """
    if end == start:
        if above:
            if end == len(arr) or arr[start] >= target: return start
            return start + 1
        else:
            if start == 0 or arr[start] <= target: return start
            return start - 1

    mid = (end - start) // 2 + start
    if arr[mid] == target:
        return mid
    if arr[mid] < target:
        return find_closest(arr, target, mid + 1, end, above)
    return find_closest(arr, target, start, mid - 1, above)

def split_word(word):
    # stocks name are usually long so we split it to 2 lines
    mid = len(word) // 2
    for i in range(mid-1):
        if word[mid - i] in [" ", "-"]:
            return (word[:mid - i] + "\n" + word[mid - i + 1:])
        if word[mid + i] in [" ", "-"]:
            return (word[:mid + i] + "\n" + word[mid + i + 1:])
    return word

def adjust_value(type, value, split=True):
    if value in [-1, "-1", []]:
        return "-"
    else:
        if type in ["Average Volume", "Market Cap"]:
            return add_prefix(value)
        elif type in ["Debt/Assent", "Yield 1y", "Yield 5y"]:
            return two_point_percentage(value, percentage=True)
        elif type in ["Dividend 1y", "Trailing PE"]:
            return two_point_percentage(value)
        elif type == "Industry" and split:
            return split_word(value)
    return value


def filter_data(data):
    data = data[headlines]
    for s in data:  # s is the column name
        for i in data.index:  # i is the row index
                data[s][i] = adjust_value(s, data[s][i], split=False)

    return np.vstack((headlines, data))

def pretty_print(data):
    if len(data) == 0:
        print("there are no stocks left after the filter\nyou should reset your filter and try again")
        return
    data = filter_data(data)
    length = np.zeros((len(data), len(data[0])), dtype=int)
    for i, row in enumerate(data):
        for j in range(len(row)):
            length[i, j] = len(str(row[j]))

    max = np.max(length, axis=0)
    res = ""
    for i, row in enumerate(data):
        for j in range(len(row)):
            res += str(row[j]) + " "*(max[j] - length[i, j] + 4)
        res += "\n"
    print(res)
    pass


def data_to_xlsx(data):
    if len(data) == 0:
        print("there are no stocks left after the filter\nyou should reset your filter and try again")
        return
    file_name = input("enter a name, for the excel file: ")
    workbook = xlsxwriter.Workbook(os.getcwd() + "/data_files/"+file_name+".xlsx")
    worksheet = workbook.add_worksheet()
    data = filter_data(data)
    for row in range(len(data)):
        for col in range(len(data[0])):
            worksheet.write(row, col, data[row][col])
    workbook.close()
    print("the data is ready in file " + file_name + " in folder data_files")



if __name__ == '__main__':
    pass

    #data = np.asarray(pd.read_csv('data_files/data.csv', sep=';', header=None))
    #pretty_print(data[:500])
