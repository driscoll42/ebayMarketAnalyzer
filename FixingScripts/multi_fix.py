# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import datetime
import os
import random
import time
from copy import deepcopy

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from classes import EbayVariables
from main import get_quantity_hist

directory = r'C:\Users\mdriscoll6\Dropbox\PythonProjects\eBayScraper\Spreadsheets'


def get_multi_data(item_link, e_vars, sleep_len=1):
    retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504, 404],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1

    )
    http = HTTPAdapter(max_retries=retry_strategy)
    adapter = requests.Session()
    adapter.mount("https://", http)
    adapter.mount("http://", http)

    sold_list = []
    quantity_sold = 0
    try:
        time.sleep(sleep_len * random.uniform(0, 1))
        source = requests.get(item_link).text
        soup = BeautifulSoup(source, 'lxml')

        try:
            iitem = soup.find_all('a', attrs={'class': 'vi-txt-underline'})
            quantity_sold = int(iitem[0].text.split()[0])

            sold_hist_url = iitem[0]['href']
            sold_list, sl_date, sl_datetime = get_quantity_hist(sold_hist_url, sold_list, adapter, e_vars)

        except Exception as e:
            if e_vars.debug or e_vars.verbose: print('ebay_scrape-seller-1', e, item_link)
            try:
                oitems = soup.find_all('a',
                                       attrs={'class': 'nodestar-item-card-details__view-link'})
                orig_link = oitems[0]['href']

                time.sleep(sleep_len * random.uniform(0, 1))
                source = requests.get(orig_link).text
                soup = BeautifulSoup(source, 'lxml')

                try:
                    nnitems = soup.find_all('a', attrs={'class': 'vi-txt-underline'})
                    quantity_sold = int(nnitems[0].text.split()[0])

                    if quantity_sold > 1:
                        sold_hist_url = nnitems[0]['href']
                        sold_list, sl_date, sl_datetime = get_quantity_hist(sold_hist_url, sold_list, adapter, e_vars)

                except Exception as e:
                    if e_vars.debug or e_vars.verbose: print('ebay_scrape-nnitems', e, orig_link)
            except Exception as e:
                if e_vars.debug or e_vars.verbose: print('ebay_scrape-oitems-2', e, item_link)
    except Exception as e:
        if e_vars.debug or e_vars.verbose: print('ebay_scrape-oitems-1', e, item_link)
    return quantity_sold, sold_list


# Set Class variables
e_vars = EbayVariables(run_cached=False,
                       sleep_len=4,
                       show_plots=True,
                       main_plot=True,
                       profit_plot=True,
                       extra_title_text='',
                       country='USA',
                       ccode='$',
                       days_before=7,
                       feedback=True,
                       quantity_hist=True,
                       debug=False,
                       verbose=False,
                       tax_rate=0.0625,
                       store_rate=0.04,  # The computer store rate
                       non_store_rate=0.1,  # The computer non-store rate
                       brand_list=[],
                       model_list=[]
                       )

# CPU specific class variables
cpu_vars = deepcopy(e_vars)
cpu_vars.sacat = 164

# Mobo specific class variables
mobo_vars = deepcopy(e_vars)
mobo_vars.sacat = 1244

# GPU specific class variables
gpu_vars = deepcopy(e_vars)
gpu_vars.sacat = 27386

# Console specific class variables
console_vars = deepcopy(e_vars)
console_vars.sacat = 139971
console_vars.store_rate = 0.0915

# Other potentially useful sacats
psu_sacat = 42017
ssd_sacat = 175669
memory_sacat = 170083
comp_case_sacat = 42014
cpu_cooler_sacat = 131486

files = [

    'RTX 3090.xlsx',

    'RX 6900.xlsx',

    'RX 6800 -XT.xlsx',
    'RX 6800 XT.xlsx',

    'RTX 3060.xlsx',
    'RTX 3070.xlsx',
    'RTX 3080.xlsx',

    '5600X.xlsx',
    '5800X.xlsx',
    '5900X.xlsx',
    '5950X.xlsx',

    '3950X.xlsx',
    '3600X -combo -custom -roku.xlsx',
    '3600XT -combo -custom.xlsx',
    '3700X -combo -custom.xlsx',
    '3800X -combo -custom.xlsx',
    '3800XT -combo -custom.xlsx',
    '3900X -combo -custom.xlsx',
    '3900XT -combo -custom.xlsx',
    '(amd, Ryzen) 3100 -combo -custom -radeon.xlsx',
    '(amd, Ryzen) 3600 -combo -custom -roku -3600x -3600xt.xlsx',
    '3300X -combo -custom.xlsx',

    '(amd, ryzen) 1200 AF.xlsx',
    '(amd, ryzen) 1200.xlsx',
    '(amd, ryzen) 1300X.xlsx',
    '(amd, ryzen) 1400.xlsx',
    '(amd, ryzen) 1500X.xlsx',
    '(amd, ryzen) 1600 AF.xlsx',
    '(amd, ryzen) 1600.xlsx',
    '(amd, ryzen) 1600X.xlsx',
    '(amd, ryzen) 1700 -1700X.xlsx',
    '(amd, ryzen) 1700X.xlsx',
    '(amd, ryzen) 1800X.xlsx',
    '(amd, ryzen) 2600 -2600X.xlsx',
    '(amd, ryzen) 2600X.xlsx',
    '(amd, ryzen) 2700 -2700X.xlsx',
    '(amd, ryzen) 2700X.xlsx',

    'i7 (2600k, 2700k).xlsx',
    'i7 (860, 970, 870k, 880).xlsx',
    'i7 (920, 930, 940, 950, 960, 965, 975).xlsx',
    'i7 (970, 980, 980X, 990X).xlsx',
    'i7 10700k.xlsx',
    'i7 3770k.xlsx',
    'i7 4770k.xlsx',
    'i7 4790k.xlsx',
    'i7 6700k.xlsx',
    'i7 7700k.xlsx',
    'i7 8700k.xlsx',
    'i7 9700k.xlsx',
    'i9 10900k.xlsx',
    'i9 9900k.xlsx',

    'b550.xlsx',
    'x570.xlsx',

    'rtx 2060 -super.xlsx',
    'rtx 2060 super.xlsx',
    'rtx 2070 -super.xlsx',
    'rtx 2070 super.xlsx',
    'rtx 2080 -super -ti.xlsx',
    'rtx 2080 super -ti.xlsx',
    'rtx 2080 ti -super.xlsx',

    'ASUS Dark Hero.xlsx',

    '5600X UK.xlsx',
    '5800X UK.xlsx',
    '5900X UK.xlsx',
    '5950X UK.xlsx',

    '1080 Ti.xlsx',
    'gtx 1060.xlsx',
    'gtx 1070 -Ti.xlsx',
    'gtx 1070 Ti.xlsx',
    'gtx 1080 -Ti -1080p.xlsx',

    'rtx 2060 -super.xlsx',
    'rtx 2060 super.xlsx',
    'rtx 2070 -super.xlsx',
    'rtx 2070 super.xlsx',
    'rtx 2080 -super -ti.xlsx',
    'rtx 2080 super -ti.xlsx',
    'rtx 2080 ti -super.xlsx',
    'RTX 3060 UK.xlsx',
    'RTX 3070 UK.xlsx',
    'RTX 3080 UK.xlsx',
    'RTX 3090 UK.xlsx',
    'rx 5500 xt.xlsx',
    'rx 5600 xt.xlsx',
    'rx 5700 -xt.xlsx',
    'rx 5700 xt.xlsx',
    'RX 6800 -XT UK.xlsx',
    'RX 6800 XT UK.xlsx',
    'RX 6900 UK.xlsx',

    'ps4 -pro -repair -box -broken -parts -bad.xlsx',
    'PS4 pro -repair -box -broken -parts -bad.xlsx',

    'PS5 -digital UK.xlsx',
    'PS5 -digital.xlsx',
    'PS5 Digital UK.xlsx',
    'PS5 Digital.xlsx',

    'xbox one s -pro -series -repair -box -broken -parts -bad.xlsx',
    'xbox one x -repair -series -box -broken -parts -bad.xlsx',
    'Xbox Series S UK.xlsx',
    'Xbox Series S.xlsx',
    'Xbox Series X UK.xlsx',
    'Xbox Series X.xlsx',

    'titan x -xp.xlsx',
    '980 Ti.xlsx',
    'titan xp.xlsx',
    '980 -ti.xlsx',
    '970.xlsx',
    '960.xlsx',
    '950.xlsx'

    'case -pi.xlsx',
    'cooler.xlsx',
    'ddr4 -laptop -rdimm -ecc -lrdimm.xlsx',
    'power.xlsx',
    'ssd -portable -nas -external.xlsx',
]

files = [
    'ASUS Dark Hero.xlsx',

    'RTX 3080.xlsx',
    'RTX 3070.xlsx',
    'RTX (3060 Ti, 3060Ti).xlsx',
    'RTX 3060 -Ti -3060ti.xlsx',

    'RX 6900.xlsx',
    'RX 6800 -XT.xlsx',
    'RX 6800 XT.xlsx',

    '5600X.xlsx',
    '5800X.xlsx',
    '5900X.xlsx',
    '5950X.xlsx',

    'PS5 -digital.xlsx',
    'PS5 Digital.xlsx',
]

for f in os.listdir(directory):
    name, ext = os.path.splitext(f)
    if ext == '.xlsx':
        1 == 1
for f in files:
    if 1 == 1:
        print(f)
        df = pd.read_excel('Spreadsheets/' + f, index_col=0, engine='openpyxl')

        dup_df = df.copy(deep=True)
        tested = []
        for index, row in df.iterrows():
            if row['Ignore'] != 1 and row['Multi Listing'] == 1 and row['Link'] not in tested:
                curr_time = datetime.datetime.now()
                tested.append(row['Link'])
                cnt = df[(df['Link'] == row['Link'])]['Link'].count()
                tot_sold = df[(df['Link'] == row['Link'])]['Quantity'].sum()

                link_df = df[(df['Link'] == row['Link'])]
                sold_df = link_df[['Sold Date', 'Sold Datetime', 'Quantity']]

                # There's really no point in checking if it's greater than 90 days ago, eBay won't have that data public anymore
                most_recent = sold_df['Sold Date'].max()
                comp_date = datetime.datetime.now() - datetime.timedelta(days=90)

                if most_recent >= comp_date:
                    quantity_sold, sold_list = get_multi_data(row['Link'], e_vars, sleep_len=5)

                    print(cnt, quantity_sold, len(sold_list), row['Link'])

                    if len(sold_list) > 0:
                        for sindex, srow in sold_df.iterrows():
                            if not df[['Sold Date', 'Sold Datetime']].isin(
                                    {'Sold Date': [srow['Sold Date']], 'Sold Datetime': [srow['Sold Datetime']]}).all(
                                    axis='columns').any():
                                print('added to sold_list')
                                sold_list.append(['', srow['Quantity'], srow['Sold Date'], srow['Sold Datetime']])

                        index_names = dup_df[dup_df['Link'] == row['Link']].index
                        dup_df.drop(index_names, inplace=True)

                        sale_price = row['Price']
                        tot_sale_quant = 0
                        for sale in sold_list:
                            if sale[0]:
                                sale_price = sale[0]

                            df_new = {'Title'          : row['Title'], 'Brand': row['Brand'],
                                      'Model'          : row['Model'],
                                      'description'    : row['description'], 'Price': sale_price,
                                      'Shipping'       : row['Shipping'],
                                      'Total Price'    : sale_price + row['Shipping'], 'Sold Date': sale[2],
                                      'Sold Datetime'  : sale[3], 'Link': row['Link'], 'Seller': row['Seller'],
                                      'Multi Listing'  : row['Multi Listing'], 'Quantity': sale[1],
                                      'Seller Feedback': row['Seller Feedback'], 'Ignore': 0,
                                      'Store'          : row['Store'],
                                      'City'           : row['City'], 'State': row['State'],
                                      'Country'        : row['Country'], 'Sold Scrape Datetime': curr_time}
                            tot_sale_quant += sale[1]
                            dup_df = dup_df.append(df_new, ignore_index=True)

                        print(cnt, tot_sale_quant, quantity_sold, len(sold_list), row['Link'])

                        if tot_sale_quant < quantity_sold:
                            # On some listings the offer list has scrolled off (only shows latest 100) despite some beint accepted
                            # In order to not lose the data I just shove everything into one entry, assuming the regular price
                            # Not perfect, but no great alternatives
                            # I set it to be ignored because it can really screw with analytics
                            # Ignore code set to "2" to differentiate it from others
                            # The main issue here of course is that now I'm assigning a bunch of sales to a semi-arbitrary date
                            df_new = {'Title'               : row['Title'], 'Brand': row['Brand'],
                                      'Model'               : row['Model'],
                                      'description'         : row['description'], 'Price': sale_price,
                                      'Shipping'            : row['Shipping'],
                                      'Total Price'         : sale_price + row['Shipping'],
                                      'Sold Date'           : row['Sold Date'], 'Sold Datetime': row['Sold Datetime'],
                                      'Link'                : row['Link'], 'Seller': row['Seller'],
                                      'Quantity'            : quantity_sold - tot_sale_quant,
                                      'Multi Listing'       : row['Multi Listing'],
                                      'Seller Feedback'     : row['Seller Feedback'],
                                      'Ignore'              : 2, 'Store': row['Store'], 'City': row['City'],
                                      'State'               : row['State'], 'Country': row['Country'],
                                      'Sold Scrape Datetime': curr_time}

                            dup_df = dup_df.append(df_new, ignore_index=True)

                    dup_df.to_excel('MultiSpreadsheets/' + f, engine='openpyxl')
        dup_df.to_excel('MultiSpreadsheets/' + f, engine='openpyxl')
