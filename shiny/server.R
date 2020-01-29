## server.R


library(leaflet)
library(tmap)
library(tmaptools)
library(rio)
library(RColorBrewer)
library(tidyverse)
library(magrittr)

shinyServer(function(input, output) {
        
        output$map = renderLeaflet({
                tm <- tm_basemap(server = "Wikimedia") +
                        tm_shape(pizzapolls, name = "pizzas delivered") +
                        tm_markers(tmap_icons = "pizza.png") + 
                        tm_shape(us_cd, name = "Key House races", unit = "km", bbox = usa_main) +
                        tm_polygons(col = "key", title = "Key House races",
                                    palette = "Blues", alpha = 0.5,
                                    popup.vars = c("candidate1", "party1", "share1",
                                                   "candidate2", "party2", "share2")
                        ) +
                        tm_shape(us_state, name = "Key Senate races") +
                        tm_polygons(col = "key_sen", 
                                    palette = "Oranges", alpha = 0.5,
                                    title= "Key Senate races",
                                    popup.vars = c("candidate1_sen", "party1_sen", "share1_sen", "candidate2_sen", "party2_sen", "share2_sen")
                        ) + 
                        tm_shape(us_state, name = "Key governor races") + 
                        tm_polygons(col = "key_gov", 
                                    palette = "Purples", alpha = 0.5,
                                    title = "Key governor races",
                                    popup.vars = c("candidate1_gov", "party1_gov", "share1_gov", "candidate2_gov", "party2_gov", "share2_gov")
                        ) + 
                        tm_facets(as.layers = TRUE)
                tmap_leaflet(tm) %>%
                        addTiles(
                               urlTemplate = "//{s}.tiles.mapbox.com/v3/jcheng.map-5ebohr46/{z}/{x}/{y}.png",
                               attribution = 'Maps by <a href="http://www.mapbox.com/">Mapbox</a>'
                        ) %>%
                        setView(lng = -93.85, lat = 37.45, zoom = 5)
        })
        
})