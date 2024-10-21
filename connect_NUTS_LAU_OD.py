#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 11:29:07 2023

@author: tuomvais
"""

import pandas as pd
import geopandas as gpd
from shapely import LineString
import glob

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

# loop over years
for year in range(2014, 2023):
    
    # check if more recent data
    if year >= 2021:
        
        # set LAU 2021 as the one to use
        lau_col = 'GISCO_LAU_ID_2021'
        
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
        
        # every 10 000 iterations print message and reset n_iter
        if n_iter == 50000:
            
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
    subset.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/Erasmus_{}_individual_LAU_NUTS.pkl'.format(str(year)))


# list for combining data
comblist = []

# glob pickled dataframes into list
for file in glob.glob('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/Erasmus_2*.pkl'):
    
    # read file
    tempdf = pd.read_pickle(file)
    comblist.append(tempdf)
    
# concatenate combined list
resdf = pd.concat(comblist, ignore_index=True)

# generate point geometries on nuts2 centroids
points['nuts_geom'] = gpd.points_from_xy(x=points['centroid_x'], y=points['centroid_y'])

# generate a dictionary of locations and point coordinates
nuts_dict = pd.Series(points['nuts_geom'].values, points['origin'].values).to_dict()
nuts_dict2 = pd.Series(points['NUTS_ID'].values, points['origin'].values).to_dict()

# get indicator value for iterations
n_iter = 1
print('[INFO] - Connecting point geometries to place names...')

# looping over erasmus data
for i, row in data.iterrows():
    
    # get origin and destination
    orig = row['origin']
    dest = row['destination']
    
    # try to save origins
    try:
        # save origins
        data.at[i, 'orig_point'] = nuts_dict[orig]
        data.at[i, 'orig_nuts'] = nuts_dict2[orig]
    except:
        # flood the zone with none
        data.at[i, 'orig_point'] = None
        data.at[i, 'orig_nuts'] = None
    
    # try to save destinations
    try:
        # save destinations
        data.at[i, 'dest_point'] = nuts_dict[dest]
        data.at[i, 'dest_nuts'] = nuts_dict2[dest]
    except:
        # flood the zone with none
        data.at[i, 'dest_point'] = None
        data.at[i, 'dest_nuts'] = None
    
    # update n_iter
    n_iter += 1
    
    # every 10 000 iterations print message and reset n_iter
    if n_iter == 10000:
        
        # current row
        currow = i + 1
        
        # print message
        print('[INFO] - Progress {}/{}'.format(str(currow), str(len(data))))
        
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

# get long and short-term mobility
short = data[data['Mobility Duration'] < 330]
long = data[data['Mobility Duration'] >= 330]

# save data
print('[INFO] - Saving full individual-level ERASMUS+ data...')
data.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_full_student_mobility_data_NUTS2.gpkg')
print('[INFO] - Saving long-term individual-level ERASMUS+ data...')
long.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_NUTS2.gpkg')
print('[INFO] - Saving short-term individual-level ERASMUS+ data...')
short.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_NUTS2.gpkg')

short = gpd.read_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_NUTS2.gpkg')
long = gpd.read_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_NUTS2.gpkg')
# sort by year
long = long.sort_values(['year'], ascending=True).reset_index(drop=True)
short = short.sort_values(['year'], ascending=True).reset_index(drop=True)

# add ID column
long['ID'] = range(1, len(long) + 1)
short['ID'] = range(1, len(short) + 1)

# get final individual data products
flong = long[['ID', 'OD_ID','orig_nuts','dest_nuts','Participant Age',
              'Participant Gender', 'Education Level','Special Needs', 'Fewer Opportunities',
              'Disadvantaged Background','year','month','Mobility Duration']]
flong = flong.rename(columns={'orig_nuts':'ORIGIN',
                              'dest_nuts':'DESTINATION',
                              'Participant Age':'AGE',
                              'Participant Gender':'GENDER',
                              'Education Level':'ED_LEVEL',
                              'Special Needs':'SPEC_NEEDS',
                              'Fewer Opportunities':'FEW_OPPO',
                              'Disadvantaged Background':'DISADV_BG',
                              'year':'YEAR',
                              'month':'MONTH',
                              'Mobility Duration':'MOB_DUR'})

fshort = short[['ID', 'OD_ID','orig_nuts','dest_nuts','Participant Age',
                'Participant Gender','Education Level','Special Needs', 'Fewer Opportunities',
                'Disadvantaged Background','year','month','Mobility Duration']]
fshort = fshort.rename(columns={'orig_nuts':'ORIGIN',
                                'dest_nuts':'DESTINATION',
                                'Participant Age':'AGE',
                                'Participant Gender':'GENDER',
                                'Education Level':'ED_LEVEL',
                                'Special Needs':'SPEC_NEEDS',
                                'Fewer Opportunities':'FEW_OPPO',
                                'Disadvantaged Background':'DISADV_BG',
                                'year':'YEAR',
                                'month':'MONTH',
                                'Mobility Duration':'MOB_DUR'})

# convert to integer
flong['AGE'] = flong['AGE'].astype(int)
fshort['AGE'] = fshort['AGE'].astype(int)

# filter ages
flong = flong[(flong['AGE'] >= 15) & (flong['AGE'] <= 90)]
fshort = fshort[(fshort['AGE'] >= 15) & (fshort['AGE'] <= 90)]

# save to csv
flong[['ORIGIN','DESTINATION','AGE','GENDER','ED_LEVEL','SPEC_NEEDS','FEW_OPPO','DISADV_BG','YEAR','MONTH','MOB_DUR']].to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_ind_long-term_students_NUTS2.csv',
             encoding='utf-8', index=False)
fshort[['ORIGIN','DESTINATION','AGE','GENDER','ED_LEVEL','SPEC_NEEDS','FEW_OPPO','DISADV_BG','YEAR','MONTH','MOB_DUR']].to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_ind_short-term_students_NUTS2.csv',
              encoding='utf-8', index=False)

# get short-term mobility
fshort = gpd.read_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_NUTS2.gpkg')

# group by gender
gender = fshort.groupby(['OD_ID','orig_nuts','dest_nuts','year','Participant Gender'])['Actual Participants (Contracted Projects)'].sum().rename('count').reset_index()
gender = gender.rename(columns={'orig_nuts':'ORIGIN',
                        'dest_nuts':'DESTINATION',
                        'count':'COUNT',
                        'year':'YEAR',
                        'Participant Gender':'GENDER'})

# filter years
gender[gender['YEAR'] < 2015].to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/P1_OD_short-term_students_Gender_NUTS2.csv', encoding='utf-8', index=False)
gender[(gender['YEAR'] >= 2016) & (gender['YEAR'] < 2020)].to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/P2_OD_short-term_students_Gender_NUTS2.csv', encoding='utf-8', index=False)
gender[gender['YEAR'] >= 2020].to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/P3_OD_short-term_students_Gender_NUTS2.csv', encoding='utf-8', index=False)


# get unique od pairs
print('[INFO] - Processing aggregate data...')
odpairs = data[['OD_ID','orig_nuts','dest_nuts','geometry']].drop_duplicates(subset=['OD_ID']).reset_index(drop=True)

# aggregate flows by OD ID and year
long_grouped = long.groupby(['OD_ID', 'year'])['Actual Participants (Contracted Projects)'].sum().rename('count').reset_index()
short_grouped = short.groupby(['OD_ID', 'year'])['Actual Participants (Contracted Projects)'].sum().rename('count').reset_index()

# join with geometry data
long_agg = pd.merge(long_grouped, odpairs, on=['OD_ID'])
short_agg = pd.merge(short_grouped, odpairs, on=['OD_ID'])

# for annual grouped data
long_agg = long_agg.rename(columns={'orig_nuts':'ORIGIN',
                                    'dest_nuts':'DESTINATION',
                                    'count':'COUNT',
                                    'year':'YEAR'})
# for annual grouped data
short_agg = short_agg.rename(columns={'orig_nuts':'ORIGIN',
                                    'dest_nuts':'DESTINATION',
                                    'count':'COUNT',
                                    'year':'YEAR'})

# convert to geodataframe
long_agg = gpd.GeoDataFrame(long_agg, crs='EPSG:3035')
short_agg = gpd.GeoDataFrame(short_agg, crs='EPSG:3035')

# save aggregate mobilities
print('[INFO] - Saving aggregate data...')
long_agg.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_annual_aggregate_total_NUTS2.gpkg')
short_agg.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_annual_aggregate_total_NUTS2.gpkg')

# drop geometry
long_agg = long_agg[['OD_ID', 'ORIGIN', 'DESTINATION', 'YEAR', 'COUNT']]
short_agg = short_agg[['OD_ID', 'ORIGIN', 'DESTINATION', 'YEAR', 'COUNT']]

# add od pairs with 0 mobility
allod = pd.read_csv('/home/tuomvais/GIS/MOBI-TWIN/NUTS2_2021_all_possible_OD_with_distance.csv', sep=';')

# list for dataframes containing odpairs without any flows per years
longlist = []
shortlist = []

# loop over the existing years
for year in range(2014, 2021):
    
    # get subsets of data
    sublong = long_agg[long_agg['YEAR'] == year]
    subshort = short_agg[short_agg['YEAR'] == year]
    
    # get subset of od flows without observations per year
    nodlong = allod[~allod['OD_ID'].isin(sublong['OD_ID'].value_counts().reset_index()['OD_ID'].values.tolist())]
    nodshort = allod[~allod['OD_ID'].isin(subshort['OD_ID'].value_counts().reset_index()['OD_ID'].values.tolist())]
    
    # create columns
    nodlong['YEAR'] = year
    nodlong['COUNT'] = 0
    nodshort['YEAR'] = year
    nodshort['COUNT'] = 0
    
    # unify columns structure
    nodlong = nodlong[['OD_ID', 'ORIGIN', 'DESTINATION', 'YEAR', 'COUNT']].reset_index(drop=True)
    nodshort = nodshort[['OD_ID', 'ORIGIN', 'DESTINATION', 'YEAR', 'COUNT']].reset_index(drop=True)
    
    # append to lists
    longlist.append(nodlong)
    shortlist.append(nodshort)
    print(year)
    
# concatenate lists of od flows without observations
noflow_long = pd.concat(longlist, ignore_index=True)
noflow_short = pd.concat(shortlist, ignore_index=True)

# concat to actual flows
long_agg = pd.concat([long_agg, noflow_long], ignore_index=True)
short_agg = pd.concat([short_agg, noflow_short], ignore_index=True)

# unify columns
long_agg = long_agg[['ORIGIN', 'DESTINATION', 'YEAR', 'COUNT']].rename(columns={'COUNT':'FLOW_COUNT'})
short_agg = short_agg[['ORIGIN', 'DESTINATION', 'YEAR', 'COUNT']].rename(columns={'COUNT':'FLOW_COUNT'})

# Define the values to drop (French territories in Americas/Asia/Africa, Svalbard) only for Report d2.1
#values_to_drop = ['FRY1', 'FRY2', 'FRY3', 'FRY4', 'FRY5', 'NO0B', 'FR91',
#                  'FRA1','FR92','FRA2','FR93','FRA3','FR94','FRA4']

# drop values
#long_agg = long_agg[~long_agg['ORIGIN'].isin(values_to_drop)]
#long_agg = long_agg[~long_agg['DESTINATION'].isin(values_to_drop)]

#short_agg = short_agg[~short_agg['ORIGIN'].isin(values_to_drop)]
#short_agg = short_agg[~short_agg['DESTINATION'].isin(values_to_drop)]

# save to csv
long_agg.to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_aggregate_NUTS2.csv', encoding='utf-8', index=False)
short_agg.to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_aggregate_NUTS2.csv', encoding='utf-8', index=False)
print('[INFO] - ... done!')

long_agg = pd.read_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_aggregate_NUTS2.csv', encoding='utf-8')
short_agg = pd.read_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_aggregate_NUTS2.csv', encoding='utf-8')
long_agg['o_country'] = long_agg['ORIGIN'].apply(lambda x: x[:2])
long_agg['d_country'] = long_agg['DESTINATION'].apply(lambda x: x[:2])
long_agg['OD_country'] = long_agg['o_country'] + '_'+ long_agg['d_country']
short_agg['o_country'] = short_agg['ORIGIN'].apply(lambda x: x[:2])
short_agg['d_country'] = short_agg['DESTINATION'].apply(lambda x: x[:2])
short_agg['OD_country'] = short_agg['o_country'] + '_'+ short_agg['d_country']

# combine all years together for aggregate data
totlong = long_agg.groupby(['OD_country'])['COUNT'].sum().reset_index().sort_values(by='COUNT', ascending=False)
totshort = short_agg.groupby(['OD_country'])['COUNT'].sum().reset_index().sort_values(by='COUNT', ascending=False)


# combine all years together for aggregate data
totlong = long_agg.groupby(['OD_ID'])['COUNT'].sum().reset_index()
totshort = short_agg.groupby(['OD_ID'])['COUNT'].sum().reset_index()

# get origin and destination as separate fields
totlong['ORIGIN'] = totlong['OD_ID'].apply(lambda x: x.split('_')[0])
totlong['DESTINATION'] = totlong['OD_ID'].apply(lambda x: x.split('_')[1])
totshort['ORIGIN'] = totshort['OD_ID'].apply(lambda x: x.split('_')[0])
totshort['DESTINATION'] = totshort['OD_ID'].apply(lambda x: x.split('_')[1])

# save total aggregates
totlong.to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_aggregate_TOTAL_NUTS2.csv', encoding='utf-8')
totshort.to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_aggregate_TOTAL_NUTS2.csv', encoding='utf-8')

totlong = pd.read_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_aggregate_TOTAL_NUTS2.csv', encoding='utf-8')
longs = totlong.groupby(['OD_ID'])['COUNT'].sum().reset_index().sort_values(by='COUNT', ascending=False)

totshort= pd.read_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_short-term_students_aggregate_TOTAL_NUTS2.csv', encoding='utf-8')
shorts = totshort.groupby(['OD_ID'])['COUNT'].sum().reset_index().sort_values(by='COUNT', ascending=False)

# remove directionality
data = gpd.read_file("/home/tuomvais/GIS/MOBI-TWIN/Erasmus/OD_long-term_students_NUTS2.gpkg")
data['OD_PAIR'] = data.apply(lambda x: frozenset([x['orig_nuts'], x['dest_nuts']]), axis=1)
test = data.groupby(['OD_PAIR'])['Actual Participants (Contracted Projects)'].sum()
test2 = data.groupby(['OD_ID'])['Actual Participants (Contracted Projects)'].sum()
