#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 11:46:26 2023

# INFO

Run the script by opening a terminal in the directory of the script and typing:
    python geocode_erasmus.py -i /path/to/pickle/ -o /path/to/output/

"""

import pandas as pd
from geopy.geocoders import Photon, Nominatim
from geopy.extra.rate_limiter import RateLimiter
import geopandas as gpd
import time
import random
import argparse
import dictionaries

# initialize argument parser
ap = argparse.ArgumentParser()

# set up arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the Erasmus+ mobility pickled dataframe.")

ap.add_argument("-o", "--output", required=True,
                help="Path to directory where resulting CSV and pickled dataframe are saved.")

# parse arguments
args = vars(ap.parse_args())

# symbol dictionary
sym_dict = {' - ': ', ',
            ' / ': ', ',
            '/': ', ',
            ' | ': ', '}

# read pickle in
df = pd.read_pickle(args["input"])

# problem list
prob_cols = ['Sending Country', 'Sending City', 'Sending Organization',
             'Receiving Country', 'Receiving City', 'Receiving Organization']
probs = []

# list of placenames to switch for institution names
problist = ['Google', 'CheckURF', 'Check the PIC in URF For City',
            '?', '??', '-', 'Desconocido', 'desconocido',
            'DESCONOCIDO', 'XXXXX', 'xxxxx', 'Undefined',
            'Unknown', 'See Era Id', 'Enschede', 'Nepcity',
            'Dkzz', 'Otros', 'Oth']

# counters for problems
probsend = []
probrece = []

# set up organization dictionary
org_add = dictionaries.org_add

# check if sending or receiving city is "???" and replace with organization
print('[INFO] - Fixing problematic city names with institution names...')
for i, row in df.iterrows():

    # force values to string
    row['Sending City'] = str(row['Sending City'])
    row['Receiving City'] = str(row['Receiving City'])

    # check for question marks in sending
    if ('???' in row['Sending City']) or (row['Sending City'].title() in problist):
        probs.append(row[prob_cols])
        probsend.append(row)
        try:
            df.at[i, 'Sending City'] = org_add[row['Sending Organization'].title()]
        except:
            df.at[i, 'Sending City'] = row['Sending Organization'].title()

    # check for question marks in receiving city
    if ('???' in row['Receiving City']) or (row['Receiving City'].title() in problist):
        probs.append(row[prob_cols])
        probrece.append(row)
        try:
            df.at[i, 'Receiving City'] = org_add[row['Receiving Organization'].title()]
        except:
            df.at[i, 'Receiving City'] = row['Receiving Organization'].title()

# Harmonize city name capitalization
df['Sending City'] = df['Sending City'].apply(lambda x: str(x).title())
df['Receiving City'] = df['Receiving City'].apply(lambda x: str(x).title())

# set up umlaut dictionary
umlaut_dict = dictionaries.umlaut_dict

# replace the weird names
for old, new in umlaut_dict.items():

    # replace
    df['Sending City'] = df['Sending City'].str.replace(old, new, regex=False)
    df['Receiving City'] = df['Receiving City'].str.replace(old, new, regex=False)

# fix weird symbol use
for old, new in sym_dict.items():
    # replace
    df['Sending City'] = df['Sending City'].str.replace(old, new, regex=False)
    df['Receiving City'] = df['Receiving City'].str.replace(old, new, regex=False)

# Clean country
print('[INFO] - Cleaning up columns...')
df['o_country'] = df['Sending Country'].apply(lambda x: x.split(' - ')[1])
df['d_country'] = df['Receiving Country'].apply(lambda x: x.split(' - ')[1])

# strip leading and trailing whitespace
df['Sending City'] = df['Sending City'].replace(r"^ +| +$", r"", regex=True)
df['Receiving City'] = df['Receiving City'].replace(r"^ +| +$", r"", regex=True)

# Get a geocodable location
df['origin'] = df['Sending City'] + ', ' + df['o_country']
df['destination'] = df['Receiving City'] + ', ' + df['d_country']

# replace origins and destinations with the actual address for those origins and destinations that have it
for i, row in df.iterrows():

    # replace origin with accurate address if it is available
    if pd.isna(row['sending_org_address']) == False:

        # replace origin
        df.at[i, 'origin'] = row['sending_org_address']
    else:
        pass

    # check if destination has accurate address
    if pd.isna(row['receiving_org_address']) == False:

        # replace destination
        df.at[i, 'destination'] = row['receiving_org_address']
    else:
        pass

# set up place dictionary
placedict = dictionaries.placedict

# loop over data
for i, row in df.iterrows():

    # drop remaining question marks
    df.at[i, 'origin'] = row['origin'].replace('?', '')
    df.at[i, 'destination'] = row['destination'].replace('?', '')

    # drop placenames with "Cedex" as it refers to french nomenclature for postal code area
    df.at[i, 'origin'] = row['origin'].replace('Cedex', '')
    df.at[i, 'destination'] = row['destination'].replace('Cedex', '')

    # replace some place names with geocodable place names
    try:
        df.at[i, 'origin'] = placedict[row['origin']]
    except:
        pass
    try:
        df.at[i, 'destination'] = placedict[row['destination']]
    except:
        pass

# save dataframe so geocoded locations can be eventually connected to the mobility
print('[INFO] - Saving mobility data before geocoding...')
df.to_pickle(args['output'] + 'erasmus_fixed_toponyms_pre-geocoding.pkl')

# get unique origins and destinations
origins = df['origin'].value_counts().reset_index()
destinations = df['destination'].value_counts().reset_index()

# rename column
destinations = destinations.rename(columns={'destination': 'origin'})

# concatenate into a dataframe
places = pd.concat([origins, destinations], ignore_index=True)

# group by and sum
places = places.groupby(['origin'])['count'].sum(
    ).reset_index(
        ).sort_values(by=['count'], ascending=False).reset_index(drop=True)

# drop duplicates
places = places.drop_duplicates(subset='origin')

# add to location list
loclist = []
loclist.append(places)

# concatenate location list to a proper dataframe
locations = pd.concat(loclist, ignore_index=True)
probs = pd.concat(probs, ignore_index=True)
print('[INFO] - Gathering locations is done!')

# sort by counts
locations = locations.sort_values(['count'], ascending=False)

# drop duplicates
locations = locations.drop_duplicates(subset=['origin']).reset_index(drop=True)

# save locations
print('[INFO] - Saving unique toponyms before geocoding...')
locations.to_pickle(args['output'] + 'erasmus_pre-geocoded_locations_only.pkl')
locations.to_csv(args['output'] + 'erasmus_pre-geocoded_locations_only.csv',
                 encoding='utf-8', sep=';')

# initialize geocoder
geolocator = Photon(user_agent='ErasmusGeocoder')

# set up rate limiter to not abuse the free API
geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# get initial value for iterations
n_iter = 1
print('[INFO] - Starting to geocode with Photon...')

# keep tabs on unsuccesfull geocodes
unsuc = []

# geocode
for i, row in locations.iterrows():
    if n_iter != 20:

        # geocode location
        geocoded = geocoder(row['origin'], timeout=120)

        try:
            # get geocoded address
            locations.at[i, 'gc_address'] = geocoded.address

            # save latitude and longitude
            locations.at[i, 'y'] = geocoded.latitude
            locations.at[i, 'x'] = geocoded.longitude

            # update
            n_iter += 1
        except:

            # append list
            unsuc.append(row)

            # fill in empty
            locations.at[i, 'gc_address'] = 'UNSUCCESSFUL'

            # save latitude and longitude
            locations.at[i, 'y'] = None
            locations.at[i, 'x'] = None

            # update
            n_iter += 1

    elif n_iter == 20:

        # geocode location
        geocoded = geolocator.geocode(row['origin'], timeout=120)

        try:
            # get geocoded address
            locations.at[i, 'gc_address'] = geocoded.address

            # save latitude and longitude
            locations.at[i, 'y'] = geocoded.latitude
            locations.at[i, 'x'] = geocoded.longitude

            # update
            n_iter += 1
        except:

            # append list
            unsuc.append(row)

            # fill in empty
            locations.at[i, 'gc_address'] = 'UNSUCCESSFUL'

            # save latitude and longitude
            locations.at[i, 'y'] = None
            locations.at[i, 'x'] = None

            # update
            n_iter += 1

        # 1-indexed iterator
        current_i = i + 1

        # print progress
        print('[INFO] - Geocoding progress ' +
              str(current_i) + '/' + str(len(locations)))

        # save progress
        locations.to_pickle(args['output'] +
                            'geocoded_locations_intermediate.pkl')

        # wait
        time.sleep(random.randint(40, 60))

        # reset n_iter
        n_iter = 1

# save locations
locations.to_pickle(args['output'] + 'geocoded_locations_Photon_first_run.pkl')

# get locations with unsuccessful and successful geocoding
unloc = locations[locations['gc_address'].isin(['UNSUCCESSFUL',
                                                'nan'])
                  ].reset_index(drop=True)
success = locations[~locations['gc_address'].isin(['UNSUCCESSFUL',
                                                   'nan'])
                    ].reset_index(drop=True)

# duplicate origins for unlocs for fixing
unloc['origin2'] = unloc['origin']

# set up second unmlaut dictionary
udict = dictionaries.udict

# fix place names for mobilities with 2 or more flows
for old, new in udict.items():

    # replace
    unloc['origin2'] = unloc['origin2'].str.replace(old, new, regex=False)


# get initial value for iterations
n_iter = 1
print('[INFO] - Starting to geocode manually fixed toponyms...')

# keep tabs on unsuccesfull geocodes
unsuc = []

# geocode
for i, row in unloc.iterrows():
    if n_iter != 25:
        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)

        try:
            # get geocoded address
            unloc.at[i, 'gc_address'] = geocoded.address

            # save latitude and longitude
            unloc.at[i, 'y'] = geocoded.latitude
            unloc.at[i, 'x'] = geocoded.longitude

            # update
            n_iter += 1
        except:

            # append list
            unsuc.append(row)

            # fill in empty
            unloc.at[i, 'gc_address'] = 'UNSUCCESSFUL'

            # save latitude and longitude
            unloc.at[i, 'y'] = None
            unloc.at[i, 'x'] = None

            # update
            n_iter += 1

    elif n_iter == 25:

        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)

        try:
            # get geocoded address
            unloc.at[i, 'gc_address'] = geocoded.address

            # save latitude and longitude
            unloc.at[i, 'y'] = geocoded.latitude
            unloc.at[i, 'x'] = geocoded.longitude

            # pdate
            n_iter += 1
        except:

            # append list
            unsuc.append(row)

            # fill in empty
            unloc.at[i, 'gc_address'] = 'UNSUCCESSFUL'

            # save latitude and longitude
            unloc.at[i, 'y'] = None
            unloc.at[i, 'x'] = None

            # update
            n_iter += 1

        # 1-indexed iterator
        current_i = i + 1

        # print progress
        print('[INFO] - Geocoding progress ' +
              str(current_i) + '/' + str(len(unloc)))

        # save progress
        unloc.to_pickle(args['output'] +
                        'geocoded_fixed_locations_intermediate.pkl')

        # wait
        time.sleep(random.randint(40, 60))

        # reset n_iter
        n_iter = 1

# drop origin2
unloc_res = unloc[['origin', 'count', 'gc_address', 'y', 'x']]

# save better fixed locations
unloc_res.to_pickle(args['output'] + 'geocoded_fixed_locations_second_run.pkl')

# separate unsuccesfuls
unloc_res_u = unloc_res[unloc_res['x'].isna()]
unloc_res_s = unloc_res[~unloc_res['x'].isna()]

# read in manual corrections
mancor = pd.read_excel("data/Unsuccessfuls_geocoded_ALL_DONE.xlsx",
                       converters={'origin': str,
                                   'count': int,
                                   'gc_address': str,
                                   'y': float,
                                   'x': float})

# simplify data
mancor = mancor[['origin', 'count', 'gc_address', 'y', 'x']]

# update unsuccesfully corrected geocodes with manually checked geocodes
up_unsuc = pd.merge(unloc_res_u[['origin']], mancor, on='origin', how='left')
up_unsuc = up_unsuc[['origin', 'count', 'gc_address', 'y', 'x']]

# get error rows
up_unsuc_errors = up_unsuc[up_unsuc['origin2'].isna()]

# initialize geocoder
geolocator = Nominatim(user_agent='ErasmusGeocoding')

# set up rate limiter
geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# duplicate origins for unlocs for fixing
up_unsuc_errors['origin2'] = up_unsuc_errors['origin']

# set up final corrections dictionary
fincor = dictionaries.fincor

# fix place names for mobilities with 2 or more flows
for old, new in fincor.items():

    # replace
    up_unsuc_errors['origin2'] = up_unsuc_errors['origin2'].str.replace(old,
                                                                        new,
                                                                        regex=False)

# get initial value for iterations
n_iter = 1
print('[INFO] - Starting to geocode with Nominatim to finalize the data...')

# keep tabs on unsuccesfull geocodes
unsuc2 = []

# geocode
for i, row in up_unsuc_errors.iterrows():
    if n_iter != 25:
        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)

        try:
            # get geocoded address
            up_unsuc_errors.at[i, 'gc_address'] = geocoded.address

            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = geocoded.latitude
            up_unsuc_errors.at[i, 'x'] = geocoded.longitude

            # update
            n_iter += 1
        except:

            # append list
            unsuc2.append(row)

            # fill in empty
            up_unsuc_errors.at[i, 'gc_address'] = 'UNSUCCESSFUL'

            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = None
            up_unsuc_errors.at[i, 'x'] = None

            # update
            n_iter += 1

    elif n_iter == 25:

        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)

        try:
            # get geocoded address
            up_unsuc_errors.at[i, 'gc_address'] = geocoded.address

            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = geocoded.latitude
            up_unsuc_errors.at[i, 'x'] = geocoded.longitude

            # update
            n_iter += 1
        except:

            # append list
            unsuc2.append(row)

            # fill in empty
            up_unsuc_errors.at[i, 'gc_address'] = 'UNSUCCESSFUL'

            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = None
            up_unsuc_errors.at[i, 'x'] = None

            # update
            n_iter += 1

        # 1-indexed iterator
        current_i = i + 1

        # print progress
        print('[INFO] - Geocoding progress ' + str(current_i) +
              '/' + str(len(up_unsuc_errors)))

        # save progress
        up_unsuc_errors.to_pickle(args['output'] +
                                  'geocoded_fixed_nominatims_locations_intermediate.pkl')

        # wait
        time.sleep(random.randint(40, 60))

        # reset n_iter
        n_iter = 1

# columns to use in result
rescols = ['origin', 'count', 'gc_address', 'y', 'x']

# join together
result = pd.concat([success[rescols], unloc_res_s[rescols],
                    up_unsuc_errors[rescols]], ignore_index=True).sort_values(
                        ['count'], ascending=False).reset_index(drop=True)

# save
print("[INFO] - Saving final results...")
result.to_pickle(args['output'] + 'geocoded_erasmus_placenames_final.pkl')

# drop unsuccessful results
result = result.dropna(subset=['x']).reset_index(drop=True)

# force datatypes to float for x and y
result['x'] = pd.to_numeric(result['x'])
result['y'] = pd.to_numeric(result['y'])

# convert to geodataframe
print('[INFO] - Turning geocoded locations into a GeoDataFrame..')
result = gpd.GeoDataFrame(result,
                          geometry=gpd.points_from_xy(result['x'],
                                                      result['y']),
                          crs='EPSG:4326')
result.to_file(args['output'] +
               'geocoded_erasmus_placenames_finla.gpkg', driver='GPKG')
print('[INFO] - Saved result to geopackage..')

print("[INFO] - ... done!")
