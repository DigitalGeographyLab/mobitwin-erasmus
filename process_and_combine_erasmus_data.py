#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 15:15:35 2024

# INFO

Run the script by opening a terminal in the directory of the script and typing:
    python process_and_combine_erasmus_data.py -i /path/to/excels/ -o /path/to/output/ -n combined_erasmus_data

"""

import argparse
import pandas as pd
import glob

# initialize argument parser
ap = argparse.ArgumentParser()

# set up arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to directory with the Erasmus+ mobility Excel files.\nNOTE: Make sure the directory does not contain other .xlsx files!")

ap.add_argument("-o", "--output", required=True,
                help="Path to directory where resulting CSV and pickled dataframe are saved.")

ap.add_argument("-n", "--name", required=True,
                help="Designate the name of the output files without a file extension.")

# parse arguments
args = vars(ap.parse_args())

# list of csv files
files = []

# set up input filepath
i_fp = args["input"] + "*.xlsx"

# glob all the csvs
for file in glob.glob(i_fp):
    files.append(file)

# empty list for dataframes
edf = []
    
# loop over the csv files
for fi in files:
    
    # get filename
    fn = fi.split('/')[-1][:-5]
    
    # get year
    yr = int(fn.split('-')[-1])
    
    # print message
    print('[INFO] - Reading file ' + str(fn))
    
    # check if file is from newer erasmus program
    if yr >= 2021:
        
        # get excel file object
        xls = pd.ExcelFile(fi)
        
        # get sheet names
        sheets = xls.sheet_names
        
        # empty list of mobilities from both programmes
        emprog = []
        
        # loop over sheets
        for sh in sheets:
            
            # read sheet
            data = pd.read_excel(fi, sheet_name=sh)
            
            # append
            emprog.append(data)
        
        # concatenate into one dataframe
        df = pd.concat(emprog, ignore_index=True)
        
        # forget list and data
        del emprog, data, xls
    
    # check if data is from earlier programme
    else:
        
        # read csv in
        df = pd.read_excel(fi)
    
    # drop NA from mobility duration
    df = df.dropna(subset=['Mobility Duration'])
    
    # drop shorter mobility
    df = df[df['Mobility Duration'] >= 90]
    
    # drop records where age isn't reported
    df = df[df['Participant Age'] != '-']
    
    # drop too young participants
    df = df[df['Participant Age'].astype(int) >= 18]
    
    # ensure all participants are students
    df = df[df['Participant Profile'] == 'Learner']
    
    # send to empty list
    edf.append(df)
    
# final concatenation
print('[INFO] - Concatenating result...')
result = pd.concat(edf, ignore_index=True)

# get year
result['year'] = result['Mobility Start Year/Month'].apply(lambda x: int(x.split('-')[0]))

# assign mover type
result['mov_type'] = result['Mobility Duration'].apply(lambda x: 'Short-term' if x < 330 else 'Long-term')

# set up output filenames
output = args['output'] + args['name']

# save as csv
print('[INFO] - Saving result to CSV...')
result.to_csv(output + ".csv", sep=';', encoding='utf-8')

# save as pickle
print('[INFO] - Saving result to pickle...')
result.to_pickle(output + ".pkl")

print('[INFO] - ... done!')
