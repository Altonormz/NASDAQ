
<img width="300" src="https://upload.wikimedia.org/wikipedia/commons/8/87/NASDAQ_Logo.svg" alt="nasdaq_image">

[NASDAQ_repo](https://github.com/Altonormz/NASDAQ)
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
- Stocks discussed (tickers)

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
into the object attributes. All the info mentioned is then transferred to the last stage.
5. The last step takes a list of article objects and inserts the data within them to the DB created in stage 2.
The data is checked, and if not found within the DB the data is inserted.

### User Arguments:
3 filters arguments are available:
- scrape_all - scraping all data from all pages and article with no filter (when used no other argument may be used).
- pages - scrape x number of pages starting from the first (*see note 1 below) the default value is 1000 pages.
- time - given a date and possibly time the program will scrape any article from 
today till the date and time mentioned (*see notes below).
For full list of options for this argument please see: https://dateparser.readthedocs.io/en/latest/

    - note 1: the pages and time arguments may be operated together, however, the first to reach its limit will determine the
amount of articles scraped.

    - note 2: depending on the recent news the date of the last article may vary, meaning that the date entered may scrape 
more, less or all data.

example: 

    `python NASDAQ_scraper.py --scrape_all -pages 500 -time 2023-04-04T05:00:00`


### Installations Required

All the installations required including versions can be found in the "requirements.txt"  file


## Database Structure and Features

![da68d2da-f84e-4cac-b053-6b8d34a8839c.jpeg](Images%2Fda68d2da-f84e-4cac-b053-6b8d34a8839c.jpeg)

**Authors:**
- author_id [int] - primary key generated automatically
- author_name [varchar] - author name

**Articles:**
- article_id [int] - primary key generated automatically
- author_id [int] - Foreign key from Authors
- title [varchar] - the title of the article
- article_content [varchar] - the article text
- url [varchar] - the article url
- published_date [datetime] - thr date and time the article was published

**Article_Tags:**
- article_tag_id [int] - primary key generated automatically
- article_id [int] - Foreign key from Articles
- tag_id [int] - Foreign key from Tags

**Tags:**
- tag_id [int] - primary key generated automatically
- tag_name [varchar] - the tag name (text)

**Stock_Articles:**
- stock_article_id [int] - primary key generated automatically
- stock_id [int] - Foreign key from Stocks
- article_id [int] - Foreign key from Articles

**Stocks:**
- stock_id [int] - primary key generated automatically
- stock_tick [varchar] - stock tick (symbol)
- name [varchar] - the company name
- currency [varchar] - the currency the stock is traded with
- country [varchar] - the country the company is listed in
- sector [varchar] - the sector in the industry the company belongs to
- industry [varchar] - the industry the company belongs to

**Stocks_Prices:**
- stock_price_id [int] - primary key generated automatically 
- stock_id [int] - Foreign key from Stocks 
- date [datetime] - the date of prices record 
- open [int] - opening stock price 
- high [int] - highest stock price in that date 
- low [int] - lowest stock price in that date 
- close [int] - closing stock price 
- volume [int] - number of shares

## Running the program

To start the program please run "NASDAQ_scraper.py" (with the arguments of your choice).

Please download "Class_Article.py", "NASDAQ_datacollecter.py"  and "conf.json", and make sure to follow the
"requirements.txt" installations before running the program.

Before running the program please change the detail of the MySQL username and password in "conf.json" file:

"USER": "root"

"PASSWORD": "root"

## API - Alphavantage 
Link: https://www.alphavantage.co/documentation/

Alphavantage is stock market API with a very large amount of data about the stocks, companies, currencies,
news, cryptocurrencies, commodities and much more!
In this project the API was used to collect data regarding the stocks (and companies) and stock prices.
The data the scaper does not collect and is added through the API script:
1. In Stocks table: name, currency, country, sector, industry.
2. In the Stock_Prices table - all fields.

The API has free limited access per day - only 500 queries and each stock, for each subject, requires 1 query.
We use 2 API keys inorder to:
1. Update 250 newly added stocks (in Stocks table) and add prices of the last 100 days of these stocks to the 
Stocks_Prices table (500 API calls in total).
2. Update previously added stocks with new dates and prices records (in the Stocks_Prices table). The update is done by 
checking the 500 earliest dates each of the stocks were last updated in, and update these stocks 
with all dates in between the last date and the currant date (500 calls in total).

The program first updates the stocks info of newly discovered NASDAQ scraped stocks
and the initial prices (100 days back) and only then updates previously add dates.

It is important to provide 2 API keys in the configuration file ("conf.json").

"info_token" : Your first token 

"price_token" : You second token 

"queries" : number of queries according to the number of tokens, 
your pricing program and records you wish to update.

**Note**: when reaching the limit of the token the program will stop automatically and log a message.
Please see the log file if you suspect that is the case.

## Authors:
### Alot Mecilati:
<img src="Images/T0465J1ATNJ-U04QC18RRNX-c642a0e43fbc-512.jpeg" alt="Alt Text" width="200"/>

[Git](https://github.com/Altonormz)

[LinkIn](https://www.linkedin.com/in/alon-mecilati/)

### Jonathan Schwarz:
<img src="Images/T0465J1ATNJ-U04RM4GPJKA-1f8915af8719-512.png" alt="Alt Text" width="200"/>

[Git](https://github.com/Jonnyds)

[LinkIn](https://www.linkedin.com/in/jonathan-schwarz91/)