import logging
import json
from Class_Article import Article
import pymysql.cursors

with open("conf.json") as f:  ## Add NASDAQ_sql_schema.sql file to conf file
    config = json.load(f)

# logging config
logging.basicConfig(level=logging.INFO, filename="NASDAQ_scraper.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NASDAQ_scraper.log")


def create_database(database_create_code):
    """
    Creates a database for the NASDAQ articles according to the NASDAQ_sql_schema.sql file
    """
    try:
        co = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             cursorclass=pymysql.cursors.DictCursor)  # Probably should ask for password from  user
        with co:
            with co.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS `NASDAQ`')
                cursor.execute('USE `NASDAQ`')
                with open(database_create_code, 'r') as file:
                    sql_script = file.read()
                    queries = sql_script.split(';')
                    for query in queries[:-1]:
                        cursor.execute(query)
                        co.commit()
                logging.info('NASDAQ database was created')

    except FileNotFoundError as er:
        print(f'{er} Please make sure the sql file exists')


def add_author_to_database(author_name, connection):
    """
    Gets author name and adds it to the database
    Returns the authors_id
    """
    cursor = connection.cursor()
    cursor.execute("INSERT IGNORE INTO Authors (author_name) VALUES (%s)", (author_name,))
    connection.commit()
    cursor.execute("SELECT author_id FROM Authors WHERE author_name = %s ", (author_name,))
    author_id = cursor.fetchone()['author_id']
    connection.commit()
    return author_id


def add_article_to_database(author_id, title, article_content, url, published_date, connection):
    """
    Gets author author_id, title, article_content,url, date and adds them to the database
    Returns the article_id
    """
    cursor = connection.cursor()
    sql = """
          INSERT IGNORE INTO Articles (author_id, title, article_content,url,
          published_date) VALUES (%s, %s, %s, %s, %s)
          """
    cursor.execute(sql, (author_id, title, article_content, url, published_date))
    connection.commit()
    cursor.execute("SELECT article_id FROM Articles WHERE url = %s", (url,))
    article_id = cursor.fetchone()['article_id']

    return article_id


def add_tickers_to_database(ticker_list, connection):
    """
    Gets tickers list and adds them to the database
    Returns the list of ticks_ids
    """
    cursor = connection.cursor()
    stock_ids = []
    for tick in ticker_list:
        cursor.execute("INSERT IGNORE INTO Stocks (stock_tick) VALUES (%s)", (tick,))
        connection.commit()
        cursor.execute("SELECT stock_id FROM Stocks WHERE stock_tick = %s", (tick,))
        stock_ids.append(cursor.fetchone()['stock_id'])

    return stock_ids


def add_stock_articles_to_database(article_id, stock_ids, connection):
    """
    Gets stock_ids list, article_id and adds them to the database
    """
    cursor = connection.cursor()
    for stock_id in stock_ids:
        cursor.execute("INSERT IGNORE INTO Stock_Articles (stock_id, article_id) VALUES (%s, %s)",
                       (stock_id, article_id))
        connection.commit()
        cursor.execute("SELECT stock_article_id FROM Stock_Articles WHERE stock_id = %s AND article_id = %s ",
                       (stock_id, article_id))


def add_tags_to_database(tag_list, connection):
    """
    Gets tags list and adds them to the database
    Returns the list of tag_ids
    """
    cursor = connection.cursor()
    tag_ids = []
    for tag_name in tag_list:
        cursor.execute("INSERT IGNORE INTO Tags (tag_name) VALUES (%s)", (tag_name,))
        connection.commit()
        cursor.execute("SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,))
        tag_ids.append(cursor.fetchone()['tag_id'])
    return tag_ids


def add_article_tags_to_database(article_id, tag_ids, connection):
    """
    Gets tag_ids list, article_id and adds them to the database
    """
    cursor = connection.cursor()
    for tag_id in tag_ids:
        cursor.execute("INSERT IGNORE INTO Article_Tags (tag_id, article_id) VALUES (%s, %s)",
                       (tag_id, article_id))
        connection.commit()
        cursor.execute("SELECT article_tag_id FROM Article_Tags WHERE tag_id = %s AND article_id = %s ",
                       (tag_id, article_id))


def get_all_urls(connection):
    """
    get a list of urls currently in the database
    """
    url_list = []
    cursor = connection.cursor()
    cursor.execute("SELECT url FROM Articles")
    query = cursor.fetchall()
    for result in query:
        url_list.append(result['url'])
    return url_list


def update_database(articles_list):  # Function assumes database was created in the main program
    """
    Gets a list of article objects and updates the database with new information.
    """
    if articles_list and type(articles_list) == list:
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='password',
                                     database='NASDAQ',
                                     cursorclass=pymysql.cursors.DictCursor)
        for article in articles_list:
            article_data_dict = article.row_info()

            author_name = article_data_dict['author']
            author_id = add_author_to_database(author_name=author_name, connection=connection)

            title, article_content, url, published_date = article_data_dict['title'], \
                article_data_dict['article_content'], article_data_dict['tags'], article_data_dict['date']
            article_id = add_article_to_database(author_id=author_id, title=title, article_content=article_content,
                                                 url=url, published_date=published_date, connection=connection)

            tickers = article_data_dict['tickers']
            stock_ids = add_tickers_to_database(ticker_list=tickers, connection=connection)

            add_stock_articles_to_database(article_id=article_id, stock_ids=stock_ids, connection=connection)

            tags = article_data_dict['tags']
            tag_ids = add_tags_to_database(tag_list=tags, connection=connection)

            add_article_tags_to_database(article_id=article_id, tag_ids=tag_ids, connection=connection)
            logging.info(f'article "{title}" was added to the database with id: {article_id}')
    else:
        logging.error('articles_list was empty or in the wrong format')


def test():
    create_database('NASDAQ_sql_schema.sql')
    url = "https://www.nasdaq.com/articles/australia-regulator-asks-anz-to-justify-benefits-of-%243.3-bln-suncorp-deal"
    id_num = 4
    title = "Australia regulator asks ANZ to justify benefits of $3.3 bln Suncorp deal"
    author = 'Chris Broad'
    date = "April 03, 2023 — 09:28 pm EDT"
    tags = ['Markets']
    tickers = ['NAPA', 'SABR']
    article_content = """
    April 03, 2023 — 09:28 pm EDT
    
          Written by
                            Scott Murdoch for                             
            
    
    
    
    
    Reuters ->
    
    
    By Scott Murdoch
    SYDNEY, April 4 (Reuters) - Australia's competition regulator said it had asked ANZ Group ANZ.AX to further justify the public benefits of its proposed A$4.9 billion ($3.32 billion) takeover of rival Suncorp's SUN.AX banking business ahead of a formal decision on the deal's future.
    The Australian Competition and Consumer Commission (ACCC) on Tuesday asked both parties to submit more information before a final ruling is delivered by June 12.
    ANZ, Australia's fourth-largest bank by market capitalisation, last July announced plans to buy the banking arm of the Queensland-based regional bank and insurance group Suncorp to help grow its mortgage book.
    The deal requires ACCC approval and sign-off from the Queensland government and Australia's federal treasurer.
    In a report published Tuesday, the ACCC said its preliminary view was the information it had was insufficient to substantiate the "nature, likelihood and extent of the claimed public benefits, including ANZ's estimates of future synergies that will be achieved".
    ANZ said when the deal was announced buying Suncorp's banking arm would boost its mortgage book by A$47 billion to A$307 billion and help it reclaim market share lost to its main competitors.
    "Any acquisition of a potential rival by one of the major banks must be closely considered," ACCC deputy chair Mick Keogh said in a statement separate to the report.
    Australia's banking industry is dominated by four large banks, including ANZ.
    Suncorp said in a statement that it would provide a comprehensive response to address the ACCC's concerns and the deal remained in the best interests of the company. Suncorp will become a pure insurance firm if the deal is completed.
    ANZ did not immediately respond to a Reuters request for comment.
    ($1 = 1.4738 Australian dollars)
    (Reporting by Scott Murdoch; Editing by Jamie Freed)
    ((Scott.Murdoch@thomsonreuters.com;))
    The views and opinions expressed herein are the views and opinions of the author and do not necessarily reflect those of Nasdaq, Inc.
    
    © 2023, Nasdaq, Inc. All Rights Reserved.
    
    
    
    
    
    
    
    
    
    
    To add symbols:
    
    
    These symbols will be available throughout the site during your session.
    To add symbols:
    
    
    These symbols will be available throughout the site during your session.
    """
    art1 = Article(id_num=id_num, title=title, url=url, author=author, tickers=tickers, article_content=article_content,
                   date=date, tags=tags)
    update_database([art1])


def main():
    test()


if __name__ == "__main__":
    main()