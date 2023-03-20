from gevent import monkey

monkey.patch_all()
import grequests
from bs4 import BeautifulSoup

BATCH_SIZE = 10
PAGES = 1000

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


def main():
    new_links = []
    for i in range(1, PAGES, BATCH_SIZE):
        ten_pages = [f'https://www.nasdaq.com/news-and-insights/topic/markets/page/{j}' for j in
                     range(i, i + BATCH_SIZE)]
        responses = get_response(ten_pages)
        for url in responses:
            if url.status_code == 200:
                new_links = new_links + scrape_page(url)
            else:
                print(f"Request failed with status code: {url.status_code}")
        print(f'Batch number {i // BATCH_SIZE + 1}/100 done')
    print(new_links)
    save_links(new_links)


if __name__ == "__main__":
    main()
