import logging
import pymysql.cursors
import gevent.monkey
if not gevent.monkey.saved:
    gevent.monkey.patch_all()
import grequests
from bs4 import BeautifulSoup
import json
from Class_Article import Article
from fake_useragent import UserAgent
import argparse
import dateparser
import NASDAQ_datacollecter
import API_datacollector


# logging config
logging.basicConfig(level=logging.INFO, filename="NASDAQ_scraper.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NASDAQ_scraper.log")

with open("conf.json") as f:
    config = json.load(f)



def scrape_page(URL, args):
    """
    gathers articles urls from a NASDAQ articles web page
    """
    logging.info(f'Scraping url: {URL}')
    soup = BeautifulSoup(URL.text, 'html.parser')
    pages = [f"https://www.nasdaq.com{a['href']}" for a in soup.find_all('a', class_="content-feed__card-title-link")]
    times = soup.find_all('div', class_='content-feed__card-timestamp')
    if args.time is not None:
        for i, time in enumerate(times[0:-2:2]):
            if dateparser.parse(time.text) < args.time:
                return True, pages[:i - 1]
    return False, pages[:len(pages) - 1]


def get_response(urls):
    """
    using grequests threads to get responses from several web pages at a time
    """
    ua = UserAgent()
    logging.info(f'Sending the following urls to grequests\n{urls}')
    headers = {'user-agent': ua.random}
    request = [grequests.get(url, headers=headers) for url in urls]
    responses = grequests.map(request)
    return responses


def fetch_articles_urls(args):
    """
    creates the article pages urls in batches of 10 and calls the get_response (server response) and scrape_page
    functions
    """
    new_links = []

    for i in range(1, args.pages + 1, config["BATCH_SIZE"]):
        if args.pages - i < 10:
            ten_pages = [f'https://www.nasdaq.com/news-and-insights/topic/markets/page/{j}' for j in
                         range(i, i + (args.pages - i + 1))]
            logging.info(f'successfully created links batch number: {args.pages}.\n The links: '
                         f'{ten_pages}')
        else:
            ten_pages = [f'https://www.nasdaq.com/news-and-insights/topic/markets/page/{j}' for j in
                         range(i, i + config["BATCH_SIZE"])]
            logging.info(f'successfully created links batch number: {i // config["BATCH_SIZE"] + 1}.\n The links: '
                         f'{ten_pages}')
        try:
            responses = get_response(ten_pages)
            logging.info(f'successfully got responses from server for the urls: {ten_pages}')
        except Exception as err:
            logging.error(f"error getting responses from pages: {ten_pages}")
            raise RuntimeError(f"error getting responses: {err}")

        for url in responses:
            if url.status_code == config["STATUS_CODE"]:

                stop, scraped_pages = scrape_page(url, args)
                if scraped_pages:
                    logging.info(f"successfully scraped {scraped_pages}\n")
                else:
                    logging.error(f"could not scrape response page")
                new_links = new_links + scraped_pages
                if stop:
                    print(f'Batch number {i // config["BATCH_SIZE"] + 1}/100 done')
                    return new_links
            else:
                logging.error(f"Request failed with status code: {url.status_code}")
    return new_links


def get_soup(response):
    """
    Parses the HTML content and returns a soup object.
    """
    return BeautifulSoup(response.content, "html.parser")


def setting_info(article_list):
    """
    Takes a list of Article objects and creates a dataframe with the article information.
    Prints the article short information without the content.
    The article content will be saved into a text file in a sub-folder named "article content files".
    """
    ua = UserAgent()
    headers = {'user-agent': ua.random}
    try:
        logging.info('Setting Info Phases Started')
        rs = (grequests.get(t.url, headers=headers, timeout=config['TIMEOUT']) for t in article_list)
        logging.info(f'successfully got responses from server')
    except Exception as err:
        logging.error(f"error getting responses from server")
        raise RuntimeError(f"error getting responses: {err}")

    countdown = 0

    article_object_info = []
    for response in grequests.imap(rs, size=config["BATCH_SIZE"]):
        if response.status_code == config["STATUS_CODE"]:
            article = next((t for t in article_list if t.url == response.url), None)
            if article:
                soup = get_soup(response)
                article.set_info(soup)
                print(article)
                logging.info(f"successfully scraped {article.title}\n")

                # concat to object list

                article_object_info.append(article)
                countdown += 1
                if countdown >= config["INSERT"]:
                    NASDAQ_datacollecter.update_database(article_object_info)
                    article_object_info = []
                    countdown = 0
                else:
                    logging.error(f"Request failed with status code: {response.status_code}")
            else:
                logging.error(f"Request failed with status code: {response.status_code}")
    NASDAQ_datacollecter.update_database(article_object_info)

    # df.to_csv('article_info.csv', index=False)


def get_articles(links_list):
    """
    Returns a list of Article objects containing the id number and URL of an article.
    """

    article_list = [Article(index, url) for index, url in enumerate(links_list)]
    return article_list


def parse():
    """
    parsing arguments from command line
    """
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
    try:
        args = parse()
        NASDAQ_datacollecter.create_database(config["DB_COMMANDS_FILE"])
        if args.update:
            API_datacollector.update_stock_prices()
        else:

            co = pymysql.connect(host='localhost',
                                 user=config["USER"],
                                 password=config["PASSWORD"],
                                 database='NASDAQ',
                                 cursorclass=pymysql.cursors.DictCursor)
            new_links = fetch_articles_urls(args)  # creates file with articles urls.

            urls = NASDAQ_datacollecter.get_all_urls(co)

            new_links = list(set(new_links) - set(urls))

            get_objects = get_articles(new_links)

            setting_info(get_objects)
            API_datacollector.new_tickers()
            print('Finished Running')
    except Exception as err:
        print(f'Error: {err}')


if __name__ == "__main__":
    main()
