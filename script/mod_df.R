####----------------------------
## This script creates a map of US congressional district
## and plots polling locations where Pizza To The Polls
## delivered pizzas. 
####----------------------------

x <- c("tidyverse", "magrittr", "rio")
lapply(x, library, character.only = TRUE, quietly = TRUE)
load("data/acs_cd.Rdata")
load("data/map_data.Rdata")
load("2018-election-results.Rdata")

us_cd %<>% as.data.frame() %>% dplyr::select(-geometry) %>%
        filter(CD115FP != 98) # remove non-voting districts

us_state %<>% as.data.frame() %>% dplyr::select(-geometry)

all <- pizzapolls_cd %>% as.data.frame() %>% 
        dplyr::select(count, GEOID) %>%
        group_by(GEOID) %>% # group by districts 
        summarize(count = sum(count)) %>%
        right_join(us_cd, by = "GEOID") %>% # join with other districts
        mutate(count = ifelse(is.na(count), 0, count)) 


mod_df <- all %>% left_join(us_state, by = c("state" = "STUSPS")) %>%
        rename(key_rep = key,
               woman1_rep = woman1, woman2_rep = woman2) %>%
        left_join(median_houseinc, by = "GEOID") %>%
        left_join(black_pop, by = "GEOID") %>%
        left_join(hisp_pop, by = "GEOID") %>%
        left_join(total_pop, by = "GEOID") %>%
        left_join(age18to19_male, by = "GEOID") %>%
        left_join(age18to19_female, by = "GEOID") %>%
        left_join(age20to24_female, by = "GEOID") %>%
        left_join(age20to24_male, by = "GEOID") %>%
        mutate(medianHouseInc_log = log(medianHouseInc_estimate),
               blackPop_log = log(blackPop_estimate),
               hispPop_log = log(hispPop_estimate),
               totalPop_log = log(totalPop_estimate),
               age18to19 = age18to19_female_estimate + age18to19_male_estimate,
               age20to24 = age20to24_female_estimate + age20to24_male_estimate,
               age18to24_log = log(age18to19 + age20to24)
               ) %>%
        dplyr::select(-contains("_moe"), -contains("_estimate")) %>%
        mutate(zero = ifelse(count == 0, TRUE, FALSE),
               women_rep = factor(woman1_rep + woman2_rep, 
                                  levels = c(0, 1, 2)),
               women_sen = factor(woman1_sen + woman2_sen,
                                  levels = c(0, 1, 2)),
               women_gov = factor(woman1_gov + woman2_gov,
                                  levels = c(0, 1, 2)),
               count_log = log(count + 0.1)
        )

save(mod_df, file = "data/mod_df.Rdata")