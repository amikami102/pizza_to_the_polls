#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The script scrapes 
"""
import sys
import argparse
import logging
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
import re
import os
import json


# set argument parser
parser = argparse.ArgumentParser(description='Get junior faculty for each school.')
parser.add_argument("-datadir", type = str,
                    help = "Directory to store output of this file.",
                    default = "data/cawp")
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





"""STEP 1"""

def get_htmlpage(url = "https://cawp.rutgers.edu/2018-women-candidates-us-congress-and-statewide-elected-executive"):
    """
        Get html page to scrape
    """
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    try:
        headers = {'User-Agent' : user_agent } 
        response = requests.get(url, headers = headers)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        log.warn(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        log.warn(f'Other error occurred: {err}')  # Python 3.6
    else:
        log.info('Success!')

    
    response.encoding = "utf-8"
    html = response.text
    
   
   # Save to file
    with open(os.path.join(args.datadir, 'women-candidate-2018.html'), "w") as h:
        h.write(html)
    return html


"""STEP 2"""
def parse_htmlpage(html):
    """ 
    Parse the html page returned by get_htmlpage().
    """
    
    soup = BeautifulSoup(html, "html.parser")
    tbody = soup.tbody
    
    # put all rows into a list
    list_ = []
    blocks = tbody.find_all("tr")
    for block in blocks[1:-1]:
        list_.append([string for string in block.stripped_strings])
    for item in list_:
        if item == []:
            list_.remove(item)
            
    return list_

""" STEP 3 """
def label_block(i, block):
    
    """
    Identify if `block` corresponds to a row or a header or a footer.
    If header, label 0,
    If footer, label as some arbitrary large number.
    If row is for non-congressional seat, label -1.
    """
    
    congress = re.compile("(U.S. Rep.)|(U.S. Sen.)|(Governor)")
    state = re.compile("[A-Z]{2}")
    
    m = congress.match(block[0])
    if m: # the block begins with "U.S. REp.", "U.S. Sen.", or "Governor"
        pass
    else:
        s = state.match(block[0])
        if s: # the block is a state
            i = 0
        else:
            match = [s for s in block if "↑↑" in s]
            if match != []: # block contains "↑↑"
                i = 10000000
            else:
                i = -1
                
    
    return i


if __name__ == "__main__":
    
    tr_blocks = parse_htmlpage(get_htmlpage())
    counter = []
    for i, block in enumerate(tr_blocks):
        counter.append(label_block(i, block))
    counter.append(max(counter)) # add "end" marker for last block
    
    OUT = {}
    list_ = []
    for i, count in enumerate(counter):
        #while i <= len(tr_blocks):
            if count == 0:
                state = tr_blocks[i][0]
            if count == -1:
                pass
            if count > 0 and count < max(counter):
                list_.append(tr_blocks[i])
                
            if count == max(counter):
                OUT.update({state: list_})
                list_ = []
            i += 1
    
    with open(os.path.join(args.datadir, "women-candidate-2018.json"), "w") as j:
        json.dump(OUT, j)
    sys.exit()
        
            
           
        
    

