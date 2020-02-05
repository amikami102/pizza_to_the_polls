
This prooject locates long polling lines based on tweets posted by Pizza to the Polls, a nonprofit org that delivers pizzas to voters waiting in line, on 2018 Midterm Election day. I investigate the profile of voters who were potentially engaging with Pizza to the Polls, and identify missed opportunities and recommend how PttP can increase its outreach for the upcoming 2020 Election. 

Full report available at RPubs: https://rpubs.com/afmikami/pizza_to_the_polls.

Shiny app of interactive map: https://asakomikami.shinyapps.io/pizza_to_the_polls/.

# What to expect in this project 🍕

- **Data collection**: Twitter API, Google's Geocoding API, scraping Wikipedia articles
- **Visualization**: interactive map, histograms
- **Data analysis**: Bag of words, Poisson regression, negative binomial count model, propensity score calculation with logistic regression


# Tutorials based on this project 🍕

I am also writing a series of blog posts on how to use Twitter API to make search requests with premium subscription. 

- ["Collecting and parsing tweets, part I"](https://asakomikami.com/2019/05/29/webscraping-twitter-part1/)
- "Collecting and parsing tweets, part II" (forthcoming)
- "Scraping Wikipedia pages" (forthcoming)
- "Creating an interactive map with spatial points and polygon data" (forthcoming)

# Repository organization 🍕

```
|-- README.md
|-- analysis.Rmd
|-- analysis.html
|-- data/                       # raw, cleaned, and augmented data files
|-- fig/                        # figure outputs 
|-- script/     
        |-- friends_of_PTTP/    # .py scripts for looking up users on Twitter API
        |-- map/                # .R scripts for making
        |-- scrape_tweets/      # .py scripts for Twitter API and parsing tweets
        |-- scrape_wiki/        # .py scripts for scraping Wikipedia pages 
        |-- women/               # .py scripts for scraping CAWP page
        |-- 2018-election-results.R
        |-- clean_pizza.R
        |-- count_tweets.R
        |-- create_map.R
        |-- download_acs_data.R
        |-- download_USCensus_shpfile.R 
        |-- missed_opp.R
        |-- mod_df.R
        |-- pairwise_plots.R
|-- shiny/                      # R Shiny app displaying interactive map 
```
