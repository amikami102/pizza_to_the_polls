#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from requests.exceptions import HTTPError
import json
import sys
from commonregex import CommonRegex
import logging
import re
import argparse
import xml.etree.ElementTree as ET
import time

# set up parser
parser = argparse.ArgumentParser(description='Clean and process tweets')
parser.add_argument('-script01dir', type = str,
                    help = 'Directory storing outputs from 01_scrape_twitter.py',
                    default = 'data/tweets/01_scraped')
parser.add_argument('-script02dir', type = str,
                    help = 'Directory storing outputs from 02_clean_and_find_address.py',
                    default = "data/tweets/02_cleaned")
parser.add_argument('-v','--verbose', 
                    help = "Set log level to debug", 
                    action="store_true")
args = parser.parse_args()



# set up logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
if args.verbose:
    log.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler(sys.stderr)
loghandler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
log.addHandler(loghandler)



""" STEP 1: clean and record whether tweet text contains street address"""
regex_parser = CommonRegex()


def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing 
    links and special characters using regex.
    '''
    return ' '.join(re.sub("(@[\S]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def find_address(jsonfile):
    """
    Cleans tweet text.
    Adds entry {'contain_address': (logical)} to tweet dictionary where 
    (logical) indicates whether the cleaned tweet contains street addresses.
    ===================
    jsonfile = (str of .json file name containing the tweets)
    """
    # Load the JSON file 
    with open(os.path.join(args.script01dir, jsonfile), "r", errors = "ignore") as j:
        tweets = json.load(j)
        
    
    
    out_list = []
    c = 0 # counter for number of tweets containing address
    for tweet in tweets:
        query = clean_tweet(tweet['text'])
        tweet.update({'clean_text': query}) # add clean text to `tweet`
        # Check whether the cleaned text contains street address
        if regex_parser.street_addresses(query) == []:
            tweet.update({'contain_address': False})
        else:
            if re.search('pizza', query) != None or re.search('1 8{1-3}[0-9]{1-2}', query) != None:
                tweet.update({'contain_address': False})
                
            else:
                tweet.update({'contain_address': True})
                c += 1
                out_list.append(tweet)
    
    # Save to "cleaned*.json" file
    cleanfile = jsonfile.replace("scraped", "cleaned")
    with open(os.path.join(args.script02dir, cleanfile), "w") as j:
        json.dump(out_list, j)
    
    # Log how many tweets were found containing address
    message = "{} tweets containing address"
    log.info(message.format(c))

        

               
if __name__ == "__main__":
    
    os.chdir(os.path.abspath("/Users/asako/Google Drive/pizza_to_the_polls"))
    
    path = os.path.join(os.getcwd(), args.script01dir)  
    for file in sorted(os.listdir(path)):
        find_address(file)
    
    
    print("Reached last file")
    sys.exit()
        
    
