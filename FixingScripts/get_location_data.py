# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import datetime
import os
import random
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_city_data(item_link, sleep_min=1, sleep_rand=1, verbose=False, debug=False):
    city, state, country, bids = 0, 0, 0, 0
    try:
        time.sleep(sleep_min + sleep_rand * random.uniform(0, 1))
        source = requests.get(item_link).text
        soup = BeautifulSoup(source, 'lxml')

        try:
            bids = soup.find('a', attrs={'class': 'vi-bidC'})
            bids = int(re.sub(r'[^\d.]+', '', bids.text))
        except Exception as e:
            if debug or verbose: print('ebay_scrape-vi-bidC', e, item_link)
            bids = -1

        try:
            loc = soup.find('div', attrs={'class': 'iti-eu-bld-gry'})
            loc = loc.find('span').text.split(',')
            city, state, country = loc[0], loc[1], loc[2]
            if len(loc) == 2:
                city, state, country = loc[0], '', loc[1]
            elif len(loc) == 3:
                city, state, country = loc[0], loc[1], loc[2]



        except Exception as e:
            if debug or verbose: print('ebay_scrape-seller-1', e, item_link)
            try:
                loc_2 = soup.find('div', attrs={'class': 'vi-wp vi-VR-cvipCntr1'})
                loc_2 = loc_2.find_all('tr', attrs={'class': 'vi-ht20'})
                for l in loc_2:
                    if l.text.find('Item location:') > 0:
                        i_loc = l.find_all('div', attrs={'class': 'u-flL'})
                        loc_text = i_loc[1].text.split(',')
                        if len(loc_text) == 2:
                            city, state, country = loc_text[0], '', loc_text[1]
                        elif len(loc_text) == 3:
                            city, state, country = loc_text[0], loc_text[1], loc_text[2]
                        break
            except Exception as e:
                if debug or verbose: print('ebay_scrape-seller-2', e, item_link)
                try:
                    oitems = soup.find_all('a',
                                           attrs={'class': 'nodestar-item-card-details__view-link'})
                    orig_link = oitems[0]['href']

                    time.sleep(sleep_min + sleep_rand * random.uniform(0, 1))
                    source = requests.get(orig_link).text
                    soup = BeautifulSoup(source, 'lxml')

                    try:
                        bids = soup.find('a', attrs={'class': 'vi-bidC'})
                        bids = int(re.sub(r'[^\d.]+', '', bids.text))
                    except Exception as e:
                        if debug or verbose: print('ebay_scrape-vi-bidC', e, item_link)
                        bids = -1

                    try:

                        loc = soup.find('div', attrs={'class': 'iti-eu-bld-gry'})
                        loc = loc.find('span').text.split(',')
                        if len(loc) == 2:
                            city, state, country = loc[0], '', loc[1]
                        elif len(loc) == 3:
                            city, state, country = loc[0], loc[1], loc[2]
                        try:
                            loc = soup.find('div', attrs={'class': 'vi-wp vi-VR-cvipCntr1'})
                            loc = loc.find_all('tr', attrs={'class': 'vi-ht20'})

                            for l in loc:
                                if l.text.find('Item location:') > 0:
                                    i_loc = l.find_all('div', attrs={'class': 'u-flL'})
                                    loc_text = i_loc[1].text.split(',')
                                    city, state, country = loc_text[0], loc_text[1], loc_text[2]
                                    if len(loc_text) == 2:
                                        city, state, country = loc_text[0], '', loc_text[1]
                                    elif len(loc_text) == 3:
                                        city, state, country = loc_text[0], loc_text[1], loc_text[2]
                                    break
                        except Exception as e:
                            if debug or verbose: print('ebay_scrape-vi-wp', e, item_link)
                    except Exception as e:
                        if debug or verbose: print('ebay_scrape-iti-eu-bld-gry', e, item_link)
                except Exception as e:
                    if debug or verbose: print('ebay_scrape-nodestar', e, item_link)
    except Exception as e:
        if debug or verbose: print('ebay_scrape-oitems-1', e, item_link)
    return city, state, country, bids


directory = r'C:\Users\mdriscoll6\Dropbox\PythonProjects\eBayScraper\Spreadsheets'
seller_cities = {}
seller_state = {}
seller_country = {}

sleep_min = 0.25
sleep_rand = 1.5
verbose = False
debug = False

for f in os.listdir(directory):
    print(f)
    df = pd.read_excel('Spreadsheets/' + f, index_col=0, engine='openpyxl')
    if 'City' not in df:
        df['City'] = 0
    if 'State' not in df:
        df['State'] = 0
    if 'Country' not in df:
        df['Country'] = 0

    for index, row in df.iterrows():

        if row['City'] != 0 and str(row['City']) != 'nan' and row['Seller'] not in seller_cities:
            seller_cities[row['Seller']] = row['City']
            seller_state[row['Seller']] = row['State']
            seller_country[row['Seller']] = row['Country']

    print(len(seller_cities))

files = [
    '5600X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5800X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5900X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5950X -image -jpeg -img -picture -pic -jpg.xlsx',

    # 'RTX 3060 -image -jpeg -img -picture -pic -jpg.xlsx',
    # 'RTX 3070 -image -jpeg -img -picture -pic -jpg.xlsx',
    # 'RTX 3080 -image -jpeg -img -picture -pic -jpg.xlsx',
    # 'RTX 3090 -image -jpeg -img -picture -pic -jpg.xlsx',

    #'PS5 -digital -image -jpeg -img -picture -pic -jpg.xlsx',
    #'PS5 Digital -image -jpeg -img -picture -pic -jpg.xlsx',

    # 'Xbox Series S -image -jpeg -img -picture -pic -jpg.xlsx',
    # 'Xbox Series X -image -jpeg -img -picture -pic -jpg.xlsx',


]

# for f in os.listdir(directory):
for f in files:
    print('')
    print('')
    print('----------------------------------------------')
    print(f)
    df = pd.read_excel('Spreadsheets/' + f, index_col=0, engine='openpyxl')
    dup_df = df.copy(deep=True)

    if 'City' not in dup_df:
        dup_df['City'] = 0
    if 'State' not in dup_df:
        dup_df['State'] = 0
    if 'Country' not in dup_df:
        dup_df['Country'] = 0
    if 'Bids' not in dup_df:
        dup_df['Bids'] = 0
    for index, row in dup_df.iterrows():

        if row['City'] != 0 and str(row['City']) != 'nan' and row['Seller'] not in seller_cities:
            seller_cities[row['Seller']] = row['City']
            seller_state[row['Seller']] = row['State']
            seller_country[row['Seller']] = row['Country']

        elif row['Seller'] in seller_cities and row['City'] != seller_cities[row['Seller']]:
            dup_df.loc[index, 'City'] = seller_cities[row['Seller']]
            dup_df.loc[index, 'State'] = seller_state[row['Seller']]
            dup_df.loc[index, 'Country'] = seller_country[row['Seller']]

        elif row['Ignore'] != 1 and seller_cities.get(row['Seller'], -1) == -1 and row[
            'Sold Date'] >= datetime.datetime(2020, 11, 4):
            item_link = row['Link']
            city, state, country, bids = get_city_data(item_link, sleep_rand, verbose, debug)
            if verbose: print(row['Seller'], city, state, country, row['Link'])
            if city == 0:
                print(index, row['Seller'], row['Sold Date'], row['Link'])
            else:
                print(index, row['Seller'], city, state, country, bids, row['Sold Date'])
                dup_df.loc[index, 'City'] = city
                dup_df.loc[index, 'State'] = state
                dup_df.loc[index, 'Country'] = country
                dup_df.loc[index, 'Bids'] = bids
                seller_cities[row['Seller']] = city
                seller_state[row['Seller']] = state
                seller_country[row['Seller']] = country

        if index % 100 == 0:
            dup_df.to_excel('temp/' + f, engine='openpyxl')
    dup_df.to_excel('temp/' + f, engine='openpyxl')
