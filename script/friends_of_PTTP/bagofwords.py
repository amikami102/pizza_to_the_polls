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
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text 
import pandas as pd


# set argument parser
parser = argparse.ArgumentParser(description='Feature extraction.')
parser.add_argument("-outdir", type = str,
                    help = "Directory to store output of this file.",
                    default = "data/friends")
parser.add_argument("-csvdir", type = str,
                    help = "Directory to store output of this file.",
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


""" STEP 1 """
def scrape_userobj(user_obj):
    """
    Scrapes relevant information from user_obj,
    ----
    user_obj (dict, user obj dictionary)
    """
    
    try:
        id_ = user_obj['id_str']
    except:
        id_ = None
    try:
        name_ = user_obj['name']
    except:
        name_ = None
#    try:
#        screenname_ = user_obj['screenname']
#    except:
#        screenname_ = None
    try:
        location_ = user_obj['location']
    except:
        location_ = None
    try:
        description_ = user_obj['description']
    except:
        description_ = None
    try:
        verified_ = user_obj['verified']
        created_at = user_obj['created_at']
    except:
        verified_ = created_at = None
    try:
        url_ = user_obj['url']
    except:
        url_ = None
    try:
        followers = user_obj['followers_count']
    except:
        followers = None
    
    dict_ =  { "id": id_,
             "name": name_,
#             "screenname": screenname_,
             "location": location_,
             "description": description_,
             "verified": verified_,
             "created_at": created_at,
             "url": url_, 
             "n_followers": followers}
    
    log.info(dict_['name'])
    return dict_
        

""" STEP 2 """
def bag_of_words(corpus):
    """
    Perform bag-of-words analysis: 
        1. get top 50 terms in the corpus;
        2. get keyword frequencies.
    ----
    corpus (list of strings)
    """
    
    # Fit CountVectorizer
    stop_words = text.ENGLISH_STOP_WORDS.union(
            ('twitter', 'email', 'https', 'com', 'politics', 'gmail', 'account',
            'tweets', 'views', 'american', 'state', 'opinions'))
    vectorizer = CountVectorizer(stop_words = stop_words, 
                                  analyzer = "word")
    X = vectorizer.fit_transform(corpus)
    features = vectorizer.get_feature_names()
    log.info("Output of bag of words: {} \n {}".format(type(X), X.shape))
    
    # get top 50 terms
    Xcolsum = np.array(X.sum(axis = 0))[0] # sum along axis and convert to list
    asc_ordered_Xindex = Xcolsum.argsort()
    ordered_Xindex = asc_ordered_Xindex[::-1]
    with open(os.path.join(args.outdir, "top_50terms.txt"), "w") as t:
        for i in ordered_Xindex[:50]: # save to file
            log.info("Top 50 terms, # {}: {}".format(Xcolsum[i], features[i]))
            t.write("{}, {}".format(Xcolsum[i], features[i]) + os.linesep)
        t.close()
    
    # count keyword frequencies
    keywords = ["house", "senator", "rep.", "sen", "governor", "candidate",
                "Democratic","Republican", "campaign", 
                "(R)", "(D)"]
    keyfeatures = [i for i in keywords if i in features]
    keywordcount = dict(zip(keyfeatures, [features.index(w) for w in keyfeatures]))
    with open(os.path.join(args.outdir, "count_keywords.txt"), "w") as t:
        for k, v in keywordcount.items():
            t.write("# of accounts mentioning '{}': {}".format(k, Xcolsum[v]) +
                    os.linesep)
            log.info("{}: {}\n".format(k, Xcolsum[v]))
    t.close()
    

    # save result to csv file
    df = pd.DataFrame(X.todense(), columns = features)
    df.to_csv(os.path.join(args.csvdir, "friends_bagofwords.csv"))
    

if __name__ == "__main__":
    
    # Build corpus and create pandas dataframe from scrape_userobj
    corpus = []
    df = pd.DataFrame()
    for i in range(4):
        scraped = {}
        filename = os.path.join(args.outdir, "friends_lookup_" + str(i) + ".json")
        with open(filename, "r") as j:
            users = json.load(j)
        for user in users:
            dict_ = scrape_userobj(user)
            row = pd.DataFrame(dict_, index = [0])
            df = pd.concat([df, row], axis = 0, ignore_index = True)
            scraped.update({dict_['id']: dict_.pop('id')})
            corpus.append(dict_['description'])
        filename = filename.replace("lookup", "scraped")
        with open(filename, "w") as j:
            json.dump(scraped, j)
    
    log.info(df.shape)
    df.to_csv(os.path.join(args.csvdir, "friends_of_PTTP.csv"))
    
    # Conduct bag of words on corpus
    bag_of_words(corpus)
    
    
    sys.exit()