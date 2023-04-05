
<img width="300" src="https://upload.wikimedia.org/wikipedia/commons/8/87/NASDAQ_Logo.svg">


#
Authors: Alot Mecilati & Jonathan Schwarz

## NASDAQ Market News and Insights 

Nasdaq is a global electronic marketplace that permits investors and traders to buy and sell securities.
NASDAQ is one of the leading stock exchanges in the world and the world’s first electronic stock exchange. Its 
performance can provide insights into the overall health of the stock market.
Market news report insights and analysis on the transformative forces shaping the global economy like Mergers, 
Acquisitions or FDA approvals, they would likely be seen as a bullish indicator as a result of that material event. 
Overall, scraping NASDAQ news can provide valuable insights into market trends, competitor activities, and potential 
risks or challenges, allowing individuals and organizations to make more informed decisions about their investments 
and strategies.

### the data scraped:
We chose to scrape the following information from these news articles: 
- Dates
- Titles
- Authors 
- Content of articles 
- Stocks discussed (tickers) and their trend

All the info is gathered inorder to better understand stocks trends and their effect on the market.

### Objectives:
- successfully scrape relevant data from NASDAQ market news (including all information mentioned above).
- process the data scraped to filter noise and focus on what's important.
- Market statistical analysis: analyse the data scraped and cleaned to test hypothesis theories and learn what we can
from each piece of the puzzle
- create a large DB of information about market trends for future use (Prediction algorithms).


## Methods and Used Libraries

Generally the code is divided into a few main stages:
1. parse the user arguments and filters using argparse library (for further information please see "User Arguments 
section below)
2. Creating the DB (for more information about the DB structure and content please see "Database Structure and Features"
section below)
3. Acquiring the urls for each article from the "Recent Markets headlines" pages (one thousand pages overall),
the requests were done using grequests (in batches of 10) and searching each page once a response was received. 
The urls are searched and acquired using an HTML class (unique to the article pages) taking the href attribute using 
bs4. The urls are transferred to the second phase - the article scraping.
4. Acquiring the urls from the previous stage, the next stage makes use of an object called Article.
Requests (using grequests threads in batches of 10) are made to the server using the urls read and for each url. If the 
request was successful, with the help of bs4, data regrading the date, title, authors, tags and the text is collected
into the object attributes. All the info mentioned is then transferred to the last stage 

### User Arguments:
3 filters are available:
- scrape_all - scraping all data from all pages and article with no filter (when used no other argument may be used).
- pages - scrape x number of pages starting from the first (*see note 1 below) the default value is 1000 pages.
- time - given a date and possibly time (**important note:** use ISO format) the program will scrape any article from 
today till the date and time mentioned (*see notes below).

note 1: the pages and time arguments may be operated together, however, the first to reach its limit will determine the
amount of articles scraped.

note 2: depending on the recent news the date of the last article may vary, meaning that the date entered may scape 
more, less or all data.

example: 

### Installations Required

All the installations required including versions can be found in the "requirements.txt"  file

## Database Structure and Features


## Running the program

To start the program please run "NASDAQ_scraper.py" file with no parameters.

Please download the "Class_Article.py" and "JSON.config" file, and make sure to follow the "requirements.txt"
installations before running the program.
