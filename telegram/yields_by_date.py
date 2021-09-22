import math

import pandas_datareader as dr
import numpy as np
import itertools
import xlsxwriter
import os
import pandas as pd


def data_to_xlsx(data, file_name):
    if len(data) == 0:
        print("there are no stocks left after the filter\nyou should reset your filter and try again")
        return
    workbook = xlsxwriter.Workbook(os.getcwd()+"\\excel_data\\"+file_name+".xlsx")
    worksheet = workbook.add_worksheet()

    worksheet.set_column(0, len(data[0]), width=30)
    for col in range(len(data[0])):
        for row in range(len(data)):
            value = data[row][col]
            if not isinstance(value, str):
                value = float(str(value)[:5])
            worksheet.write(row, col, value)
    workbook.close()
    print("the data is ready in file " + file_name + " in folder data_files")


def get_price(df, date):
    if isinstance(date, int):
        date = date*252-1
        return df.Open[date]

    for i, y in enumerate(df.index.year):
        if y == date[2]:
            date_index = i
            break

    for i, m in enumerate(df.index.month[date_index:]):
        if m == date[1]:
            date_index += i
            break

    not_found = True
    for i, d in enumerate(df.index.day[date_index:]):
        if d == date[0]:
            date_index += i
            not_found = False
            break

    if not_found:
        date_index += np.abs(df.index.day[date_index:date_index+30] - date[0]).argmin()

    return df.Open[date_index]


def get_data(symbols):
    dates_labels = ["3 years", "pre corona", "corona bottom", "now"]
    dates = [-3, [10,2,2020], [16,3,2020], 0]
    prices = np.zeros((len(symbols), len(dates)))
    for s_i, s in enumerate(symbols):
        try:
            df = dr.DataReader(s, 'yahoo')
        except:
            try:
                if isinstance(s, float) and math.isnan(s):
                    continue
                elif "." in s:
                    s.replace(".", "-")
                elif s.isnumeric():
                    s = s + ".HK"
                else:
                    continue
                df = dr.DataReader(s, 'yahoo')
            except Exception as e:
                print(e)
                print("symbol ", s, " didnt make it")
                continue
        for d_i, d in enumerate(dates):
            try:
                prices[s_i, d_i] = get_price(df, d)
            except:
                print("there was a problem in ", s, " at date ", d)

    yields_labels = []
    yields = []

    np.seterr(divide='ignore')
    for start, end in list(itertools.combinations(range(len(dates)), 2)):
        tmp = (prices.T[end]/prices.T[start] - 1).T
        tmp = np.asarray([str(t)[:5] for t in tmp])
        tmp[tmp != tmp] = 0
        tmp[tmp == "nan"] = 0
        tmp[tmp == 'inf'] = 0

        yields.append(tmp)
        yields_labels.append(dates_labels[start]+" - "+dates_labels[end])

    np.seterr(divide='raise')
    yields = np.asarray(yields).T

    prices_tmp = []
    for p in prices:
        p = [str(t)[:5] for t in p]
        prices_tmp.append(p + [""] * (len(yields[0])-len(prices[0])))
    dates_labels = dates_labels + [""]*(len(yields[0])-len(prices[0]))
    prices = prices_tmp
    gap_line = [""]*len(yields[0])

    data = np.vstack((dates_labels, prices, gap_line, yields_labels, yields, gap_line,gap_line))
    labels = np.hstack(("symbols", symbols, "", "symbols", symbols, "", "")).T

    data_labels = np.hstack((np.asarray([labels]).T, data))
    return data_labels


def get_yields(symbol):
    symbol = symbol.upper()
    l = 'https://etfdb.com/etf/'+symbol+'/#holdings'
    df = pd.read_html(l)
    try:
        df = df[2].values[:-1, [0,2]]
    except:
        df = df[1].values[:-1, [0,2]]
    holdings = np.hstack(([symbol], df.T[0]))

    data = get_data(holdings)
    data_to_xlsx(data, file_name=symbol)

def test():
    s = "8473.HK"
    df = dr.DataReader(s, 'yahoo')
    dates = [-3, [10,2,2020], [16,3,2020], 0]
    prices = []
    for d_i, d in enumerate(dates):
        try:
            prices.append(get_price(df, d))
        except:
            print("there was a problem in ", s, " at date ", d)

if __name__ == '__main__':
    symbols = ["SPY"]
    for s in symbols:
        #try:
        get_yields(s)
        #except Exception as e:
        #    print(e)
    print("done")