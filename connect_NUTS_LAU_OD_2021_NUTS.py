#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 11:29:07 2023

@author: tuomvais
"""

import pandas as pd
import geopandas as gpd
from shapely import LineString

# reading individual data in
print('[INFO] - Reading individual data in...')
data = pd.read_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/erasmus_combined_2014-2022_pre-geocoding.pkl')

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
print('[INFO] - Reading geocoded points in...')
points = gpd.read_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_2014-2022_fixed_locations_NUTS_LAU_codes.gpkg')

# get NUS 3 codes for 2021
nutpoints = points[~points['NUTS_ID_2021'].isna()]

# read NUTS 2021 layer
nuts = gpd.read_file("/home/tuomvais/GIS/MOBI-TWIN/NUTS/NUTS/NUTS_3_01M_2021_3035.gpkg")

# get representative points
nuts['rep_x'] = nuts['geometry'].representative_point().x
nuts['rep_y'] = nuts['geometry'].representative_point().y

# get geometric point
nuts['rep_geom'] = gpd.points_from_xy(x=nuts['rep_x'], y=nuts['rep_y'])

# generate a dictionary of locations and point coordinates
nuts_dict = pd.Series(nuts['rep_geom'].values, nuts['NUTS_ID'].values).to_dict()
nuts_dict2 = pd.Series(nutpoints['NUTS_ID_2021'].values, nutpoints['origin'].values).to_dict()

# get indicator value for iterations
n_iter = 1
print('[INFO] - Assigning NUTS 3 codes to place names...')

# looping over erasmus data
for i, row in data.iterrows():
    
    # get origin and destination
    orig = row['origin']
    dest = row['destination']
    
    # try to save origins
    try:
        # save origins
        data.at[i, 'orig_nuts'] = nuts_dict2[orig]
    except:
        # flood the zone with none
        data.at[i, 'orig_nuts'] = None
    
    # try to save destinations
    try:
        # save destinations
        data.at[i, 'dest_nuts'] = nuts_dict2[dest]
    except:
        # flood the zone with none
        data.at[i, 'dest_nuts'] = None
    
    # update n_iter
    n_iter += 1
    
    # every 10 000 iterations print message and reset n_iter
    if n_iter == 100000:
        
        # current row
        currow = i + 1
        
        # print message
        print('[INFO] - Assigning NUTS 3 codes to place names. Progress {}/{}'.format(str(currow), str(len(data))))
        
        # update n_iter
        n_iter = 1

# get indicator value for iterations
n_iter = 1

# looping over erasmus data
for i, row in data.iterrows():
    
    # get origin and destination
    orig = row['orig_nuts']
    dest = row['dest_nuts']
    
    # try to save origins
    try:
        # save origins
        data.at[i, 'orig_point'] = nuts_dict[orig]
    except:
        # flood the zone with none
        data.at[i, 'orig_point'] = None
    
    # try to save destinations
    try:
        # save destinations
        data.at[i, 'dest_point'] = nuts_dict[dest]
    except:
        # flood the zone with none
        data.at[i, 'dest_point'] = None
    
    # update n_iter
    n_iter += 1
    
    # every 10 000 iterations print message and reset n_iter
    if n_iter == 100000:
        
        # current row
        currow = i + 1
        
        # print message
        print('[INFO] - Assigning point geometries to NUTS 3 codes. Progress {}/{}'.format(str(currow), str(len(data))))
        
        # update n_iter
        n_iter = 1

# get original data size
osize = len(data)

# drop mobilities that are not between two NUTS regions (e.g. in Asia, Africa, Americas etc.)
print('[INFO] - Finalizing individual-level ERASMUS mobility data...')
data = data.dropna(subset=['orig_nuts','dest_nuts']).reset_index(drop=True)

# print info on retained data
share = round((len(data)/osize) * 100, 2)
print('[INFO] - {} % of all mobilities can be mapped'.format(share))

# generate OD pair ID
data['OD_ID'] = data['orig_nuts'] + '_' + data['dest_nuts']

# generate linestrings
print('[INFO] - Converting OD points to line geometries...')
data['geometry'] = data.apply(lambda x: LineString([x['orig_point'], x['dest_point']]), axis=1)

# instatiate geodataframe with proper CRS
data = gpd.GeoDataFrame(data=data, geometry='geometry', crs="EPSG:3035")

# drop point geometries
data = data.drop(columns=['orig_point', 'dest_point'])

print('[INFO] - Saving full individual-level ERASMUS+ data...')
data.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/OD_full_student_mobility_data_2014-2022_NUTS3_v2021.gpkg')

# get unique od pairs
print('[INFO] - Processing aggregate data...')
odpairs = data[['OD_ID','orig_nuts','dest_nuts','geometry']].drop_duplicates(subset=['OD_ID']).reset_index(drop=True)

# aggregate flows by OD ID and year
grouped = data.groupby(['OD_ID', 'year'])['Actual Participants'].sum().rename('count').reset_index()

# join with geometry data
studagg = pd.merge(grouped, odpairs, on=['OD_ID'])

# for annual grouped data
studagg = studagg.rename(columns={'orig_nuts':'ORIGIN',
                                    'dest_nuts':'DESTINATION',
                                    'count':'COUNT',
                                    'year':'YEAR'})
studagg = gpd.GeoDataFrame(studagg, crs='EPSG:3035')

# save aggregate mobilities
print('[INFO] - Saving aggregate data...')
studagg.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/OD_students_annual_aggregate_total_NUTS3_2014-2022.gpkg')
