## ui.R
library(leaflet)

shinyUI(navbarPage("Locating Long Polling Lines with Twitter Data",
        absolutePanel(
                div(class="outer",
                tags$head(
                    includeCSS("styles.css")# Include our custom CSS
                    ),
                leafletOutput("map", width = "100%", height = "100%"),
                tags$div(id="cite",
                         'Data collected by Asako Mikami (2019)', 
                         a(icon(name = "github", lib = "font-awesome"),
                           href = "https://github.com/amikami102/pizza_to_the_polls")
                )
        )
)))