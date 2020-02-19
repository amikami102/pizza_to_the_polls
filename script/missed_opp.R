##------------------------
# This script identifies Pizza to the Poll's missed opportunities.
##------------------------

library(RColorBrewer)
library(ggplot2)
library(tidyverse)
library(magrittr)
load("data/mod_df.Rdata")



# Logit model
mod_log <- glm(zero ~ key_rep + key_sen + key_gov + 
                       women_rep + women_sen + women_gov,
               data = mod_df, family = binomial)


d <- mod_df %>% mutate(prob0 = predict(mod_log, type = "response")) %>%
        tidyr::spread(zero, prob0, sep = "_p")

color <- brewer.pal(n=3, "Set2")
ggplot(d) + 
        geom_histogram(bins = 50, aes(zero_pTRUE), fill = color[1]) + 
        geom_label( aes(x=0.95, y= 20, label="Zeros"), color=color[1]) +
        geom_histogram(bins = 50, aes(x = zero_pFALSE, y = -..count..), 
                       fill = color[2]) + 
        geom_label( aes(x=0.95, y=-5, label="Non-zeros"), color=color[2]) +
        ylab("count") + xlab("propensity score") +
        geom_hline(yintercept = 0, lwd = 0.5) +
        scale_y_continuous(labels = abs) +
        labs(title = "Propensity score distribution",
             caption = "The histogram above the 0 line is the distribution of 
            propensity score among zero == TRUE, and below the 0 line is the 
            distribution of propensity score among zero == FALSE.") + 
        theme_minimal(base_size = 12) 
ggsave(filename = "fig/pscore_hist.png")

# identify missed opportunites 
missed_opp <- d %>% filter(zero_pTRUE <= 0.70) %>% 
        mutate(medianHouseInc_q = ntile(medianHouseInc_log, 10),
               totalPop_q = ntile(totalPop_log, 10),
               blackPopShare_q = ntile(blackPopShare_log, 10),
               age18to24_q = ntile(age18to24Share_log, 10),
               zero_pTRUE = round(zero_pTRUE, digits = 3)
        ) %>%
        dplyr::select(label, zero_pTRUE, key_rep, key_sen, key_gov,
                      women_rep, women_sen, women_gov, 
                      medianHouseInc_q, totalPop_q, blackPopShare_q, 
                      age18to24_q)  %>%
        rename(pscore = zero_pTRUE) %>% 
        dplyr::arrange(label) %>% column_to_rownames("label") 

save(mod_log, missed_opp, file = "data/missed_opp.Rdata")
