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
from dotenv import load_dotenv
load_dotenv()
google_api_key = os.getenv('google_api_key')

# set up parser
parser = argparse.ArgumentParser(description='Clean and process tweets')
parser.add_argument('-script02dir', type = str,
                    help = 'Directory storing outputs from 02_clean_and_find_address.py',
                    default = "data/tweets/02_cleaned")
parser.add_argument('-script02dir', type = str,
                    help = 'Directory storing outputs from 02_clean_and_find_address.py',
                    default = "data/tweets/03_parsed")
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




""" STEP 1: Pass tweet text to API """

def get_address(tweet):
    """
    Pass the tweet text to Google's Geocode API to get structured 
    address data in xml format. 
    """
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/xml?address"
    if tweet['contain_address'] == True:
       query = tweet['clean_text']
       req_url = base_url + "=" + query + '&lang=en&key=' + google_api_key
       try:
           resp = requests.get(req_url)
           # If the response was successful, no Exception will be raised
           resp.raise_for_status()
       except HTTPError as http_err:
           log.info(f'HTTP error occurred: {http_err}')  
       except Exception as err:
           log.info(f'Other error occurred: {err}')  
       else:
           log.info('Success!')
    else:
       resp = None
       
    
    return resp

""" STEP 2: Parse API response """

def parse_address(resp):
    """
    Parses the `get_address` response output and constructs
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
        except UnboundLocalError:
            full = None
        try:
            st_num = root.find(path + "address_component/[type='street_number']/long_name").text
        except:
            st_num = None
        try:
            route = root.find(path + "address_component/[type='route']/long_name").text
        except:
            route = None
        try:
            city = root.find(path + "address_component/[type='locality']/long_name").text
        except:
            try:
                city = root.find(path + "address_component/[type='sublocality']/long_name").text
            except:
                city = None
        try:
            county = root.find(path + "address_component/[type='administrative_area_level_2']/long_name").text
        except:
            county = None
        try:
            state = root.find(path + "address_component/[type='administrative_area_level_1']/long_name").text
            state_abbv = root.find(path + "address_component/[type='administrative_area_level_1']/short_name").text
        except:
            state = state_abbv = None
        try:
            zipcode = root.find(path + "address_component/[type='postal_code']/short_name").text
        except:
            zipcode = None
        try:
            lat = root.find(path + "geometry/location/lat").text
            lng = root.find(path + "geometry/location/lng").text
        except:
            lat = lng = None
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

    os.chdir(os.path.abspath("/Users/asako/Google Drive/pizza_to_the_polls"))
    path = os.path.join(os.getcwd(), args.script02dir)

    # iterate over files in 'data/02_cleaned'
    for file in sorted(os.listdir(path)):
        with open(os.path.join(path, file), "r") as j:
            tweets = json.load(j)
        for tweet in tweets:
            xml_resp = get_address(tweet) 
            if xml_resp is not None:
                address_dict = parse_address(xml_resp)
                tweet.update(address_dict)
            else:
                pass
        time.sleep(2.5)
        parsed = file.replace("cleaned", "parsed")
        with open(os.path.join(args.script03dir, parsed), "w") as j:
            json.dump(tweets, j)
    log.message('Reached last file')
    sys.exit()