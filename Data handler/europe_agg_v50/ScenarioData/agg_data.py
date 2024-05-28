# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 15:28:07 2020

@author: stianbac

dict_countrycode = {"AT": "Austria", "BA": "Bosnia H", "BE": "Belgium",
                  "BG": "Bulgaria", "CH": "Switzerland", "CZ": "Czech R",
                  "DE": "Germany", "DK": "Denmark", "EE": "Estonia",
                  "ES": "Spain", "FI": "Finland", "FR": "France",
                  "GB": "Great Brit.", "GR": "Greece", "HR": "Croatia",
                  "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
                  "LT": "Lithuania", "LU": "Luxemb.", "LV": "Latvia",
                  "MK": "Macedonia", "NL": "Netherlands", "NO1": "NO1",
                  "NO2": "NO2", "NO3": "NO3", "NO4": "NO4", 
                  "NO5": "NO5", "PL": "Poland", "PT": "Portugal", 
                  "RO": "Romania", "RS": "Serbia", "SE": "Sweden", 
                  "SI": "Slovenia","SK": "Slovakia"}

inv_dict_countrycode = dict(map(reversed, dict_countrycode.items()))

dict_regioncode = {"AT": "East", "BA": "East", "BE": "West",
                  "BG": "East", "CH": "West", "CZ": "East",
                  "DE": "East", "DK": "North", "EE": "North",
                  "ES": "West", "FI": "North", "FR": "West",
                  "GB": "North", "GR": "East", "HR": "East",
                  "HU": "East", "IE": "North", "IT": "West",
                  "LT": "North", "LU": "East", "LV": "North",
                  "MK": "East", "NL": "West", "NO1": "North",
                  "PL": "East", "PT": "West", "RO": "East",
                  "RS": "East", "SE": "North", "SI": "East",
                  "SK": "East", "NO2": "North", "NO3": "North",
                  "NO4": "North", "NO5": "North"}
"""
def filter_countries(region, df):
    filtered_region = []
    for c in region:
        if c in df.columns:
            filtered_region.append(c)
    return filtered_region

import pandas as pd

filenames = ['electricload', 'hydroror', 'hydroseasonal', 'solar',
             'windoffshore', 'windonshore']

for name in filenames:
    df = pd.read_csv('country_data/' + name + '.csv')
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H")
    df['year'] = df['time'].dt.year
    df = df.loc[df.year.isin([2015,2016,2017,2018,2019]), :]
    df = df.drop(columns=['year'])
    
    east = ['AT', 'BA', 'BG', 'HR', 'CZ', 'DE', 'GR', 'HU', 'LU', 'MK', 'PL',
            'RO', 'RS', 'SK', 'SI']
    north = ['DK', 'EE', 'FI', 'GB', 'IE', 'LT', 'LV', 'NO1', 'NO2', 'NO3',
             'NO4', 'NO5', 'NO', 'SE']
    west = ['BE', 'CH', 'ES', 'FR', 'IT', 'NL', 'PT']
    
    east_f = filter_countries(region=east, df=df)
    north_f = filter_countries(region=north, df=df)
    west_f = filter_countries(region=west, df=df)
    
    europe_f = east_f + north_f + west_f
    
    if name in ['electricload', 'hydroseasonal']:
        df['East'] = df[east_f].sum(axis=1)
        df['North'] = df[north_f].sum(axis=1)
        df['West'] = df[west_f].sum(axis=1)
    else:
        df['East'] = df['DE']
        df['North'] = df['GB']
        df['West'] = df['FR']

    df = df.drop(columns = europe_f)

    df.to_csv(name + '.csv', index=False)

