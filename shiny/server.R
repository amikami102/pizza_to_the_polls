## server.R


library(leaflet)
library(tmap)
library(rio)
library(RColorBrewer)

shinyServer(function(input, output) {
        
        output$map = renderLeaflet({
                color <- brewer.pal(3, "Set2")
                tm <- #tm_basemap(server = "OpenStreetMap") +
                        tm_shape(us_cd, name = "US congressional district", unit = "km",
                                 bbox = usa_main) + 
                        tm_polygons(alpha = 0, col = NA, # do not color polygons
                                    border.col = color[1], border.alpha = 0.8, # district lines
                                    lwd = 0.8, lty = 3, # state boundary lines
                                    id = "label", 
                                    popup.vars = c("state_name", 
                                                   "candidate1", "party1", "share1",
                                                   "candidate2", "party2", "share2")) + 
                        tm_shape(pizzapolls) +
                        tm_markers(palette = color)
                tmap_leaflet(tm) %>%
                        addTiles(
                                urlTemplate = "//{s}.tiles.mapbox.com/v3/jcheng.map-5ebohr46/{z}/{x}/{y}.png",
                                attribution = 'Maps by <a href="http://www.mapbox.com/">Mapbox</a>'
                        ) %>%
                        setView(lng = -93.85, lat = 37.45, zoom = 5)
        })
        
})