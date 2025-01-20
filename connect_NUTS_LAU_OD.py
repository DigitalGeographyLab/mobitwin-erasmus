#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 11:29:07 2023

# INFO

This script takes the geocoding results with LAU and NUTS 3 codes attached
and joins them to the mobility data. The output is the individual-level and
the aggregate-level mobility data.

Run the script in the terminal by typing:
    python connect_NUTS_LAU_OD.py -i /path/to/file.pkl -p /path/to/points.gpkg -o /path/to/directory/

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

ap.add_argument("-o", "--output", required=True,
                help="Path to directory where resulting CSVs and pickled dataframes are saved.")

# parse arguments
args = vars(ap.parse_args())

# reading individual data in
print('[INFO] - Reading individual data with fixed toponyms in...')
data = pd.read_pickle(args['input'])

# get year
data['year'] = data['Mobility Start Year/Month'].apply(lambda x: int(x.split('-')[0]))

# list of countries to accept
countrylist = ['France', 'Spain', 'Germany', 'Italy', 'Netherlands', 'United Kingdom',
               'Turkey', 'Poland', 'Belgium', 'Portugal', 'Czech Republic', 'Austria',
               'Romania', 'Finland', 'Greece', 'Sweden', 'Denmark', 'Hungary',
               'Ireland', 'Lithuania', 'Slovakia', 'Norway', 'Slovenia', 'Bulgaria',
               'Croatia', 'Latvia', 'Türkiye', 'Ukraine', 'Estonia', 'Cyprus',
               'Luxembourg', 'Serbia', 'Albania', 'Iceland', 'The Republic of North Macedonia',
               'Malta', 'Kosovo * UN resolution', 'Montenegro', 'Bosnia and Herzegovina',
               'Liechtenstein', 'North Macedonia', 'Kosovo', 'Switzerland', 'Monaco',
               'Kosovo', 'Andorra', 'Faroe Islands', 'Turkey']

# filter countries
data = data[data['o_country'].isin(countrylist)]
data = data[data['d_country'].isin(countrylist)]

# read points
print('[INFO] - Reading geocoded points with LAU and NUTS 3 codes in...')
points = gpd.read_file(args['points'])

# list for combining data
comblist = []

# loop over years
for year in range(2014, 2023):
    
    # check if more recent data
    if year >= 2020:
        
        # set LAU 2021 as the one to use
        lau_col = 'GISCO_LAU_ID_2020'
        
    # otherwise do this for LAU codes
    else:
        
        # use the current year LAU codes
        lau_col = 'GISCO_LAU_ID_{}'.format(str(year))
        
    # check if need to use 2013 NUTS 3
    if year < 2016:
        
        # set NUTS code appropriately
        nuts_col = 'NUTS_ID_2013'
        
    # check if need to use 2016 NUTS 3
    elif (year >= 2016) & (year <2021):
        
        # set NUTS code appropriately
        nuts_col = 'NUTS_ID_2016'
        
    # check if need to use 2021 NUTS 3
    elif year >= 2021:
        
        # set NUTS code appropriately
        nuts_col = 'NUTS_ID_2021'        
    
    # get subset of original data
    subset = data[data['year'] == year].reset_index(drop=True)
    
    # get original size of subset
    osize = len(subset)
    
    # get subsets of points for LAU and NUTS
    laupoints = points[~points[lau_col].isna()]
    nutpoints = points[~points[nuts_col].isna()]
    
    # generate dictionaries for LAU and NUTS
    lau_dict = pd.Series(laupoints[lau_col].values, laupoints['origin'].values).to_dict()
    nuts_dict = pd.Series(nutpoints[nuts_col].values, nutpoints['origin'].values).to_dict()
    
    # set iterator for current subset
    n_iter = 1
    
    # looping over erasmus data
    for i, row in subset.iterrows():
        
        # get origin and destination
        orig = row['origin']
        dest = row['destination']
        
        # try to save origin LAUs
        try:
            # save origins
            subset.at[i, 'orig_LAU'] = lau_dict[orig]
        except:
            # flood the zone with none
            subset.at[i, 'orig_LAU'] = None
        
        # try to save destination LAUs
        try:
            # save destinations
            subset.at[i, 'dest_LAU'] = lau_dict[dest]
        except:
            # flood the zone with none
            subset.at[i, 'dest_LAU'] = None
        
        # try to save origin NUTS
        try:
            # save origins
            subset.at[i, 'orig_NUTS'] = nuts_dict[orig]
        except:
            # flood the zone with none
            subset.at[i, 'orig_NUTS'] = None
        
        # try to save destination NUTS
        try:
            # save destinations
            subset.at[i, 'dest_NUTS'] = nuts_dict[dest]
        except:
            # flood the zone with none
            subset.at[i, 'dest_NUTS'] = None
        
        # update n_iter
        n_iter += 1
        
        # every 100 000 iterations print message and reset n_iter
        if n_iter == 100000:
            
            # current row
            currow = i + 1
            
            # print message
            print('[INFO] - Progress {}/{}'.format(str(currow), str(len(subset))))
            
            # update n_iter
            n_iter = 1
    
    # drop mobilities that are not between two NUTS regions (e.g. in Asia, Africa, Americas etc.)
    print('[INFO] - Finalizing individual-level ERASMUS mobility subset...')
    subset = subset.dropna(subset=['orig_NUTS','dest_NUTS']).reset_index(drop=True)

    # print info on retained subset
    share = round((len(subset)/osize) * 100, 2)
    print('[INFO] - {} % of original mobilities in {} can be mapped on NUTS/LAU level'.format(share, str(year)))

    # generate OD pair ID
    subset['OD_ID_LAU'] = subset['orig_LAU'] + '_' + subset['dest_LAU']
    subset['OD_ID_NUTS'] = subset['orig_NUTS'] + '_' + subset['dest_NUTS']
    
    # save the current year's data
    comblist.append(subset)
    
# concatenate combined list
combined = pd.concat(comblist, ignore_index=True).sort_values(by=['year']).reset_index(drop=True)

# get original data size
osize = len(data)

# print info on retained data
share = round((len(combined)/osize) * 100, 2)
print('[INFO] - {} % of all mobilities could be mapped'.format(share))

print('[INFO] - Saving full individual-level ERASMUS+ data...')
combined.to_csv(args['output'] + 'Erasmus_2014-2022_individual.csv', index=False)

# get unique od pairs
print('[INFO] - Processing aggregate data on LAU and NUTS 3 levels...')
odpairs_lau = combined[['OD_ID_LAU','orig_LAU','dest_LAU']].drop_duplicates(subset=['OD_ID_LAU']).reset_index(drop=True)
odpairs_nuts = combined[['OD_ID_NUTS','orig_NUTS','dest_NUTS']].drop_duplicates(subset=['OD_ID_NUTS']).reset_index(drop=True)

# aggregate flows by OD ID and year
lau_g = combined.groupby(['OD_ID_LAU', 'year'])['Actual Participants'].sum().rename('count').reset_index()
nuts_g = combined.groupby(['OD_ID_NUTS', 'year'])['Actual Participants'].sum().rename('count').reset_index()

# join with geometry data
lauagg = pd.merge(lau_g, odpairs_lau, on=['OD_ID_LAU'])
nutsagg = pd.merge(nuts_g, odpairs_nuts, on=['OD_ID_NUTS'])

# rename columns
lauagg = lauagg.rename(columns={'OD_ID_LAU':'OD_ID',
                                'orig_LAU':'ORIGIN',
                                'dest_LAU':'DESTINATION',
                                'count':'COUNT',
                                'year':'YEAR'})
nutsagg = nutsagg.rename(columns={'OD_ID_NUTS':'OD_ID',
                                  'orig_NUTS':'ORIGIN',
                                  'dest_NUTS':'DESTINATION',
                                  'count':'COUNT',
                                  'year':'YEAR'})

# column order
colorder = ['OD_ID','ORIGIN','DESTINATION','YEAR','COUNT']

# order columns
lauagg = lauagg[colorder]
nutsagg = nutsagg[colorder]

# save aggregate mobilities
print('[INFO] - Saving aggregate data...')
lauagg.to_csv(args['output'] + 'Erasmus_2014-2022_aggregate_LAU.csv',
              sep=';', encoding='utf-8', index=False)
nutsagg.to_csv(args['output'] + 'Erasmus_2014-2022_aggregate_NUTS.csv',
               sep=';', encoding='utf-8', index=False)

# print message
print('[INFO] - ... done!')

