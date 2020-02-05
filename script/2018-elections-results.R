# !usr/bin/env R
#----------------------------------------
# This script imports 2018 midterm election results data that I 
# scraped from Wikipedia and stored in csv files.
#----------------------------------------
library(tidyverse)
library(magrittr)
library(rio)

# key races for House, Senate, and Governor offices
house_key <- c("MN-01", "CA-10", "CA-25", "CA-39", "CA-45", "CA-48",
               "FL-15", "FL-26", "IA-03", "IL-14", "KS-02", "KY-06", "ME-02",
               "MI-08", "NC-09", "NC-13", "NJ-03", "NJ-07", "NM-02",
               "NY-19", "NY-22", "PA-01", "TX-07", "UT-04", "VA-02",
               "VA-07", "WA-08", "AZ-02", "CA-49", "CO-06", 
               "FL-27", "IA-01", "IL-06", "KS-03", "MI-11", "MN-02",
               "MN-03", "NJ-11", "NV-03", "NV-04", "PA-07", "VA-10") %>% sort()
senate_key <- c("AZ", "FL", "IN", "MO", "MT", "NV", "MN", "NJ", 
                "WV", "WS", "ND", "TX", "TN", "MS") %>% sort()
governor_key <- c("AK", "CT", "FL", "GA", "IA", "KA", "ME", 
                  "MI", "NV", "NM", "OH", "OR", "SD", "WI") %>% sort()

# HOUSE RACES
house_races <- import("data/csv/house_elections_2018_merged.csv", 
                      header = TRUE, na = c("", "NA", "Write-ins")) %>%
        dplyr::select(-V1, -state) %>%
        mutate(key = ifelse(district %in% house_key, TRUE, FALSE),
               name_woman1 = na_if(name_woman1, ""),
               name_woman2 = na_if(name_woman2, ""),
               woman1 = ifelse(!is.na(name_woman1), TRUE, FALSE),
               woman2 = ifelse(!is.na(name_woman2), TRUE, FALSE),
               women = factor(woman1 + woman2,
                              levels = c(0, 1, 2), exclude = NULL)
               ) %>%
        dplyr::select(-ends_with("_woman1"), -ends_with("_woman2"))
        

# SENATE RACES
senate_races <- import("data/csv/senate_elections_2018_merged.csv", 
                       header = TRUE, na = c("", "NA", "Write-ins")) %>%
        dplyr::select(-V1) %>%
        rename(share1 = percentage1, share2 = percentage2) %>%
        mutate(key = ifelse(state %in% senate_key, TRUE, FALSE),
               name_woman1 = na_if(name_woman1, ""),
               name_woman2 = na_if(name_woman2, ""),
               # woman1 = ifelse((!is.na(name_woman1) & result_woman1 == "WON") | 
               #                         (!is.na(name_woman2) & result_woman2 == "WON"), 
               #                 TRUE, FALSE),
               # woman2 = ifelse(!is.na(result_woman2), TRUE,
               #                 ifelse(result_woman1 == "Lost", TRUE, FALSE)),
               # woman1 = ifelse(is.na(name_woman1) & is.na(name_woman2), FALSE, woman1),
               # woman2 = ifelse(is.na(name_woman2), FALSE, woman2)
               woman1 = ifelse(!is.na(name_woman1), TRUE, FALSE),
               woman2 = ifelse(!is.na(name_woman2), TRUE, FALSE),
               women = factor(woman1 + woman2,
                              levels = c(0, 1, 2), exclude = NULL)
               ) %>%
        dplyr::select(-ends_with("_woman1"), -ends_with("_woman2"))


# GOVENOR RACES
governor_races <- import("data/csv/gubernatorial_elections_2018_merged.csv",
                         header = TRUE, na = c("", "NA", "Write-ins")) %>%
        dplyr::select(-V1) %>%
        rename(share1 = percentage1, share2 = percentage2) %>%
        mutate(key = ifelse(state %in% governor_key, TRUE, FALSE),
               woman1 = ifelse(!is.na(name_woman), TRUE, FALSE),
               woman2 = FALSE, 
               women = factor(woman1, levels = c(0, 1, 2), exclude = NULL)
               ) %>%
        dplyr::select(-ends_with("_woman"))


# SAVE DATA
save(house_key, senate_key, governor_key,
     house_races, senate_races, governor_races, 
     file = "data/2018-election-results.Rdata")



