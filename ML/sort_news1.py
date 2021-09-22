import pandas as pd
import numpy as np
import json

def store():
    df = pd.read_csv("./data_files\\new_data\\data-1616698559479.csv")
    df = [list(l) for l in np.asarray(df)]

    a = {}
    for i in range(len(df)):
        symbol = df[i][0]
        if a.get(symbol, None) is None:
            a[symbol] = [df[i]]
        else:
            a[symbol].append(df[i])

    with open('./data_files\\new_data\\data-479.json', 'w') as file:
        json.dump(a, file)

def load():
    with open('./data_files\\new_data\\data-479.json', 'r') as file:
        a = json.load(file)
        return a

a = store()
print("done")