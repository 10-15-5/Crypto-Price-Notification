import requests
import time
from pycoingecko import CoinGeckoAPI

# global variables
bot_token = "Add your Telegram bot token here"
chat_id = "Add your chat ID here"
threshold = 20000   # You will get a special message if the price goes below this number
time_interval = 3600  # in seconds


def get_crypto_price():

    geckoAPI = CoinGeckoAPI()
    response = geckoAPI.get_price(ids="bitcoin", vs_currencies="eur")
    return response["bitcoin"]["eur"]


# fn to send_message through telegram
def send_message(chat_id, msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}"

    # send the msg
    requests.get(url)


def format_msg(price_list):
    pricefirst = round(price_list[0], 2)
    pricesecond = round(price_list[1], 2)
    diff = round(pricesecond - pricefirst, 2)

    msg = f'The price of Btc at the start was {pricefirst}€ and the price at the end was {pricesecond}€! The price of Btc changed {diff}€ during this time!'

    return msg


def main():
    price_list = []

    # infinite loop
    while True:
        price = get_crypto_price()
        price_list.append(price)

        # if the price falls below threshold, send an immediate msg
        if price < threshold:
            send_message(chat_id=chat_id, msg=f'BTC Price Drop Alert: {price}')

        # send last 6 btc price
        if len(price_list) >= 2:
            msg = format_msg(price_list)
            send_message(chat_id=chat_id, msg=msg)
            # empty the price_list
            del price_list[0]

        # fetch the price for every dash minutes
        time.sleep(time_interval)


if __name__ == '__main__':
    main()
