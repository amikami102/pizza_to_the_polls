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
parser.add_argument('-chamber', type = str,
                    help = 'Chamber to create csv for: "house" or "senate".',
                    default = "senate")
parser.add_argument('-senatedir', type = str,
                    help = 'Directory storing raw files for Senate races.',
                    default = "data/raw_wiki/senate")
parser.add_argument('-housedir', type = str,
                    help = 'Directory storing raw files for House races.',
                    default = "data/raw_wiki/house")
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




""" STEP 0: create """

def create_senate_df(chamber = "senate"):
    """
    Read "senate_elections_2018.json" in args.senatedir
    and create a dataframe out of the dictionary.
    """
    json_file = chamber + "_elections_2018" + ".json"
    with open(os.path.join(args.senatedir, json_file)) as j:
        dict_ = json.load(j)
    
    # create pd.DataFrame from dictionary
    df = pd.DataFrame.from_dict(dict_, orient = "index")
    # strip "\n" white space from strings 
    for col in df.columns:
        df[col] = [re.sub("\n", "", x) for x in df[col]]
    
    # add a column for state abbreviation
    df.index = [re.sub(x, states_dict[x], x) for x in df.index]
    
    # save as csv
    csv_file = re.sub(".json", ".csv", json_file)
    df.to_csv(os.path.join(args.csvdir, csv_file))
    
    return df
    

""" STEP 1: create House dataframe """

def create_house_df(chamber = "house"):
    """
    Read "house_elections_2018.json" stored in args.housedir
    and create a row from each district dictionary. 
    Output is pd.DataFrame. 
    """
    
    json_file = chamber + "_elections_2018" + ".json"
    
    with open(os.path.join(args.housedir, json_file)) as j:
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
        
        # define a function to format the index label
        pattern = "^District[_](?P<num>[0-9]{1,2})$"
        def format_district(matchobj):
            if matchobj.group('num') != None:
                return states_dict[state] + "-" + matchobj.group('num').zfill(2)
        df.index = [re.sub(pattern, format_district, x) for x in df.index]
        df.index = [re.sub("at-large", states_dict[state] + "-00", x) for x in df.index]
        
        
        # define a function to add "%" sign
        def add_percent(matchobj):
            if matchobj.group(0) != None:
                return matchobj.group(0) + "%"
        pattern = "^[0-9]{1,2}\.[0-9]{1,2}$"
        
        # strip "\n" white space from strings and add "%" to percentages
        for col in df.columns:
            df[col] = [re.sub("\n", "", x) for x in df[col]]
            if col in ("share1", "share2"):
                df[col] = [re.sub(pattern, add_percent, x) for x in df[col]]
        
        # append df to house_df
        house_df = house_df.append(df)
            
        # save to csv
        df.to_csv(os.path.join(args.csvdir, state + "-house_elections_2018.csv"))
        log.info("CSV saved for House elections in {}".format(state))
        
        
    
    # save to file
    csv_file = re.sub(".json", ".csv", json_file)
    house_df.to_csv(os.path.join(args.csvdir, csv_file))
    
    return house_df



        

if __name__ == "__main__":
    
    
    create_senate_df("senate")
    
    create_house_df("house")
    
    sys.exit()

    
    
    
    
    
    
    
    
    
    
    
    