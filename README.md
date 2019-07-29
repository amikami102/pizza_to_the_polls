# About the project

See [my blogpost](https://asakomikami.com/2019/04/03/introduce-pizza-to-the-polls/) for more information about this project. 

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