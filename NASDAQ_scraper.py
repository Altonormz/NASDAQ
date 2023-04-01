import argparse
import datetime
import dateparser

from gevent import monkey

monkey.patch_all()
import grequests
from bs4 import BeautifulSoup
import json
import logging
from Class_Article import Article

with open("conf.json") as f:
    config = json.load(f)

# logging config
logging.basicConfig(level=logging.INFO, filename="NASDAQ_scraper.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NASDAQ_scraper.log")


def scrape_page(URL):
    """
    gathers articles urls from a NASDAQ articles web page
    """
    soup = BeautifulSoup(URL.text, 'html.parser')
    pages = [f"https://www.nasdaq.com{a['href']}" for a in soup.find_all('a', class_="content-feed__card-title-link")]
    return pages[:len(pages) - 1]


def get_response(urls):
    """
    using grequests threads to get responses from several web pages at a time
    """
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/75.0.3770.142 Safari/537.36'}
    request = [grequests.get(url, headers=headers) for url in urls]
    responses = grequests.map(request)
    return responses


def save_links(links_list):
    """
    Save the links into a file
    """
    with open(f'links_list.txt', 'w') as f:
        for link in links_list:
            f.write(link + '\n')

    print('Finished making the file')


def fetch_articles_urls():
    """
    creates the article pages urls in batches of 10 and calls the get_response (server response) and scrape_page
    functions
    """
    new_links = []

    for i in range(1, config["PAGES"], config["BATCH_SIZE"]):

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
            if url.status_code == 200:

                scraped_pages = scrape_page(url)
                if scraped_pages:
                    logging.info(f"successfully scraped {scraped_pages}\n")
                else:
                    logging.error(f"could not scrape response page")
                new_links = new_links + scraped_pages

            else:
                logging.error(f"Request failed with status code: {url.status_code}")

        print(f'Batch number {i // config["BATCH_SIZE"] + 1}/100 done')
    print(new_links)
    save_links(new_links)


def calculate_date(days):
    return datetime.datetime.today() - datetime.timedelta(days)


def parse():
    parser = argparse.ArgumentParser(prog='NASDAQ_scraper',
                                     description='web scraper for NASDAQ website',
                                     epilog='for further information please see README.md file')
    parser.add_argument('--scrape_all', action='store_true', help="scrape all pages and info")
    parser.add_argument('-pages', type=int, help="scrape x pages (starting from first)", default=1000)
    parser.add_argument('-days', type=int, help="scrape pages s days back till today", default=30)
    args = parser.parse_args()
    args.days = calculate_date(args.days)
    return args


def scraper_main():
    try:
        args = parse()
        fetch_articles_urls()  # creates file with articles urls.
        Class_Article.main()  # Creates DataFrame with articles info, and saves their content in a sub-folder.
    except Exception as err:
        print(f'Error: {err}')


if __name__ == "__main__":
    scraper_main()


### Start of class_article functions.
def get_soup(response):
    """
    Parses the HTML content and returns a soup object.
    """
    return BeautifulSoup(response.content, "html.parser")


def setting_info(article_list, df, config):
    """
    Takes a list of Article objects and creates a dataframe with the article information.
    Prints the article short information without the content.
    The article content will be saved into a text file in a sub-folder named "article content files".
    """
    ua = UserAgent()
    headers = {'user-agent': ua.random}
    try:
        rs = (grequests.get(t.url, headers=headers, timeout=config['TIMEOUT']) for t in article_list)
        logging.info(f'successfully got responses from server')
    except Exception as err:
        logging.error(f"error getting responses from server")
        raise RuntimeError(f"error getting responses: {err}")

    countdown = 0

    for response in grequests.imap(rs, size=config["BATCH_SIZE"]):
        if response.status_code == 200:
            article = next((t for t in article_list if t.url == response.url), None)
            if article:
                article.set_info(response)
                print(article)
                logging.info(f"successfully scraped {article.title}\n")

                new_row_df = pd.DataFrame([article.row_info()])
                df = pd.concat([df, new_row_df], ignore_index=True)
                countdown += 1
                if countdown >= 500:
                    df.to_csv('article_info.csv', index=False)
                    countdown = 0
                else:
                    logging.error(f"Request failed with status code: {response.status_code}")
            else:
                logging.error(f"Request failed with status code: {response.status_code}")

    df.to_csv('article_info.csv', index=False)


def get_articles():
    """
    Returns a list of Article objects containing the id number and URL of an article.
    """
    try:
        with open('links_list.txt', 'r') as f:
            links_list = f.read().splitlines()
            article_list = [Article(index, url) for index, url in enumerate(links_list)]
            return article_list

    except FileNotFoundError as er:
        logging.error(f"{er}: links_list.txt wasn't found")
        return []


def main():
    try:
        with open("conf.json") as f:
            config = json.load(f)
    except FileNotFoundError as er:
        print(f'{er}: Please make sure config file exists in the folder.')
        return

    article_list = get_articles()
    columns = ['id', 'title', 'authors', 'date', 'tags', 'URL']
    df = pd.DataFrame(columns=columns)
    setting_info(article_list, df, config)


if __name__ == "__main__":
    main()
