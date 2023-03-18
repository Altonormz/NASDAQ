from gevent import monkey

monkey.patch_all()

import os
import requests
import grequests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import logging
import time


class Article:
    """
    Class Article holds information about a news article from Nasdaq.com/markets.
    Information includes: id, title, authors, date, and tags.
    """

    def __init__(self, id_num, url, response):
        self.id_num = id_num
        self.url = url
        self._soup = self._get_soup(response)
        self.title = self._get_title()
        self.authors = self._get_authors()
        self.date = self._get_date()
        self.tags = self._get_tags()
    def _get_soup(self, response):
        """
        Parses the HTML content and returns a soup object.
        """
        return BeautifulSoup(response.content, "html.parser")

    def _get_title(self):
        """
        Returns the name of the title of the article from the soup object.
        """
        title_block = self._soup.find('h1', {'class':"jupiter22-c-hero-article-title"})
        if title_block:
            title = title_block.get_text().strip()
            return title
        else:
            return None

    def _get_authors(self):
        """
        Returns the names of the authors of the article from the soup object.
        """
        authors_block = self._soup.find('span', {"class": "jupiter22-c-author-byline__author-no-link"})
        authors = authors_block.get_text().strip()
        return authors



def _get_date(self):
    """
    Returns the date of the article from the soup object.
    """
    time_stamp_block = self._soup.find('p', {"class": "jupiter22-c-author-byline__timestamp"})
    time_stamp = time_stamp_block.get_text().strip()
    return time_stamp

def _get_tags(self): #Fix

    """
    Returns the tags of the article from the soup object.
    """
    tags_block = self.soup.find('div', {"class": "jupiter22-c-tags-container"})
    tags_list = tags_block.get_text(" ").split()
    return tags_list


def _create_article_content_file(self, content):
    """
    Creates a text file containing the article content in a subfolder
    """
    # The plan is to take the content in this function instead of making another conent.
    if not os.path.isdir("article content files"):  # Creates the folder if it doesn't exist.
        os.mkdir("article content files")

    with open(f'{self.id}.txt', 'w') as f:  # The file will have the id name.
        f.write(content)


article_list = []
headers =  {"User-Agent": UserAgent(browsers=["edge", "chrome"]).random}
for id_index,article in enumerate(article_list):



