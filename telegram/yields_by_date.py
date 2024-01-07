import numpy as np
import xlsxwriter
import os
import pandas as pd
import yfinance as yf
from pandas import Timestamp
from datetime import timedelta
from collections import OrderedDict


def get_closest_valid_date(data, date_key):
    for i in range(7):
        if date_key in data and pd.notna(data[date_key]):
            return data[date_key]
        date_key -= timedelta(days=1)
    raise Exception(f"value not found in date {date_key}")

def calc_yearly_yields(ordered_dict):

    yields = OrderedDict()
    ordered_dict_items = list(ordered_dict.items())
    for (_, previous), (year, current) in zip(ordered_dict_items, ordered_dict_items[1:]):
        yields[year] = current/previous - 1

    return yields



def get_yearly_data(symbols):

    dates_labels = ["pre corona", "corona bottom"]
    dates = [[2020, 2, 10], [2020,3, 16]]


    prices_by_years, dividends_by_years, desires_prices = {}, {}, {}
    prices_yield_by_years, dividends_yield_by_years, desires_prices_yield = {}, {}, {}

    for symbol in symbols:
        data = yf.download(symbol, period="max", interval="1d", actions=True)
        prices, dividends = data["Open"], data["Dividends"]

        num_of_years = min(5, (len(prices) - 7)//365)
        prices_by_years[symbol] = OrderedDict()
        current_year = prices.keys()[-1].year
        for i in range(num_of_years, -1, -1):
            year = current_year - i
            date_key = Timestamp(year, 1, 1)
            prices_by_years[symbol][date_key.strftime('%d-%m-%Y')] = get_closest_valid_date(prices, date_key)

        prices_yield_by_years[symbol] = calc_yearly_yields(prices_by_years[symbol])

        desires_prices[symbol] = OrderedDict()
        for label, date in zip(dates_labels, dates):
            date_key = Timestamp(*date)
            desires_prices[symbol][label] = get_closest_valid_date(prices, date_key)

        desires_prices_yield[symbol] = calc_yearly_yields(desires_prices[symbol])

        valid_dividends = dividends[dividends.notna()]
        dividends_by_years[symbol] = valid_dividends.groupby(valid_dividends.index.year).sum()
        dividends_by_years[symbol] = dividends_by_years[symbol][-(num_of_years + 1):-1]
        dividends_by_years[symbol].index = [f"01-01-{i+1}" for i in dividends_by_years[symbol].index]
        dividends_by_years[symbol] = OrderedDict(dividends_by_years[symbol])

        dividends_yield_by_years[symbol] = calc_yearly_yields(dividends_by_years[symbol])

    df_list = []

    for symbol in symbols:
        prices_df1 = pd.DataFrame(prices_by_years[symbol], ["prices"])
        prices_df2 = pd.DataFrame(desires_prices[symbol], ["prices"])
        prices_df = pd.concat([prices_df1, prices_df2], axis=1)

        yields_df1 = pd.DataFrame(prices_yield_by_years[symbol], ["prices yields"])
        yields_df2 = pd.DataFrame(desires_prices_yield[symbol], ["prices yields"])
        yields_df = pd.concat([yields_df1, yields_df2], axis=1)

        dividends_df = pd.DataFrame(dividends_by_years[symbol], ["dividends"])

        dividends_yield_df = pd.DataFrame(dividends_yield_by_years[symbol], ["dividends yields"])

        acc_div = dividends_df.T.cumsum().T
        acc_div = pd.concat([pd.DataFrame([0], index=["dividends"], columns=[prices_df1.columns[0]]), acc_div], axis=1)
        total_yields0 = acc_div + prices_df1.iloc[0]
        total_yields = pd.DataFrame([float("nan")] + [total_yields0.values[0][i+1] / total_yields0.values[0][i] - 1
                                                      for i in range(len(total_yields0.values[0]) - 1)],
                                                        index=prices_df1.columns, columns=["total yields"]).T

        df_list.append(pd.concat([prices_df, yields_df, dividends_df, dividends_yield_df, total_yields], axis=0))

    return df_list

def data_to_xlsx(symbols, df_list):

    workbook = xlsxwriter.Workbook(os.getcwd()+"\\excel_data\\"+"Stocks"+".xlsx")
    worksheet = workbook.add_worksheet()

    rows_titles = df_list[0].index
    num_of_rows_for_symbol = len(rows_titles) + 1

    cols_dates = df_list[0].columns
    num_of_cols_for_symbol = len(cols_dates) + 2

    worksheet.set_column(0, num_of_cols_for_symbol, width=30)

    # write headers
    for i, date in enumerate(cols_dates):
        worksheet.write(0, 2+i, date)

    for i, (symbol, df) in enumerate(zip(symbols, df_list)):
        worksheet.write(num_of_rows_for_symbol*i + 1, 0, symbol)
        for row, row_title in enumerate(rows_titles):
            worksheet.write(row + num_of_rows_for_symbol*i + 1, 1, row_title)
        for col, col_name in enumerate(df):
            for row, value in enumerate(df[col_name]):
                if not isinstance(value, str):
                    if np.isnan(value): continue
                    value = float(str(value)[:5])
                worksheet.write(row + num_of_rows_for_symbol*i + 1, col + 2, value)
    workbook.close()

def get_yearly_data_file(symbols):
    symbols = symbols.split(",")
    symbols = [symbol.upper() for symbol in symbols]

    df_list = get_yearly_data(symbols)
    data_to_xlsx(symbols, df_list)


if __name__ == '__main__':
    get_yearly_data_file("SPY, QQQ, AAPL")
