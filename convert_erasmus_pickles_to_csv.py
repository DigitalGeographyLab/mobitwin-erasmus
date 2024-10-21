#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 09:26:34 2024

@author: tuomvais
"""

import pandas as pd
import glob

# glob pickled dataframes into list
for file in glob.glob('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/Erasmus_2*.pkl'):
    
    # get file name
    fn = file.split('/')[-1][:-4]
    
    # set output path
    op = '/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/csv/' + fn + '.csv'
    
    # read file
    tempdf = pd.read_pickle(file)
    
    # save file
    tempdf.to_csv(op, encoding='utf-8', index=False)
