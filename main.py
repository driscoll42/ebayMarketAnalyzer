# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import os
import pathlib
import random
import re
import time
from datetime import datetime, timedelta
from typing import List, Union

import numpy as np
import pandas as pd
import requests
import requests_cache
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from classes import ebayVariables
from plotting import ebay_plot
from plotting import plot_profits


# XML Formatter: https://jsonformatter.org/xml-formatter

def get_quantity_hist(sold_hist_url: str,
                      sold_list: List[Union[float, int, datetime, datetime]],
                      adapter: requests,
                      e_vars: ebayVariables) -> List[Union[float, int, datetime, datetime]]:
    """

    Parameters
    ----------
    sold_hist_url :
    sold_list :
    adapter :
    e_vars :

    Returns
    -------

    """
    time.sleep(
            e_vars.sleep_len * random.uniform(0,
                                              1))  # eBays servers will kill your connection if you hit them too frequently
    try:
        with requests_cache.disabled():  # We don't want to cache all the calls into the individual listings, they'll never be repeated
            source = adapter.get(sold_hist_url, timeout=10).text
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
                    if e_vars.debug or e_vars.verbose: print('get_quantity_hist-price', e, sold_hist_url)
                    price = ''
                quantity = int(tds[3].text)
                sold_date = tds[4].text.split()[0]
                sold_time = tds[4].text.split()[1]

                try:
                    sold_date = datetime.strptime(sold_date, '%b-%d-%y')
                except Exception as e:
                    sold_date = datetime.strptime(sold_date, '%d-%b-%y')

                sold_time = datetime.strptime(sold_time, '%H:%M:%S').time()
                sold_time = sold_time.replace(second=0, microsecond=0)
                sold_datetime = datetime.combine(sold_date, sold_time)

                if e_vars.verbose: print(price, quantity, sold_datetime)

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
                        sold_date = datetime.strptime(sold_date, '%b-%d-%y')
                    except Exception as e:
                        sold_date = datetime.strptime(sold_date, '%d-%b-%y')

                    sold_time = datetime.strptime(sold_time, '%H:%M:%S').time()
                    sold_time = sold_time.replace(second=0, microsecond=0)
                    sold_datetime = datetime.combine(sold_date, sold_time)

                    if accepted == 'Accepted':
                        if e_vars.verbose: print(accepted, quantity, sold_datetime)
                        sold_list.append(['', quantity, sold_date, sold_datetime])
                except Exception as e:
                    accepted = 'None'
                    if e_vars.debug or e_vars.verbose: print('get_quantity_hist-trs', e, sold_hist_url)
    except Exception as e:
        if e_vars.debug or e_vars.verbose: print('get_quantity_hist', e, sold_hist_url)
    return sold_list


def ebay_scrape(base_url: str,
                df: pd.DataFrame,
                adapter: requests,
                e_vars: ebayVariables,
                min_date: datetime = datetime(2020, 1, 1)) -> pd.DataFrame:
    """

    Parameters
    ----------
    base_url :
    df :
    adapter :
    e_vars :
    min_date :

    Returns
    -------

    """
    days_before_date = datetime.today()
    days_before_date = days_before_date.replace(hour=0, minute=0, second=0, microsecond=0)
    comp_date = days_before_date - timedelta(days=e_vars.days_before)

    for x in range(1, 5):

        time.sleep(
                e_vars.sleep_len * random.uniform(0,
                                                  1))  # eBays servers will kill your connection if you hit them too frequently
        url = f"{base_url}{x}"

        if x == 4:
            source = adapter.get(url, timeout=10).text
        else:
            with requests_cache.disabled():  # We don't want to cache all the calls into the individual listings, they'll never be repeated
                source = adapter.get(url, timeout=10).text
        soup = BeautifulSoup(source, 'lxml')
        items = soup.find_all('li', attrs={'class': 's-item'})

        time_break = False

        if e_vars.verbose: print(x, len(items), url)

        for n, item in enumerate(items):
            if n > 0:
                try:
                    item_link = item.find('a', class_='s-item__link')['href']
                except Exception as e:
                    item_link = 'None'
                    if e_vars.debug or e_vars.verbose: print('ebay_scrape-item_link', e)

                if e_vars.verbose: print('URL:', item_link)

                try:
                    currentYear = datetime.now().year
                    currentMonth = datetime.now().month

                    orig_item_datetime = f"{currentYear} {item.find('span', class_='s-item__endedDate').text}"
                    if e_vars.country == 'UK':
                        item_datetime = datetime.strptime(orig_item_datetime, '%Y %d-%b %H:%M')
                    else:
                        item_datetime = datetime.strptime(orig_item_datetime, '%Y %b-%d %H:%M')

                    # When we run early in the year
                    if currentMonth < 6 and item_datetime.month > 6:
                        last_year = currentYear - 1
                        item_datetime = item_datetime.replace(year=last_year)

                    item_date = item_datetime.replace(hour=0, minute=0)
                    days_before_date = min(item_date, days_before_date)

                except Exception as e:
                    if e_vars.debug or e_vars.verbose: print('ebay_scrape-orig_item_datetime', e, item_link)
                    try:
                        orig_item_datetime = item.find('span', class_='s-item__title--tagblock__COMPLETED').text
                        orig_item_datetime = orig_item_datetime.replace('Sold item', '').replace('Sold', '').strip()
                        item_datetime = orig_item_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

                        item_date = datetime.strptime(orig_item_datetime, '%d %b %Y')
                        item_date = item_date.replace(hour=0, minute=0, second=0, microsecond=0)
                        days_before_date = min(item_date, days_before_date)

                    except Exception as e:
                        item_datetime = 'None'
                        item_date = 'None'
                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-item_datetime', e, item_link)

                if days_before_date < comp_date or days_before_date < min_date:
                    time_break = True
                    break

                if e_vars.verbose: print('Date:', item_date)
                if e_vars.verbose: print('Datetime:', item_datetime)
                if e_vars.verbose: print(
                        not df[['Link', 'Sold Datetime']].isin(
                                {'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                                axis='columns').any())

                # Only need to add new records
                if not df[['Link', 'Sold Datetime']].isin({'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                        axis='columns').any():

                    try:
                        item_title = item.find('h3', class_='s-item__title').text
                    except Exception as e:
                        item_title = 'None'
                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-item_title', e, item_link)

                    if e_vars.verbose: print('Title:', item_title)

                    try:
                        item_desc = item.find('div', class_='s-item__subtitle').text
                    except Exception as e:
                        item_desc = 'None'
                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-item_desc', e, item_link)
                    if e_vars.verbose: print('Desc: ', item_desc)

                    try:
                        item_price = item.find('span', class_='s-item__price').text
                        item_price = float(re.sub(r'[^\d.]+', '', item_price))
                    except Exception as e:
                        item_price = -1
                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-item_price', e, item_link)
                    if e_vars.verbose: print('Price:', item_price)

                    try:
                        item_shipping = item.find('span', class_='s-item__shipping s-item__logisticsCost').text
                        if item_shipping.upper().find("FREE") == -1:
                            item_shipping = float(re.sub(r'[^\d.]+', '', item_shipping))
                        else:
                            item_shipping = 0
                    except Exception as e:
                        item_shipping = 0
                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-item_shipping', e, item_link)

                    if e_vars.verbose: print('Shipping:', item_shipping)

                    try:
                        item_tot = item_price + item_shipping
                    except Exception as e:
                        item_tot = -1
                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-item_tot', e, item_link)

                    if e_vars.verbose: print('Total:', item_tot)

                    quantity_sold = 1
                    sold_list = []
                    multi_list = False
                    store = False
                    city, state, country_name = '', '', ''

                    if e_vars.feedback or e_vars.quantity_hist:
                        try:
                            time.sleep(e_vars.sleep_len * random.uniform(0, 1))
                            with requests_cache.disabled():  # We don't want to cache all the calls into the individual listings, they'll never be repeated
                                source = adapter.get(item_link).text
                            soup = BeautifulSoup(source, 'lxml')

                            try:
                                seller = soup.find_all('span', attrs={'class': 'mbg-nw'})
                                seller = seller[0].text

                                seller_fb = soup.find_all('span', attrs={'class': 'mbg-l'})
                                seller_fb = int(seller_fb[0].find('a').text)

                                store_id = soup.find_all('div', attrs={'id': 'storeSeller'})

                                if len(store_id[0].text) > 0:
                                    store = True

                                try:
                                    loc = soup.find('div', attrs={'class': 'iti-eu-bld-gry'})
                                    loc = loc.find('span').text.split(',')
                                    city, state, country_name = loc[0], loc[1], loc[2]
                                    if len(loc) == 2:
                                        city, state, country_name = loc[0], '', loc[1]
                                    elif len(loc) == 3:
                                        city, state, country_name = loc[0], loc[1], loc[2]

                                except Exception as e:
                                    if e_vars.debug or e_vars.verbose: print('ebay_scrape-seller-1', e, item_link)
                                    loc_2 = soup.find('div', attrs={'class': 'vi-wp vi-VR-cvipCntr1'})
                                    loc_2 = loc_2.find_all('tr', attrs={'class': 'vi-ht20'})
                                    for l in loc_2:
                                        if l.text.find('Item location:') > 0:
                                            i_loc = l.find_all('div', attrs={'class': 'u-flL'})
                                            loc_text = i_loc[1].text.split(',')
                                            if len(loc_text) == 2:
                                                city, state, country_name = loc_text[0], '', loc_text[1]
                                            elif len(loc_text) == 3:
                                                city, state, country_name = loc_text[0], loc_text[1], loc_text[2]
                                            break

                                try:
                                    iitem = soup.find_all('a', attrs={'class': 'vi-txt-underline'})
                                    quantity_sold = int(iitem[0].text.split()[0])
                                    multi_list = True

                                    if e_vars.quantity_hist:
                                        sold_hist_url = iitem[0]['href']
                                        sold_list = get_quantity_hist(sold_hist_url, sold_list, adapter=adapter,
                                                                      e_vars=e_vars)

                                except Exception as e:
                                    sold_hist_url = ''
                                    if e_vars.debug or e_vars.verbose: print('ebay_scrape-iitem', e, item_link)

                            except Exception as e:
                                if e_vars.debug or e_vars.verbose: print('ebay_scrape-seller-1', e, item_link)
                                try:
                                    oitems = soup.find_all('a',
                                                           attrs={'class': 'nodestar-item-card-details__view-link'})
                                    orig_link = oitems[0]['href']

                                    time.sleep(e_vars.sleep_len * random.uniform(0, 1))
                                    with requests_cache.disabled():  # We don't want to cache all the calls into the individual listings, they'll never be repeated
                                        source = adapter.get(orig_link).text
                                    soup = BeautifulSoup(source, 'lxml')

                                    seller = soup.find_all('span', attrs={'class': 'mbg-nw'})
                                    seller = seller[0].text

                                    seller_fb = soup.find_all('span', attrs={'class': 'mbg-l'})
                                    seller_fb = int(seller_fb[0].find('a').text)

                                    store_id = soup.find_all('div', attrs={'id': 'storeSeller'})

                                    if len(store_id[0].text) > 0:
                                        store = True

                                    try:

                                        loc = soup.find('div', attrs={'class': 'iti-eu-bld-gry'})
                                        loc = loc.find('span').text.split(',')
                                        if len(loc) == 2:
                                            city, state, country_name = loc[0], '', loc[1]
                                        elif len(loc) == 3:
                                            city, state, country_name = loc[0], loc[1], loc[2]
                                    except Exception as e:
                                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-vi-wp', e, item_link)
                                        loc = soup.find('div', attrs={'class': 'vi-wp vi-VR-cvipCntr1'})
                                        loc = loc.find_all('tr', attrs={'class': 'vi-ht20'})

                                        for l in loc:
                                            if l.text.find('Item location:') > 0:
                                                i_loc = l.find_all('div', attrs={'class': 'u-flL'})
                                                loc_text = i_loc[1].text.split(',')
                                                city, state, country_name = loc_text[0], loc_text[1], loc_text[2]
                                                if len(loc_text) == 2:
                                                    city, state, country_name = loc_text[0], '', loc_text[1]
                                                elif len(loc_text) == 3:
                                                    city, state, country = loc_text[0], loc_text[1], loc_text[2]
                                                break

                                    try:
                                        nnitems = soup.find_all('a', attrs={'class': 'vi-txt-underline'})
                                        quantity_sold = int(nnitems[0].text.split()[0])
                                        multi_list = True

                                        if e_vars.quantity_hist and quantity_sold > 1:
                                            sold_hist_url = nnitems[0]['href']
                                            sold_list = get_quantity_hist(sold_hist_url, sold_list, adapter=adapter,
                                                                          e_vars=e_vars)

                                    except Exception as e:
                                        sold_hist_url = ''
                                        if e_vars.debug or e_vars.verbose: print('ebay_scrape-nnitems', e, item_link)
                                except Exception as e:
                                    # print(url)
                                    # print(e)
                                    seller = 'None'
                                    seller_fb = 'None'
                                    if e_vars.debug or e_vars.verbose: print('ebay_scrape-oitems-2', e, item_link)
                        except Exception as e:
                            seller = 'None'
                            seller_fb = 'None'
                            if e_vars.debug or e_vars.verbose: print('ebay_scrape-oitems-1', e, item_link)
                    else:
                        seller = 'None'
                        seller_fb = 'None'

                    if e_vars.verbose: print('Seller: ', seller)
                    if e_vars.verbose: print('Seller Feedback: ', seller_fb)
                    if e_vars.verbose: print('Quantity Sold: ', quantity_sold)

                    brand = ''
                    title = item_title

                    for b in e_vars.brand_list:
                        if b.upper() in title.upper():
                            b = b.replace(' ', '')
                            brand = b

                    model = ''
                    for m in e_vars.model_list:
                        if m[0].upper() in title.upper():
                            model = m[0].replace(' ', '')
                            brand = m[1].replace(' ', '')
                    if e_vars.verbose: print('Brand', brand)
                    if e_vars.verbose: print('Model', model)

                    sold_list = np.array(sold_list)

                    ignor_val = 0
                    if item_desc.upper().find("PARTS ONLY") >= 0 or item_desc.upper().find("BENT PIN") >= 0:
                        ignor_val = 1

                    if sold_list.size == 0:
                        try:
                            cap_sum = df[(df['Link'] == item_link)]['Quantity'].sum()
                        except Exception as e:
                            cap_sum = 0
                            if e_vars.debug or e_vars.verbose: print('ebay_scrape-cap_sum', e, item_link)

                        df__new = {'Title'          : item_title, 'Brand': brand, 'Model': model,
                                   'description'    : item_desc, 'Price': item_price,
                                   'Shipping'       : item_shipping, 'Total Price': item_tot, 'Sold Date': item_date,
                                   'Sold Datetime'  : item_datetime, 'Link': item_link, 'Seller': seller,
                                   'Multi Listing'  : multi_list, 'Quantity': quantity_sold - cap_sum,
                                   'Seller Feedback': seller_fb,
                                   'Ignore'         : ignor_val, 'Store': store, 'City': city, 'State': state,
                                   'Country'        : country_name}

                        if e_vars.verbose: print(df__new)

                        if not df[['Link', 'Sold Datetime']].isin(
                                {'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                                axis='columns').any() and item_tot > 0 and (quantity_sold - cap_sum) > 0:
                            df = df.append(df__new, ignore_index=True)
                            # Considered processing as went along, more efficient to just remove duplicates in postprocessing
                    else:
                        for sale in sold_list:
                            # When scraping multilistings they can go back months, years even which really throws off graphs
                            # Generally best to just ignore values far in the past
                            if sale[2] < datetime.now() - timedelta(days=90):
                                ignor_val = 1
                            sale_price = item_price
                            if sale[0]:
                                sale_price = sale[0]
                            df__new = {'Title'        : item_title, 'Brand': brand, 'Model': model,
                                       'description'  : item_desc, 'Price': sale_price,
                                       'Shipping'     : item_shipping, 'Total Price': item_tot, 'Sold Date': sale[2],
                                       'Sold Datetime': sale[2], 'Link': item_link, 'Seller': seller,
                                       'Multi Listing': multi_list, 'Quantity': sale[1], 'Seller Feedback': seller_fb,
                                       'Ignore'       : ignor_val, 'Store': store, 'City': city, 'State': state,
                                       'Country'      : country_name}

                            # There's a chance when we get to multiitem listings we'd be reinserting data, this is to prevent it
                            if not df[['Link', 'Sold Datetime']].isin(
                                    {'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                                    axis='columns').any() and item_tot > 0:
                                df = df.append(df__new, ignore_index=True)

                        tot_sale_quant = np.sum(sold_list[:, 1])

                        if tot_sale_quant < quantity_sold:
                            # On some listings the offer list has scrolled off (only shows latest 100) despite some beint accepted
                            # In order to not lose the data I just shove everything into one entry, assuming the regular price
                            # Not perfect, but no great alternatives
                            # The main issue here of course is that now I'm assigning a bunch of sales to a semi-arbitrary date
                            df__new = {'Title'        : item_title, 'Brand': brand, 'Model': model,
                                       'description'  : item_desc, 'Price': item_price,
                                       'Shipping'     : item_shipping, 'Total Price': item_tot,
                                       'Sold Date'    : item_date, 'Sold Datetime': item_datetime, 'Link': item_link,
                                       'Seller'       : seller, 'Quantity': quantity_sold - tot_sale_quant,
                                       'Multi Listing': multi_list, 'Seller Feedback': seller_fb, 'Ignore': 2,
                                       'Store'        : store, 'City': city, 'State': state, 'Country': country_name}
                            # There's a chance when we get to multiitem listings we'd be reinserting data, this is to prevent it
                            if not df[['Link', 'Sold Datetime', 'Quantity']].isin(
                                    {'Link'    : [item_link], 'Sold Datetime': [item_datetime],
                                     'Quantity': [quantity_sold - tot_sale_quant]}).all(
                                    axis='columns').any() and item_tot > 0:
                                df = df.append(df__new, ignore_index=True)
        if e_vars.country == 'UK' and len(items) < 193:
            break
        elif len(items) < 201:
            break
        elif time_break:
            break

    return df


def ebay_search(query: str,
                e_vars: ebayVariables,
                queryexclusions: List[str] = [],
                msrp: int = 0,
                min_price: int = 0,
                max_price: int = 10000,
                min_date: datetime = datetime.now() - timedelta(days=90)) -> pd.DataFrame:
    """

    Parameters
    ----------
    query :
    e_vars :
    queryexclusions :
    msrp :
    min_price :
    max_price :
    min_date :

    Returns
    -------

    """
    start = time.time()
    print(query)

    start_datetime = datetime.today().strftime("%Y%m%d%H%M%S")
    # https://realpython.com/caching-external-api-requests/
    curr_path = pathlib.Path(__file__).parent.absolute()
    print(curr_path)
    cache_name = f"{curr_path}\\cache_{start_datetime}"

    requests_cache.install_cache(cache_name, backend='sqlite', expire_after=300)
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

    # https://stackoverflow.com/questions/35807605/create-a-file-if-it-doesnt-exist?lq=1
    filename = query + e_vars.extra_title_text + '.xlsx'

    try:
        df = pd.read_excel('Spreadsheets/' + filename, index_col=0, engine='openpyxl')
        df = df.astype({'Brand': 'object'})
        df = df.astype({'Model': 'object'})

    except Exception as e:
        # if file does not exist, create it
        dict = {'Title'      : [], 'Brand': [], 'Model': [], 'description': [], 'Price': [], 'Shipping': [],
                'Total Price': [],
                'Sold Date'  : [], 'Sold Datetime': [], 'Quantity': [], 'Multi Listing': [],
                'Seller'     : [], 'Seller Feedback': [], 'Link': [], 'Store': [], 'Ignore': [],
                'City'       : [], 'State': [], 'Country': []}
        df = pd.DataFrame(dict)
        df = df.astype({'Brand': 'object'})
        df = df.astype({'Model': 'object'})
        if e_vars.verbose or e_vars.debug: print('ebay_search df_load: ', e)
        if e_vars.run_cached:
            print(
                    f'WARNING: Cannot find "{filename}". In order to use run_cached = True an extract must already exists. Try setting run_cached=False first and rerunning.')
            return None

    try:
        df_sum = pd.read_excel('summary.xlsx', index_col=0, engine='openpyxl')

    except:
        # if file does not exist, create it
        dict_sum = {'Run Datetime'                         : [], 'query': [], 'Country': [], 'MSRP': [],
                    'Past Week Median Price'               : [],
                    'Median Price'                         : [], 'Past Week Average Price': [],
                    'Average Price'                        : [], 'Total Sold': [], 'Total Sales': [],
                    'PayPal Profit'                        : [], 'Est eBay Profit': [],
                    'Est eBay + PayPal Profit'             : [], 'Total Scalpers/eBay Profit': [],
                    'Estimated Scalper Profit'             : [], 'Estimated Break Even Point for Scalpers': [],
                    'Minimum Break Even Point for Scalpers': []}
        df_sum = pd.DataFrame(dict_sum)

    start_datetime = datetime.now()

    if not e_vars.run_cached:
        price_ranges = [min_price, max_price]

        query_w_excludes = query

        if len(queryexclusions) > 0:
            for exclusion in queryexclusions:
                query_w_excludes += ' -' + exclusion

        if e_vars.verbose: print(query_w_excludes)

        # Determine price ranges to search with
        i = 0
        if e_vars.country == 'UK':
            extension = 'co.uk'
            num_check = 193
        else:
            extension = 'com'
            num_check = 201

        while i != len(price_ranges) - 1:
            time.sleep(
                    e_vars.sleep_len * random.uniform(0,
                                                      1))  # eBays servers will kill your connection if you hit them too frequently
            fomatted_query = query_w_excludes.replace(' ', '+').replace(',', '%2C').replace('(', '%28').replace(')',
                                                                                                                '%29')
            url = f"https://www.ebay.{extension}/sch/i.html?_from=R40&_nkw={fomatted_query}&_sacat={e_vars.sacat}&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo={price_ranges[i]}&_udhi={price_ranges[i + 1]}&rt=nc&_ipg=200&_pgn=4"

            source = adapter.get(url, timeout=10).text
            soup = BeautifulSoup(source, 'lxml')
            items = soup.find_all('li', attrs={'class': 's-item'})
            if e_vars.verbose: print(price_ranges, len(items), i, price_ranges[i], price_ranges[i + 1], url)

            # Get the last item on the page, if it's earlier than min_date or currentDate - days_before this break works
            # despite there being >800 items as the others are too old
            last_item = items[-1]

            currentYear = datetime.now().year
            currentMonth = datetime.now().month

            item_datetime = f"{currentYear} {last_item.find('span', class_='s-item__endedDate').text}"
            if e_vars.country == 'UK':
                item_datetime = datetime.strptime(item_datetime, '%Y %d-%b %H:%M')
            else:
                item_datetime = datetime.strptime(item_datetime, '%Y %b-%d %H:%M')

            # When we run early in the year
            if currentMonth < 6 and item_datetime.month > 6:
                last_year = currentYear - 1
                item_datetime = item_datetime.replace(year=last_year)

            last_item_date = item_datetime.replace(hour=0, minute=0)
            days_before_date = datetime.now() - timedelta(days=e_vars.days_before)
            days_before_date = days_before_date.replace(hour=0, minute=0, second=0, microsecond=0)

            if e_vars.verbose: print(last_item_date)

            if days_before_date > last_item_date or last_item_date > min_date:
                i += 1
            elif len(items) >= num_check and round(price_ranges[i + 1] - price_ranges[i], 2) > 0.01:
                # If there's only one cent difference between the two just increment, we need to do some special logic below
                midpoint = round((price_ranges[i] + price_ranges[i + 1]) / 2, 2)
                price_ranges = price_ranges[:i + 1] + [midpoint] + price_ranges[i + 1:]
            elif len(items) >= num_check and round(price_ranges[i + 1] - price_ranges[i], 2) == 0.01:
                # If there is a one cent difference between the two, we can have eBay just return that specific price to get a little bit finer detail
                price_ranges = price_ranges[:i + 1] + [price_ranges[i]] + [price_ranges[i + 1]] + price_ranges[i + 1:]
                i += 2
            else:
                i += 1

        if e_vars.debug or e_vars.verbose: print(price_ranges)

        for i in range(len(price_ranges) - 1):
            fomatted_query = query_w_excludes.replace(' ', '+').replace(',', '%2C').replace('(', '%28').replace(')',
                                                                                                                '%29')
            url = f"https://www.ebay.{extension}/sch/i.html?_from=R40&_nkw={fomatted_query}&_sacat={e_vars.sacat}&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo={price_ranges[i]}&_udhi={price_ranges[i + 1]}&rt=nc&_ipg=200&_pgn="

            if e_vars.verbose: print(price_ranges[i], price_ranges[i + 1], url)

            df = ebay_scrape(url, df, adapter, e_vars=e_vars, min_date=min_date)

            # Best to save semiregularly in case eBay kills the connection
            df = pd.DataFrame.drop_duplicates(df)
            df.to_excel(f"Spreadsheets/{query}{e_vars.extra_title_text}.xlsx", engine='openpyxl')
            requests_cache.remove_expired_responses()

    df = df[df['Ignore'] == 0]
    if min_date:
        df = df[df['Sold Date'] >= min_date]

    median_price, est_break_even, min_break_even, tot_sold, estimated_shipping = ebay_plot(query, msrp, df,
                                                                                           e_vars=e_vars)

    ebay_profit, pp_profit, scalp_profit = plot_profits(df, query.replace("+", " ").split('-', 1)[
        0].strip() + e_vars.extra_title_text, msrp, e_vars=e_vars)

    last_week = df.loc[
        df['Sold Date'] >= (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)]
    tot_sales = (df['Total Price'] * df['Quantity']).sum()
    tot_ini_sales = (df['Price'] * df['Quantity']).sum()

    print(f"Past Week Median Price: {e_vars.ccode}{last_week['Total Price'].median()}")
    print(f"Median Price: {e_vars.ccode}{median_price}")
    print(f"Past Week Average Price: {e_vars.ccode}{round(last_week['Total Price'].mean(), 2)}")
    print(f"Average Price: {e_vars.ccode}{round(df['Total Price'].mean(), 2)}")
    print(f"Total Sold: {tot_sold}")
    print(f"Total Sales: {e_vars.ccode}{round(tot_sales, 2)}")
    print(f"PayPal Profit: {e_vars.ccode}{int(pp_profit)}")
    print(f"Est eBay Profit: {e_vars.ccode}{int(ebay_profit)}")
    print(f"Est eBay + PayPal Profit: {e_vars.ccode}{int(ebay_profit + pp_profit)}")
    if msrp > 0:
        total_scalp_val = round(tot_sales - tot_sold * (msrp * (1.0 + e_vars.tax_rate) + estimated_shipping), 2)
        print(f"Total Scalpers/eBay Profit: {e_vars.ccode}{total_scalp_val}")
        print(f"Estimated Scalper Profit: {e_vars.ccode}{round(scalp_profit)}")
        print(f"Estimated Break Even Point for Scalpers: {e_vars.ccode}{est_break_even}")
        print(f"Minimum Break Even Point for Scalpers: {e_vars.ccode}{min_break_even}")

        dict_sum_new = {'Run Datetime'                           : start_datetime,
                        'Country'                                : e_vars.country,
                        'query'                                  : query, 'MSRP': msrp,
                        'Past Week Median Price'                 : last_week['Total Price'].median(),
                        'Median Price'                           : median_price,
                        'Past Week Average Price'                : round(last_week['Total Price'].mean(), 2),
                        'Average Price'                          : round(df['Total Price'].mean(), 2),
                        'Total Sold'                             : tot_sold,
                        'Total Sales'                            : round(tot_sales, 2),
                        'PayPal Profit'                          : round(pp_profit, 2),
                        'Est eBay Profit'                        : int(ebay_profit),
                        'Est eBay + PayPal Profit'               : int(ebay_profit + pp_profit),
                        'Total Scalpers/eBay Profit'             : total_scalp_val,
                        'Estimated Scalper Profit'               : round(scalp_profit),
                        'Estimated Break Even Point for Scalpers': est_break_even,
                        'Minimum Break Even Point for Scalpers'  : min_break_even}
    else:
        dict_sum_new = {'Run Datetime'                           : start_datetime,
                        'query'                                  : query,
                        'Country'                                : e_vars.country, 'MSRP': msrp,
                        'Past Week Median Price'                 : last_week['Total Price'].median(),
                        'Median Price'                           : median_price,
                        'Past Week Average Price'                : round(last_week['Total Price'].mean(), 2),
                        'Average Price'                          : round(df['Total Price'].mean(), 2),
                        'Total Sold'                             : tot_sold,
                        'Total Sales'                            : round(tot_sales, 2),
                        'PayPal Profit'                          : round(pp_profit, 2),
                        'Est eBay Profit'                        : int(ebay_profit),
                        'Est eBay + PayPal Profit'               : int(ebay_profit + pp_profit),
                        'Total Scalpers/eBay Profit'             : '',
                        'Estimated Scalper Profit'               : '',
                        'Estimated Break Even Point for Scalpers': '',
                        'Minimum Break Even Point for Scalpers'  : ''}

    elapsed = time.time() - start
    print("Runtime: %02d:%02d:%02d" % (elapsed // 3600, elapsed // 60 % 60, elapsed % 60))
    print('')
    df_sum = df_sum.append(dict_sum_new, ignore_index=True)

    df_sum.to_excel('summary.xlsx', engine='openpyxl')

    query_item_name = query.split('-', 1)[0]

    df = df.assign(item=query_item_name)
    df = df.assign(msrp=msrp)
    os.remove(f"{cache_name}.sqlite")
    return df
