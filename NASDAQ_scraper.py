from gevent import monkey

monkey.patch_all()
import grequests
from bs4 import BeautifulSoup
import Class_Article
import json
import logging


with open("conf.json") as f:
    config = json.load(f)

# logging config
logging.basicConfig(level=logging.INFO, filename="NASDAQ_scraper.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NASDAQ_scraper.log")


def scrape_page(URL):
    """
    gathers articles urls from a NASDAQ articles web page
    :param URL: response from server
    :return: articles urls (beside the last one which is empty)
    """
    soup = BeautifulSoup(URL.text, 'html.parser')
    pages = [f"https://www.nasdaq.com{a['href']}" for a in soup.find_all('a', class_="content-feed__card-title-link")]
    return pages[:len(pages) - 1]


def get_response(urls):
    """
    using grequests threads to get responses from several web pages at a time
    :param urls: list of urls
    :return: responses from server
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


def main():
    try:
        fetch_articles_urls()  # creates file with articles urls.
        Class_Article.main()  # Creates DataFrame with articles info, and saves their content in a sub-folder.
    except Exception as err:
        print(f'Error: {err}')


if __name__ == "__main__":
    main()

