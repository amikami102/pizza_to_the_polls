
This project locates long polling lines in the United States using Twitter data. The tweets come from Pizza to the Polls, a nonprofit organization that delivers pizzas to voters waiting in line, on 2018 Midterm Election day. I investigate which districts were in contact with Pizza to the Polls on 2018 Midterm Election Day and how the organization can improve its outreach for the 2020 election based on the data. 

Full report available at RPubs: https://rpubs.com/afmikami/pizza_to_the_polls.

Shiny app of interactive map: https://asakomikami.shinyapps.io/pizza_to_the_polls/.

# What to expect in this project 🍕

- **Data collection**: Twitter API, Google's Geocoding API, scraping Wikipedia articles
- **Visualization**: interactive map, histograms
- **Data analysis**: Bag of words, Poisson regression, negative binomial count model, propensity score calculation with logistic regression


# Tutorials based on this project 🍕

The main data collection task was using Twitter API to collect the tweets, cleaning them, and then converting the street addresses to geocoordinates with Google's Geocoding API. I have written a three-part tutorial series explaining how to use these API's and extract street addresses from text strings. 

- ["Collecting and parsing tweets, part I"](https://asakomikami.com/2019/05/29/collecting-and-parsing-tweets-part1/)
- ["Collecting and parsing tweets, part II"](https://asakomikami.com/2019/06/03/collecting-and-parsing-tweets-part2/)
- ["Collecting and parsing tweets, part III"](https://asakomikami.com/2020/03/01/collecting-and-parsing-tweets-part3/)


# Repository organization 🍕

```
|-- README.md
|-- analysis.Rmd
|-- analysis.html
|-- data/                       # raw, cleaned, and augmented data files
|-- fig/                        # figure outputs 
|-- script/     
        |-- friends_of_PTTP/    # .py scripts for looking up users on Twitter API
        |-- map/                # .R scripts for making the interactive map
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
