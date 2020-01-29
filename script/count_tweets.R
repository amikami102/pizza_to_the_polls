# !usr/bin/env Rscript
#----------------------------------------
# This script counts the number of tweets at 
# various stages of data collection. 
#----------------------------------------

library(magrittr)
library(tidyverse)
library(rio)
library(rjson)
library(lubridate)
library(RColorBrewer)
select <- dplyr::select

# number of tweets retrieved from Twitter API search request
## @knitr raw_counts

raw_counts <- fromJSON(file = "data/counts.json")$results
raw_counts %<>% map_df(~map_at(., "timePeriod", ymd_hm, tz = "UTC")) %>%
        filter(timePeriod >= as_datetime("2018-11-06 11:00:00"))


## @knitr ggplot_raw_counts
cbPalette <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", 
               "#0072B2", "#D55E00", "#CC79A7")

ggplot(data = raw_counts, mapping = aes(x = timePeriod, y = count)) + 
        geom_bar(stat = "identity", fill = cbPalette[2]) +
        labs(title = "Tweets per hour", x = "Hour", y = "Count") +
        theme_minimal() 
ggsave("fig/tweets_per_hour.png")

## @knitr parsed_counts
convert_to_tibble <- function(file) {
        json <- fromJSON(file = file)
        df <- json %>% tibble(
                created_at = map_chr(., "created_at"),
                text = map_chr(., "text"),
                id = map_chr(., "id"),
                clean_text = map_chr(., "clean_text"),
                contain_address = map_lgl(., "contain_address")
        ) %>% 
                select(- .) 
        return(df)
}

parsed <- list.files("data/tweets/script02", pattern = "parsed", full.names = TRUE) %>% 
        map_df(~convert_to_tibble(.x)) %>%
        mutate(created_at = paste("2018-11-06", 
                                  str_extract(created_at, 
                                              "[0-9]{2}:[0-9]{2}:[0-9]{2}")) %>%
                       ymd_hms() %>% floor_date(unit = "hour")
               ) %>%
        filter(contain_address) %>%
        group_by(created_at) %>%
        summarize(count = n())

parsed_counts <- raw_counts %>% 
        left_join(parsed, by = c("timePeriod" = "created_at"),
                      suffix = c("_raw", "_parsed")) %>%
        mutate_if(is.numeric, ~replace(., is.na(.), 0))

## @knitr ggplot_parsed_counts
ggplot(data = counts, mapping = aes(x = timePeriod, y = count_parsed)) +
        geom_bar(stat = "identity", fill = cbPalette[3]) + 
        labs(title = "Tweets per hour containing street address",
             x = "Hour", y = "Count") + 
        theme_minimal()
ggsave("fig/parsed_tweets_per_hour.png")


save(raw_counts, parsed_counts, file = "data/counts.Rdata")
