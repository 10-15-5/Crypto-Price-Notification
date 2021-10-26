# <center>Crypto-Price-Notification</center>

Crypto Price Notification system that uses the CoinGecko API to get current price of specific Cryptocurrency and emails it to the user.

Before running this program for the first time the user should update the config.txt files.

User's need to update:
    
    - Sending email's SMTP settings
    - Receiving email
    - Time interval between each run (in seconds)
    - Currency to compare the prices to

If this is the first run, the program will ask the user to enter all the coins that they want to watch (seperated by commas).

Any errors that occur will be added to the logs.log file, this will also hold the info of if the email has been sent successfully.
