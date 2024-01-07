import time
import urllib

import requests
import json
import yields_by_date

bot_token = '1787104943:AAFURKAoq3_esmq6f5x5SsqAKRiXrnqv6Oo'
bot_chatID = '684239556'

def telegram_bot_sendtext(bot_message):
    # user name: stock_etf_bot
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


bot_token = "<your-bot-token>"
URL = "https://api.telegram.org/bot{}/".format(bot_token)
URL = "https://api.telegram.org/bot1787104943:AAFURKAoq3_esmq6f5x5SsqAKRiXrnqv6Oo/"


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def handle_message(text, chat_id):
    if "start" in text:
        help_mess = "Enter an ETF symbol and get excel file with its stocks data"
        send_message(help_mess, chat_id)
    else:
        help_mess = "It might take a minute"
        send_message(help_mess, chat_id)
        text = text.upper()
        yields_by_date.get_yearly_data_file(text)
        send_file("Stocks", chat_id)


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
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def send_photo(photo_name, chat_id):
    url = URL + "sendPhoto?chat_id=" + str(chat_id)
    files = {'photo': open("./"+photo_name+".jpg", 'rb')}
    status = requests.post(url, files=files)

def send_file(file_name, chat_id):
    url = URL + "sendDocument?chat_id=" + str(chat_id)
    files = {'document': open("./excel_data\\"+file_name+".xlsx", 'rb')}
    status = requests.post(url, files=files)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            get_messages(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()