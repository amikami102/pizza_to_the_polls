####----------------------------
## This script creates the dataframe to be used for analysis portion 
# of the report.
####----------------------------

x <- c("tidyverse", "magrittr", "RColorBrewer", "rio",
       "sf", "tmap", "raster", "rgdal",
       "tidycensus")
lapply(x, library, character.only = TRUE, quietly = TRUE)


## read .shp file as SpatialPolygonsDataFrame
cd <- "cb_2017_us_cd115_500k" # district shpfile
state <- "cb_2018_us_state_500k" # state shpfile
county <- "cb_2018_us_county_within_cd116_500k"
us_cd <- readOGR(dsn = file.path("data", "shp", cd), 
                 layer = cd,
                 verbose = FALSE)
us_state <- readOGR(dsn = file.path("data", "shp", state), 
                    layer = state,
                    verbose = FALSE)
us_county <- readOGR(Dsn = file.path("data", "shp", county),
                     layer = county,
                     verbose = FALSE)

## create a dataframe of state names and their 2-digit FIPS code
data(fips_codes) # from `tidycensus`
states <- fips_codes %>% 
        dplyr::select(state, state_code, state_name) %>%
        filter(!duplicated(.))

## clean data
us_cd@data %<>% dplyr::select(-AFFGEOID, -LSAD,-CDSESSN, 
                              -ALAND, -AWATER) %>%
        left_join(states, by = c("STATEFP" = "state_code")) %>% 
        mutate(label = paste(state, CD115FP, sep = "-"))
us_state@data %<>%dplyr::select(-STATENS, - AFFGEOID, -GEOID,
                                 -LSAD, -ALAND, -AWATER) 


## merge with election data
load("data/2018-election-results.Rdata")
us_cd@data %<>% left_join(house_races, by = c("label" = "district")) 
state_level <- full_join(senate_races, governor_races, by = "state", 
                         suffix = c("_sen", "_gov"))
us_state@data %<>% left_join(state_level, by = c("STUSPS" = "state"))



# import `unqiue_locs` from 'data/clean_pizza.Rdata' and 
# turn into spatial object
load(file = "data/clean_pizza.Rdata")
pizzapolls <- unique_locs %>% st_as_sf(coords = c("lng", "lat"))
st_crs(pizzapolls) <- st_crs(us_cd)$proj4string
print(dim(pizzapolls))

# STEP 4:
# set up bounding box for coterminous US
usa_main <- matrix(c(-120, 25, -70, 45), nrow = 2, byrow = FALSE)

# STEP 5:
# intersect us_cd with pizzapolls and convert to sf object
us_cd %<>% st_as_sf() 
us_state %<>% st_as_sf() 
pizzapolls_cd <- pizzapolls %>% st_as_sf() %>% st_join(us_cd)
print(dim(us_cd))
print(dim(us_state))
print(dim(pizzapolls_cd))

# STEP 6: save to file in data/ and shiny/ folders
save(pizzapolls, us_cd, us_state, usa_main, pizzapolls_cd,
     file = "data/map_data.Rdata")
save(pizzapolls, us_cd, us_state, usa_main, pizzapolls_cd,
     file = "shiny/map_data.Rdata")



