from gevent import monkey

monkey.patch_all()
import os
import grequests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import json
import logging

# logging config
logging.basicConfig(level=logging.INFO, filename="Class_Article.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Class_Article.log")


class Article:
    """
    Class Article holds information about a news article from Nasdaq.com/markets.
    Information includes: id, title, authors, date, and tags.
    """

    def __init__(self, id_num, url):
        self.title = None
        self.authors = None
        self.date = None
        self.tags = None
        self.id_num = id_num
        self.url = url

    @staticmethod
    def _get_title(soup):
        """
        Returns the name of the title of the article from the soup object.
        """
        title_block = soup.find('h1', {'class': "jupiter22-c-hero-article-title"})
        if title_block:
            title = title_block.get_text().strip()
            return title
        else:
            return None

    @staticmethod
    def _get_authors(soup):
        """
        Returns the names of the authors of the article from the soup object.
        """
        authors_block = soup.find('span', {"class": "jupiter22-c-author-byline__author-no-link"})
        if authors_block:
            authors = authors_block.get_text().strip()
        else:
            authors = "Unknown"
        return authors

    @staticmethod
    def _get_date(soup):
        """
        Returns the date of the article from the soup object.
        """
        time_stamp_block = soup.find('p', {"class": "jupiter22-c-author-byline__timestamp"})
        if time_stamp_block:
            time_stamp = time_stamp_block.get_text().strip()
        else:
            time_stamp = "Unknown"
        return time_stamp

    @staticmethod
    def _get_tags(soup):

        """
        Returns the tags of the article from the soup object.
        """
        tags_block = soup.find('div', {"class": "jupiter22-c-tags-container"})
        if tags_block:
            tags_list = tags_block.get_text(" ").split()
        else:
            tags_list = ["Unknown"]
        return tags_list

    @staticmethod
    def _get_tickers(soup):
        """
        Returns the tickers of the article from the soup object.
        """
        tickers_block = soup.find('div', {"class": "jupiter22-c-related-stocks-horizontal__list"})
        if tickers_block:
            tickers_list = tickers_block.get_text(" ").split()
            tickers_dict = {tickers_list[i]: tickers_list[i + 1] for i in range(0, len(tickers_list), 2)}
        else:
            tickers_dict = {}
        return tickers_dict

    def set_info(self, response):
        """
        Sets the article information to the class from the response.
        """
        soup = get_soup(response)
        self.title = self._get_title(soup)
        self.authors = self._get_authors(soup)
        self.date = self._get_date(soup)
        self.tags = self._get_tags(soup)
        self._create_article_content_file(self.id_num, soup)

    @staticmethod
    def _create_article_content_file(id_num, soup):
        """
        Creates a text file containing the article content in a subfolder.
        """
        if not os.path.isdir("article content files"):
            os.mkdir("article content files")
        try:
            with open(os.path.join("article content files", f'{id_num}.txt'), 'w') as f:
                paragraphs = soup.find_all('p')
                content = "\n".join([p.get_text() for p in paragraphs])
                f.write(content)
        except Exception as e:
            print(f"Error writing content for article {id_num}: {e}")

    def __str__(self):
        """
        Returns a string representation of the Article object.        """
        message = f"ID: {self.id_num}, Name: {self.title}, Authors: {self.authors}, Date: {self.date}, " \
                  f"Tags: {self.tags}, URL: {self.url}"
        return message

    def row_info(self):
        """
        Returns the article information in panda row format.
        """
        data = {'id': self.id_num,
                'title': self.title,
                'authors': self.authors,
                'date': self.date,
                'tags': self.tags,
                'URL': self.url}
        return data


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
            article = next(t for t in article_list if t.url == response.url)
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
