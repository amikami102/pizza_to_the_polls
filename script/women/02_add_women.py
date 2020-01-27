#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This scipt files columns to "[race]-elections-2018.csv" dataframes
that indicate whether candidate1 or candidate2 is female. 
If candidate1 is a woman but not candidate2, female1 == 1 and female2 == 0, 
and vice versa. 
"""
import sys
import argparse
import logging
import os
import pandas as pd
import json
import re

# set argument parser
parser = argparse.ArgumentParser(description='Get junior faculty for each school.')
parser.add_argument("-csvdir", type = str,
                    help = "Directory storing csv files.",
                    default = "data/csv")
parser.add_argument("-v", "--verbose", 
                    help = "Set logging level to DEBUG.",
                    action = "store_true")
args = parser.parse_args()

# set logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
if args.verbose:
    log.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler(sys.stderr)
loghandler.setFormatter(logging.Formatter("[%(asctime)s %(message)s]"))
log.addHandler(loghandler)

governor_pre = pd.read_csv(os.path.join(args.csvdir,      
                                     "gubernatorial_elections_2018.csv"))
governor_pre.rename(columns = {"Unnamed: 0": "state"}, inplace = True)


senate_pre = pd.read_csv(os.path.join(args.csvdir, 
                                  "senate_elections_2018.csv"))
senate_pre.rename(columns = {"Unnamed: 0": "state"}, inplace = True)

house_pre = pd.read_csv(os.path.join(args.csvdir, 
                                 "house_elections_2018.csv"),
    index_col = 0)


with open("data/cawp/women-candidate-2018.json", "r") as j:
    women = json.load(j)




"""Step 1"""
def convert_women(dict_ = women):
    """
    Converts `women` from a collection of lists into a collection of
    dictionaries. 
    """
    
    s_col = ["office", "name", "party", "status", "result"]
    h_col = ["office", "district", "name", "party", "status", "result"]
    
    OUT = {}
    for k, v in dict_.items():
        d = []
        for e in v:
            if len(e) == len(s_col):
                d.append(dict(zip(s_col, e)))
            if len(e) == len(h_col):
                d.append(dict(zip(h_col, e)))
        OUT.update({k: d})
    
    return OUT



""" Step 2"""
def create_df(dict_):
    """
    Converts the dictionary output of convert_women() into
    a dataframe with columns "district", "office", "name", "party",
    "status", "result", and "state."
    """
    
    
    OUT = pd.DataFrame()
    for k in dict_.keys():
        rows = pd.DataFrame.from_dict(dict_[k])
        rows['state'] = k 
        OUT = pd.concat([OUT, rows], sort = True)
    
    
        
    # clean dataframe
    OUT = OUT.replace({r"\*": ""}, regex = True)
    
    # fix the following rows
    to_fix = ['Christine Russell (R)', 'Candius Stearns (R)',
              'Renee M. Zeno (R)','Anya Tynio (R)']
    for f in to_fix:
        row = OUT.party == f
        OUT.district[row] = OUT.name[row]
        try:
            pattern = "(?P<full>\w+\s\w+) (?P<party>\(\w\))"
            match = re.search(pattern, OUT.party[row].to_string()) 
            OUT.name[row] = match.group("full")
            OUT.party[row] = match.group("party")
        except AttributeError:
            pattern = "(?P<full>\w+\s\w+.\s\w+) (?P<party>\(\w\))"
            match = re.search(pattern, OUT.party[row].to_string()) 
            OUT.name[row] = match.group("full")
            OUT.party[row] = match.group("party")
    
    # rename parties
    OUT.loc[OUT['party'].isin(["(DFL)", "(D-NPL)"]), "party"] = "(D)"
    OUT.loc[OUT.party == "(D)", "party"] = "Democratic"
    OUT.loc[OUT.party == "(R)", "party"] = "Republican"
    
    # add suffix to column names 
    colnames = OUT.columns[~OUT.columns.isin(["state", "office", "district"])]
    OUT.rename(columns = dict(zip(colnames, 
                list(map(lambda x: x + "_woman", colnames)))), inplace = True)


    return OUT



""" Step 3"""
def split_df(df):
    """
    Splits the dataframe output from create_df() into three
    separate dataframes by office. Since some senate and house races
    had two female candidates, the function moves these duplicate rows
    to entries of new columns. 
    """
    
    groups = df.groupby("office")
    g = groups.get_group("Governor").drop(['district', 'office'], axis = 1)
    s = groups.get_group("U.S. Sen.").drop(['district', 'office'], axis = 1)
    h = groups.get_group("U.S. Rep.").drop("office", axis = 1)
    
    # Senate
    s = s[~s.name_woman.isin(["Tina Smith", "Karin Housley"])] #special election
    new_col = s.loc[s.state.duplicated(keep = "first"), :]
    s = pd.merge(s.loc[~s.state.duplicated(keep = "first"), :],
                       new_col, on = "state", 
                       how = "left", suffixes=('1', '2'))
    
    # House of representatives
    ## rename all-state districts to "00" and concactenate state and district 
    h.loc[h.district == 'AL', 'district'] = "00"
    h.loc[:, 'district'] = h.loc[:, 'state'] + "-" + h.loc[:, 'district']
    new_col = h.loc[h.district.duplicated(keep = "first"), 
                    h.columns[h.columns != "state"]]
    h = pd.merge(h.loc[~h.district.duplicated(keep = "first"), :],
                       new_col, on = "district", how = "left",
                       suffixes=('1', '2'))
    

    return g, s, h


if __name__ == "__main__":
    
 
    women_df = create_df(convert_women())
    
    g, s, h = split_df(women_df)
    
    governor = pd.merge(governor_pre, g, on = 'state', how = 'left')
    senate = pd.merge(senate_pre, s, on = 'state', how = 'left')
    house = pd.merge(house_pre, h, on = "district", how = "left")
    
    
    file_names = [s + "_elections_2018_merged.csv" for s in ['gubernatorial', 'senate', 'house']]
    
    for df, file in zip([governor, senate, house], file_names):
            df.to_csv(os.path.join(args.csvdir, file))
    
    
    log.info(governor.info())
    log.info(senate.info())
    log.info(house.info())
    
    sys.exit()
    
