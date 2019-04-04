####----------------------------
## This script creates a map of US congressional district
## and plots polling locations where pizzas
## were delivered by Pizza To The Polls.
####----------------------------

x <- c("tidyverse", "magrittr", "RColorBrewer", "rio",
       "sf", "tmap", "raster", "rgdal",
       "tidycensus")
lapply(x, library, character.only = TRUE, quietly = TRUE)
color <- brewer.pal(3, "Accent")
data(fips_codes) # from `tidycensus`

## read .shp file as SpatialPolygonsDataFrame
district <- "cb_2016_us_cd115_500k"
county <- "cb_2016_us_county_500k"
us_cd <- readOGR(dsn = file.path("data", "shp", district), layer = district)
us_county <- readOGR(dsn = file.path("data", "shp", county), layer = county)

states <- fips_codes %>% dplyr::select(state, state_code, state_name) %>%
        filter(!duplicated(.))
senate <- import(file.path("data", "csv", "senate_elections_2018.csv"),
                 header = TRUE)
house <- import(file.path("data", "csv", "house_elections_2018.csv"),
                header = TRUE)
us_cd@data %<>% left_join(states, by = c("STATEFP" = "state_code")) %>% 
        mutate(label = paste(state, CD115FP, sep = "-")) %>%
        left_join(house, by = c("label" = "V1"))
        





# import pizzapolls.csv
pizzapolls <- import(file.path("data", "csv", "PizzaToThePolls.csv"), 
                     format = "csv", header = TRUE) %>%
        st_as_sf(coords = c("lng", "lat"))
st_crs(pizzapolls) <- st_crs(us_cd)$proj4string


# STEP 4:
# set up bounding box for coterminous US
usa_main <- matrix(c(-120, 25, -70, 45), nrow = 2, byrow = FALSE)


# STEP 5:
# create interactive map
tmap_mode("view")
tm <- tm_shape(us_cd, name = "US congressional district", unit = "km",
         bbox = usa_main) + 
        tm_polygons(border.col = color[2], id = "label", 
                    popup.vars = c("state_name", 
                                   "candidate1", "party1", "share1",
                                   "candidate2", "party2", "share2")) + 
        tm_shape(pizzapolls) +
        tm_markers()

