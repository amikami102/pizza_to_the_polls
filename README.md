
Locate long polling lines based on tweets posted by Pizza to the Polls, a nonprofit org that delivers pizzas to voters waiting in line, on 2018 Midterm Election day. Investigate the profile of voters who knew about and reported long lines to Pizza to the Polls. Identify missed opportunities and recommend how PttP can increase its outreach for the upcoming 2020 Election. 



# What to expect in this project:

- **Data collection**: Twitter API, Google's Geocoding API, scraping Wikipedia articles
- **Visualization**: interactive map, histograms
- **Data analysis**: Bag of words, Poisson regression, Zero-inflated poisson regression, model comparison test, proopensity score matching. 


# Tutorials based on this project

I am also writing a blog post series on how to use Twitter API to make search requests with premium subscription. 

- ["Collecting and parsing tweets, part I"](https://asakomikami.com/2019/05/29/webscraping-twitter-part1/)
- "Collecting and parsing tweets, part II" (forthcoming)
- "Scraping Wikipedia pages" (forthcoming)
- "Creating an interactive map with spatial points and polygon data" (forthcoming)

# Repository organization

```
|-- README.md
|-- analysis.Rmd
|-- analysis.html
|-- data/                       # raw, cleaned, and augmented data files
|-- fig/                        # figure outputs 
|-- script/     
        |-- friends_of_PTTP/    # .py scripts for looking up friends of Pizza to the Polls
        |-- map/                # .R scripts for making
        |-- scrape_tweets/      # .py scripts for Twitter API and parsing tweets
        |-- scrape_wiki/        # .py scripts for scraping Wikipedia pages 
        |-- women               # .py scripts for scraping CAWP page
        |-- 2018-election-results.R
        |-- clean_pizza.R
        |-- count_tweets.R
        |-- create_map.R
        |-- download_acs_data.R
        |-- download_USCensus_shpfile.R 
|-- shiny/                      # R Shiny app displaying interactive map 
```
