#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 11:46:23 2023

# INFO
This script retrieves the LAU and NUTS 3 codes across the years for the geocoded point data.

The script assumes the LAU files are named "LAU_{}_3035.gpkg" in the directory. The placeholder {} corresponds to the year of the data
Similar logic is used with NUTS files "NUTS_3_01M_{}_3035.gpkg".

Run the script in the terminal by typing:
    python get_NUTS_LAU_codes_to_points.py -lp /path/to/lau/ -np /path/to/nuts/ -p /path/to/points.gpkg -o /path/to/output.gpkg

@author: tuomvais
"""
import pandas as pd
import geopandas as gpd
import argparse

# initialize argument parser
ap = argparse.ArgumentParser()

# set up arguments
ap.add_argument("-lp", "--laupath", required=True,
                help="Path to the directory containing the LAU layers (.gpkg) from 2014 to 2022.")

ap.add_argument("-np", "--nutspath", required=True,
                help="Path to the directory containing the NUTS 3 layers (.gpkg) from 2013 to 2021.")

ap.add_argument("-p", "--points", required=True,
                help="Path to geopackage containing the gecoded toponym points.")

ap.add_argument("-o", "--output", required=True,
                help="Path to output Geopackage.")

# parse arguments
args = vars(ap.parse_args())

# read point geometries with Oula's corrections
print('[INFO] - Reading data in...')
points = gpd.read_file(args['points'])

# reproject to CRS used by the EU
points = points.to_crs(epsg=3035)

# copy points for joining the codes
jpoints = points.copy()

# loop over years for LAU
for year in range(2014,2022):
    
    # get string of year
    yr = str(year)
    
    # define path
    laupath = args['laupath'] + "LAU_{}_3035.gpkg".format(yr)
    
    # read in correct LAU
    lau = gpd.read_file(laupath)
    
    # column name for LAU area codes per year
    laucol = 'GISCO_LAU_ID_{}'.format(yr)
    
    # generate code for annual LAU
    lau[laucol] = lau['GISCO_ID']
    
    # sanity check
    if lau.crs == points.crs:
        print('[INFO] - LAU: Coordinate systems match for year {}, proceeding...'.format(yr))
    else:
        print('[INFO] - LAU: CRS do not match, double-check inputs! Exiting...')
        exit()
        
    # join area codes to points for current year
    joined = points.sjoin_nearest(lau, how='left', max_distance=5000, distance_col='nn_join_dist')
    
    # drop places without succesfull join
    joined = joined.dropna(subset=['nn_join_dist'])
    
    # for duplicate joins with some fuzzyness on the distance keep the one with the lowest distance
    joined = joined.sort_values(by=['origin','nn_join_dist'], ascending=[True, True])
    joined = joined.drop_duplicates(subset='origin', keep='first')
    
    # set column list to keep
    keepcols = ['origin', laucol]
    
    # result dataframe to list
    jpoints = pd.merge(jpoints, joined[keepcols], on='origin', how='left')

# loop over years for NUTS 3
for year in [2013,2016,2021]:
    
    # get string of year
    yr = str(year)
    
    # define path
    nutspath = args['nutspath'] + "NUTS_3_01M_{}_3035.gpkg".format(yr)
    
    # read in correct LAU
    nuts = gpd.read_file(nutspath)
    
    # column name for LAU area codes per year
    nutscol = 'NUTS_ID_{}'.format(yr)
    
    # generate code for annual LAU
    nuts[nutscol] = nuts['NUTS_ID']
    
    # sanity check
    if nuts.crs == points.crs:
        print('[INFO] - NUTS: Coordinate systems match for year {}, proceeding...'.format(yr))
    else:
        print('[INFO] - NUTS: CRS do not match, double-check inputs! Exiting...')
        exit()
        
    # join area codes to points for current year
    joined = points.sjoin_nearest(nuts, how='left', max_distance=5000, distance_col='nn_join_dist')
    
    # drop places without succesfull join
    joined = joined.dropna(subset=['nn_join_dist'])
    
    # for duplicate joins with some fuzzyness on the distance keep the one with the lowest distance
    joined = joined.sort_values(by=['origin','nn_join_dist'], ascending=[True, True])
    joined = joined.drop_duplicates(subset='origin', keep='first')
    
    # set column list to keep
    keepcols = ['origin', nutscol]
    
    # result dataframe to list
    jpoints = pd.merge(jpoints, joined[keepcols], on='origin', how='left')

# save geopackage
print('[INFO] - Saving...')
jpoints.to_file(args['output'], driver='GPKG')
print('[INFO] - ... done!')
