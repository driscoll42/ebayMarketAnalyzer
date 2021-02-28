# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import datetime
import random
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_quantity_hist(sold_hist_url, sold_list, sleep_len=0.4, verbose=False, debug=False):
    time.sleep(
            sleep_len * random.uniform(0, 1))  # eBays servers will kill your connection if you hit them too frequently
    try:
        source = requests.get(sold_hist_url, timeout=10).text
        soup = BeautifulSoup(source, 'lxml')

        # items = soup.find_all('tr')

        table = soup.find_all('table', attrs={'border': '0', 'cellpadding': '5', 'cellspacing': '0',
                                              'width' : '100%'})

        purchas_hist = table[0]

        trs = purchas_hist.find_all('tr')

        for r in trs:
            tds = r.find_all('td')
            if len(tds) > 1:
                # buyer = tds[1].text
                try:
                    price = float(re.sub(r'[^\d.]+', '', tds[2].text))
                except Exception as e:
                    if debug or verbose: print('get_quantity_hist-price', e, sold_hist_url)
                    price = ''
                quantity = int(tds[3].text)
                sold_date = tds[4].text.split()[0]
                sold_time = tds[4].text.split()[1]

                try:
                    sold_datetime = datetime.datetime.strptime(sold_date + ' ' + sold_time, '%b-%d-%y %H:%M:%S')
                    sold_datetime = sold_datetime.replace(second=0, microsecond=0)

                    sold_date = datetime.datetime.strptime(tds[4].text.split()[0], '%b-%d-%y')
                except Exception as e:
                    sold_datetime = datetime.datetime.strptime(sold_date + ' ' + sold_time, '%d-%b-%y %H:%M:%S')
                    sold_datetime = sold_datetime.replace(second=0, microsecond=0)

                    sold_date = datetime.datetime.strptime(tds[4].text.split()[0], '%d-%b-%y')
                if verbose: print(price, quantity, sold_datetime)

                sold_list.append([price, quantity, sold_date, sold_datetime])

        offer_hist = table[1]

        trs = offer_hist.find_all('tr')

        for r in trs:
            tds = r.find_all('td', )
            if len(tds) > 1:
                try:
                    # buyer = tds[1].text
                    accepted = tds[2].text
                    quantity = int(tds[3].text)
                    sold_date = tds[4].text.split()[0]
                    sold_time = tds[4].text.split()[1]

                    try:
                        sold_datetime = datetime.datetime.strptime(sold_date + ' ' + sold_time, '%b-%d-%y %H:%M:%S')
                        sold_datetime = sold_datetime.replace(second=0, microsecond=0)

                        sold_date = datetime.datetime.strptime(tds[4].text.split()[0], '%b-%d-%y')
                    except Exception as e:
                        sold_datetime = datetime.datetime.strptime(sold_date + ' ' + sold_time, '%d-%b-%y %H:%M:%S')
                        sold_datetime = sold_datetime.replace(second=0, microsecond=0)

                        sold_date = datetime.datetime.strptime(tds[4].text.split()[0], '%d-%b-%y')

                    if accepted == 'Accepted':
                        if verbose: print(accepted, quantity, sold_datetime)
                        sold_list.append(['', quantity, sold_date, sold_datetime])
                except Exception as e:
                    accepted = 'None'
                    if debug or verbose: print('get_quantity_hist-trs', e, sold_hist_url)
    except Exception as e:
        if debug or verbose: print('get_quantity_hist', e, sold_hist_url)
    return sold_list


def get_multi_data(item_link, sleep_len=1, verbose=False, debug=False):
    sold_list = []
    quantity_sold = 0
    try:
        time.sleep(10 + sleep_len * random.uniform(0, 1))
        source = requests.get(item_link).text
        soup = BeautifulSoup(source, 'lxml')

        try:
            iitem = soup.find_all('a', attrs={'class': 'vi-txt-underline'})
            quantity_sold = int(iitem[0].text.split()[0])

            sold_hist_url = iitem[0]['href']
            sold_list = get_quantity_hist(sold_hist_url, sold_list, sleep_len=sleep_len,
                                          verbose=verbose)

        except Exception as e:
            if debug or verbose: print('ebay_scrape-seller-1', e, item_link)
            try:
                oitems = soup.find_all('a',
                                       attrs={'class': 'nodestar-item-card-details__view-link'})
                orig_link = oitems[0]['href']

                time.sleep(10 + sleep_len * random.uniform(0, 1))
                source = requests.get(orig_link).text
                soup = BeautifulSoup(source, 'lxml')

                try:
                    nnitems = soup.find_all('a', attrs={'class': 'vi-txt-underline'})
                    quantity_sold = int(nnitems[0].text.split()[0])

                    if quantity_sold > 1:
                        sold_hist_url = nnitems[0]['href']
                        sold_list = get_quantity_hist(sold_hist_url, sold_list, sleep_len=sleep_len,
                                                      verbose=verbose)

                except Exception as e:
                    if debug or verbose: print('ebay_scrape-nnitems', e, orig_link)
            except Exception as e:
                if debug or verbose: print('ebay_scrape-oitems-2', e, item_link)
    except Exception as e:
        if debug or verbose: print('ebay_scrape-oitems-1', e, item_link)
    return quantity_sold, sold_list


files = [

    'RTX 3090 -image -jpeg -img -picture -pic -jpg.xlsx',

    'RX 6900 -image -jpeg -img -picture -pic -jpg.xlsx',

    'RX 6800 -XT -image -jpeg -img -picture -pic -jpg.xlsx',
    'RX 6800 XT -image -jpeg -img -picture -pic -jpg.xlsx',

    'RTX 3060 -image -jpeg -img -picture -pic -jpg.xlsx',
    'RTX 3070 -image -jpeg -img -picture -pic -jpg.xlsx',
    'RTX 3080 -image -jpeg -img -picture -pic -jpg.xlsx',

    '5600X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5800X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5900X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5950X -image -jpeg -img -picture -pic -jpg.xlsx',

    '3950X -image -jpeg -img -picture -pic -jpg.xlsx',
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

    'ASUS Dark Hero -image -jpeg -img -picture -pic -jpg.xlsx',

    '5600X -image -jpeg -img -picture -pic -jpg UK.xlsx',
    '5800X -image -jpeg -img -picture -pic -jpg UK.xlsx',
    '5900X -image -jpeg -img -picture -pic -jpg UK.xlsx',
    '5950X -image -jpeg -img -picture -pic -jpg UK.xlsx',

    '1080 Ti -image -jpeg -img -picture -pic -jpg.xlsx',
    'gtx 1060 -image -jpeg -img -picture -pic -jpg.xlsx',
    'gtx 1070 -Ti -image -jpeg -img -picture -pic -jpg.xlsx',
    'gtx 1070 Ti -image -jpeg -img -picture -pic -jpg.xlsx',
    'gtx 1080 -Ti -image -jpeg -img -picture -pic -jpg -1080p.xlsx',

    'rtx 2060 -super.xlsx',
    'rtx 2060 super.xlsx',
    'rtx 2070 -super.xlsx',
    'rtx 2070 super.xlsx',
    'rtx 2080 -super -ti.xlsx',
    'rtx 2080 super -ti.xlsx',
    'rtx 2080 ti -super.xlsx',
    'RTX 3060 -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RTX 3070 -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RTX 3080 -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RTX 3090 -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'rx 5500 xt.xlsx',
    'rx 5600 xt.xlsx',
    'rx 5700 -xt.xlsx',
    'rx 5700 xt.xlsx',
    'RX 6800 -XT -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RX 6800 XT -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RX 6900 -image -jpeg -img -picture -pic -jpg UK.xlsx',

    'ps4 -pro -repair -box -broken -parts -bad.xlsx',
    'PS4 pro -repair -box -broken -parts -bad.xlsx',

    'PS5 -digital -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'PS5 -digital -image -jpeg -img -picture -pic -jpg.xlsx',
    'PS5 Digital -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'PS5 Digital -image -jpeg -img -picture -pic -jpg.xlsx',

    'xbox one s -pro -series -repair -box -broken -parts -bad.xlsx',
    'xbox one x -repair -series -box -broken -parts -bad.xlsx',
    'Xbox Series S -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'Xbox Series S -image -jpeg -img -picture -pic -jpg.xlsx',
    'Xbox Series X -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'Xbox Series X -image -jpeg -img -picture -pic -jpg.xlsx',

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

    '5600X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5800X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5900X -image -jpeg -img -picture -pic -jpg.xlsx',
    '5950X -image -jpeg -img -picture -pic -jpg.xlsx',

    '3950X -image -jpeg -img -picture -pic -jpg.xlsx',
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
]

for f in files:
    print(f)
    df = pd.read_excel('Spreadsheets/' + f, index_col=0, engine='openpyxl')

    dup_df = df.copy(deep=True)
    tested = []
    for index, row in df.iterrows():
        if row['Ignore'] != 1 and row['Multi Listing'] == 1 and row['Link'] not in tested:
            tested.append(row['Link'])
            cnt = df[(df['Link'] == row['Link'])]['Link'].count()
            tot_sold = df[(df['Link'] == row['Link'])]['Quantity'].sum()

            link_df = df[(df['Link'] == row['Link'])]
            sold_df = link_df[['Sold Date', 'Sold Datetime', 'Quantity']]

            if cnt < tot_sold:
                quantity_sold, sold_list = get_multi_data(row['Link'], sleep_len=15)

                print(cnt, quantity_sold, len(sold_list), row['Link'])

                if len(sold_list) > 0:
                    for sindex, srow in sold_df.iterrows():
                        if not df[['Sold Date', 'Sold Datetime']].isin(
                                {'Sold Date': [srow['Sold Date']], 'Sold Datetime': [srow['Sold Datetime']]}).all(
                                axis='columns').any():
                            print('added to sold_list')
                            print(sold_list)
                            sold_list.append(['', srow['Quantity'], srow['Sold Date'], srow['Sold Datetime']])
                            print(sold_list)

                    index_names = dup_df[dup_df['Link'] == row['Link']].index
                    dup_df.drop(index_names, inplace=True)

                    sale_price = row['Price']
                    tot_sale_quant = 0
                    for sale in sold_list:
                        if sale[0]:
                            sale_price = sale[0]

                        df_new = {'Title'          : row['Title'], 'Brand': row['Brand'], 'Model': row['Model'],
                                  'description'    : row['description'], 'Price': sale_price,
                                  'Shipping'       : row['Shipping'],
                                  'Total Price'    : sale_price + row['Shipping'], 'Sold Date': sale[2],
                                  'Sold Datetime'  : sale[3], 'Link': row['Link'], 'Seller': row['Seller'],
                                  'Multi Listing'  : row['Multi Listing'], 'Quantity': sale[1],
                                  'Seller Feedback': row['Seller Feedback'], 'Ignore': 0, 'Store': row['Store']}
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
                        df_new = {'Title'        : row['Title'], 'Brand': row['Brand'], 'Model': row['Model'],
                                  'description'  : row['description'], 'Price': sale_price, 'Shipping': row['Shipping'],
                                  'Total Price'  : sale_price + row['Shipping'], 'Sold Date': row['Sold Date'],
                                  'Sold Datetime': row['Sold Datetime'], 'Link': row['Link'], 'Seller': row['Seller'],

                                  'Quantity'     : quantity_sold - tot_sale_quant,

                                  'Multi Listing': row['Multi Listing'], 'Seller Feedback': row['Seller Feedback'],
                                  'Ignore'       : 2, 'Store': row['Store']}

                        dup_df = dup_df.append(df_new, ignore_index=True)

                dup_df.to_excel('MultiSpreadsheets/' + f, engine='openpyxl')
    dup_df.to_excel('MultiSpreadsheets/' + f, engine='openpyxl')
