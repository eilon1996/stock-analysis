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
import matplotlib.pyplot as plt
import matplotlib.figure as figure
import pandas as pd

import stock
import etf
import finance_product as fp
import database_handler


class Partfolio:

    def __init__(self):
        self.stocks_wrong = []
        self.mydb = database_handler.DatabaseHandler()

        self.headlines = np.asarray(["symbol", "name", "type", "price", "5 years yield", "1 year yield", "pe ratio",
                                     "profitability", "debt/assents", "market_cap", "top_sector", "country",
                                     "avg volume", "analyst score"]) # last dividend?

    def save_product(self, symbol):
        try:
            product = fb.FinanceProduct(symbol.upper())
            self.mydb.add_column(product)
        except:
            pass

    def create_all_symbols(self):
        """
        :return: all the possible stocks symbols up to 4 letters
        :rtype: nested list
        """
        s = time.time()
        # 1 letter
        a = []
        a1 = []
        for i in range(26):
            symbol = chr(65 + i)
            a.append([symbol])
            self.save_product(symbol)
        print("1 letter, ", time.time() - s)

        # 2 letter
        b = np.full((26, 26), "AA")
        b1 = []
        for j in range(26):
            b1.append([])
            for i in range(26):
                symbol = str(a[j][0] + a[i][0])
                b[j, i] = symbol
                self.save_product(symbol)

        print("2 letter, ", time.time() - s)

        # 3 letter
        c = np.full((26, 26 * 26), "AAA")
        c1 = []
        for j in range(26):
            for i in range(26):
                c1.append([])
                for k in range(26):
                    symbol = str(b[j][i] + a[k][0])
                    c[j, i * 26 + k] = symbol
                    self.save_product(symbol)

        print("3 letter, ", time.time() - s)

        # 4 letter
        d = np.full((26, 26 ** 3), "AAAA")
        d1 = []
        for j in range(26):

            for i in range(26 ** 2):
                d1.append([])
                for k in range(26):
                    t = str(c[j][i] + a[k][0])
                    d[j, i * 26 + k] = t
                    self.save_product(symbol)

            print("4 letter: ", j, " ,", time.time() - s)
        return [a1, b1, c1, d1]

    def get_stocks_symbols_to_xlsx(self, file_name, info):
        # info should be nested list with the stocks symbols divided acording to the first letter
        # saving file with existing file name will run-over the old one
        workbook = xlsxwriter.Workbook("C:\\Users\\Uriya\\Desktop\\all stocks symbols.xlsx")
        index = 0
        s = time.time()
        for i in info:
            print(index, time.time() - s)
            worksheet = workbook.add_worksheet()
            for col, stocks_per_letter in enumerate(i):
                for row, symbol in enumerate(stocks_per_letter):
                    worksheet.write(row, col, symbol)
        workbook.close()

        workbook = xlsxwriter.Workbook("C:\\Users\\Uriya\\Desktop\\not stocks symbols.xlsx")
        worksheet = workbook.add_worksheet()
        for index, value in self.stocks_wrong:
            worksheet.write((index) % 100, 2 * index // 100, value[0])
            worksheet.write((index) % 100, 2 * index // 100 + 1, value[1])

    def show_data(self, show=True):
        fig, ax = plt.subplots()
        # hide axes
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')
        data = np.asarray(self.mydb.get_all_products())
        row_lable = []
        for i, row in enumerate(data):
            for index in range(len(row[1]) // 2 - 2, len(row[1]) - 1):
                if row[1][index] == " ":
                    row_lable.append(row[1][:index] + "\n" + row[1][index + 1:])
                    break

        data = data[:, 2:]
        df = pd.DataFrame(data, columns=self.headlines[2:])
        table = ax.table(cellText=df.values, colLabels=df.columns, rowLabels=row_lable, loc='center')
        fig.tight_layout()
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        if show:
            plt.show()
        else:
            return table

    def compare(self, symbols):
        if len(symbols) > 5:
            print("too many products to compare")
            return

        data = []
        row_lable = []
        for s in symbols:
            tmp = self.mydb.get_product_by_symbol(s.upper())
            if tmp is not None and len(tmp) > 0:
                row = tmp[0]
            else:
                try:
                    p = fp.FinanceProduct(s.upper())
                    self.mydb.insert_product(p)
                except Exception as e:
                    print("a problem occurred will loading ", s.upper(), "\n", e)
                    continue
                row = self.mydb.get_product_by_symbol(s.upper())
            for index in range(max(0, len(row[1]) // 2 - 2), len(row[1]) - 1):
                if row[1][index] == " ":
                    row_lable.append(row[1][:index] + "\n" + row[1][index + 1:])
                    break
            data.append(list(row[2:]))

        fig, ax = plt.subplots(2, 1)
        # hide axes
        fig.patch.set_visible(False)

        # full screen
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')

        ax[1].axis('off')
        ax[1].axis('tight')


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

    def interface(self):
        while True:
            print("hi, what action wuold you like to do know?\n"
                  "check - to check a certain stock or etf\n"
                  "compare - to compare several stocks & etfs"
                  "exit - to exit this program")
            user_input = input()
            if user_input == "exit":
                print("we hope you enjoyed the program\n"
                      "to get even better we would glad if you could leave us a comment what do you think ubout the program"
                      "if you dont want just press Enter")
                user_input = input()
                if len(user_input) > 1:
                    self.mydb.add_comment(user_input)
                print("goodbye")
                break
            if user_input == "check":
                user_input = input("please enter the symbol of the finance product you want to check: ")
                # try:
                product = fp.FinanceProduct(user_input)
                product.show_data()
                # except:
                #    print("///")
                continue

            if user_input == "compare":
                print("please enter the symbols of the finance product you want to compare one by one\n"
                      "when you want to start compare just press another Enter: ")
                symbols = []
                while True:
                    user_input = input("->")
                    if user_input == "":
                        break
                    symbols.append(user_input)
                # try:
                self.compare(symbols)
                # except:
                #    print("///")
                continue

if __name__ == '__main__':
    p = Partfolio()
    p.mydb.delete()

    p.compare(["tecl", "qqq"])
    # info = fp.create_all_symbols()
    # fp.get_stocks_symbols_to_xlsx("", info)
