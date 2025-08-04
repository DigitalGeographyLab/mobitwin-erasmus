#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 11:29:07 2023

# INFO

This script takes the geocoding results with LAU and NUTS 3 codes attached
and joins them to the mobility data using a spatial layer from a specified
year. The output is the individual-level and the aggregate-level
mobility data.

Run the script in the terminal by typing:
    python connect_NUTS_LAU_OD_specific.py -i /path/to/file.pkl -p /path/to/points.gpkg -t NUTS -y 2021 -l /path/to/nuts.gpkg -o /path/to/directory/

"""

import pandas as pd
import geopandas as gpd
import argparse

# initialize argument parser
ap = argparse.ArgumentParser()

# set up arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the Erasmus+ mobility data pickle with fixed toponyms saved before geocoding.")

ap.add_argument("-p", "--points", required=True,
                help="Path to geopackage containing the gecoded toponym points with LAU and NUTS 3 codes.")

ap.add_argument("-t", "--type", required=True,
                help="Type of spatial layer: LAU or NUTS. Write in all caps.")

ap.add_argument("-y", "--year", required=True,
                help="Year to use for for the spatial layer. Please check LAU and NUTS year versions for reference.")

ap.add_argument("-l", "--layer", required=True,
                help="Path to spatial layer corresponding to the year to use in aggregation.")

ap.add_argument("-o", "--output", required=True,
                help="Path to directory where resulting CSVs and pickled dataframes are saved.")

# parse arguments
args = vars(ap.parse_args())

# reading individual data in
print('[INFO] - Reading individual data in...')
data = pd.read_pickle(args['input'])

# get year
data['year'] = data['Mobility Start Year/Month'].apply(
    lambda x: int(x.split('-')[0]))

# list of countries to accept
countrylist = ['Albania', 'Andorra', 'Austria', 'Belgium', 'Bosnia and Herzegovina',
               'Bulgaria', 'Croatia', 'Cyprus', 'Czechia', 'Czech Republic',
               'Denmark', 'Estonia', 'Faroe Islands', 'Finland', 'France',
               'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy',
               'Kosovo', 'Kosovo * UN resolution', 'Latvia', 'Liechtenstein',
               'Lithuania', 'Luxembourg', 'Malta', 'Monaco', 'Montenegro',
               'Netherlands', 'North Macedonia', 'Norway', 'Poland', 'Portugal',
               'Romania', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia',
               'Spain', 'Sweden', 'Switzerland', 'The Republic of North Macedonia',
               'Turkey', 'Türkiye', 'Ukraine', 'United Kingdom']

# filter countries
data = data[data['o_country'].isin(countrylist)]
data = data[data['d_country'].isin(countrylist)]

# read points
print('[INFO] - Reading geocoded points in...')
points = gpd.read_file(args['points'])

# define the spatial layer column to use
if args['type'] == 'NUTS':

    # construct columns to use
    spatcol = '{}_ID_{}'.format(args['type'], args['year'])
    idcol = 'NUTS_ID'

elif args['type'] == 'LAU':

    # construct columns to use
    spatcol = 'GISCO_{}_ID_{}'.format(args['type'], args['year'])
    idcol = 'GISCO_ID'

# get NUS 3 codes for 2021
nutpoints = points[~points[spatcol].isna()]

# read the singular spatial aggregation layer layer
nuts = gpd.read_file(args['layer'])

# get representative points
nuts['rep_x'] = nuts['geometry'].representative_point().x
nuts['rep_y'] = nuts['geometry'].representative_point().y

# get geometric point
nuts['rep_geom'] = gpd.points_from_xy(x=nuts['rep_x'], y=nuts['rep_y'])

# generate a dictionary of locations and point coordinates
nuts_dict = pd.Series(nuts['rep_geom'].values, nuts[idcol].values).to_dict()
nuts_dict2 = pd.Series(nutpoints[spatcol].values,
                       nutpoints['origin'].values).to_dict()

# get indicator value for iterations
n_iter = 1
print('[INFO] - Assigning spatial codes to place names...')

# looping over erasmus data
for i, row in data.iterrows():

    # get origin and destination
    orig = row['origin']
    dest = row['destination']

    # try to save origins
    try:
        # save origins
        data.at[i, 'orig_code'] = nuts_dict2[orig]
    except:
        # flood the zone with none
        data.at[i, 'orig_code'] = None

    # try to save destinations
    try:
        # save destinations
        data.at[i, 'dest_code'] = nuts_dict2[dest]
    except:
        # flood the zone with none
        data.at[i, 'dest_code'] = None

    # update n_iter
    n_iter += 1

    # every 100 000 iterations print message and reset n_iter
    if n_iter == 100000:

        # current row
        currow = i + 1

        # print message
        print('[INFO] - Assigning NUTS 3 codes to place names. Progress {}/{}'.format(str(currow), str(len(data))))

        # update n_iter
        n_iter = 1

# get original data size
osize = len(data)

# drop mobilities that are not between two NUTS regions (e.g. in Asia, Africa, Americas etc.)
print('[INFO] - Finalizing individual-level ERASMUS mobility data...')
data = data.dropna(subset=['orig_code', 'dest_code']).reset_index(drop=True)

# print info on retained data
share = round((len(data)/osize) * 100, 2)
print('[INFO] - {} % of all mobilities can be mapped'.format(share))

# generate OD pair ID
data['OD_ID'] = data['orig_code'] + '_' + data['dest_code']

print('[INFO] - Saving full individual-level ERASMUS+ data...')
data.to_csv(args['output'] +
            'Erasmus_2014-2023_individual_{}_{}.csv'.format(args['type'],
                                                            args['year']),
            sep=';', encoding='utf-8')

# get unique od pairs
print('[INFO] - Processing aggregate data...')
odpairs = data[['OD_ID','orig_code','dest_code']].drop_duplicates(subset=['OD_ID']).reset_index(drop=True)

# aggregate flows by OD ID and year
grouped = data.groupby(['OD_ID', 'year'])['Actual Participants'].sum().rename('count').reset_index()

# join with geometry data
studagg = pd.merge(grouped, odpairs, on=['OD_ID'])

# for annual grouped data
studagg = studagg.rename(columns={'orig_code': 'ORIGIN',
                                  'dest_code': 'DESTINATION',
                                  'count': 'COUNT',
                                  'year': 'YEAR'})

# save aggregate mobilities
print('[INFO] - Saving aggregate data...')
studagg.to_csv(args['output'] +
                'Erasmus_2014-2023_aggregate_{}_{}.csv'.format(
                    args['type'],
                    args['year']), sep=';', encoding='utf-8')
