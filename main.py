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
import platform

import stock
import etf
import finance_product as fp
import database_handler
import calculation


class Partfolio:

    def __init__(self):
        self.stocks_wrong = []
        self.mydb = database_handler.DatabaseHandler()


    def save_product(self, symbol):
        try:
            product = fp.FinanceProduct(symbol.upper())
            self.mydb.add_product(product)
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
        
        return a1   # temparery 

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

            
    def show_product_data(self, symbols):

        col_label = ["yield", "dividend", "dividend in %"]
        col_label_stock = ["revenue", "income",  "assents", "free cash", "debt"]
        col_label_etf = ["top holdings", "stocks share",  "bond share", "sectors"]

        row_lable_stock= ["5 years yield", "profitability", "debt/assents", "market_cap", "top_sector", "country",
                          "pe ratio",  "avg volume", "analyst score"]
        
        data = []
        row_lable = []
        for s in symbols:
            tmp = self.mydb.get_product_by_symbol(s.upper())
            if len(tmp) > 0:
                row = tmp[0]
            else:
                try:
                    self.mydb.add_product(fp.FinanceProduct(s.upper()))
                except:
                    print("a problem occurred will loading ", s.upper())
                    continue
                row = self.mydb.get_product_by_symbol(s.upper())[0]
            for index in range(max(0, len(row[1]) // 2 - 2), len(row[1]) - 1):
                if row[1][index] == " ":
                    row_lable.append(row[1][:index] + "\n" + row[1][index + 1:])
                    break
                data.append(list(row))
            

        fig, ax = plt.subplots(2, 1)
        # hide axes
        fig.patch.set_visible(False)

        # full screen
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')

        ax[1].axis('off')
        ax[1].axis('tight')

        data = np.asarray(data)[:, 2:]
        df = pd.DataFrame(data, columns=calculation.headlines[2:])
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
        df = pd.DataFrame(data, columns=calculation.headlines[2:])
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
        print("comparing...")
        for s in symbols:
            tmp = self.mydb.get_product_by_symbol(s.upper())
            if tmp is not None and len(tmp) > 0:
                row = list(tmp)
            else:
                #try:
                p = fp.FinanceProduct(s.upper())
                self.mydb.add_product(p)
               # except Exception as e:
               #     print("a problem occurred will loading ", s.upper(), "\n", e)
               #     continue
                row = list(self.mydb.get_product_by_symbol(s.upper()))

            #stocks name are usaly long so we split it to 2 lines
            for index in range(max(0, len(row[1]) // 2 - 2), len(row[1]) - 1):
                if row[1][index] == " ":
                    row_lable.append(row[1][:index] + "\n" + row[1][index + 1:])
                    break

            # transforming market cap to readble view with prefix of K, M, B, T
            market_cap = row [10] # once we add dividends its need to be 10
            multiply = -1
            for i in range(4):
                #if market_cap%1000 == 0:
                if market_cap>10000:
                    multiply += 1 
                    market_cap = market_cap/1000
                else:
                    break
            if multiply >-1:
                row[10] = str(market_cap)+str(calculation.prefix[multiply])

            
            data.append(row[2:])

        fig, ax = plt.subplots(2, 1)
        # hide axes
        fig.patch.set_visible(False)

        # full screen
        mng = plt.get_current_fig_manager()
        print("I'm running on "+ platform.system())
        if(platform.system() == "Linux"):
            try:
                mng.full_screen_toggle()
                print("the first worked")
            except Exception:
                mng.window.showMaximized(True)
                print("the second worked")
        else:
            #for windows
            mng.window.state('zoomed')

        ax[1].axis('off')
        ax[1].axis('tight')

        df = pd.DataFrame(data, columns=calculation.headlines[2:])
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
    
    def delete_data(self):
        self.mydb.delete_products()

    def interface(self):
        while True:
            print("hi, what action wuold you like to do now?\n"
                  "check - to check a certain stock or etf\n"
                  "compare - to compare several stocks & etfs\n"
                  "exit - to exit this program")
            user_input = input()
            if user_input == "exit":
                print("we hope you enjoyed the program\n"
                      "to get even better we would glad if you could leave us a comment what do you think ubout the program\n\n"
                      "if you dont want just press Enter\n")
                user_input = input()
                if len(user_input) > 1:
                    self.mydb.add_comment(user_input)
                print("goodbye")
                break
            if user_input == "check":
                user_input = input("please enter the symbol of the finance product you want to check: ")
                print("gathering information...")
                # try:
                product = fp.FinanceProduct(user_input)
                #show_data()
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
    p.delete_data()
    print("data deleted")
    p.mydb.create_table()
    print("table created")

    p.compare([ "msft", "aapl", "qqq", "agg"])
    print("compare done running")
    #p.interface()
