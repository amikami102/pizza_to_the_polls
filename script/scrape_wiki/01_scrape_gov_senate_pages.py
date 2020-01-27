#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""
from mediawiki import MediaWiki
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import os
import argparse
import logging
import sys
import re
import json
sys.path.append(os.getcwd() + "/script/scrape_wiki")
import us_states_list as us 


# set argument parser
parser = argparse.ArgumentParser(description='Scrape wikipedia pages.')
parser.add_argument("-datadir", type = str,
                    help = "Directory to store output of this file.",
                    default = "data/raw_wiki")
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

# set global environments
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
wikipedia = MediaWiki(user_agent = user_agent)
base_url = "https://en.wikipedia.org"






""" STEP 0: get list of states that had federal election in 2018"""
def get_states(office):
    """
    Go to the 2018 election page for the specified office and
    get a list of states that held elections for that office in 2018. 
    ---
    office (chr, )
    """
    if office == "governor":
        electionpage = wikipedia.page("2018 United States gubernatorial elections")
    if office == "senate":
        electionpage = wikipedia.page("2018 United States Senate elections")
    
    return [x for x in us.states if x in electionpage.sections]


""" STEP 1: get href link to each state's gubernatorial election page """

def get_state_link(state, office):
    """"
    Get url to the 2018 senate election in `state` and save to json file.
    ----
    state (chr, full name)
    office (chr)
    """
    def get_url(office = office):
        if office == "senate":
            return base_url + "/wiki/2018_United_States_Senate_elections" 
        if office == "governor":
            return base_url + "/wiki/2018_United_States_gubernatorial_elections"
    url = get_url()
    
    try:
        response = requests.get(url)
        
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
        page = BeautifulSoup(response.content, "lxml")
    
    def create_heading(state = state, office = office):
        if office == "senate":
            return "2018 United States Senate election in {}".format(state)
        if office == "governor":
            return "{} gubernatorial election, 2018".format(state)
    heading = create_heading()
    
    
    def get_href(office = office, heading = heading):
        if office == "senate":
            suffix = page.find(title = heading)["href"]
            return base_url + suffix
        if office == "governor":
            title = page.find(title = heading).get("title").replace(" ", "_")
            prefix = "/w/index.php?title="
            suffix = "&redirect=yes"
            return base_url + prefix + title + suffix
    
    state_href = get_href()
    
    fname = state + "-wikilink" + ".json"
    
    # save to file
    with open(os.path.join(args.datadir, office, fname), "w") as h:
        h.write(state_href)
    
    # return link
    return state_href
    



""" STEP 2: get html of the state election page """

def get_state_html(link):
    """
    Get the html of the wikipage given by get_state_link(). 
    Save html to file.
    """
    
    
    try:
        response = requests.get(link)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
        response.encoding = "utf-8"
        html = response.text
    
    # save html to file
    fname = state + "-wikipage" + ".html"
    with open(os.path.join(args.datadir, office, fname), "w") as h:
        h.write(response.text)
        
    # return html
    return html


    

""" STEP 3: parse the html """

def parse_state_html(html):
    """
    Parse the html returned by get_state_html()
    and return a dictionary, `state_dict` with the following keys.
    --------------------------------------
                            ["candidate1", # candidate elected 
                           "candidate2", # second runner candidate
                           "party1",    # party of candidate1
                           "party2",     # party of candidate 2
                           "incumbent",  # incumbent party
                           "share1", # vote share for candidate1
                           "share2",  # vote share for candidate2
                           ]
    ------------
    eg: https://en.wikipedia.org/w/index.php?title=2018_Michigan_gubernatorial_election&redirect=yes
    """
    soup = BeautifulSoup(html, "html.parser")
    box = soup.find("table", {"class": "infobox vevent"})
    
    # candidate names
    if "Nominee\n" in box.strings:
        candidates = box.find(string="Nominee\n").find_parent("tr").find_all("td")
    else:
        candidates = box.find(string="Candidate\n").find_parent("tr").find_all("td")
    candidate1 = candidates[0].find(text=True)
    candidate2 = candidates[1].find(text=True)
    
    log.info("candidates: {}, {}".format(candidate1, candidate2))
        
    
    # parties
    parties = box.find(string="Party\n").find_parent("tr").find_all("a")
    party1 = parties[0].find(text=True)
    party2 = parties[1].find(text=True)
    
    log.info("parties: {}, {}".format(party1, party2))
    
    # vote shares
    voteshares = box.find(string="Percentage\n").find_parent("tr").find_all("td")
    share1 = voteshares[0].find("b").string
    share2 = voteshares[1].string
    
    log.info("vote shares: {}, {}".format(share1, share2))
    
    # incumbent party
    
    def before_election(s):
        pattern = re.compile("before election")
        return pattern.search(s) != None 
    incumbent = box.find(string = before_election).find_parent("td").find_all("a")[-1].string
    
    log.info("incumbent party: {}".format(incumbent))
    
    
    dict_ = { "candidate1": candidate1,
                      "candidate2": candidate2,
                      "party1": party1,
                      "party2": party2,
                      "percentage1": share1,
                      "percentage2": share2,
                      "incumbent": incumbent
            }
    
    # save to file
    with open(os.path.join(args.datadir, office, state + ".json"), "w") as j:
        json.dump(dict_, j)
    
    return dict_



# run in command line
# $ python script/scrape_wiki/scrape_wiki.py

if __name__ == "__main__":
    
    # Get current directory
    current_dir = os.getcwd()
    
    
    for office in ['governor', 'senate']:
        races = get_states(office)
        OUT = {}
        for state in races:
            log.info(state)
            wikilink = get_state_link(state, office)
            wikipage = get_state_html(wikilink)
            OUT.update({state: parse_state_html(wikipage)})
        # save output to file 
        file = office + "_elections_2018.json"
        with open(os.path.join(args.datadir, office, file), "w") as j:
            json.dump(OUT, j)
    
    sys.exit()
        
        

        
        
    
        
    
    
        

