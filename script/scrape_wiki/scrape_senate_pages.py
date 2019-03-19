# -*- coding: utf-8 -*-
"""
Scrape from Wikipedia pages of 2018 senate races. 
"""

from mediawiki import MediaWiki
import requests
from bs4 import BeautifulSoup
from datetime import datetime 
import os
import argparse
import logging
import sys
import json
import re


# set up parser
parser = argparse.ArgumentParser(description='Scrape wikipedia')
parser.add_argument('-rawdir', type = str, 
                    help = 'Direcotry to store row html files', 
                    default = "data/raw_wiki/senate")
parser.add_argument('-state', type = str, 
                    help = 'State for which the election data is required.')
parser.add_argument('-v','--verbose', 
                    help = "Set log level to debug", 
                    action="store_true")
args = parser.parse_args()


# set up log
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
if args.verbose:
    log.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler(sys.stderr)
loghandler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
log.addHandler(loghandler)


# set global environments
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
wikipedia = MediaWiki(user_agent = user_agent)
base_url = "https://en.wikipedia.org/"
states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
              "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
              "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
              "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
              "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
              "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
              "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
              "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
senate_page = wikipedia.page("2018 United States Senate elections")
## get a list of Class 1 US states that had senate race in 2018
class1 = [x for x in states if x in senate_page.sections]



""" STEP 0: get href link to the senate election page """

def get_state_link(state):
    """"
    Get url to the 2018 senate election in `state` and save to json file
    ----
    state (chr)
    """
    
    url = base_url + "wiki/2018_United_States_Senate_elections"
    senate = BeautifulSoup(requests.get(url).content, "lxml")
    
    title = "2018 United States Senate election in {}".format(state)
    link = senate.find(title = title).get("href")
    log.info("HREF to {}: {} \n".format(state, base_url + link))
    
    fname = args.state + "-wikilink" + ".json"
    
    # save to file
    with open(os.path.join(args.rawdir, fname), "w") as h:
        h.write(link)
    
    # return link
    return link
    



""" STEP 1: get html of the senate election page """

def get_state_html(link):
    """
    Get the html of the wikipage given by the `link` returned by 
    `get_state_link(state)`. Save the html to rawdir and return it.
    """
    
    url = base_url + link
    accessed = datetime.strftime(datetime.now(), "%Y-%m-%d-%H%M")
    headers = { 'User-Agent' : user_agent, 
               'Date accessed':  accessed}
    response = requests.get(url, headers = headers)
    html = response.content
    
    
    # save to file
    fname = args.state + "-wikipage" + ".html"
    with open(os.path.join(args.rawdir, fname), "w") as h:
        h.write(response.text)
        
    # return html
    return html


    

""" STEP 2: parse the html """

def parse_state_html(html):
    """
    Parse the html returned by `get_state_html(link)`
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
    eg: https://en.wikipedia.org/wiki/United_States_Senate_election_in_Arizona,_2018
    """
    soup = BeautifulSoup(html, "lxml")
    box = soup.find("table", {"class": "infobox vevent"})
    if "Nominee\n" in box.strings:
        candidates = box.find(string="Nominee\n").find_parent("tr").find_all("td")
    else:
        candidates = box.find(string="Candidate\n").find_parent("tr").find_all("td")
    candidate1 = candidates[0].find(text=True)
    candidate2 = candidates[1].find(text=True)
    
    log.info("candidates: {}, {}".format(candidate1, candidate2))
        
    
    parties = box.find(string="Party\n").find_parent("tr").find_all("a")
    party1 = parties[0].find(text=True)
    party2 = parties[1].find(text=True)
    
    log.info("parties: {}, {}".format(party1, party2))
    
    voteshares = box.find(string="Percentage\n").find_parent("tr").find_all("td")
    share1 = voteshares[0].find("b").string
    share2 = voteshares[1].string
    
    log.info("vote shares: {}, {}".format(share1, share2))
    
    incumbent = box.find(string=" before election").find_parent("td").find_all("a")[2].string
    
    log.info("incumbent party: {}".format(incumbent))
    
    state_dict = { "candidate1": candidate1,
                      "candidate2": candidate2,
                      "party1": party1,
                      "party2": party2,
                      "incumbent": incumbent,
                      "percentage1": share1,
                      "percentage2": share2
            }
    
    # save to file
    with open(os.path.join(args.rawdir, args.state + ".json"), "w") as j:
        json.dump(state_dict, j)
    
    return state_dict



# run in command line
# $ python script/scrape_wiki/scrape_wiki.py

if __name__ == "__main__":
    
    # Get current directory
    current_dir = os.getcwd()
    
    senate_race = {}
    for state in class1:
        args.state = re.sub("\s", "_", state)
        wikilink = get_state_link(state)
        wikipage = get_state_html(wikilink)
        senate_race.update({state: parse_state_html(wikipage)})
    
    # save `senate_race` dictionary to file 
    with open(os.path.join(args.rawdir, "senate_elections_2018.json"), "w") as j:
        json.dump(senate_race, j)
    
    sys.exit()
        
        

        
        
    
        
    
    
        
