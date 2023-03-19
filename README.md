# NASDAQ 

## NASDAQ Market News and Insights 

Nasdaq is a global electronic marketplace that permits investors and traders to buy and sell securities. 
It was the world’s first electronic stock exchange.
Market news report insights and analysis on the transformative forces shaping the global economy like Mergers and 
Acquisitions or FDA approvals, they would likely be seen as a bullish indicator as a result of that material event. 
We chose to scrape the information from these news articles dates, authors, tags, and most importantly the content of 
articles and the discussed stocks.


## Methods and Used Libraries

Generally the code is divided into two main stages:
1. Acquiring the urls for each article from the "Recent Markets headlines" pages (one thousand pages overall),
the requests were done using grequests (in batches of 10) and searching each page once a response was received. 
The urls are searched and acquired using an HTML class (unique to the article pages) taking the href attribute using 
bs4. The urls are then saved to a text file. 
2. Opening and reading the text file from the previous stage, the next stage makes use of an object called Article.
Requests (using grequests threads in batches of 10) are made to the server using the urls read and for each url. If the 
request was successful, with the help of bs4, data regrading the date, title, authors, tags and the text is collected
into the object attributes giving a unique ID number in process. All the info mentioned is then transferred to a pandas 
DataFrame object and saved as a csv file.

## Installations Required

All the installations required including versions can be found in the "requirements.txt"  file

## Running the Code


