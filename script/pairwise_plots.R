####----------------------------
## This script creates preliminary plots with mod_df created by
# "script/mod_df.R" file.
####----------------------------
library(tidyverse)
library(GGally)
load("data/mod_df.Rdata")

## ggpairs_num
mod_df %>% dplyr::select(count, totalPop_log,
                         medianHouseInc_log, 
                         blackPop_log, 
                         age18to24_log) %>%
        ggpairs(
                upper = list(continuous = "cor"),
                lower = list(continuous = wrap(ggally_smooth, color = color[1])),
                columnLabels = c("count", 
                                 "log total pop.",
                                 "log median house income", 
                                 "log Black pop.", 
                                 "log ages 18-24 pop."),
                title = "Pairwise plots of numerical variables",
                axisLabels = "none"
        ) + theme_minimal(base_size = 10) 
ggsave("fig/ggpairs_num.png")

# ggpairs_cat
house1 <- ggplot(data = mod_df, aes(x = key_rep, y = count)) + 
        geom_boxplot(fill = color[1], na.rm = TRUE) + 
        xlab("Key House race") +
        ylab("Logged count") + 
        theme_minimal()
senate1 <- ggplot(data = mod_df, aes(x= key_sen, y = count)) +
        geom_boxplot(fill = color[2], na.rm = TRUE) +
        xlab("Key Senate race") + ylab("Logged count") + 
        theme_minimal()
governor1 <- ggplot(data = mod_df, aes(x= key_gov, y = count)) +
        geom_boxplot(fill = color[3], na.rm = TRUE) +
        xlab("Key governor race") + ylab("Logged count") + 
        theme_minimal()
house2 <- ggplot(data = mod_df, aes(x = women_rep, y = count)) + 
        geom_boxplot(fill = color[1]) + 
        xlab("Women candidates for House") + ylab("Logged count") + 
        theme_minimal(base_size = 10)
senate2 <- ggplot(data = mod_df, aes(x= women_sen, y = count)) +
        geom_boxplot(fill = color[2]) +
        xlab("Women candidates for Senate") + ylab("Logged count") + 
        theme_minimal(base_size = 10)
governor2 <- ggplot(data = mod_df, aes(x= women_gov, y = count)) +
        geom_boxplot(fill = color[3]) +
        xlab("Women candidates for governor") + ylab("Logged count") + 
        theme_minimal(base_size = 10)

grid.arrange(house1, senate1, governor1, 
             house2, senate2, governor2,
             nrow = 2)
ggsave("fig/ggpairs_cat.png")


# hist_cd
caption <- "The histogram shows the distribution of number of unique polling 
locations identified by PttP tweets per district. For example, about 80 percent of\n 
districts did not have any polling location identified, meaning that there were no 
PttP pizza deliveries observed for these 350+ districts.\n On the other extreme end, 
there is one district that had 12 different polling locations that received pizzas 
from PttP."

ggplot(data = mod_df, mapping = aes(count)) +
        geom_histogram(fill = "red") + 
        labs(title = "Number of unique polling locations sampled per congressional district", 
             caption = caption) +
        ylab("district count") +
        xlab("# of polling locations identified") +
        theme_minimal(base_size = 10)
ggsave("fig/hist_cd.png")
