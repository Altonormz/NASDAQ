from gevent import monkey
monkey.patch_all()
import requests
import grequests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def main():
    URL = 'https://www.nasdaq.com/news-and-insights/topic/markets'
    r = requests.get(URL).text
    soup = BeautifulSoup(r, 'html.parser')
    pages = [f"https://www.nasdaq.com{a['href']}" for a in soup.find_all('a', class_="content-feed__card-title-link")]
    print(pages)


if __name__ == "__main__":
    main()
