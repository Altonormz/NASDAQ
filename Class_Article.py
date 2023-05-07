import logging


# logging config
logging.basicConfig(level=logging.INFO, filename="Class_Article.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Class_Article.log")


class Article:
    """
    Class Article holds information about a news article from Nasdaq.com/markets.
    Information includes: id, title, author, date, and tags.
    """

    def __init__(self, id_num, url, title=None, author=None, date=None, tags=None, article_content=None,
                 tickers=None):
        if tickers is None:
            tickers = []
        if tags is None:
            tags = []
        self.title = title
        self.author = author
        self.date = date
        self.tags = tags
        self.article_content = article_content
        self.tickers = tickers
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
    def _get_author(soup):
        """
        Returns the names of the author of the article from the soup object.
        """
        author_block = soup.find('span', {"class": "jupiter22-c-author-byline__author-no-link"})
        if author_block:
            author = author_block.get_text().strip()
        else:
            author = "Unknown"
        return author

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
    def _get_tickers_list(soup):
        """
        Returns the tickers of the article from the soup object.
        """
        tickers_block = soup.find('div', {"class": "jupiter22-c-related-stocks-horizontal__list"})
        if tickers_block:
            tickers_list = tickers_block.get_text(" ").split()
        else:
            tickers_list = []
        return tickers_list

    def set_info(self, soup):
        """
        Sets the article information to the class from the soup object.
        """

        self.title = Article._get_title(soup)
        self.author = Article._get_author(soup)
        self.date = Article._get_date(soup)
        self.tags = Article._get_tags(soup)
        self.article_content = Article._get_article_content(soup)
        self.tickers = Article._get_tickers_list(soup)

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
        message = f"ID: {self.id_num}, Name: {self.title}, Author: {self.author}, Date: {self.date}, " \
                  f"Tags: {self.tags}, URL: {self.url}"
        return message

    def row_info(self):
        """
        Returns the article information in panda row format.
        """
        data = {'id': self.id_num,
                'title': self.title,
                'author': self.author,
                'date': self.date,
                'tags': self.tags,
                'tickers': self.tickers,
                'article_content': self.article_content,
                'url': self.url,
                }
        return data


