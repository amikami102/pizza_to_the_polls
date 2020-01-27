#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert dictionaries stored in data/raw_wiki/senate_election.json 
to dataframe and save to csv file. 
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

# add path to this subdirectory
sys.path.append(os.getcwd() + "/script/scrape_wiki")
import us_states_list as us 

# set up parser
parser = argparse.ArgumentParser(description='Scrape wikipedia')
parser.add_argument('-rawdir', type = str, 
                    help = 'Direcotry to store raw html and json containing urls.', 
                    default = "data/raw_wiki/house")
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

house_page = wikipedia.page("2018 United States House of Representatives elections")

## get a list of states that appear on `house_page`
races = [x for x in us.states if x in house_page.sections]


## create a list of states that are at-large districts
atlarge = ["Alaska", "Delaware", "Montana", "North Dakota",
           "South Dakota", "Vermont", "Wyoming"]

## create a dictionary of state and district that held special elections
## prior to November 6, 2018
special = {"Pennsylvania": "District_18",
           "Arizona": "District_8",
           "Texas": "District_27",
           "Ohio": "District_12"}


""" STEP 0: get href link to the HoR election page """

def get_state_link(state):
    """"
    Get href to the section of the 2018 HoR election in `state` 
    on the "2018 United States House of Rep. elections" Wikipedia page.
    Save the link to json file. 
    ----
    state (chr)
    """
    
    url = base_url + "wiki/2018_United_States_House_of_Representatives_elections"
    house = BeautifulSoup(requests.get(url).content, "lxml")
    
    if state in atlarge:
        title = "2018 United States House of Representatives election in {}".format(state)
    else:
        title = "2018 United States House of Representatives elections in {}".format(state)
    link = house.find(title = title)["href"]
    log.info("HREF to {}: {} \n".format(state, base_url + link))
    
    fname = args.state + "-wikilink" + ".json"
    
    # save to file
    with open(os.path.join(args.rawdir, fname), "w") as h:
        h.write(link)
    
    # return link
    return link
    


""" STEP 1: get html of the HoR election page """

def get_state_html(link):
    """
    Get the html of the Wiki page given by the `link` returned by 
    `get_state_link(state)`. Save the html to file.
    """
    if link.startswith("/"):
        link = link[1:]
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




""" STEP 2.1: parse the html for states with multiple districts"""

def parse_state_html(html):
    """
    Parse the html returned by get_state_html() to obtain the 
    race details for each district. Return dictionary output
    -------
    [                       "district", # district name
                            "candidate1", # candidate elected 
                           "candidate2", # second runner candidate
                           "party1",    # party of candidate1
                           "party2",     # party of candidate 2
                           "incumbent",  # incumbent party
                           "share1", # vote share for candidate1
                           "share2",  # vote share for candidate2
                           ]
    """
    # e.g. https://en.wikipedia.org/wiki/2018_United_States_House_of_Representatives_elections_in_Alabama

    soup = BeautifulSoup(html, "lxml")

    
    state_dict = {}
    # for each district, find the table with the title,
    # "<state>'s <district#> congressional district, 2018"
    districts = soup.find_all(["h2", "span"], {"class": "mw-headline", "id": re.compile("^District")})
    for d in districts:
        district = d.find_previous("h2").find("span")["id"]
        log.info("Parsing {}".format(district))
        general = d.find_next(["h3", "span"], {"id": re.compile("^General")}).find_next("caption")
        rows = general.find_all_next("tr", limit=3)
        row1 = [text for text in rows[1].stripped_strings]
        try:
            row2 = [text for text in rows[2].stripped_strings]
        except IndexError:
            log.exception("Check for candidate2 details")
            row2 = ["NA"]*3
            
        # check that this district did not have special election before
        # November 6, 2018
        if (state, district) in special.items():
            continue 
        else:
            state_dict.update({
                        district: {
                                "candidate1": row1[1],
                                "candidate2": row2[1],
                                "party1": row1[0],
                                "party2": row2[0],
                                "share1": row1[-1],
                                "share2": row2[-1]}
                        })
    
    # save to file
    fname = args.state +  ".json"
    with open(os.path.join(args.rawdir, fname), "w") as j:
        json.dump(state_dict, j)
        
        
    return state_dict


""" STEP 2.2: parse the html for states with only one district """


def parse_atlarge_html(html):
    """
    This function is for at-large district states, namely Alaska,
    Delaware, Montana, North Dakota, Vermont, Wyoming as of 2018.
    ------------------------------
    Parse the html returned by get_state_html() to obtain the 
    race details for the state. Return dictionary output
    -------------------------------
    [
                            "candidate1", # candidate elected 
                           "candidate2", # second runner candidate
                           "party1",    # party of candidate1
                           "party2",     # party of candidate 2
                           "incumbent",  # incumbent party
                           "share1", # vote share for candidate1
                           "share2",  # vote share for candidate2
                           ]
    """
    # e.g. https://en.wikipedia.org/wiki/2018_United_States_House_of_Representatives_election_in_Alaska
    
    
    soup = BeautifulSoup(html, "lxml")
    if args.state == "North_Dakota":
        box = soup.find("table", {"class": "infobox vevent"}).find_all("table", limit = 2)[-1]
    else:
        box = soup.find("table", {"class": "infobox vevent"})
    if "Nominee\n" in box.strings:
        candidates = box.find(string = "Nominee\n").find_parent("tr").find_all("td")
    if "Candidate\n" in box.strings:
        candidates = box.find(string = "Candidate\n").find_parent("tr").find_all("td")
    parties = box.find(string = "Party\n").find_parent("tr").find_all("td")
    voteshares = box.find(string = "Percentage\n").find_parent("tr").find_all("td")
    candidate1 = candidates[0].find(text = True)
    party1 = parties[0].find(text = True)
    share1 = voteshares[0].find(text = True)
    
    try:
        candidate2 = candidates[1].find(text=True)
        party2 = parties[1].find(text = True)
        share2 = voteshares[1].find(text = True)
    except IndexError:
        log.exception("Candidate2 missing")
        candidate2 = party2 = share2 = "NA"
    
    state_dict = { "at-large":{
                "candidate1": candidate1,
                  "candidate2": candidate2,
                  "party1": party1,
                  "party2": party2,
                  "share1": share1,
                  "share2": share2}
        }
    
    # save to file
    with open(os.path.join(args.rawdir, args.state + ".json"), "w") as j:
        json.dump(state_dict, j)
    
    
    return state_dict




""" STEP 2.3: Parse html for Florida """

def parse_florida_html(state = "Florida"):
    """
    The Florida race wikipage displays the results for 
    unopposed candidates differently from other state's Wikipages.
    ------------
    Parses the html to give the same output as parse_state_html()
    but is adjusted for general elections where candidates were unopposed.
    """
    
    link = get_state_link(state)
    html = get_state_html(link)
    
    soup = BeautifulSoup(html, "lxml")
    
    florida_dict = {} # store the dictionary generated for each district
    

    # grab the districts where candidate ran unopposed
    unopposed = []
    trows = soup.find("table", \
                        {"class": "wikitable plainrowheaders sortable"}).\
                        find_all("tr", \
                        style = re.compile("background:#FFB6B6|background:#B0CEFF"))
    for row in trows:
        if '0.00%' in row.stripped_strings:
            unopposed.append(re.sub(r"\s", "_", row.find("a").string))
            
            
    # now we start parsing 
    
    spans = soup.find_all("span", {"id": re.compile("^General")})
    for span in spans:
        district = span.find_previous("h2").find("span")["id"]
        log.info("Parsing {}".format(district))
        if district in unopposed: # unopposed district
            candidate1 = re.search(r"(?<=Incumbent\s)(?P<name>\w+\s\w+)(?=\swill)", 
                                   span.find_next("p").string).group("name")
            party1 = re.search(r"(?P<party>\w+)(?=\sprimary)", 
                               span.find_previous(title=candidate1).\
                               find_previous("h3").\
                               find("span", {"class":"mw-headline"}).string)\
                               .group("party")
            row1 = [party1, candidate1, "NA"]
            log.info("Candidate2 missing")
            row2 = ["NA"] * 3
        else: # non-unopposed district 
            rows = span.find_next("table").find_all("tr")
            row1 = [text for text in rows[1].stripped_strings]
            try:
                row2 = [text for text in rows[2].stripped_strings]
            except IndexError:
                log.exception("Candidate 2 missing")
                row2 = ["NA"] * 3
        florida_dict.update({
                        district: {
                                "candidate1": row1[1],
                                "candidate2": row2[1],
                                "party1": row1[0],
                                "party2": row2[0],
                                "share1": row1[-1],
                                "share2": row2[-1]}
                        })
    # save to file
    with open(os.path.join(args.rawdir, "Florida.json"), "w") as j:
        json.dump(florida_dict, j)

    return florida_dict


""" STEP 2.4: Parse html for California """

def parse_california_html(state = "California"):
    
    link = get_state_link(state)
    html = get_state_html(link)
    
    soup = BeautifulSoup(html, "lxml")
    
    california_dict = {} # store the dictionary generated for each district
    
    h3spans = soup.find_all(["h3", "span"], {"id": re.compile("^District")})
    for h3 in h3spans:
        district = h3["id"]
        log.info("Parsing {}".format(district))
        general = h3.find_next(["table", "tbody", "tr", "th"], colspan = "5", string = "General election\n")
        rows = general.find_parent("tr").find_all_next("tr", limit=2)
        row1 = [string for string in rows[0].stripped_strings]
        try:
            row2 = [string for string in rows[1].stripped_strings]
        except IndexError:
            row2 = ["NA"] * 3
        california_dict.update({
                    district : {
                            "candidate1": row1[1],
                            "candidate2": row2[1],
                            "party1": row1[0],
                            "party2": row2[0],
                            "share1": row1[-1],
                            "share2": row2[-1]
                            }
                })
        
    # save to file
    with open(os.path.join(args.rawdir, "California.json"), "w") as j:
        json.dump(california_dict, j)
        
    return california_dict

# run in command line:
# $ python script/scrape_wiki/scrape_wiki.py

if __name__ == "__main__":
    
    # Get current directory
    current_dir = os.getcwd()
    
    house_race = {}
    for state in races:
        args.state = re.sub("\s", "_", state)
        if state == "Florida":
            house_race.update({args.state : parse_florida_html(state)})
        if state == "California":
            house_race.update({args.state : parse_california_html(state)})
        else:
            wikilink = get_state_link(state)
            wikipage = get_state_html(wikilink)
            if state in atlarge:
                house_race.update({state : parse_atlarge_html(wikipage)})
            else:
                house_race.update({state : parse_state_html(wikipage)})

    
    # save `senate_race` dictionary to file 
    with open(os.path.join(args.rawdir, "house_elections_2018.json"), "w") as j:
        json.dump(house_race, j)
    
    sys.exit()
        



