import logging
import json
import requests
import pandas as pd
import pymysql.cursors
import time

with open("conf.json") as f:
    config = json.load(f)

# logging config
logger = logging.getLogger("API_datacollector")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs/API_datacollector.log", mode="w")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def start_sql_connection():
    """
    Returns connection to MySQL, using the user and password from the config file.
    """
    connection = pymysql.connect(host='localhost',
                                 user=config["USER"],
                                 password=config["PASSWORD"],
                                 database='NASDAQ',
                                 cursorclass=pymysql.cursors.DictCursor)
    logger.info("Connection started to SQL")
    return connection


def check_database_exists(connection):
    """
    Returns True if the database and required tables exist, else returns False.
    """
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES LIKE 'Stocks'")
    stocks_exists = cursor.fetchone()
    cursor.execute("SHOW TABLES LIKE 'Stocks_Prices'")
    stocks_prices_exists = cursor.fetchone()
    logger.info(f"stocks_exists and stocks_prices_exists: {stocks_exists} and {stocks_prices_exists}")
    return stocks_exists and stocks_prices_exists


def call_info_stocks_api(ticker, info_token_flag):
    """
    Returns DataFrame containing the information about the ticker.
    Returns a boolean flag representing if the queries are spent from the token.
    """
    tick_info = []
    info_token = config['API']['info_token']
    api_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={info_token}"
    response = requests.get(api_url)
    response = response.json()

    if 'Note' in response:
        info_token_flag = False
    if info_token_flag:
        tick_info.append(response)
    tick_info_df = pd.DataFrame(tick_info)
    return tick_info_df, info_token_flag


def call_price_stocks_api(ticker, price_token_flag):
    """
    Returns DataFrame containing the information about the ticker prices.
    Returns a boolean flag representing if the queries are spent from the token.
    """
    tick_prices_df = pd.DataFrame({})
    price_token = config['API']['price_token']
    api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize" \
              f"=compact&apikey={price_token}"
    response = requests.get(api_url)
    response = response.json()
    if 'Note' in response:
        price_token_flag = False
    if price_token_flag:

        if response:
            tick_prices_df = pd.DataFrame(response["Time Series (Daily)"]).T

    return tick_prices_df, price_token_flag


def update_stocks(tick_info, connection):
    """
    Gets a DataFrame containing the ticker information, and updates the Stocks Table using the information.
    """
    for i, row in tick_info.iterrows():
        cursor = connection.cursor()
        cursor.execute(f'UPDATE Stocks SET name = %s, currency = %s, country = %s, sector = %s, industry = %s '
                       f'WHERE stock_tick = %s;', (row['Name'], row['Currency'], row['Country'], row['Sector'],
                                                   row['Industry'], row['Symbol'],))
        connection.commit()


def insert_stock_prices(prices, ticker, connection):
    """
    Gets a DataFrame containing the ticker prices and name, and updates the Stocks Table using the information.
    """
    cursor = connection.cursor()
    cursor.execute('SELECT stock_id FROM Stocks where stock_tick = %s', (ticker,))
    stock_id = cursor.fetchone()['stock_id']
    for i, row in prices.iterrows():
        cursor.execute("INSERT INTO Stocks_Prices (stock_id, date, open, high, low, close, volume) VALUES (%s,"
                       " %s, %s, %s, %s, %s, %s)", (stock_id, row.name, row['1. open'], row['2. high'], row['3. low'],
                                                    row['4. close'], row['6. volume']))
        connection.commit()


def update_stock_prices():
    """
    Updates the Table Stocks_Prices, with the most recent available prices without duplicates.
    """

    connection = start_sql_connection()
    if not check_database_exists(connection):
        logger.error("Database or required tables do not exist.")
        return

    cursor = connection.cursor()
    # Query to get the last date the price was updated with the ticker name.
    cursor.execute("SELECT jj.stock_tick AS stock_tick, jj.MAX_DATE AS last_date FROM ("
                   "SELECT j.stock_tick AS stock_tick, DATE(MAX(j.date)) AS MAX_DATE FROM ("
                   "SELECT stock_tick, date FROM Stocks_Prices LEFT JOIN Stocks ON "
                   "Stocks_Prices.stock_id = Stocks.stock_id) AS j GROUP BY j.stock_tick ORDER BY MAX(date)) AS jj "
                   "WHERE jj.MAX_DATE < CURDATE()")
    last_prices = pd.DataFrame(cursor.fetchall())
    if last_prices.empty:
        logger.info("No stock tickers available for update.")
        return
    price_token_flag = True
    for i, ticker in enumerate(last_prices['stock_tick']):
        if price_token_flag:
            tick_prices_df, price_token_flag = call_price_stocks_api(ticker, price_token_flag)
            if not tick_prices_df.empty:
                last_prices['last_date'] = pd.to_datetime(last_prices['last_date'])
                tick_prices_df.index = pd.to_datetime(tick_prices_df.index)
                tick_prices_df_new = tick_prices_df[tick_prices_df.index > last_prices['last_date'][i]]
                insert_stock_prices(tick_prices_df_new, ticker, connection)
                logger.info(f' "{ticker}" was updated in the Stocks_Prices table.')


def new_tickers():
    """
    Adds the tickers Information and stock prices to DataBase for stocks with no information.
    """
    connection = start_sql_connection()
    if not check_database_exists(connection):
        logger.error("Database or required tables do not exist.")
        return

    cursor = connection.cursor()
    cursor.execute('SELECT stock_tick FROM Stocks where name IS NULL')
    tickers = cursor.fetchall()
    tickers = [ticker['stock_tick'] for ticker in tickers]
    for i, ticker in enumerate(tickers):
        info_token_flag = True
        if i > config['API']['query_limit']:
            break
        if (i > 0) and (i % 2 == 0):
            time.sleep(config['API']['sleep_time'])

        if info_token_flag:
            tick_info_df, info_token_flag = call_info_stocks_api(ticker, info_token_flag)
            if not tick_info_df.empty:
                update_stocks(tick_info_df, connection)
                logger.info(f' "{ticker}" was updated in the Stocks table. ')

        price_token_flag = True
        if price_token_flag:
            tick_prices_df, price_token_flag = call_price_stocks_api(ticker, price_token_flag)
            if not tick_prices_df.empty:
                insert_stock_prices(tick_prices_df, ticker, connection)
                logger.info(f' "{ticker}" was updated in the Stocks_Prices table. ')





