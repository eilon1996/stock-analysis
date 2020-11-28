import json
import numpy as np
import time
import csv
import os
import pandas as pd
import calculation

def complete_to5(num_list):
    res = [None]*len(num_list)
    for i, v in enumerate(num_list):
        word = str(v)
        while len(word) < 5: word = "0"+word
        res[i] = word
    return res

def store_in_csv():
    s = time.time()
    # the + to the right of the w mean clear the file before writing to it
    with open(os.getcwd()+'/data_files/data.csv', mode='w') as data_file:
        data_o = csv.writer(data_file, delimiter=';', quotechar="'", quoting=csv.QUOTE_MINIMAL)

        with open('data_files/raw_data.json') as json_file:
            data = json.load(json_file)
            # the +1 is one for the symbol
            products = [[None] * (1 + len(calculation.default_values)) for i in range(len(data.keys()))]
            # products = [[None] * (1 + len(calculation.default_values))] * len(data.keys())

            for index, (key, values) in enumerate(zip(data.keys(), data.values())):
                products[index][0] = key
                for i, (k, v) in enumerate(zip(calculation.default_values.keys(), calculation.default_values.values())):
                    if values.get(k) is not None:
                        if isinstance(calculation.default_values[k], str):
                            if len(str(values[k])) == 0 or str(values[k]) == "error": products[index][i+1] = "-"
                            else: products[index][i+1] = str(values[k]).replace("\n", " ").replace("&amp;", "&")
                        else:
                            products[index][i+1] = values[k]
                    elif isinstance(v, str):
                        try:
                            if isinstance(calculation.default_values()[k], bool): products[index][i+1] = bool(v)
                            elif isinstance(calculation.default_values()[k], list): products[index][i+1] = list(v)
                            elif isinstance(calculation.default_values()[k], (float, int)): products[index][i+1] = float(v)
                        except:
                            products[index][i + 1] = "-"
                    else:
                        products[index][i + 1] = v
                data_o.writerow(products[index])

    return products

def add_sort_str(arr):
    num_of_fields = len(arr[0])
    order = [None]*num_of_fields
    arr = arr[arr[:, 0].argsort()] # sort by symbol
    order[0] = complete_to5(range(len(arr)))
    numbering = np.asarray((range(len(arr)),)).T
    arr = np.hstack((arr, numbering))

    for i in range(num_of_fields)[1:]:
        arr = arr[arr[:, i].argsort()]
        order[i] = complete_to5(arr.T[-1])

    order = np.asarray(order).T
    order = np.asarray((["".join(i) for i in order],)).T
    arr = arr[arr[:, 0].argsort()] # restore to order by symbols
    arr = np.hstack((arr[:,0:-1], order))

    with open(os.getcwd()+'/data_files/sorted_data.csv', 'w') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC,  quotechar="'", delimiter=";")
        for i in arr:
            writer.writerow(i)

    df = pd.read_csv('data_files/sorted_data.csv', sep=';', header=None)
    pass


def add_sort_index(arr):
    for i in range(len(arr[0])):
        arr = arr[arr[:, i].argsort()]
        numbering = np.asarray((range(len(arr)),)).T
        arr = np.hstack((arr, numbering))

    arr = arr[arr[:, 0].argsort()] # restore to order by symbols

    with open(os.getcwd()+'/data_files/sorted_data.csv', 'w') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC,  quotechar="'", delimiter=";")
        for i in arr:
            writer.writerow(i)


products = store_in_csv()
df=pd.read_csv('data_files/data.csv', sep=';', header=None)
add_sort_index(np.asarray(df))
df=pd.read_csv('data_files/sorted_data.csv', sep=';', header=None)
pass