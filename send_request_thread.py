import json
import requests
import time
import numpy as np
import threading

print((time.time() - 1605645453.7461252) / 60)

letters = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
           'V', 'W', 'X', 'Y', 'Z']
errors = []


def send_req(symbol):
    product = {"symbol": symbol}
    url = "https://us-central1-tokyo-charge-283016.cloudfunctions.net/function-1"
    json_o = json.dumps(product)
    response = requests.post(url, json=json_o)
    if response.text != "done" and not response.text in "cant get ticker for":
        errors.append(symbol)
        print(symbol + " " + response.text)


def handle_errors():
    for symbol in errors:
        send_req(symbol)


def create_all_symbols():
    """
    :return: all the possible stocks symbols up to 4 letters
    :rtype: nested list
    """

    # TODO: compress to one nested loop
    # 2 letter

    start_letters = ['A', 'D', 'R']
    start_num = [1, 1, 1]

    s = time.time()

    for i in letters[1:27]:
        print("new cycle" + i)
        for j in letters[1:27]:
            # if j > 'A': start_num[1] = 1
            for k in letters[start_num[1]:27]:
                # if k > 'F': start_num[2] = 1
                for l in letters[start_num[2]:27]:
                    time.sleep(0.5)
                    symbol = str(i + j + k + l)
                    x = threading.Thread(target=send_req, args=(symbol,))
                    x.start()

    print("3 letter end in " + str(time.time() - s))
    handle_errors()

    for i in letters:
        time.sleep(0.5)
        x = threading.Thread(target=send_req, args=(symbol,))
        x.start()

    """
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
    return [a1, b1, c1, d1] """


create_all_symbols()
