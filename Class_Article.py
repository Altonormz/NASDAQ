from gevent import monkey

monkey.patch_all()
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
        self.article_content = None
        self.tickers_name = []
        # self.stocks_change = [] ## In case we want the information in the future
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
    def _get_tickers_dict(soup):
        """
        Returns the tickers of the article from the soup object.
        """
        tickers_block = soup.find('div', {"class": "jupiter22-c-related-stocks-horizontal__list"})
        if tickers_block:
            tickers_list = tickers_block.get_text(" ").split()
            tickers_dict = {tickers_list[i]: tickers_list[i + 1] for i in range(0, len(tickers_list) - 1, 2)}
        else:
            tickers_dict = {}
        return tickers_dict

    def set_info(self, soup):
        """
        Sets the article information to the class from the response.
        """

        self.title = Article._get_title(soup)
        self.authors = Article._get_authors(soup)
        self.date = Article._get_date(soup)
        self.tags = Article._get_tags(soup)
        self.article_content = Article._get_article_content(soup)
        tickers_dict = Article._get_tickers_dict(soup)
        self.tickers_name = list(tickers_dict.keys())
        # self.stocks_change = list(tickers_dict.values()) ## In case we want the information in the future.

    @staticmethod
    def _get_article_content(soup):
        """
        Returns a string containing the article content.
        """

        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text() for p in paragraphs])
        return content

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


