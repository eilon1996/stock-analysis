import json
import numpy as np
import time
import csv
import os
from numpy import genfromtxt
import pandas as pd

fields = ["symbol", "name", "currency", "trailingPe", "marketCap", "averageValume", "previousClose", "product_type",
          "sector", "industry", "profitability", "debt_to_assent", "leveraged", "price_history", "yearly_dividend",
          "last_full_year_div", "yield_1y", "yield_5y"]

default_values = {
    "averageValume": -1,
    "currency": "-1",
    "debt_to_assent": -1,
    "industry": "-1",
    "last_full_year_div": -1,
    "leveraged": False,
    "marketCap": -1,
    "name": "name",
    "previousClose": -1,
    "price_history": [],
    "product_type": "-1",
    "profitability": -1,
    "sector": "-1",
    "trailingPe": "-1",
    "yearly_dividend": [],
    "yield_1y": -1,
    "yield_5y": -1
}

def store_in_csv():
    s = time.time()
    # the + to the right of the w mean clear the file before writing to it
    with open(os.getcwd()+'/data.csv', mode='w') as data_file:
        data_o = csv.writer(data_file, delimiter=';', quotechar="'", quoting=csv.QUOTE_MINIMAL)

        with open('raw_data.json') as json_file:
            data = json.load(json_file)
            # products = np.zeros((len(fields), len(data)))
            products = [[None] * (1 + len(default_values))] * len(data.keys())

            for index, (key, values) in enumerate(zip(data.keys(), data.values())):
                products[index][0] = key
                for i, (k, v) in enumerate(zip(default_values.keys(), default_values.values())):
                    if values.get(k) is not None:
                        if isinstance(values[k], str):
                            products[index][i+1] = values[k].replace("\n", " ").replace("&amp;", "&")
                        else: products[index][i+1] = values[k]
                    else: products[index][i+1] = v

                data_o.writerow(products[index])

            ''' 
                values["symbol"] = key
                for index, (key, values) in enumerate(zip(data.keys(), data.values())):
                values["symbol"] = key
                products[index] = [values[k].replace("\n", " ") if values.get(k) != None else v
                    for i, (k, v) in enumerate(zip(defualt_values.keys(), defualt_values.values()))]
                data_o.writerow(products[index])'''

    print("finiseh in "+str(time.time() - s)+ " seconds")

store_in_csv()
df=pd.read_csv('data.csv', sep=';',header=None)
pass