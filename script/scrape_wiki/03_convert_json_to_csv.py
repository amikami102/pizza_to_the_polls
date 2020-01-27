#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create dataframe from "<state>.json" files in "data/raw_wiki/house"
and "data/raw_wiki/state". Save dataframe as csv in "data/csv". 
"""

import argparse
import logging
import sys
import os
import json
import re
import pandas as pd
sys.path.append('/Users/asako/Google Drive/pizza_to_the_polls/script/scrape_wiki')
from us_states_list import states_dict 



# set up parser
parser = argparse.ArgumentParser(description='Convert json to csv.')
parser.add_argument('-senatedir', type = str,
                    help = 'Directory storing raw files for Senate races.',
                    default = "data/raw_wiki/senate")
parser.add_argument('-housedir', type = str,
                    help = 'Directory storing raw files for House races.',
                    default = "data/raw_wiki/house")
parser.add_argument('-govdir', type = str,
                    help = 'Directory storing raw files for gubernatorial races.', default = "data/raw_wiki/governor")
parser.add_argument('-csvdir', type = str,
                    help = 'Directory to store csv files.',
                    default = "data/csv")
parser.add_argument('-v', '--verbose', 
                    help = 'Set logging level to DEBUG.',
                    action = "store_true")
args = parser.parse_args()


# set up logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
if args.verbose:
    log.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler(sys.stderr)
loghandler.setFormatter(logging.Formatter("[%(asctime)s %(message)s"))
log.addHandler(loghandler)




""" STEP 0: create csv for senate and gubernatorial races"""

def create_df(race = "senate", datadir = args.senatedir):
    """
    Read "[race]_elections_2018.json" from corresponding data dir and
    and create a dataframe out of the dictionary.
    """
    json_file = race + "_elections_2018" + ".json"
    with open(os.path.join(datadir, json_file)) as j:
        dict_ = json.load(j)
    
    # create pd.DataFrame from dictionary
    df = pd.DataFrame.from_dict(dict_, orient = "index")
    # strip "\n" white space from strings 
    for col in df.columns:
        df[col] = [re.sub("\n", "", x) for x in df[col]]
    # convert percentages to numeric data type
    for col in ['percentage1', 'percentage2']:
        df.loc[:, col].astype('str')
        df = df.replace({col : r"[\%|\n]"}, 
                         {col: r""}, regex = True)
    
    
    # add a column for state abbreviation
    df.index = [re.sub(x, states_dict[x], x) for x in df.index]
    
    # save as csv
    csv_file = re.sub(".json", ".csv", json_file)
    df.to_csv(os.path.join(args.csvdir, csv_file))
    
    return df
    

""" STEP 1: create House dataframe """

def create_house_df(race = "house", datadir = args.housedir):
    """
    Read "house_elections_2018.json" stored in args.housedir
    and create a row from each district dictionary. 
    Output is pd.DataFrame. 
    """
    
    json_file = race + "_elections_2018" + ".json"
    
    with open(os.path.join(datadir, json_file)) as j:
        dict_ = json.load(j)
    
    house_df = pd.DataFrame()
    for state, districts in dict_.items():
        # state (str) and districts (dict)
        
        log.info("Adding rows for {}".format(state))
        
        # create pd.DataFrame from dictionary containing district race dictionaries
        df = pd.DataFrame.from_dict(districts, orient = "index")
        # drop rows if index label is "Results_summary"
        if "Results_summary" in df.index:
            df.drop(index = "Results_summary", inplace = True)
        
        # define a function to format district label
        pattern = "^District[_](?P<num>[0-9]{1,2})$"
        def format_district(matchobj):
            if matchobj.group('num') != None:
                return states_dict[state] + "-" + matchobj.group('num').zfill(2)
        df.index = [re.sub(pattern, format_district, x) for x in df.index]
        df.index = [re.sub("at-large", states_dict[state] + "-00", x) for x in df.index]
        
        
        # strip "\n" white space from strings
        for col in df.columns:
            df[col] = [re.sub("\n", "", x) for x in df[col]]

        # append df to house_df
        house_df = house_df.append(df)
            
        # save to csv
        df.to_csv(os.path.join(args.csvdir, state + "-house_elections_2018.csv"))
        log.info("CSV saved for House elections in {}".format(state))
        
    
    return house_df


""" STEP 2: clean House dataframe """
def clean_house_df(df):
    """
    Clean house_df returned from create_house_df() by
        - recode party labels,
        - convert percentages to numeric data type,
        - manually correct rows.
    """
    
    # rename index column
    df['district'] = df.index
    df = df.reset_index(drop = True)
    
    # recode party labels
    parties = ["Republican", "Democratic"]
    df.loc[~df.party1.isin(parties), "party1"] = "Other"
    df.loc[~df.party2.isin(parties), "party2"] = "Other"
    
    
    
    
    # manually correct rows
    df.loc[df['district'] == "AL-07", "candidate2"] = "Write-ins"
    df.loc[df['district'] == "ME-02", :] = [
                        "Jared Golden", "Bruce Poliquin",
                        "Democratic", "Republican", 50.62, 49.38, "ME-02"]
    df = df[df.district != "Results_Summary"]
    
    df.loc[df['district'] == "NY-05", ["candidate2", "share2"]] = ['NA', 0]
    df.loc[df['district'] == 'NC-03', ["candidate2", "share2"]] = ['NA', 0]
    df.loc[df['district'] == 'FL-21', :] = ['Lois Frankel', 'NA', 
                                          'Democratic', 'NA',
                                          100.0, 0, "FL-21"]
    df.loc[df['district'] == "FL-14", :] = ["Kathy Castor", "NA",
                                          "Democratic", "NA", 
                                          100.0, 0, "FL-14"]
    df.loc[df['district'] == "FL-15", :] = ["Ross Spano", "Kristen Carlson",
                                             "Republican", "Democratic",
                                             53.0, 47.0, "FL-15"]
    df.loc[df['district'] == 'FL-10', :] = ["Val Demings", "NA",
                                          "Democratic", "NA",
                                          100.0, 0, "FL-10"]
    df.loc[df['district'] == 'FL-24', :] = ["Frederica Wilson", "NA",
                                          "Democratic", "NA",
                                          100.0, 0, "FL-24"]
    df.loc[df['district'] == "NY-10", :] = ["Jerrold Nadler", "Naomi Levin",
                                          "Democratic", "Republican",
                                          82.1, 17.9, "NY-10"]
    df.loc[df['district'] == "NY-13", :] = ["Adriano Espaillat", "Jineea Butler",
                                          "Democratic", "Republican",
                                          94.6, 5.4, "NY-13"]
    df.loc[df['district'] == "NY-02", :] = ["Peter T. King", "Liuba Grechen Shirley",
                                             "Republican", "Democratic",
                                              53.1, 46.9, "NY-02"]
    df.loc[df['district'] == "NY-22", :] = ["Anthony Brindisi", "Claudia Tenney",
                                          "Democratic", "Republican",
                                          50.9, 49.1, "NY-22"]
    df.loc[df['district'] == "NY-23", :] = ["Tom Reed", "Tracy Mitrano", 
                                          "Republican", "Democratic",
                                          54.2, 45.8, "NY-23"]
    df.loc[df['district'] == "NY-24", :] = ["John Katko", "Dana Balter", 
                                          "Republican", "Democratic",
                                          52.6, 47.4, "NY-24"]
    df.loc[df['district'] == "NY-25", :] = ["Joseph Morelle", "Jim Maxwell", 
                                          "Democratic", "Republican",
                                          59.0, 41.0, "NY-25"]
    df.loc[df['district'] == "NY-26", :] = ["Brian Higgins", "Renee Zeno", 
                                          "Democratic", "Republican",
                                          73.3, 26.7, "NY-26"]
    df.loc[df['district'] == "PA-18", :] = ["Michael Doyle", "NA",
                                              "Democratic", "NA",
                                              100.0, 0, "PA-18"]


    # convert percentages to numeric data type
    for col in ['share1', 'share2']:
        df.loc[:, col].astype('str')
        df = df.replace({col : r"[\%|\n]"}, 
                         {col: r""}, regex = True)
        
    # save to file
    df.to_csv(os.path.join(args.csvdir, "house_elections_2018.csv"))
    
    return df
    
    
        

if __name__ == "__main__":
    
    
    senate_df = create_df("senate", args.senatedir)
    log.info(senate_df.info())
    
    guber_df = create_df("gubernatorial", args.govdir)
    log.info(guber_df.info())
    
    house_df = create_house_df()
    house_df = clean_house_df(house_df)
    log.info(house_df.info())
    
    sys.exit()

    
    
    
    
    
    
    
    
    
    
    
    