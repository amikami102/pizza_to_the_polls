#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import json
import os
import sys
import base64
import requests
import logging
import config # config.py

# set up parser 
parser = argparse.ArgumentParser(description='Scrape twitter')
parser.add_argument('-credentials', type = str,
                    help = "Directory storing credential json files.",
                    default = "script/credentials")
parser.add_argument('-scrapeddir', type = str,
                    help = 'Direcotry to store scraped data files', 
                    default = 'data/scraped')
parser.add_argument('-rawdir', type = str,
                    help = 'Directory to store raw responses',
                    default = 'data/raw')
parser.add_argument('-v','--verbose', 
                    help = "Set log level to debug", action="store_true")
args = parser.parse_args()

# set up logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
if args.verbose:
    log.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler(sys.stderr)
loghandler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
log.addHandler(loghandler)

""" STEP 0: OAuth2 Authorization """

# Load my credentials from json file
with open(os.path.join(args.credentials,"twitter_credentials.json"), "r") as j:
    creds = json.load(j)

client_key = creds['api_key']
client_secret = creds['api_secret']

# Encode my keys in base64 per instructed on 
# https://developer.twitter.com/en/docs/basics/authentication/overview/application-only
key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
b64_encoded_key = base64.b64encode(key_secret)
b64_encoded_key = b64_encoded_key.decode('ascii')


# Build authorization request 
auth_url = 'https://api.twitter.com/oauth2/token'
auth_headers = {
    'Authorization': 'Basic {}'.format(b64_encoded_key),
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
auth_data = {'grant_type': 'client_credentials'}
auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

# Check status code is 200, meaning "okay"
if auth_resp.status_code != 200:
    log.error("Authorization status code: {}".format(auth_resp.status_code))
else:
    log.info("Authorization request successful")

# Store access token
access_token = auth_resp.json()['access_token']


""" STEP 1: Get counts """
base_url = 'https://api.twitter.com/1.1/tweets/search/'
search_headers = {'Authorization': 'Bearer {}'.format(access_token)}
count_params = {'query': '@PizzaToThePolls',
                'fromDate': '201811061100',
                'toDate': '201811062359',
                'bucket': 'hour'}
count_url = '{}fullarchive/research/counts.json'.format(base_url)
count_resp = requests.get(count_url, headers = search_headers, 
                          params = count_params)

# Check status code is 200
if count_resp.status_code != 200:
    log.error("Count request status code: {}".format(count_resp.status_code))
else:
    log.info("Count data request successful")

# Save to file
count_data = count_resp.json()
with open(os.path.join(args.datadir, "counts.json"), "w") as j:
    json.dump(count_data, j)



""" STEP 2: Scrape tweets per hour """ 


def request_search(fromDate, toDate, next_, pgcount):
    """
    This function collects tweets posted by @PizzaToThePolls on
    2018 midterm Election during the hour 'fromDate' to 'toDate'.
    Some hours are busier than others and will require multiple responses to 
    cover all the data pages.
    ======================
    fromDate = 'YYYYMMDDHHMM'
    toDate = 'YYYYMMDDHHMM'
    pgcount = (int indictating page count)
    next_ = (str token for the next page of search result)
    """
    request_out = [] # output list 
    
    # set the search parameters
    search_params = {'query': '@PizzaToThePolls',
                     'fromDate': fromDate, 'toDate': toDate,
                     'maxResults': 500, 
                     'next': next_}
    if next_ == 0:
        del search_params['next']
        
        
    # make search request
    search_url = '{}fullarchive/research.json'.format(base_url)
    search_resp = requests.get(search_url, headers = search_headers, 
                               params = search_params)
    
    
    # Check status code is 200
    if search_resp.status_code != 200:
        log.error("Request status code: {}".format(search_resp.status_code))
    else:
        log.info("Request successful")
        
    search_data = search_resp.json()
	
	# Save to file
    filename = fromDate + "-" + toDate + "-" + str(pgcount) 
    with open(os.path.join(args.rawdir, "search_resp" + filename + ".json"), "w") as j:
        json.dump(search_data, j)
    
    # Scrape the date created, text, and id of each tweet 
    # in the search response. Add the dictionary to output list.
    for res in search_data['results']:
        t = {'created_at': res['created_at'], 
             'text': res['text'], 
             'id': res['id']}
        request_out.append(t)
    
    # Save to file
    with open(os.path.join(args.datadir, "scraped" + filename +".json"), "w") as j:
        json.dump(request_out, j)
    
    # Get 'next' token for the next page if exists, else stop.
    if 'next' not in search_data:
        log.info("We've reached the last page")
        return(0)
    else:
        return(search_data['next'])
    




""" STEP 3: Build a loop to feed arguments """

if __name__ == "__main__":
    
    current_dir = os.getcwd()
    
    with open(os.path.join(args.datadir, "counts.json"), "r") as j:
       counts = json.load(j)['results']
    for count in counts:
       fromDate = count['timePeriod']
       toDate = str(int(fromDate) + 100)
       c = 0
       to_next = request_search(fromDate, toDate, pgcount = c, next_ = 0)
       while(to_next != 0):
           c += 1
           to_next = request_search(fromDate, toDate, pgcount = c, next_ = to_next)
    sys.exit()
           
           
    
    


