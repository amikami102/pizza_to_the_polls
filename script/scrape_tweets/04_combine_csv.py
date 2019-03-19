#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import pandas as pd
"""
Combine csv files in 'data/csv' into one dataframe
"""
path = "data/csv"
name = "PizzaToThePolls"
pizzapoll_csv = os.path.join("data", "PizzaToThePolls.csv")


df_list = []
for item in os.listdir(path):
    if item.endswith(".csv") == True:
        file_path = os.path.join(path, item)
        df = pd.read_csv(file_path)
        df_list.append(df)
        print("added {}".format(item))
combined_df = pd.concat(df_list, axis = 0, ignore_index = True)
combined_df.drop(combined_df.columns[df.columns.str.contains('unnamed',case = False)],
                                      axis = 1)
combined_df.to_csv(os.path.join("data", "PizzaToThePolls.csv"),
                   index = False) # removes "Unnnamed" column


df = pd.read_csv("data/PizzaToThePolls.csv")
df.info()

