## ui.R
library(leaflet)

shinyUI(navbarPage("2018 midterm polling locations",
        tabPanel("pizzas delivered",
                div(class="outer",
                tags$head(
                    includeCSS("styles.css")# Include our custom CSS
                    ),
                leafletOutput("map", width = "100%", height = "100%"),
                tags$div(id="cite",
                         'Data collected by Asako Mikami (2019)', 
                         a(icon(name = "github", lib = "font-awesome"),
                           href = "https://amikami102.github.io")
                )
        )
)))