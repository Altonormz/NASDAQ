import logging
import json
import requests
import pandas as pd
import pymysql.cursors
import dateparser
import time
import datetime

with open("conf.json") as f:
    config = json.load(f)

# logging config
logging.basicConfig(level=logging.INFO, filename="NASDAQ_scraper.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NASDAQ_scraper.log")


def start_sql_connection():
    connection = pymysql.connect(host='localhost',
                                 user=config["USER"],
                                 password=config["PASSWORD"],
                                 database='NASDAQ',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def call_info_stocks_api(ticker, info_token_flag):
    tick_info = []
    info_token = config['API']['info_token']
    api_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={info_token}"
    response = requests.get(api_url)
    if 'Note' in response:
        info_token_flag = False
    if info_token_flag:
        tick_info.append(response.json())

    tick_info_df = pd.DataFrame(tick_info)
    return tick_info_df, info_token_flag


def call_price_stocks_api(ticker, price_token_flag):
    tick_prices_df = pd.DataFrame({})
    price_token = config['API']['price_token']
    api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize" \
              f"=compact&apikey={price_token}"
    response = requests.get(api_url)
    if 'Note' in response:
        price_token_flag = False
    if price_token_flag:
        response = response.json()
        if response:
            tick_prices_df = pd.DataFrame(response["Time Series (Daily)"]).T

    return tick_prices_df, price_token_flag
#
# response = requests.get(api_url)
#         response = response.json()
#         prices = pd.DataFrame(response["Time Series (Daily)"]).T


def update_stocks(tick_info, connection):
    for i, row in tick_info.iterrows():
        cursor = connection.cursor()
        cursor.execute(f'UPDATE Stocks SET name = %s, currency = %s, country = %s, sector = %s, industry = %s '
                       f'WHERE stock_tick = %s;', (row['Name'], row['Currency'], row['Country'], row['Sector'],
                                                   row['Industry'], row['Symbol'],))
        connection.commit()


def insert_stock_prices(prices, ticker, connection):
    cursor = connection.cursor()
    cursor.execute('SELECT stock_id FROM Stocks where stock_tick = %s', (ticker,))
    stock_id = cursor.fetchone()['stock_id']
    for i, row in prices.iterrows():
        cursor.execute("INSERT INTO Stocks_Prices (stock_id, date, open, high, low, close, volume) VALUES (%s,"
                       " %s, %s, %s, %s, %s, %s)", (stock_id, row.name, row['1. open'], row['2. high'], row['3. low'],
                                                    row['4. close'], row['6. volume']))
        connection.commit()


def update_stock_prices(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT j.stock_tick, MAX(j.date) FROM ("
                   "SELECT stock_tick, date FROM Stocks_Prices LEFT JOIN Stocks ON "
                   "Stocks_Prices.stock_id = Stocks.stock_id) as j GROUP BY j.stock_tick ORDER BY MAX(date) DESC")
    last_prices = pd.DataFrame(cursor.fetchall())
    print(last_prices)


def new_tickers():
    connection = start_sql_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT stock_tick FROM Stocks where name IS NULL')
    tickers = cursor.fetchall()
    tickers = [ticker['stock_tick'] for ticker in tickers]
    for i, ticker in enumerate(tickers):
        info_token_flag = True
        if i > config['API']['query_limit']:
            break
        if (i > 0) and (i % 3 == 0):
            time.sleep(65)

        if info_token_flag:
            tick_info_df, info_token_flag = call_info_stocks_api(ticker, info_token_flag)
            if not tick_info_df.empty:
                update_stocks(tick_info_df, connection)

        price_token_flag = True
        if price_token_flag:
            tick_prices_df, price_token_flag = call_price_stocks_api(ticker, price_token_flag)
            if not tick_prices_df.empty:
                insert_stock_prices(tick_prices_df, ticker, connection)

        connection.commit()



def emp():

    q = """
    UPDATE Stocks SET name = null, currency = null, country = null, sector = null, industry = null where stock_tick = 'SNY';
    """
    connection = start_sql_connection()
    cursor = connection.cursor()
    cursor.execute(q)
    connection.commit()



new_tickers()
# emp()


