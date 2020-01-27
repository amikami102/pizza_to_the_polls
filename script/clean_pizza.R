####----------------------------
## This script imports PizzaToThePolls.csv 
## and creates aggregated dataframes. 
## all_locs (the raw dataset created from all tweets containing street addresses)
## unique_locs (aggregated dataset of unique street addresses) 
####----------------------------

x <- c("tidyverse", "magrittr", "RColorBrewer", "rio",
       "sf", "tmap", "raster", "rgdal",
       "tidycensus")
lapply(x, library, character.only = TRUE, quietly = TRUE)

all_locs <- read_csv("data/csv/PizzaToThePolls.csv", 
                  col_types = cols(X1 = col_skip())) %>%
        dplyr::select(id, created_at, lat, lng, 
                      st_num, route, city, county, zipcode, state_abbv, clean_text
                      ) %>%
        mutate(id = as.character(id),
               created_at = paste("2018-11-06", 
                        str_extract(created_at, "[0-9]{2}:[0-9]{2}:[0-9]{2}")) %>% 
                       ymd_hms(),
               lng = round(lng, digits = 3),
               lat = round(lat, digits = 3)
        ) 


unique_locs <- all_locs %>% 
  group_by(st_num, route, city, state_abbv, lng, lat) %>% 
  summarize(count = n()) %>%
  drop_na() 
unique_locs[unique_locs$route == "Saint Marks Avenue", "st_num"] <- 442 
print(dim(unique_locs))

# fix rows with same address but slightly different geocoordinates
duplicates <- c("Bees Ferry Road", "Bright Street", "Centerville Highway",
  "Chamberlain Street Southeast", "Garibaldi Street Southwest",
  "Mikell Drive", "North Rogers Avenue", "Saint Marks Avenue")

coord <- duplicates %>% 
  map(~ unique_locs[unique_locs$route == .x, ]) %>% 
  map_df(~.x[1, c("lng", "lat")], .x[2, c("lng", "lat")]) %>%
  as.data.frame() %>% cbind(route = duplicates)

for (r in duplicates){
  unique_locs[unique_locs$route == r, c("lng", "lat")] <- coord[coord$route == r, c("lng", "lat")]
}

# group by addresses again and aggregate the count values 
unique_locs %<>% group_by(st_num, route, city, state_abbv, lng, lat) %>%
  summarize(count = sum(count)) %>%
        st_as_sf(coords = c("lng", "lat")) 
print(dim(unique_locs))

save(all_locs, unique_locs, file = "data/clean_pizza.Rdata")
