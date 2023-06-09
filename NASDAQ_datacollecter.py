import logging
import json
import dateparser


with open("conf.json") as f:
    config = json.load(f)

# logging config

logger = logging.getLogger("NASDAQ_datacollector")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/NASDAQ_datacollector.log", mode="w")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def create_database(database_create_code, connection):
    """
    Creates a database for the NASDAQ articles according to the NASDAQ_sql_schema.sql file.
    """
    try:
        cursor = connection.cursor()
        logger.info('Creating database')
        with open(database_create_code, 'r') as file:
            sql_script = file.read()
            queries = sql_script.split(';')
            for query in queries[:-1]:
                cursor.execute(query)
        connection.commit()
        logger.info('Database was created')

    except FileNotFoundError as er:
        print(f'{er} Please make sure the sql file exist')


def add_author_to_database(author_name, connection):
    """
    Gets author name and adds it to the database.
    Returns the authors_id.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT author_id FROM Authors WHERE author_name = %s", (author_name,))
    result = cursor.fetchone()
    if result:
        return result['author_id']
    else:
        cursor.execute("INSERT INTO Authors (author_name) VALUES (%s)", (author_name,))
        connection.commit()
        cursor.execute("SELECT author_id FROM Authors WHERE author_name = %s ", (author_name,))
        author_id = cursor.fetchone()['author_id']
        connection.commit()
        return author_id


def add_article_to_database(author_id, title, article_content, url, published_date, connection):
    """
    Gets author author_id, title, article_content,url, date and adds them to the database.
    Returns the article_id.
    """
    cursor = connection.cursor()
    published_date = dateparser.parse(published_date)
    sql = """
          INSERT INTO Articles (author_id, title, article_content,url,
          published_date) VALUES (%s, %s, %s, %s, %s)
          """
    cursor.execute(sql, (author_id, title, article_content, url, published_date))
    connection.commit()
    cursor.execute("SELECT article_id FROM Articles WHERE url = %s", (url,))
    article_id = cursor.fetchone()['article_id']
    return article_id


def add_tickers_to_database(ticker_list, connection):
    """
    Gets tickers list and adds them to the database.
    Returns the list of ticks_ids.
    """
    logger.info(f'Adding {len(ticker_list)} tickers to the database')
    cursor = connection.cursor()
    stock_ids = []
    for tick in ticker_list:
        cursor.execute("SELECT stock_id FROM Stocks WHERE stock_tick = %s", (tick,))
        result = cursor.fetchone()
        if result:
            stock_ids.append(result['stock_id'])
        else:
            cursor.execute("INSERT INTO Stocks (stock_tick) VALUES (%s)", (tick,))
            connection.commit()
            cursor.execute("SELECT stock_id FROM Stocks WHERE stock_tick = %s", (tick,))
            stock_ids.append(cursor.fetchone()['stock_id'])

    return stock_ids


def add_stock_articles_to_database(article_id, stock_ids, connection):
    """
    Gets stock_ids list, article_id and adds them to the database.
    """
    cursor = connection.cursor()
    for stock_id in stock_ids:
        cursor.execute("INSERT INTO Stock_Articles (stock_id, article_id) VALUES (%s, %s)",
                       (stock_id, article_id))
        connection.commit()


def add_tags_to_database(tag_list, connection):
    """
    Gets tags list and adds them to the database.
    Returns the list of tag_ids.
    """
    cursor = connection.cursor()
    tag_ids = []
    for tag_name in tag_list:
        cursor.execute("SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,))
        result = cursor.fetchone()
        if result:
            tag_ids.append(result['tag_id'])
        else:
            cursor.execute("INSERT INTO Tags (tag_name) VALUES (%s)", (tag_name,))
            connection.commit()
            cursor.execute("SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,))
            tag_ids.append(cursor.fetchone()['tag_id'])
    return tag_ids


def add_article_tags_to_database(article_id, tag_ids, connection):
    """
    Gets tag_ids list, article_id and adds them to the database.
    """
    cursor = connection.cursor()
    for tag_id in tag_ids:
        cursor.execute("INSERT INTO Article_Tags (tag_id, article_id) VALUES (%s, %s)",
                       (tag_id, article_id))
        connection.commit()


def get_all_urls(connection):
    """
    get a list of urls currently in the database.
    """
    logger.info("Getting url links")
    url_list = []
    cursor = connection.cursor()
    cursor.execute("SELECT url FROM Articles")
    query = cursor.fetchall()
    if query:
        for result in query:
            url_list.append(result['url'])
    logger.info(f"Found {len(url_list)} url links")
    return url_list


def update_database(articles_list, connection):  # Function assumes database was created in the main program
    """
    Gets a list of article objects and updates the database with new information.
    """
    logger.info(f'Number of articles: {len(articles_list)}')
    if articles_list and type(articles_list) == list:
        for article in articles_list:
            article_data_dict = article.row_info()

            author_name = article_data_dict['author']
            author_id = add_author_to_database(author_name=author_name, connection=connection)

            title, article_content, url, published_date = article_data_dict['title'], \
                article_data_dict['article_content'], article_data_dict['url'], article_data_dict['date']
            article_id = add_article_to_database(author_id=author_id, title=title, article_content=article_content,
                                                 url=url, published_date=published_date, connection=connection)

            tickers = article_data_dict['tickers']
            stock_ids = add_tickers_to_database(ticker_list=tickers, connection=connection)

            add_stock_articles_to_database(article_id=article_id, stock_ids=stock_ids, connection=connection)

            tags = article_data_dict['tags']
            tag_ids = add_tags_to_database(tag_list=tags, connection=connection)

            add_article_tags_to_database(article_id=article_id, tag_ids=tag_ids, connection=connection)
            logger.info(f'article "{title}" was added to the database with id: {article_id}')
    else:
        logger.error(f'articles_list was empty or in the wrong format\n{articles_list}')