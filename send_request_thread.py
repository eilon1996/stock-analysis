import json
import requests
import time
import threading

letters = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
           'V', 'W', 'X', 'Y', 'Z']
errors = []


def send_req(symbol):
    product = {"symbol": symbol}
    url = "https://us-central1-tokyo-charge-283016.cloudfunctions.net/function-1"
    json_o = json.dumps(product)
    response = requests.post(url, json=json_o)
    if response.text != "done" and not "cant get ticker for" in response.text:
        errors.append(symbol)
    print(symbol + " " + response.text)

def handle_errors():
    for symbol in errors:
        send_req(symbol)
    errors.clear()


def create_all_symbols(start_letters=[" ", " ", " ", " "]):
    """
    :return: all the possible stocks symbols up to 4 letters
    :rtype: nested list
    """

    start_num = [0 if i == " " else ord(i)-64 for i in start_letters]

    s = time.time()

    for i in letters[start_num[0]:27]:
        print("new cycle" + i)
        if i > start_letters[0]: start_num[1] = 1
        for j in letters[start_num[1]:27]:
            if j > start_letters[1]: start_num[2] = 1
            for k in letters[start_num[2]:27]:
                if k > start_letters[2]: start_num[3] = 1
                for l in letters[start_num[3]:27]:
                    time.sleep(0.1)
                    symbol = str(i + j + k + l)
                    x = threading.Thread(target=send_req, args=(symbol,))
                    x.start()

    print("end in " + str(time.time() - s)/60)
    handle_errors()


def create_all_symbols2(start_letters=[" ", " ", " ", " "]):
    """
    :return: all the possible stocks symbols up to 4 letters
    :rtype: nested list
    """

    start_num = [0 if i == " " else ord(i)-64 for i in start_letters]

    s = time.time()

    for j in letters[start_num[1]:27]:
        if j > start_letters[1]: start_num[2] = 1
        for k in letters[start_num[2]:27]:
            if k > start_letters[2]: start_num[3] = 1
            for l in letters[start_num[3]:27]:
                time.sleep(0.01)
                symbol = str(j + k + l)
                x = threading.Thread(target=send_req, args=(symbol,))
                x.start()

    print("end in " + str(time.time() - s)/60)
    handle_errors()

create_all_symbols2(" AAA")
#create_all_symbols()
