#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 11:25:01 2024
"""

import pandas as pd
import geopandas as gpd
import argparse

# initialize argument parser
ap = argparse.ArgumentParser()

# set up arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the geopackage containing toponym points with LAU and NUTS 3 codes.")

ap.add_argument("-o", "--output", required=True,
                help="Path to output Excel.")

# parse arguments
args = vars(ap.parse_args())

# read data to be sampled
print("[INFO] - Reading in geopackage....")
df = gpd.read_file(args['input'])

# reduce column clutter
df = df[['origin', 'gc_address', 'NUTS_ID_2013', 'NUTS_ID_2016','NUTS_ID_2021', 'count']]

# convert count to numeric
df['count'] = pd.to_numeric(df['count'], downcast='integer', errors='coerce')

# drop rows without any counts
df = df[df['count'] >=1]

# drop rows that are outside NUTS regions (e.g. in Russia, USA)
df = df.dropna(subset=['NUTS_ID_2013', 'NUTS_ID_2016','NUTS_ID_2021'], how='all')

# get a sample of 1000
sample = df.sample(n=1000, weights=df['count'])

# save to excel
print("[INFO] - Saving the weighted sample of 1000 points...")
sample.to_excel(args['output'])

print("[INFO] - ... done!")
