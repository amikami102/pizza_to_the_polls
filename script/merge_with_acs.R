## @knitr setup
# load favorite libraries
x <- c("tidyverse", "magrittr", "RColorBrewer", "rio",
       "sf", "tmap", "raster", "rgdal",
       "tidycensus")
lapply(x, library, character.only = TRUE, quietly = TRUE)

## @knitr pizzapolls
# prepare pizzapolls
pizzapolls <- import(file.path("data", "csv", "PizzaToThePolls.csv"), 
                     format = "csv", 
                     header = TRUE) %>%
        mutate(id = as.character(id)) %>%
        st_as_sf(coords = c("lng", "lat")) %>%
        as('Spatial') 
crs(pizzapolls) <- crs(us_county)


## @knitr read_shpfile
## read .shp file as SpatialPolygonsDataFrame
district <- "cb_2016_us_cd115_500k"
county <- "cb_2016_us_county_500k"
us_cd <- readOGR(dsn = file.path("data", "shp", district), layer = district)
us_county <- readOGR(dsn = file.path("data", "shp", county), layer = county)


## merge us_cd with election data scraped from Wikipedia
states <- fips_codes %>% dplyr::select(state, state_code, state_name) %>%
        filter(!duplicated(.))
senate <- import(file.path("data", "csv", "senate_elections_2018.csv"),
                 header = TRUE)
house <- import(file.path("data", "csv", "house_elections_2018.csv"),
                header = TRUE)
us_cd@data %<>% dplyr::select(-AFFGEOID, -GEOID, -LSAD,-CDSESSN, 
                              -ALAND, -AWATER) %>%
        left_join(states, by = c("STATEFP" = "state_code")) %>% 
        mutate(label = paste(state, CD115FP, sep = "-")) %>%
        left_join(house, by = c("label" = "V1")) 


## @knitr acs_data
# get ACS data
#---------------------------------------
# Census table numbers, variable code:
# "B19013" median household income, 
# "C02003" population by race, "C02003_004" for black population
# "B23006" educational attainment 25 to 64 years old, "B23006_009" for hs grad
# "B01003" total population 

#source("script/acs_census_data.R")

# import data and define objects to be used in join_acs()
import_acs <- function(file_list){
        # Import 'acs' objects from files created by
        # census_data.R, and reduce these objects to 
        # dataframes. 
        #---------------------
        # file_list (list of files storing `acs` objects)
        #---------------------
        total <- import(grep("B01003", file_list, value = TRUE))
        black <- import(grep("C02003", file_list, value = TRUE))
        hsgrad <- import(grep("B23006", file_list, value = TRUE))
        medianincome <- import(grep("B19013", file_list, value = TRUE))
        
        reduce_acs <- function(acs_obj){
                #--------------------
                # Reduce `acs`` object to a dataframe
                # with 3 columns.
                #--------------------
                # acs_obj (acs object)
                #--------------------
                obj_name <- deparse(substitute(acs_obj))
                acs_obj@estimate %>%
                        merge(acs_obj@standard.error, by = 0) %>%
                        merge(acs_obj@geography, 
                              by.x = "Row.names", by.y = "NAME") %>%
                        dplyr::select(-state, -county, -Row.names)
        }
        # apply reduce_acs to the imported `acs` objects
        out <- list(total = total, black = black, hsgrad = hsgrad, 
                    medianincome = medianincome) %>%
                map(~ reduce_acs(.x)) 
        return(out)    
        
}

acs_list <- list.files("data/acs", pattern = "2015.rds$", 
                       full.names = TRUE) %>% import_acs()

us_county@data %<>% dplyr::select(-AFFGEOID, -GEOID, -LSAD, -ALAND, -AWATER) %>%
        mutate(fips_code = paste0(as.character(STATEFP), as.character(COUNTYFP))) %>%
        left_join(acs_full$total, by = "fips_code") %>%
        left_join(acs_list$black, by = "fips_code") %>%
        left_join(acs_list$hsgrad, by = "fips_code") %>%
        left_join(acs_list$medianincome, by = "fips_code") %>%
        rename(total.est = "B01003_001.x", 
               total.se = "B01003_001.y",
               black.est = "C02003_004.x", 
               black.se = "C02003_004.y",
               hsgrad.est = "B23006_009.x", 
               hsgrad.se = "B23006_009.y",
               medianincome.est = "B19013_001.x", 
               medianincome.se = "B19013_001.y") %>%
        mutate(blackpop.pct = black.est/total.est,
               hsgrad.pct = hsgrad.est/total.est)


## @knitr calc_conditionalprob
## calculate conditional probabilities 
dat <- over(pizzapolls, us_county) %>% 
        group_by(fips_code) %>%
        summarize(delivery_count = n()) %>%
        right_join(us_county@data, by = "fips_code") %>% 
        mutate(delivery_count = ifelse(is.na(delivery_count), 0, delivery_count)) 


calc_conditionalprob <- function(upper, increment){
        lower <- upper - increment
        delivery_cond_on_black <- sum(dat$delivery_count[dat$blackpop.pct >= lower & 
                                     dat$blackpop.pct <= upper] >= 1, 
                             na.rm = TRUE)/
                sum(dat$blackpop.pct >= lower & 
                            dat$blackpop.pct <= upper, na.rm = TRUE)
        black_cond_on_delivery <- sum(dat$delivery_count[dat$blackpop.pct >= lower & 
                                        dat$blackpop.pct <= upper] >= 1, 
                                na.rm = TRUE)/
                sum(dat$delivery_count >= 1, na.rm = TRUE)
        delivery_cond_on_hsgrad <- sum(dat$delivery_count[dat$hsgrad.pct >= lower & 
                                        dat$hsgrad.pct <= upper ] >= 1,
                              na.rm = TRUE)/
                sum(dat$hsgrad.pct >= lower & 
                            dat$hsgrad.pct <= upper, na.rm = TRUE)
        hsgrad_cond_on_delivery <- sum(dat$delivery_count[dat$hsgrad.pct >= lower & 
                                                dat$hsgrad.pct <= upper ] >= 1,
                                       na.rm = TRUE)/
                sum(dat$delivery_count >= 1, na.rm = TRUE)
        return(c(delivery_cond_on_black, black_cond_on_delivery,
                 delivery_cond_on_hsgrad, hsgrad_cond_on_delivery))
        
}

cond_prob_list <- seq(0.10, 0.50, by = 0.05) %>% 
        map_dfr(~ as.data.frame(rbind(calc_conditionalprob(.x, increment = 0.05))))

## @knitr plot_conditionalprob
plot(x = seq(0.10, 0.50, by = 0.05), y = cond_prob_list[,1])
