####----------------------------
## This script creates preliminary plots with mod_df created by
# "script/mod_df.R" file.
####----------------------------
library(tidyverse)
library(GGally)
library(RColorBrewer)
library(gridExtra)
load("data/mod_df.Rdata")
count_df <- mod_df[mod_df$count > 0, ]
color <- brewer.pal(n = 8, name = "Set1")

## ggpairs_num
mod_df %>% dplyr::select(count, totalPop_log,
                         medianHouseInc_log, 
                         blackPopShare_log, 
                         age18to24Share_log) %>%
        ggpairs(
                upper = list(continuous = "cor"),
                lower = list(continuous = wrap(ggally_smooth, color = color[8])),
                columnLabels = c("count", 
                                 "log total pop.",
                                 "log median house inc.", 
                                 "log Black pop.", 
                                 "log ages 18-24"),
                title = "Pairwise plots of numerical variables",
                axisLabels = "none"
        ) + theme_minimal(base_size = 12) 
ggsave("fig/ggpairs_num.png")

# ggpairs_cat
house1 <- ggplot(data = count_df, aes(x = key_rep, y = count_log)) + 
        geom_boxplot(fill = color[1], na.rm = TRUE) + 
        xlab("Key House race") +
        ylab("") + 
        theme_minimal(base_size = 12)
senate1 <- ggplot(data = count_df, aes(x= key_sen, y = count_log)) +
        geom_boxplot(fill = color[2], na.rm = TRUE) +
        xlab("Key Senate race") + ylab("") + 
        theme_minimal(base_size = 12)
governor1 <- ggplot(data = count_df, aes(x= key_gov, y = count_log)) +
        geom_boxplot(fill = color[3], na.rm = TRUE) +
        xlab("Key governor race") + ylab("") + 
        theme_minimal(base_size = 12)
house2 <- ggplot(data = count_df, aes(x = women_rep, y = count_log)) + 
        geom_boxplot(fill = color[1]) + 
        xlab("Women candidates for House")  + ylab("") + 
        theme_minimal(base_size = 12)
senate2 <- ggplot(data = count_df, aes(x= women_sen, y = count_log)) +
        geom_boxplot(fill = color[2]) +
        xlab("Women candidates for Senate") + ylab("") + 
        theme_minimal(base_size = 12)
governor2 <- ggplot(data = count_df, aes(x= women_gov, y = count_log)) +
        geom_boxplot(fill = color[3]) +
        xlab("Women candidates for governor")  + ylab("") + 
        theme_minimal(base_size = 12)

grid.arrange(house1, senate1, governor1, 
             house2, senate2, governor2,
             nrow = 2, left = "Logged count")
ggsave("fig/ggpairs_cat_nozeros.png")


# hist_cd
ggplot(data = mod_df, mapping = aes(count)) +
        geom_histogram(fill = color[2], binwidth = 10) + 
        labs(title = "Number of unique polling locations identified" 
             )+
        ylab("count") +
        xlab("Number of polling locations per district") +
        theme_minimal(base_size = 12)
ggsave("fig/hist_cd.png")
