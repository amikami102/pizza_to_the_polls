#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 20:28:41 2019

@author: asako
"""

import json

# Twitter API credentials
credentials = {}  
credentials['CONSUMER_KEY'] = "reufxiQ06iskjez8a1WDKQFka" 
credentials['CONSUMER_SECRET'] = "jYyQvT2sfIgTYgRIkJCHLGgpwnXufWudkFJiajssQMdyrK1zWZ"
credentials['ACCESS_TOKEN'] = "967430942821318657-CAILxegcEERRp2sLxh8qYqR13RWc9us"
credentials['ACCESS_SECRET'] = "9jDN3d4vXkEyOOPFW2cOZkVfpl5Um7lJjN51K3oWt9jbJ"

# Save the credentials object to file
with open("twitter_credentials.json", "w") as file:  
    json.dump(credentials, file)

# Google Geocoding API credentials 
google_api = "AIzaSyAyPt0j1C6iqYgoQnWCIqhOOPuaV6sKnA4"

with open("google_credentials.json", "w") as file:
    json.dump(google_api, file)