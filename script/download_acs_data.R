# !usr/bin/env Rscript
#----------------------------------------
# This script downloads 2013-2017 5-year ACS data and 
# create a column of district labels. 
#----------------------------------------


# load favorite libraries
x <- c("tidyverse", "magrittr", "RColorBrewer", "rio",
       "tidycensus","dotenv")
lapply(x, library, character.only = TRUE, quietly = TRUE)
load_dot_env(file = ".env")
census_api_key(Sys.getenv("census_api_key"))


# get ACS data with tidycensus::get_acs()
#---------------------------------------
# Census table numbers, variable code:
# "B19013_001" median household income, 
# "B01003_001" total population,
# "C02003_004" for Black population,
# "B03001_001" for Hispanic population
# "B16010_029" college degree and in labor force, 
# "B16010_016" high school or eq. degree and in labor force

get_cd_data <- function(geography = 'congressional district', var, varname){
        # Retrieves ACS data with tidycensus::get_acs() for the 
        # specified variable, renames columns, and 
        # drops unnecessary columns.
        #-----------------------------------
        # geography (char, set by default to 'congressional district')
        # var (char, ACS variable label)
        #-----------------------------------
        tab <- get_acs(geography, variable = var, year = 2017
                       ) %>%
                rename_at("estimate", ~ paste(varname, ., sep = "_")) %>%
                rename_at("moe", ~ paste(varname, ., sep = "_")) %>%
                dplyr::select(-variable, -NAME)
        
        
        return(tab)
        
}

median_houseinc <- get_cd_data(var = "B19013_001", varname = "medianHouseInc")
total_pop <- get_cd_data(var = "B01003_001", varname = "totalPop")
black_pop <- get_cd_data(var = "C02003_004", varname = "blackPop")
hisp_pop <- get_cd_data(var = "B03001_001", varname = "hispPop")
age18to19_male <- get_cd_data(var = "B01001_007", varname = "age18to19_male")
age18to19_female <- get_cd_data(var = "B01001A_022", varname = "age18to19_female")
age20to24_male <- get_cd_data(var = "B01001A_008", varname = "age20to24_male")
age20to24_female <- get_cd_data(var = "B01001A_023", varname = "age20to24_female")

# save data
save(median_houseinc, total_pop, black_pop, hisp_pop, 
     age18to19_male, age18to19_female,
     age20to24_male, age20to24_female,
     file = "data/acs_cd.Rdata")




