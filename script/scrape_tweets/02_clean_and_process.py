#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
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
parser.add_argument('-rawdir', type = str,
                    help = 'Direcotry of raw Twitter API output files',
                    default = 'data/raw')
parser.add_argument('-scrapeddir', type = str,
                    help = 'Directory of scraped twitter files',
                    default = 'data/scraped')
parser.add_argument('-cleaneddir', type = str,
                    help = 'Directory of cleaned twitter files',
                    default = "data/cleaned")
parser.add_argument('-parseddir', type = str,
                    help = 'Directory of parsed twitter files',
                    default = 'data/parsed')
parser.add_argument('-v','--verbose', 
                    help = "Set log level to debug", 
                    action="store_true")
args = parser.parse_args()



# set up logging
log = logging.getLogger(__name__)
f_handler = logging.FileHandler('{}.log'.format(__file__))
f_format = logging.basicConfig(format='%(asctime)s - %(message)s')
f_handler.setFormatter(f_format)
log.addHandler(f_handler)



""" STEP 0: clean and record whether tweet text contains street address"""
regex_parser = CommonRegex()


def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing 
    links and special characters using regex.
    '''
    return ' '.join(re.sub("(@[\S]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def find_address(jsonfile):
    """
    Cleans tweet text and adds to tweet dictionary.
    Adds entry {'contain_address': (logical)} to tweet dictionary where 
    (logical) indicates whether the cleaned tweet contains street addresses.
    ===================
    jsonfile = (str of .json file name containing the tweets)
    """
    # Load the jsonfile containing scraped tweets
    with open(os.path.join(args.scrapeddir, jsonfile), "r", errors = "ignore") as j:
        tweets = json.load(j)
        
    
    
    out_list = []
    c=0 # counter for number of tweets containing address
    for tweet in tweets:
        query = clean_tweet(tweet['text'])
        tweet.update({'clean_text': query}) # add clean text to `tweet`
        # Check whether the cleaned text contains street address
        if regex_parser.street_addresses(query) == []:
            tweet.update({'contain_address': False})
        else:
            tweet.update({'contain_address': True})
            c += 1
        out_list.append(tweet)
    
    # Save to "cleaned*.json" file
    cleanfile = jsonfile.replace("scraped", "cleaned")
    with open(os.path.join(args.cleaneddir, cleanfile), "w") as j:
        json.dump(out_list, j)
    
    # Log how many tweets were found containing address
    message = "{} tweets containing address".format(c)
    log.info(message)
    print(message)
        



""" STEP 1: geocode and parse"""

def get_address(tweet):
    """
    Passes the tweet text to Google's Geocode API to get structured 
    address data in xml format. 
    """
    with open("credentials/google_credentials.json", "r") as c:
        api_key = json.load(c)
    
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/xml?address"
    if tweet['contain_address'] == True:
       query = tweet['clean_text']
       req_url = base_url + "=" + query + '&lang=en&key=' + api_key
       resp = requests.get(req_url)
    else:
       resp = None
    
    return resp


def parse_address(resp):
    """
    Parses the `pass_address` response output and constructs
    dictionary output to be returned.
    =====================
    resp (the response xml output of `get_address`)
    """
    # set up tree
    root = ET.fromstring(resp.content)
    
    # only parse if google API response is 'ok' and 
    # address type is in the `type_list`
    type_list = ['street_address',
                 'church',
                 'locality',
                 'clothing_store',
                 'subpremise',
                 'colloquial_area',
                 'premise',
                 'establishment',
                 'bar']
    
    if (root.find('status').text.lower() == "ok" and 
        root.find('./result/type').text in type_list):
        add_type = root.find('./result/type').text
        path = "./result/[type='{}']/".format(add_type)
        try:
            full = root.find(path + "formatted_address").text
            st_num = root.find(path + "address_component/[type='street_number']/long_name").text
            route = root.find(path + "address_component/[type='route']/long_name").text
            city = root.find(path + "address_component/[type='locality']/long_name").text
            county = root.find(path + "address_component/[type='administrative_area_level_2']/long_name").text
            state = root.find(path + "address_component/[type='administrative_area_level_1']/long_name").text
            state_abbv = root.find(path + "address_component/[type='administrative_area_level_1']/short_name").text
            zipcode = root.find(path + "address_component/[type='postal_code']/short_name").text
            lat = root.find(path + "geometry/location/lat").text
            lng = root.find(path + "geometry/location/lng").text
        except:
            full = st_num = route = city = county = state = state_abbv = zipcode = lat = lng = None
    else:
        full = st_num = route = city = county = state = state_abbv = zipcode = lat = lng = None
    # construct dictionary 
    address = {"full": full,
                "st_num": st_num, 
               "route": route,
                "city": city,
                "county": county,
                "state": state,
                "state_abbv": state_abbv,
                "zipcode": zipcode,
                "lat": lat,
                "lng": lng}
    return address



               
if __name__ == "__main__":
    
    os.chdir(os.path.abspath("/Users/asako/Google Drive/scrape_twitter"))
    currentdir = os.getcwd()
    
    # create a list of files in "data/scraped"
    scraped_files = []
    path = os.path.join(currentdir, args.scrapeddir)
    for file in sorted(os.listdir(path)):
        if file.endswith(".json"):
            scraped_files.append(file)
            
    # iterate over 'scraped_list' list to find address
    for file in scraped_files:
        find_address(file)
    
    # create a list of files in "data/cleaned"
    clean_files= []
    path = os.path.join(currentdir, args.cleaneddir)
    for file in sorted(os.listdir(path)):
        if file.endswith(".json"):
            clean_files.append(file)
            
    
    # iterate over `clean_files` list
    
    for file in clean_files:
        with open(os.path.join(args.cleaneddir, file), "r") as j:
            tweets = json.load(j)
        print(file)
        for tweet in tweets:
            if tweet.get('contain_address') == True:
                print(tweets.index(tweet))
                xml_resp = get_address(tweet) 
                if xml_resp is not None:
                    address_dict = parse_address(xml_resp)
                    tweet.update(address_dict)
                else:
                    pass
            else:
                pass
        time.sleep(2.5)
        filename = file.replace("cleaned", "parsed")
        with open(os.path.join(args.parseddir,filename), "w") as j:
            json.dump(tweets, j)
    print("Reached last file")
    sys.exit()
        
    
