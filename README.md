# About the project

I was watching my Twitter feed during the 2018 Midterm election and came across a tweet by Pizza To The Polls saying that it had sent pizzas to some polling location in response to a request. At that point in time, I was vaguely interested in electoral integrity of American elections.  One way to suppress voting is to close polling stations or remove voting machines. I was interested in locating long polling lines, but data on polling locations is not publicly available. Although some states allow you to purchase the data, most states do not disclose this information. So when I saw the tweets by Pizza To The Polll and that they contained addresses, I thought it would be an inexpensive alternative for getting the data. 



# Tutorials based on this project

I am also writing a blog post series on how to use Twitter API to make search requests with premium subscription. 

- ["How to collect and parse tweets, part I"](https://asakomikami.com/2019/05/29/webscraping-twitter-part1/)
- "How to collect and parse tweets, part II" (forthcoming)

# Repository organization

```
|-- .gitignore
|-- data/                       # data files
|-- fig/                        # figure outputs 
|-- README.md
|-- script/     
        |-- create_map.R        # creates interactive map 
        |-- credentials/        # stores API credentials (not uploaded to Github)
        |-- dl_shpfile_from_uscensus.R 
        |-- scrape_tweets/      # python scripts for Twitter API and parsing tweets
        |-- scrape_wiki/        # python scripts for scraping Wikipedia pages 
|-- shiny/                      # R Shiny app displaying interactive map 
```
