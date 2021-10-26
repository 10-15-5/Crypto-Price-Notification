import os
import logging
import configparser
import sys
import smtplib
import csv
import time

from pycoingecko import CoinGeckoAPI

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------------------------------------------------------
#   Logging Setup
# ------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(lineno)d - %(message)s',
                              datefmt='%d-%m-%y %H:%M:%S')

file_handler = logging.FileHandler("settings\\logs.log", encoding='utf8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# ------------------------------------------------------------------

# Config Setup
config = configparser.RawConfigParser()
configFilePath = r"settings/config.txt"
config.read(configFilePath, encoding="utf-8")

# Global Variables
geckoAPI = CoinGeckoAPI()


def get_coins():
    """
        Gets user inputted coins and adds them to a csv file.

        Only gets run on the first run of the program.
        If the coins.csv file isn't found this function will be run
        It asks the user to input the names of the coins they want to track, splitting them up by commas
        It then graps each coin and makes sure that the coin can be found on CoinGecko
        If not an error is returned
        Then adds all coins to a csv and writes them to file
    """
    
    print("\nPlease enter the FULL NAME of the coins you want to get the price of (if getting multiple, seperate them with commas):")
    coins = input().split(",")

    for i in range(len(coins)):
        coins[i] = coins[i].strip()
        response = geckoAPI.get_price(ids=coins[i], vs_currencies=config.get("CONFIG", "VS_CURRENCY"))
        if len(response) == 0:
            print(coins[i] + " doesn't exist on CoinGecko, please try again!")
            sys.exit()

    with open("settings/coins.csv", "w") as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(coins)


def get_crypto_price():
    """
        Reads the coins and returns the price and 24hr change data back to the main function

        First reads the coins from the coins.csv
        It gets the price against the defined vs Currency and the 24hr change
        Adds all the necessary info to a dictionary and returns it to the main function
        Any errors get added to the log files

        Raises
        ------
        TypeError
            Raised when syntax is wrong in code
        KeyError
            Raised when the coin name in the csv is different than the name returned from CoinGecko; happens normally with coins with a space ie. Shiba Inu
        Exception
            Just there to catch any extra exceptions that I may have missed
    """
    
    crypto_list = []

    try:
        with open("settings/coins.csv", "r") as file:
            reader = csv.reader(file)
            coins = next(reader)

        for crypto in coins:
            response = geckoAPI.get_price(ids=crypto, vs_currencies=config.get("CONFIG", "VS_CURRENCY"), include_24hr_change=True,)
            listings = {
                "coin": crypto,
                "price": "{:,}".format(response[crypto.replace(" ", "")][config.get("CONFIG", "VS_CURRENCY").lower()]),
                "change": round(response[crypto.replace(" ", "")][config.get("CONFIG", "VS_CURRENCY").lower() + "_24h_change"], 2)
            }
            crypto_list.append(listings)

        return crypto_list
    except TypeError as e:
        logger.error("Type Error: ", e)
    except KeyError as e:
        logger.error("Key Error for: ", e)
    except Exception as e:
        logger.erorr("General Error: ", e)


def send_email(listings):
    """
        Sends an email to the user with the data for each coin

        Sets up the SMTP connection to the user's email with the details given in config.txt
        Creates a string called msg
        Loops through the listings and adds the details to the msg
        Sends that finished message to the user via email

        Parameters
        -----------
        listings : list, required
            The data for each coin, their price and 24hr change

        Raises
        ------
        Exception
            Raised when something goes wrong with the email being sent. Output gets sent to the logger
    """
    try:
        email_content = "Here is your crypto updates:"
        for i in range(len(listings)):
            # msg += f'\n{listings[i]["coin"]} ->\tPrice:\t{listings[i]["price"]} {config.get("CONFIG", "VS_CURRENCY")}\tChange:\t{listings[i]["change"]}%'
            email_content += "\n" + listings[i]["coin"].upper() + " - >Price: " + str(listings[i]["price"]) + config.get("CONFIG", "VS_CURRENCY") + "-> Change: " + str(listings[i]["change"]) + "%"
        
        smtp = smtplib.SMTP(config.get('CONFIG', 'SMTP_SERVER'), int(config.get('CONFIG', 'SMTP_PORT')))
        smtp.ehlo()
        smtp.starttls()

        smtp.login(config.get('CONFIG', 'SMTP_SENDING_EMAIL'), config.get('CONFIG', 'SMTP_PASSWORD'))

        message = MIMEMultipart()
        message["Subject"] = "Crypto Price Updates"
        message.attach(MIMEText(email_content))

        smtp.sendmail(
            from_addr=config.get('CONFIG', 'SMTP_SENDING_EMAIL'),
            to_addrs=config.get('CONFIG', 'SMTP_RECEIVING_EMAIL'),
            msg=message.as_string()
        )

        logger.info("Email successfully sent to " + config.get('CONFIG', 'SMTP_RECEIVING_EMAIL'))
    except Exception as e:
        logger.error(e)
    finally:
         smtp.quit()



def main():
    if not os.path.isfile("settings/coins.csv"):
        get_coins()

    # infinite loop
    while True:
        pricelistings = get_crypto_price()

        send_email(pricelistings)

        time.sleep(config.get("CONFIG", "TIME_INTERVAL"))


if __name__ == '__main__':
    main()
