#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""
import os
import sys
import argparse
import logging
import json
import base64
import requests
from dotenv import load_dotenv
load_dotenv()
from requests.exceptions import HTTPError


# set argument parser
parser = argparse.ArgumentParser(description='Get junior faculty for each school.')
parser.add_argument("-outdir", type = str,
                    help = "Directory to store output of this file.",
                    default = "data/friends")
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

""" STEP 0: OAuth2 Authorization """

# Load my credentials from json file
client_key = os.getenv('twitter_api_key')
client_secret = os.getenv('twitter_api_secret')

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

""" STEP 1 """
def build_APIrequest(count = 0, cursor = -1):
    """
    Builds API request url and retrieves response json, which is saved to file.
    ----
    count (int, current result page number)
    cursor (int)
    """
    base_url = "https://api.twitter.com/1.1/friends/ids.json"
    search_headers = {'Authorization': 'Bearer {}'.format(access_token)}
    params = {"screen_name": "PizzaToThePolls",
              "count": 5000, 
              "cursor": cursor}
    try:
        response = requests.get(base_url, params = params, headers = search_headers)
        response.raise_for_status()
    except HTTPError as http_err:
        log.error(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        log.error(f'Other error occurred: {err}')  # Python 3.6
    else:
        log.info('Success!')
    
    
    # Save to file
    friends = response.json()
    with open(os.path.join(args.outdir, "friends" + str(count) + ".json"), "w") as j:
        json.dump(friends, j)
    
    # If next cursor exists, return next cursor
    if friends['next_cursor'] != 0:
        log.info("There's next page!")
        next_ = friends['next_cursor']
        return next_
    else:
        log.info("Reached last page!")
        return 0 

""" STEP 2"""
def lookup_friend(friends_, count):
    """
    Look ups the friend with user id given by `friend_id `and 
    gretrieves the user object, which is saved as json file.
    ------
    friend_id (int, user id of the friend to look up)
    """
    
    
    # convert friends_ to a comma-separated character string 
    friends = ','.join([str(f) for f in friends_])
    
    
    base_url = "https://api.twitter.com/1.1/users/lookup.json"
    search_headers = {'Authorization': 'Bearer {}'.format(access_token)}
    params = {"user_id": friends}
    
    try:
        response = requests.get(base_url, params = params, headers = search_headers)
        response.raise_for_status()
    except HTTPError as http_err:
        log.error(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        log.error(f'Other error occurred: {err}')  # Python 3.6
    else:
        log.info('Success!')
    
    # Save user object to file
    users_ = response.json()
    filename = os.path.join(args.outdir, "friends_lookup_" + str(count) + ".json")
    with open(filename, "w") as j:
        json.dump(users_, j)
    log.info("Saved response to {}".format(filename))
    
        
        

    
        
if __name__ == "__main__":
    
    c = 0
    next_ = build_APIrequest(count = c)
    while next_ != 0:
        c += 1
        next_ = build_APIrequest(count = c, cursor = next_)
    
    def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]
                
    with open(os.path.join(args.outdir, "friends0.json"), "r") as j:
        friends_list = list(chunks(json.load(j)["ids"], 100))
    for i, f in enumerate(friends_list):
        lookup_friend(f, i)
                
    sys.exit()