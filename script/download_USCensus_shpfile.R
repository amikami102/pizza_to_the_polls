###-----------------------
# This script downloads 2016 US congressional district and county 
# shape files from the US Census bureau.
###-----------------------

dir_url <- "https://www2.census.gov/geo/tiger/GENZ2016/shp/"
ss <- "us" 
entity <- c("cd115", # congressional district
            "county") # county
rr <- "500k" # resolution size
shpname <- paste("cb_2016", ss, entity, rr, sep = "_")

## download and extract zipfiles
shpname %>% map(~ {
        url <- paste0(dir_url, ., ".zip")
        temp <- tempfile()
        download.file(url, destfile = temp)
        dir <- file.path("data", "shp", .)
        unzip(temp, exdir = dir)
})