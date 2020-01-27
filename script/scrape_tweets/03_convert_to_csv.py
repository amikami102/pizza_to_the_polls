#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import json
import sys
import pandas as pd


# set up arg parser 
parser = argparse.ArgumentParser(description='Clean and process tweets')
parser.add_argument('-script02dir', type = str,
                    help = "Directory storing outputs from 02_clean_and_process.py",
                    default = "data/tweets/script02")
parser.add_argument('-shpdir', type = str,
                    help = "Directory storing shp files",
                    default = "data/shp")
parser.add_argument('-csvdir', type = str,
                    help = "Directory storing csv files",
                    default = "data/csv")
parser.add_argument('-v','--verbose',
                    help = "Set log level to debug", action="store_true")
args = parser.parse_args()



# set up logging
log = logging.getLogger(__name__)
f_handler = logging.FileHandler('{}.log'.format(__file__))
f_format = logging.basicConfig(format='%(asctime)s - %(message)s')
f_handler.setFormatter(f_format)
log.addHandler(f_handler)



if __name__ == "__main__":
    
    colnames = ("st_num", "route", "city", "state_abbv",
                "zipcode", "county", "lng", "lat", 
                "created_at", "id", "clean_text")
    df = pd.DataFrame(columns = colnames)
    
    # create a list of files in "data/tweets/script02"
    parsed_list = []
    for file in sorted(os.listdir(args.script02dir)):
        if (file.startswith("parsed") and file.endswith(".json")):
            parsed_list.append(file)
    
    # iterate over `parsed_list`
    for file in parsed_list:
        with open(os.path.join(args.script02dir, file), "r") as p:
            tweets = json.load(p)
        for tweet in tweets:
            if tweet.get('contain_address') == True:
                print(tweets.index(tweet))
                subset_tweet = {k:v for k, v in tweet.items() if k in colnames}
                df = df.append(pd.DataFrame.from_records(subset_tweet, index = [0]), 
                               sort = True)
            else:
                pass
                
    csv_path = os.path.join(args.csvdir, "PizzaToThePolls.csv")
    df.to_csv(csv_path)
    sys.exit()










