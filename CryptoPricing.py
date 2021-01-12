import requests
import time
from pycoingecko import CoinGeckoAPI

# global variables
bot_token = "Insert your bot token here"
chat_id = "Insert you Telegram chat ID here"
threshold = 20000   # You will get a special message if the price goes below this number
time_interval = 3600  # in seconds


def get_crypto_price(btcpricelist, ethpricelist, ltcpricelist, xtzpricelist, xmrpricelist):

    geckoAPI = CoinGeckoAPI()
    response = geckoAPI.get_price(ids=["bitcoin", "litecoin", "ethereum", "tezos", "monero"], vs_currencies="eur")
    btcpricelist.append(response["bitcoin"]["eur"])
    ltcpricelist.append(response["litecoin"]["eur"])
    ethpricelist.append(response["ethereum"]["eur"])
    xtzpricelist.append(response["tezos"]["eur"])
    xmrpricelist.append(response["monero"]["eur"])
    return btcpricelist, ltcpricelist, ethpricelist, xtzpricelist, xmrpricelist


# fn to send_message through telegram
def send_message(chat_id, msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}"

    # send the msg
    requests.get(url)


def format_msg(pricelisting):
    difflisting = []
    for i in range(len(pricelisting)):
        diff = round(pricelisting[i][1] - pricelisting[i][0], 2)
        difflisting.append(diff)

    msg = f'Here is your hourly crypto update:' \
          f'\nBtc: {pricelisting[0][0]}€ -> {pricelisting[0][1]}€ = {difflisting[0]}€!' \
          f'\nLtc: {pricelisting[1][0]}€ -> {pricelisting[1][1]}€ = {difflisting[1]}€!' \
          f'\nEth: {pricelisting[2][0]}€ -> {pricelisting[2][1]}€ = {difflisting[2]}€!' \
          f'\nXtz: {pricelisting[3][0]}€ -> {pricelisting[3][1]}€ = {difflisting[3]}€!' \
          f'\nXmr: {pricelisting[4][0]}€ -> {pricelisting[4][1]}€ = {difflisting[4]}€!'

    return msg


def main():
    btcpricelist = []
    ethpricelist = []
    ltcpricelist = []
    xtzpricelist = []
    xmrpricelist = []

    # infinite loop
    while True:
        pricelistings = get_crypto_price(btcpricelist, ethpricelist, ltcpricelist, xtzpricelist, xmrpricelist)

        # if the price falls below threshold, send an immediate msg
        """if price < threshold:
            send_message(chat_id=chat_id, msg=f'BTC Price Drop Alert: {price}')"""

        # send last 6 btc price
        if len(pricelistings[0]) >= 2:
            msg = format_msg(pricelistings)
            send_message(chat_id=chat_id, msg=msg)
            # empty the price_list
            for i in range(len(pricelistings)):
                del pricelistings[i][0]

        # fetch the price for every dash minutes
        time.sleep(time_interval)


if __name__ == '__main__':
    main()
