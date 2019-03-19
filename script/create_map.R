####----------------------------
## Create a map of US congressional district
## and plot polling locations where pizzas
## were delivered.
####----------------------------

x <- c("dplyr", "purrr", "forcats",
       "sf", "RColorBrewer", "tmap", "raster", "rgdal",
       "tidycensus")
lapply(x, library, character.only = TRUE, quietly = TRUE)
color <- brewer.pal(3, "Set1")


# STEP 1: load shape files

## build `shpname`
dir_url <- "https://www2.census.gov/geo/tiger/GENZ2016/shp/"
ss <- "us" 
entity <- c("cd115", # congressional district
            "county") # county
rr <- "500k" # resolution
shpname <- paste("cb_2016", ss, entity, rr, sep = "_")

## download zipfile to temporary file
shpname %>% map(~ {
        url <- paste0(dir_url, ., ".zip")
        temp <- tempfile()
        download.file(url, destfile = temp)
        dir <- file.path("data", "shp", .)
        unzip(temp, exdir = dir)
})

## read .shp file as SpatialPolygonsDataFrame
us_cd <- readOGR(dsn = file.path("data", "shp", 
                                 shpname[grep("cd", shpname)]),
                 layer = shpname[grep("cd", shpname)])
us_county <- readOGR(dsn = file.path("data", "shp", 
                                     shpname[grep("county", shpname)]),
                      layer = shpname[grep("county", shpname)])


# STEP 2: clean us_cd 

## join `fips_codes` to us_cd@data
data(fips_codes) # from tidycensus
fips_codes <- fips_codes %>% 
        dplyr::select(-county_code, -county) %>% 
        map_if(is.character, factor) %>% 
        as.data.frame() 
us_cd@data <- us_cd@data %>% dplyr::select(-AWATER, -ALAND) %>%
        mutate(STATEFP = factor(STATEFP, 
                                levels(fips_codes$state_code)),
               STATE = )  



## add "senate_elections_2018.csv" columns 
senate2018 <- read.csv(file.path("data", "csv", 
                        paste("senate_elections_2018.csv"))) %>%
                mutate(state = factor(X, levels(fips_codes$state))) %>%
                dplyr::select(-X)


# STEP 3: 
# import "PizzaToThePolls.csv" as dataframe and convert to sf object
pizzapolls <- file.path("data", "csv", 
                        "PizzaToThePolls.csv") %>%
        read.csv(header = TRUE) %>%
        st_as_sf(coords = c("lng", "lat"))
st_crs(pizzapolls) <- st_crs(us_cd)$proj4string


# STEP 4:
# set up bounding box for coterminous US
usa_main <- matrix(c(-130, 25, -60, 50), nrow = 2, byrow = FALSE)


# STEP 5:
# create interactive map
tmap_mode("view")
tm_basemap("OpenStreetMap.DE") +
tm_shape(us_cd, bbox = usa_main) + tm_polygons()

+
tm_shape(us_county, bbox = usa_main) +  
        tm_borders(lty = "dotted", lwd = 0.5) 
tm_shape(pizzapolls) +
        tm_dots(col = color[1]) 


