from gevent import monkey

monkey.patch_all()
import os
import grequests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent

BATCH_SIZE = 10
TIMEOUT = 15
MAX_RETRIES = 5


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

    def _get_title(self, soup):
        """
        Returns the name of the title of the article from the soup object.
        """
        title_block = soup.find('h1', {'class': "jupiter22-c-hero-article-title"})
        if title_block:
            title = title_block.get_text().strip()
            return title
        else:
            return None

    def _get_authors(self, soup):
        """
        Returns the names of the authors of the article from the soup object.
        """
        authors_block = soup.find('span', {"class": "jupiter22-c-author-byline__author-no-link"})
        if authors_block:
            authors = authors_block.get_text().strip()
        else:
            authors = "Unknown"
        return authors

    def _get_date(self, soup):
        """
        Returns the date of the article from the soup object.
        """
        time_stamp_block = soup.find('p', {"class": "jupiter22-c-author-byline__timestamp"})
        if time_stamp_block:
            time_stamp = time_stamp_block.get_text().strip()
        else:
            time_stamp = "Unknown"
        return time_stamp

    def _get_tags(self, soup):  # Fix

        """
        Returns the tags of the article from the soup object.
        """
        tags_block = soup.find('div', {"class": "jupiter22-c-tags-container"})
        if tags_block:
            tags_list = tags_block.get_text(" ").split()
        else:
            tags_list = ["Unknown"]
        return tags_list

    def set_info(self, response):
        """
        Sets the article information to the class from the response.
        """
        soup = get_soup(response)
        self.title = self._get_title(soup)
        self.authors = self._get_authors(soup)
        self.date = self._get_date(soup)
        self.tags = self._get_tags(soup)
        self._create_article_content_file(soup)

    def _create_article_content_file(self, soup):
        """
        Creates a text file containing the article content in a subfolder.
        """
        if not os.path.isdir("article content files"):
            os.mkdir("article content files")
        try:
            with open(os.path.join("article content files", f'{self.id_num}.txt'), 'w') as f:
                paragraphs = soup.find_all('p')
                content = "\n".join([p.get_text() for p in paragraphs])
                f.write(content)
        except Exception as e:
            print(f"Error writing content for article {self.id_num}: {e}")

    def __str__(self):
        """
        Returns a string representation of the Article object.        """
        message = f"ID: {self.id_num}, Name: {self.title}, Authors: {self.authors}, Date: {self.date}, Tags: {self.tags}, URL: {self.url}"
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


def setting_info(article_list, df):
    """
    Takes a list of Article objects and creates a dataframe with the article information.
    Prints the article short information without the content.
    The article content will be saved into a text file in a sub-folder named "article content files".
    """
    ua = UserAgent()
    headers = {'user-agent': ua.random}
    rs = (grequests.get(t.url, headers=headers, timeout=TIMEOUT) for t in article_list)

    countdown = 0

    for response in grequests.imap(rs, size=BATCH_SIZE):
        if response.status_code == 200:
            article = next(t for t in article_list if t.url == response.url)
            article.set_info(response)
            print(article)

            new_row_df = pd.DataFrame([article.row_info()])
            df = pd.concat([df, new_row_df], ignore_index=True)
            countdown += 1
            if countdown >= 500:
                df.to_csv('article_info.csv', index=False)
                countdown = 0
        else:
            print(f"Request failed with status code: {response.status_code}")

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
        print('File not found')
        return []


def main():
    article_list = get_articles()
    columns = ['id', 'title', 'authors', 'date', 'tags', 'URL']
    df = pd.DataFrame(columns=columns)
    setting_info(article_list, df)


if __name__ == "__main__":
    main()
