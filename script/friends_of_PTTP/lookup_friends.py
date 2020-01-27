#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""
import sys
import argparse
import logging

# set argument parser
parser = argparse.ArgumentParser(description='Get junior faculty for each school.')
parser.add_argument("-outdir", type = str,
                    help = "Directory to store output of this file.",
                    default = "data")
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


