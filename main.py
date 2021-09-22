import pandas as pd
# import fix_yahoo_finance
import numpy as np
import pandas_datareader as dr
import matplotlib.pyplot as plt
import platform

import calculation
import sys

np.set_printoptions(threshold=sys.maxsize, precision=2, linewidth=500)

# this is where the user start, mainmly the interface method is in use

class Partfolio:
    
    @staticmethod
    def compare(data, check=False):
        symbols = []
        indexes = []
        if check: # to check only one stock
            print("please enter the symbol of the finance product you want to check: ")
            input_ok = False
            while not input_ok:
                symbols.append(input("->").upper())
                try:
                    indexes += [i for i in range(len(data)) if data["Symbol"][i] == symbols[0]]
                    # indexes.append(np.where(data[:, 0] == symbols[0].upper())[0][0])
                    break
                except:
                    print(str(symbols[0]) + " is not a finance product, try again")  # need to add suggestion
                    symbols.pop(0)
        else: # to compare several stocks
            print("please enter the symbols of the finance product you want to compare one by one\n"
                  "when you want to start compare just press another Enter: ")
            input_ok = False
            while not input_ok:
                while True:
                    user_input = input("->")
                    if user_input == "":
                        break
                    symbols.append(user_input.upper())

                if len(symbols) > 5:
                    print("too many products to compare")
                    return
                print("comparing...")
                tmp_symbols = []
                for i, s in enumerate(symbols):
                    try:
                        indexes += [j for j in range(len(data)) if data["Symbol"][j] == s.upper()]
                        # indexes.append(np.where(data[:, 0] == s.upper())[0][0])
                        tmp_symbols.append(s)
                    except:
                        print(s + " is not a finance product")  # need to add suggestion
                symbols = tmp_symbols
                if len(symbols) == 0:
                    print("all the symbols you entered were not finance products, please try again")
                else: input_ok = True
        mask_filter = ["Symbol",
                       "Average Volume",
                       "Debt/Assent",
                       "Industry",
                       "Dividend 1y",
                       "Market Cap",
                       "Trailing PE",
                       "Yield 1y",
                       "Yield 5y"
                       ]
        symbols_data = data[mask_filter].T[indexes].T
        names = np.asarray(data["Name"].T[indexes].T)
        for s in symbols_data:  # s is the column name
            for i in indexes:   # i is the value
                if symbols_data[s][i] in [-1, "-1", []]:
                    symbols_data[s][i] = "-"
                else:
                    if s in ["Average Volume", "Market Cap"]:
                        symbols_data[s][i] = calculation.add_prefix(symbols_data[s][i])
                    elif s in ["Debt/Assent", "Yield 1y", "Yield 5y"]:
                        symbols_data[s][i] = calculation.two_point_percentage(symbols_data[s][i], percentage=True)
                    elif s in ["Dividend 1y", "Trailing PE"]:
                        symbols_data[s][i] = calculation.two_point_percentage(symbols_data[s][i])
                    elif s == "Industry":
                        symbols_data[s][i] = calculation.split_word(symbols_data[s][i])

        symbols_data = np.asarray(symbols_data)
        fig, ax = plt.subplots(2, 1)
        # hide axes
        fig.patch.set_visible(False)

        # full screen
        mng = plt.get_current_fig_manager()
        try:
            if (platform.system() == "Linux"):
                mng.full_screen_toggle()
            else:
                # for windows
                mng.window.state('zoomed')
        except:
            print("main.py func: compare - there was a problem showing in full screen")

        ax[1].axis('off')
        ax[1].axis('tight')

        table = ax[1].table(cellText=symbols_data, colLabels=mask_filter, rowLabels=names, cellLoc='center')
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
        plt.grid(color='k', linestyle='-', linewidth=2)
        plt.show()
        pass

    def filter_by(self, data):
        print("choose a field you want to filter from")
        for i, v in enumerate(calculation.default_values.keys()):
            print(str(i + 1) + ": " + str(v))
        input_ok = False
        while not input_ok:
            user_input = input("enter the number of the field: ")
            try:
                user_input = int(user_input)
                if 1 <= user_input <= 17: input_ok = True
                else: print("you need to enter an index from the options")
            except:
                print("you need to enter a number")

        defualt_value = list(calculation.default_values.values())[user_input - 1]

        if isinstance(defualt_value, bool):
            input_ok = False
            print("enter if you want the value to be  1: true or 2: false : ")
            while not input_ok:
                user_input2 = input()
                if user_input2 == "1":
                    user_input2 = True
                    input_ok = True
                elif user_input2 == "2":
                    user_input2 = False
                    input_ok = True
                else: print("enter only 1 or 2")
            mask = [(user_input2 == v) for v in data[:, user_input]]
        elif isinstance(defualt_value, int):
            input_ok = False
            while not input_ok:
                try:
                    low = float(input("enter lowest value: "))
                    high = float(input("enter highest value: "))
                    if low > high: print("the lower number should be lower or equal then the higher number ;-)")
                    else:
                        mask = []
                        for v in data[:, user_input]:
                            try: mask.append(low <= float(v) <= high)
                            except: mask.append(False)
                        input_ok = True
                except:
                    print("enter only numbers")
        elif user_input == 13 or user_input == 4:
            print("index\tIndustry")
            for i, v in enumerate(calculation.all_sectors): print(str(i) + "\t" + str(v))
            user_input2 = input("choose from the above options by entering the index\n"
                                "you can choose several options by separating with a comma ',': ")
            input_ok = False
            while not input_ok:
                try:
                    user_input2 = [calculation.all_sectors[int(i)] for i in user_input2.replace(" ", "").split(",")]
                    input_ok = True
                except:
                    print("you have to choose from the above options, and enter only indexes and commas")
            mask = [any(o in v for o in user_input2) for v in data[:, user_input]]
        elif isinstance(defualt_value, list):
            input_ok = False
            while not input_ok:
                try:
                    print("by what parameter you want to filter?")
                    user_input2 = int(input("1: growth in %\n2: absolute  growth"))
                    if user_input2 == 2:
                        f = lambda a, b: (a / b - 1) * 100
                    elif user_input2 == 1:
                        f = lambda a, b: (a - b)
                    else:
                        raise ValueError
                    input_ok = True
                except:
                    print("your input should be 1 or 2")

                print("between which years you want to check? (2016 - 2020) split your choices with a comma ")
                input_ok = False
                while not input_ok:
                    try:
                        user_input2 = input()
                        user_input2 = [int(i) for i in user_input2.replace(" ", "").split(",")]
                        if user_input2[0] < 2016 or user_input2[1] > 2020 or user_input2[1] - user_input2[0] < 0:
                            raise ValueError
                        input_ok = True
                    except:
                        print("you have to choose years between 2016 to 2020 , and enter only indexes and commas")
                mask = [i.count(",") + 1 >= (2020 - user_input2[0] + 1) * 4 for i in data[:, user_input]]
                data = data[mask]

                input_ok = False
                while not input_ok:
                    try:
                        low = int(input("enter lowest value (without prefix) can also be negative values: "))
                        high = int(input("enter highest value (without prefix) can also be negative values:"))
                        if low > high: print("the lower number should be lower or equal then the higher number ;-)")
                        else: input_ok = True
                    except:
                        print("enter only numbers")

                mask = [None] * len(data)
                for i, string in enumerate(data[:, user_input]):
                    a = float(string[1:string.index(',') - 1])
                    b = float(string[string.rfind(",") + 1:-1])
                    mask[i] = low <= f(b, a) <= high
        elif isinstance(defualt_value, str):
            options = {}
            for v in data[:, user_input]: options[v] = options.get(v, 0) + 1
            print("index\tvalue\t\t\t\t amount")
            for i, k in enumerate(options):
                space = " " * (25 - len(k))
                print(str(i) + "\t" + k + space + str(options[k]))

            print("choose from the above options by entering the index\n" + "you can choose several options by separating with a comma ','")
            input_ok = False
            while not input_ok:
                try:
                    user_input2 = input()
                    a = list(options.keys())
                    user_input2 = [list(options.keys())[int(i)] for i in user_input2.replace(" ", "").split(",")]
                    input_ok = True
                except:
                    print("you have to choose from the above options, and enter only indexes and commas")
            mask = [any(o in v for o in user_input2) for v in data[:, user_input]]

        data = data[mask]
        print("there are " + str(len(data)) +
              " finance products that answer your filters, do you want to \n1: view them \n2: filter more \n3: reset filter \n4: export to excel file")
        input_ok = False
        while not input_ok:
            user_input2 = input()
            if user_input2 == "1":
                calculation.pretty_print(data)
                print("\ndo you want to \n1: return to the main menu \n2: filter more \n3: reset filter \n4: export to excel file")
                user_input2 = input()
                if user_input2 == "1": input_ok = True
            if user_input2 == "2":
                input_ok = True
                self.filter_by(data)
            if user_input2 == "3":
                input_ok = True
                data = np.asarray(pd.read_csv('data_files/data.csv', sep=';', header=None))
                self.filter_by(data)
            if user_input2 == "4":
                input_ok = True
                calculation.data_to_xlsx(data)
            if not input_ok: print("enter only 1, 2, 3 or 4 ")


    def interface(self):
        data = pd.read_csv('data_files/data.csv', sep=';', header=None)
        data = pd.DataFrame(data.values, columns=calculation.fields)

        while True:
            print("hi, what action would you like to do now?\n"
                  "1: to check a certain stock or etf (not working yet)\n"
                  "2: to compare several stocks & etfs\n"
                  "3: to filter finance products by fields of your choice\n"
                  "4: to exit this program")
            user_input = input()
            if user_input == "0":
                print("we hope you enjoyed the program\n"
                      "to get even better we would glad if you could leave us a comment what do you think ubout the program\n\n"
                      "if you dont want just press Enter\n")
                user_input = input()
                # if len(user_input) > 1:
                #    self.mydb.add_comment(user_input)
                print("goodbye")
                break
            if user_input == "1":
                self.compare(data, True)

            if user_input == "2":
                self.compare(data)
                print("comparing done")

            if user_input == "3":
                self.filter_by(data.copy())
                continue
            else: print("you need to enter an index from the options")

def show_precise_graph(self, length=5, start_date=None, end_date=None):
    pass


if __name__ == '__main__':
    p = Partfolio()
    p.interface()
