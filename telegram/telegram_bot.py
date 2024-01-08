import time
import urllib
import requests
import json
import yields_by_date
from dotenv import dotenv_values


# Load variables from .env file
config = dotenv_values('.env')
BOT_TOKEN = config.get('BOT_TOKEN')
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

import os

# Get the current directory
current_directory = os.getcwd()
print("current_directory: ", current_directory)

# List all files and folders in the current directory
files_and_folders = os.listdir(current_directory)

# Print each file and folder
for item in files_and_folders:
    print(item)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=5"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_messages(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            text = urllib.parse.quote_plus(text)
            chat = update["message"]["chat"]["id"]
            handle_message(text, chat)
        except Exception as e:
            print(e)


def send_message(text, chat_id):
    url = f"{URL}sendMessage?text={text}&chat_id={chat_id}"
    get_url(url)


def send_photo(photo_name, chat_id):
    url = URL + "sendPhoto?chat_id=" + str(chat_id)
    files = {'photo': open(f"./{photo_name}.jpg", 'rb')}
    status = requests.post(url, files=files)


def send_file(file_name, chat_id):
    chat_url = f"{URL}sendDocument?chat_id={chat_id}"
    files = {'document': open(f"{file_name}.xlsx", 'rb')}
    status = requests.post(chat_url, files=files)
    print(status)


def handle_message(text, chat_id):
    if "start" in text:
        help_mess = "Enter an ETF symbol and get excel file with its stocks data"
        send_message(help_mess, chat_id)
    else:
        help_mess = "preparing data..."
        send_message(help_mess, chat_id)
        try:
            text = text.replace("%2C", ",").replace("+", " ")
            yields_by_date.get_yearly_data_file(text)
            send_file("Stocks", chat_id)
        except Exception as e:
            help_mess = f"something went wrong \n{e}"
            send_message(help_mess, chat_id)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates.get("result"):
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                get_messages(updates)

        time.sleep(0.5)


if __name__ == '__main__':
    main()
