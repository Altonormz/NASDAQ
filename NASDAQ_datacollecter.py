import logging
import json
from Class_Article import Article
import sqlite3
import os
import pandas as pd

with open("conf.json") as f:  ## Add NASDAQ.sql file to conf file
    config = json.load(f)

# logging config
logging.basicConfig(level=logging.INFO, filename="NASDAQ_scraper.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NASDAQ_scraper.log")


def create_dataframe(database_create_code, database_path):
    """
    Creates a dataframe for the NASDAQ articles according to the NASDAQ.sql file
    """
    try:
        co = sqlite3.connect(database_path)
        with open(database_create_code, 'r') as f:
            sql_script = f.read()
            sql_script = sql_script.replace('`', '"')
            queries = sql_script.split(';')
            for query in queries:
                co.cursor().execute(query)
                co.commit()
        logging.info('NASDAQ_database.sqlite file was created in the directory')

    except FileNotFoundError as er:
        print(f'{er} Please make sure the sql file exists')


def add_author_to_database(author_name, connection):
    """
    Gets author name and adds it to the database
    Returns the authors_id
    """
    cursor = connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO Authors (author_name) VALUES (?)", author_name)
    cursor.execute("SELECT author_id FROM Author WHERE ?", author_name)
    author_id = cursor.fetchone()[0]
    return author_id


def add_article_to_database(author_id, title, article_content, url, published_date, connection):
    """
    Gets author author_id, title, article_content,url, date and adds them to the database
    Returns the article_id
    """
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO Articles (author_id, title, article_content,url, published_date) VALUES (?, ?, ?, ?, ?)",
        (author_id, title, article_content, url, published_date))
    cursor.execute("SELECT article_id FROM Articles WHERE ?", url)
    article_id = cursor.fetchone()[0]
    return article_id


def add_stocks_to_database(tickers, connection):
    """
    Gets tickers list and adds them to the database
    Returns the list of ticks_ids
    """
    cursor = connection.cursor()
    tickers_ids = []
    for tick in tickers:
        cursor.execute("INSERT OR IGNORE INTO Stocks (stock_tick) VALUES (?)", tick)
        cursor.execute("SELECT stock_id FROM Stocks WHERE ?", tick)
        tickers_ids.append(cursor.fetchone()[0])
    return tickers_ids


def add_stock_articles_to_database(article_id, stock_ids, connection):
    """
    Gets stock_ids list, article_id and adds them to the database
    """
    cursor = connection.cursor()
    for stock_id in stock_ids:
        cursor.execute("INSERT OR IGNORE INTO Stock_Articles (stock_id, article_id) VALUES (?, ?)",
                       (stock_id, article_id))
        cursor.execute("SELECT stock_article_id FROM Stock_Articles WHERE stock_id = ? AND article_id = ? ",
                       (stock_id, article_id))


def add_tags_to_database(tags, connection):
    """
    Gets tags list and adds them to the database
    Returns the list of tag_ids
    """
    cursor = connection.cursor()
    tag_ids = []
    for tag_name in tags:
        cursor.execute("INSERT OR IGNORE INTO Tags (tag_name) VALUES (?)", tag_name)
        cursor.execute("SELECT tag_id FROM Stocks WHERE ?", tag_name)
        tag_ids.append(cursor.fetchone()[0])
    return tag_ids


def add_article_tags_to_database(article_id, tag_ids, connection):
    """
    Gets tag_ids list, article_id and adds them to the database
    """
    cursor = connection.cursor()
    for tag_id in tag_ids:
        cursor.execute("INSERT OR IGNORE INTO Article_Tags (tag_id, article_id) VALUES (?, ?)",
                       (tag_id, article_id))
        cursor.execute("SELECT stock_article_id FROM Article_Tags WHERE stock_id = ? AND article_id = ? ",
                       (tag_id, article_id))


def get_all_urls(connection):
    """
    get a list of urls currently in the DB
    """
    cursor = connection.cursor()
    return list(cursor.execute("SELECT url FROM Articles"))