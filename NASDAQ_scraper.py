import logging
import os

if not os.path.exists("logs"):
    os.makedirs("logs")
import pymysql.cursors
import gevent.monkey

if not gevent.monkey.saved:
    gevent.monkey.patch_all()
import grequests
from bs4 import BeautifulSoup
import json
from Class_Article import Article
import argparse
import dateparser
import NASDAQ_datacollecter
import API_datacollector

# logging config
logger = logging.getLogger("NASDAQ_scraper")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/NASDAQ_scraper.log", mode="w")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

with open("conf.json") as f:
    config = json.load(f)


def scrape_page(url, args):
    """
    gathers articles urls from a NASDAQ articles web page.
    """
    logger.info('Scrape Page Phase')
    soup = BeautifulSoup(url.text, 'html.parser')
    pages = [f"https://www.nasdaq.com{a['href']}" for a in soup.find_all('a', class_="content-feed__card-title-link")]
    times = soup.find_all('div', class_='content-feed__card-timestamp')
    if args.time is not None:
        for i, time in enumerate(times[0:-2:2]):
            if dateparser.parse(time.text) < args.time:
                return True, pages[:i - 1]
    return False, pages[:len(pages) - 1]


def get_response(urls):
    """
    using grequests threads to get responses from several web pages at a time.
    """
    logger.info(f'Sending the following urls to grequests\n{urls}')
    headers = {'User-agent': config["HEADERS"]}
    request = [grequests.get(url, headers=headers, timeout=config['TIMEOUT']) for url in urls]
    responses = grequests.map(request)
    logger.info(f"Got these responses:\n{responses}")
    responses = [res for res in responses if res]
    return responses


def batch_url_list(pages, i):
    """
    Returns list containing a batch of urls.
    """
    logger.info('Batch URL Phase')
    if pages - i < 10:
        ten_pages = [f'https://www.nasdaq.com/news-and-insights/topic/markets/page/{j}' for j in
                     range(i, i + (pages - i + 1))]
        logger.info(f'successfully created links batch number: {pages}.\n The links: '
                    f'{ten_pages}')

    else:
        ten_pages = [f'https://www.nasdaq.com/news-and-insights/topic/markets/page/{j}' for j in
                     range(i, i + config["BATCH_SIZE"])]
        logger.info(f'successfully created links batch number: {i // config["BATCH_SIZE"] + 1}.\n The links: '
                    f'{ten_pages}')
    return ten_pages


def responses_batch(ten_pages):
    """
    Returns responses from urls in batches of 10.
    """
    logger.info('Responses Batch Phase')
    try:
        responses = get_response(ten_pages)
        if responses:
            logger.info(f'Got responses from server for the urls: {ten_pages}')
        else:
            print(f'{responses} Responses returned None for {ten_pages}')
            logger.error(f"Responses returned None {ten_pages}")
    except Exception as err:
        logger.error(f"error getting responses from pages: {ten_pages}")
        raise RuntimeError(f"error getting responses: {err}")
    return responses


def fetch_articles_urls(args):
    """
    creates the article pages urls in batches according to the conf file and calls the get_response (server response) and scrape_page
    functions.
    """
    logger.info('Fetch Articles Phase')
    new_links = []

    for i in range(1, args.pages + 1, config["BATCH_SIZE"]):
        ten_pages = batch_url_list(args.pages, i)
        responses = responses_batch(ten_pages)
        for url in responses:
            if url.status_code == config["STATUS_CODE"]:

                stop, scraped_pages = scrape_page(url, args)
                if scraped_pages:
                    logger.info(f"successfully scraped {scraped_pages}\n")
                    new_links = new_links + scraped_pages
                else:
                    logger.error(f"could not scrape response page")
                if stop:
                    print(f'Batch number {i // config["BATCH_SIZE"] + 1}/100 done')
                    return new_links
            else:
                logger.error(f"Request failed with status code: {url.status_code}")
    print(f"successfully scraped {len(new_links)}")
    return new_links


def setting_info(article_list, connection):
    """
    Takes a list of Article objects and creates a dataframe with the article information.
    Prints the article short information without the content.
    The article content will be saved into a text file in a sub-folder named "article content files".
    """
    logger.info('Setting Info Phase')
    headers = {'User-agent': config["HEADERS"]}
    try:
        logger.info('Setting Info Phases Started')
        rs = (grequests.get(t.url, headers=headers, timeout=config['TIMEOUT']) for t in article_list)
        logger.info(f'successfully got responses from server')
    except Exception as err:
        logger.error(f"error getting responses from server: {err}")
        raise RuntimeError(f"error getting responses: {err}")

    countdown = 0

    article_object_info = []
    for response in grequests.imap(rs, size=config["BATCH_SIZE"]):
        if response.status_code == config["STATUS_CODE"]:
            article = next((t for t in article_list if t.url == response.url), None)
            if article:
                # Parses the HTML content and returns a soup object.
                soup = BeautifulSoup(response.content, "html.parser")
                article.set_info(soup)
                print(article)
                logger.info(f"successfully scraped {article.title}\n")

                # concat to object list

                article_object_info.append(article)
                countdown += 1
                if countdown >= config["INSERT"]:
                    NASDAQ_datacollecter.update_database(article_object_info, connection)
                    article_object_info = []
                    countdown = 0
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
    NASDAQ_datacollecter.update_database(article_object_info, connection)


def get_articles(links_list):
    """
    Returns a list of Article objects containing the id number and URL of an article.
    """
    logger.info('Get Articles Phase')
    article_list = [Article(index, url) for index, url in enumerate(links_list)]
    return article_list


def parse():
    """
    parsing arguments from command line
    """
    logger.info('Parse Phase')
    parser = argparse.ArgumentParser(prog='NASDAQ_scraper',
                                     description='web scraper for NASDAQ website',
                                     epilog='for further information please see README.md file')
    parser.add_argument('--scrape_all', action='store_true', help="scrape all pages and info")
    parser.add_argument('--update', action='store_true', help="update prices from API")
    parser.add_argument('-pages', type=int, help="scrape x pages (starting from first)", default=config['PAGES'])
    parser.add_argument('-time', type=dateparser.parse, help="scrape pages x days back till today",
                        default=None)
    args = parser.parse_args()

    if args.scrape_all:  # if the user decides to enter scrape all with other arguments
        args.pages = config['PAGES']
        args.time = None

    return args


def main():
    args = parse()
    logger.info(f'Args input: {args}')
    try:
        connection = pymysql.connect(host=config["HOST"],
                                     user=config["USER"],
                                     password=config["PASSWORD"],
                                     database=config["DB"],
                                     cursorclass=pymysql.cursors.DictCursor)
        logger.info('Connection to mysql server')
        NASDAQ_datacollecter.create_database(config["DB_COMMANDS_FILE"], connection)
        if args.update:
            logger.info("Updating stock prices")
            API_datacollector.update_stock_prices(connection)
        else:
            new_links = fetch_articles_urls(args)  # Gets list of urls to scrape
            urls = NASDAQ_datacollecter.get_all_urls(connection)  # Gets list of urls that exists in the database

            new_links = list(set(new_links) - set(urls))  # Keeps only the links that don't exist in the database
            logger.info(f"Collected {len(new_links)} new links")
            get_objects = get_articles(new_links)
            setting_info(get_objects, connection)
            print('Updating Tickers')
            logger.info("Adding new tickers to database")
            API_datacollector.new_tickers(connection)
    except Exception as err:
        print(f'Error: {err}')


if __name__ == "__main__":
    main()
