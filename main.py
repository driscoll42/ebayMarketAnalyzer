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

from classes import EbayVariables
from plotting import ebay_plot
from plotting import plot_profits


def get_purchase_hist(trs, e_vars: EbayVariables, sold_list: List[Union[float, int, datetime, datetime]],
                      sold_hist_url: str) -> List[Union[float, int, datetime, datetime]]:
    bin_date, bin_datetime = '', ''
    # Typically these are true
    price_col = 2
    date_col = 4
    quant_col = 3

    for r in trs:
        ths = r.find_all('th')
        th_cnt = -1
        for th in ths:
            th_cnt += 1
            if 'PRICE' in th.text.upper():
                price_col = th_cnt
            elif 'QUANT' in th.text.upper():
                quant_col = th_cnt
            elif 'DATE' in th.text.upper():
                date_col = th_cnt

        tds = r.find_all('td')
        if len(tds) > 1:
            # buyer = tds[1].text
            try:
                price = float(re.sub(r'[^\d.]+', '', tds[price_col].text))
            except Exception as e:
                if e_vars.verbose: print('get_purchase_hist-price', e, sold_hist_url)
                price = ''

            if price:
                quantity = int(tds[quant_col].text)
                sold_date = tds[date_col].text.split()[0]
                sold_time = tds[date_col].text.split()[1]

                try:
                    sold_date = datetime.strptime(sold_date, '%b-%d-%y')
                except Exception as e:
                    sold_date = datetime.strptime(sold_date, '%d-%b-%y')

                sold_time = datetime.strptime(sold_time, '%H:%M:%S').time()
                sold_time = sold_time.replace(second=0, microsecond=0)
                sold_datetime = datetime.combine(sold_date, sold_time)

                if not bin_date:
                    bin_date, bin_datetime = sold_date, sold_datetime
                bin_date, bin_datetime = max(bin_date, sold_date), max(bin_datetime, sold_datetime)

                if e_vars.verbose: print('get_purchase_hist-DateTimes', price, quantity, sold_datetime)

                sold_list.append([price, quantity, sold_date, sold_datetime])

    return sold_list, bin_date, bin_datetime


def get_offer_hist(trs, e_vars: EbayVariables, sold_list: List[Union[float, int, datetime, datetime]],
                   sold_hist_url: str) -> List[Union[float, int, datetime, datetime]]:
    off_date, off_datetime = '', ''

    for r in trs:
        tds = r.find_all('td', )
        # if e_vars.verbose: print('get_offer_hist-tds', tds)
        if len(tds) > 1:
            try:
                quantity = int(tds[3].text)
            except Exception as e:
                quantity = ''
                if e_vars.verbose: print('get_offer_hist-trs', e, sold_hist_url)

            if quantity:
                # buyer = tds[1].text
                accepted = tds[2].text
                sold_date = tds[4].text.split()[0]
                sold_time = tds[4].text.split()[1]

                try:
                    sold_date = datetime.strptime(sold_date, '%b-%d-%y')
                except Exception as e:
                    sold_date = datetime.strptime(sold_date, '%d-%b-%y')

                sold_time = datetime.strptime(sold_time, '%H:%M:%S').time()
                sold_time = sold_time.replace(second=0, microsecond=0)
                sold_datetime = datetime.combine(sold_date, sold_time)

                if not off_date:
                    off_date, off_datetime = sold_date, sold_datetime
                off_date, off_datetime = max(off_date, sold_date), max(off_datetime, sold_datetime)

                if accepted == 'Accepted':
                    if e_vars.verbose: print(accepted, quantity, sold_datetime)
                    sold_list.append(['', quantity, sold_date, sold_datetime])

    return sold_list, off_date, off_datetime


# XML Formatter: https://jsonformatter.org/xml-formatter

def get_quantity_hist(sold_hist_url: str,
                      sold_list: List[Union[float, int, datetime, datetime]],
                      adapter: requests,
                      e_vars: EbayVariables) -> List[Union[float, int, datetime, datetime]]:
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
    sl_date, sl_datetime = '', ''
    time.sleep(
            e_vars.sleep_len * random.uniform(0,
                                              1))  # eBays servers will kill your connection if you hit them too frequently
    try:
        with requests_cache.disabled():  # We don't want to cache all the calls into the individual listings, they'll never be repeated
            source = adapter.get(sold_hist_url, timeout=10).text
        soup = BeautifulSoup(source, 'lxml')

        # items = soup.find_all('tr')

        tables = soup.find_all('table', attrs={'border': '0', 'cellpadding': '5', 'cellspacing': '0',
                                               'width' : '100%'})

        # eBay has a number of possible tables in the purchase history, Offer History, Offer Retraction History,
        # Purchase History, listings don't have to have all of them so just need to check
        bin_date, off_date = '', ''
        bin_datetime, off_datetime = '', ''
        for table in tables:
            trs = table.find_all('tr')
            ths = trs[0].find_all('th')
            for th in ths:
                if 'Buy It Now Price' in th.text or 'Date of Purchase' in th.text:
                    sold_list, bin_date, bin_datetime = get_purchase_hist(trs, e_vars, sold_list, sold_hist_url)
                elif 'Offer Status' in th.text:
                    sold_list, off_date, off_datetime = get_offer_hist(trs, e_vars, sold_list, sold_hist_url)

        if not bin_date and off_date:
            sl_date, sl_datetime = off_date, off_datetime
        elif not off_date and bin_date:
            sl_date, sl_datetime = bin_date, bin_datetime
        elif off_date and bin_date:
            sl_date, sl_datetime = max(bin_date, off_date), max(bin_datetime, off_datetime)

    except Exception as e:
        if e_vars.verbose: print('get_quantity_hist', e, sold_hist_url)
    return sold_list, sl_date, sl_datetime


def sp_get_datetime(item, days_before_date, e_vars, item_link):
    item_date, item_datetime = '', ''
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
        if e_vars.verbose: print('sp_get_datetime-1', e, item_link)
        try:
            orig_item_datetime = item.find('span', class_='s-item__title--tagblock__COMPLETED').text
            orig_item_datetime = orig_item_datetime.replace('Sold item', '').replace('Sold', '').strip()
            item_datetime = orig_item_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

            item_date = datetime.strptime(orig_item_datetime, '%d %b %Y')
            item_date = item_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days_before_date = min(item_date, days_before_date)

        except Exception as e:
            if e_vars.verbose: print('sp_get_datetime-2', e, item_link)
            try:
                date_time = item.find('span', attrs={'class': 'POSITIVE'})

                classes = date_time.find_all('span')
                off_dict = {}
                for c in classes:
                    cls_name = c.attrs['class'][0]
                    if cls_name not in off_dict:
                        off_dict[cls_name] = c.text
                    else:
                        off_dict[cls_name] = off_dict[cls_name] + c.text

                for od in off_dict.values():
                    if 'Sold' in od:
                        date_txt = od.replace('Sold', '').replace(',', '').strip()
                        item_date = datetime.strptime(date_txt, "%b %d %Y")
                days_before_date = min(item_date, days_before_date)

            except Exception as e:
                if e_vars.verbose: print('sp_get_datetime-3', e, item_link)

    return item_date, item_datetime, days_before_date


def ebay_scrape(base_url: str,
                df: pd.DataFrame,
                adapter: requests,
                e_vars: EbayVariables,
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

    def sp_get_item_link(item):
        try:
            item_link = item.find('a', class_='s-item__link')['href']
        except Exception as e:
            item_link = 'None'
            if e_vars.debug or e_vars.verbose: print('sp_get_item_link', e)
        return item_link

    def sp_get_title(item):
        try:
            item_title = item.find('h3', class_='s-item__title').text
        except Exception as e:
            item_title = 'None'
            if e_vars.debug or e_vars.verbose: print('sp_get_title', e, item_link)
        return item_title

    def sp_get_desc(item):
        try:
            item_desc = item.find('div', class_='s-item__subtitle').text
        except Exception as e:
            item_desc = 'None'
            if e_vars.debug or e_vars.verbose: print('sp_get_desc', e, item_link)
        return item_desc

    def sp_get_price(item):
        try:
            item_price = item.find('span', class_='s-item__price').text
            item_price = float(re.sub(r'[^\d.]+', '', item_price))
        except Exception as e:
            item_price = -1
            if e_vars.debug or e_vars.verbose: print('sp_get_price', e, item_link)
        return item_price

    def sp_get_shipping(item):
        try:
            item_shipping = item.find('span', class_='s-item__shipping s-item__logisticsCost').text
            if item_shipping.upper().find("FREE") == -1:
                item_shipping = float(re.sub(r'[^\d.]+', '', item_shipping))
            else:
                item_shipping = 0
        except Exception as e:
            item_shipping = 0
            if e_vars.debug or e_vars.verbose: print('sp_get_shipping', e, item_link)
        return item_shipping

    def ip_get_datetime(item_soup, days_before_date):
        item_date, item_datetime = '', ''
        try:
            date_one = item_soup.find('div', attrs={'class': 'u-flL vi-bboxrev-posabs vi-bboxrev-dsplinline'})
            date_one = date_one.find('span', attrs={'id': 'bb_tlft'})
            date_one = date_one.text.replace("\n", " ").replace(",", "").strip().split()

            try:
                item_datetime = datetime.strptime(f"{date_one[0]} {date_one[1]} {date_one[2]} {date_one[3]}",
                                                  "%b %d %Y %I:%M:%S")
            except Exception as e:
                item_datetime = datetime.strptime(f"{date_one[0]} {date_one[1]} {date_one[2]} {date_one[3]}",
                                                  "%b %d %Y %H:%M:%S")
            item_datetime = item_datetime.replace(second=0, microsecond=0)
            item_date = item_datetime.replace(hour=0, minute=0)
            days_before_date = min(item_date, days_before_date)

        except Exception as e:
            if e_vars.debug or e_vars.verbose: print('ip_get_datetime', e, item_link)
        return item_date, item_datetime, days_before_date

    def ip_get_loc_data(item_soup):
        city, state, country_name = '', '', ''
        try:
            loc = item_soup.find('div', attrs={'class': 'iti-eu-bld-gry'})
            loc = loc.find('span').text.split(',')
            if len(loc) == 2:
                city, state, country_name = loc[0].strip(), '', loc[1].strip()
            elif len(loc) == 3:
                city, state, country_name = loc[0].strip(), loc[1].strip(), loc[2].strip()
            else:
                raise Exception
        except Exception as e:
            if e_vars.debug or e_vars.verbose: print('ip_get_loc_data', e, item_link)
            loc_2 = item_soup.find('div', attrs={'class': 'vi-wp vi-VR-cvipCntr1'})
            loc_2 = loc_2.find_all('tr', attrs={'class': 'vi-ht20'})
            for l in loc_2:
                if l.text.find('Item location:') > 0:
                    i_loc = l.find_all('div', attrs={'class': 'u-flL'})
                    loc_text = i_loc[1].text.split(',')
                    if len(loc_text) == 2:
                        city, state, country_name = loc_text[0].strip(), '', loc_text[1].strip()
                    elif len(loc_text) == 3:
                        city, state, country_name = loc_text[0].strip(), loc_text[1].strip(), loc_text[2].strip()
                    break
        return city, state, country_name

    def ip_get_seller(item_soup):
        seller, seller_fb, store = '', '', False
        try:
            seller = item_soup.find_all('span', attrs={'class': 'mbg-nw'})
            seller = seller[0].text

            seller_fb = item_soup.find_all('span', attrs={'class': 'mbg-l'})
            seller_fb = int(seller_fb[0].find('a').text)

            store_id = item_soup.find_all('div', attrs={'id': 'storeSeller'})

            if len(store_id[0].text) > 0:
                store = True
        except Exception as e:
            if e_vars.debug or e_vars.verbose: print('ip_get_seller', e, item_link)
        return seller, seller_fb, store

    def ip_get_datetime_card(item_soup, days_before_date):
        item_date, item_datetime = '', ''
        try:
            con_card = item_soup.find_all('div',
                                          attrs={
                                              'class': 'nodestar-item-card-details__condition-row'})
            for c in con_card:
                if 'Ended' in c.text:
                    end_ele = c.text.replace('Ended:', '').replace(',', '').split()

                    item_datetime = datetime.strptime(
                            f"{end_ele[0]} {end_ele[1]} {end_ele[2]} {end_ele[3]} {end_ele[4]}",
                            "%b %d %Y %I:%M:%S %p")
                    item_datetime = item_datetime.replace(second=0, microsecond=0)
                    item_date = item_datetime.replace(hour=0, minute=0)
                    days_before_date = min(item_date, days_before_date)

        except Exception as e:
            if e_vars.debug or e_vars.verbose: print('ip_get_datetime_card', e,
                                                     item_link)
        return item_date, item_datetime, days_before_date

    def ip_get_quant_hist(item_soup, sold_list):
        sl_date, sl_datetime = '', ''
        quantity_sold, multi_list = 1, False

        try:
            iitem = item_soup.find_all('a', attrs={'class': 'vi-txt-underline'})
            quantity_sold = int(iitem[0].text.split()[0])
            multi_list = True

            if e_vars.quantity_hist:
                sold_hist_url = iitem[0]['href']
                sold_list, sl_date, sl_datetime = get_quantity_hist(sold_hist_url, sold_list, adapter=adapter,
                                                                    e_vars=e_vars)

        except Exception as e:
            if e_vars.verbose: print('ip_get_quant_hist', e, item_link)
        return quantity_sold, multi_list, sold_list, sl_date, sl_datetime

    days_before_date = datetime.today()
    days_before_date = days_before_date.replace(hour=0, minute=0, second=0, microsecond=0)
    comp_date = days_before_date - timedelta(days=e_vars.days_before)

    for x in range(1, 5):
        # eBays servers will kill your connection if you hit them too frequently
        time.sleep(e_vars.sleep_len * random.uniform(0, 1))

        url = f"{base_url}{x}"

        if x == 4:
            soup_source = adapter.get(url, timeout=10).text
        else:
            with requests_cache.disabled():  # We don't want to cache all the calls into the individual listings, they'll never be repeated
                soup_source = adapter.get(url, timeout=10).text
        soup = BeautifulSoup(soup_source, 'lxml')
        items = soup.find_all('li', attrs={'class': 's-item'})

        time_break = False

        if e_vars.verbose: print(x, len(items), url)

        for n, item in enumerate(items):
            if e_vars.debug or e_vars.verbose: print('----------------------------')
            curr_time = datetime.now()
            if e_vars.verbose: print(curr_time)
            if n > 0:

                item_link = sp_get_item_link(item)
                if e_vars.debug or e_vars.verbose: print('URL:', item_link)

                item_date, item_datetime, days_before_date = sp_get_datetime(item, days_before_date, e_vars, item_link)
                if e_vars.debug or e_vars.verbose: print('Date-1:', item_date)
                if e_vars.debug or e_vars.verbose: print('Datetime-1:', item_datetime)

                if days_before_date < comp_date or days_before_date < min_date:
                    time_break = True
                    break

                # Only need to add new records
                if not df[['Link', 'Sold Datetime']].isin({'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                        axis='columns').any() and not (df[['Link', 'Sold Date', 'Multi Listing']].isin(
                        {'Link': [item_link], 'Sold Date': [item_date], 'Multi Listing': [0]}).all(
                        axis='columns').any()):

                    item_title = sp_get_title(item)
                    if e_vars.debug or e_vars.verbose: print('Title:', item_title)

                    item_desc = sp_get_desc(item)
                    if e_vars.debug or e_vars.verbose: print('Desc:', item_desc)

                    item_price = sp_get_price(item)
                    if e_vars.debug or e_vars.verbose: print('Price:', item_price)

                    item_shipping = sp_get_shipping(item)
                    if e_vars.debug or e_vars.verbose: print('Shipping:', item_shipping)

                    item_tot = item_price + item_shipping
                    if e_vars.debug or e_vars.verbose: print('Total:', item_tot)

                    quantity_sold, sold_list, multi_list = 1, [], False
                    seller, seller_fb, store = '', '', False
                    city, state, country_name = '', '', ''

                    if e_vars.feedback or e_vars.quantity_hist:
                        time.sleep(e_vars.sleep_len * random.uniform(0, 1))
                        # We don't want to cache all the calls into the individual listings, they'll never be repeated
                        with requests_cache.disabled():
                            try:
                                isource = adapter.get(item_link).text
                            except Exception as e:
                                if e_vars.verbose: print('ebay_scrape-isource', e, item_link)
                                continue

                        item_soup = BeautifulSoup(isource, 'lxml')

                        # Check if this is the original item, or eBay trying to sell another item and having a redirect
                        oitems = item_soup.find_all('a', attrs={'class': 'nodestar-item-card-details__view-link'})

                        if len(oitems) > 0:
                            if e_vars.debug or e_vars.verbose: print(
                                    'Search Link goes to similar item, finding original')
                            orig_link = oitems[0]['href']

                            if not item_datetime:
                                item_date_temp, item_datetime, days_before_date = ip_get_datetime_card(item_soup,
                                                                                                       days_before_date)
                                if item_date_temp:
                                    item_date = item_date_temp
                                if e_vars.debug or e_vars.verbose: print('Date-2:', item_date)
                                if e_vars.debug or e_vars.verbose: print('Datetime-2:', item_datetime)

                            time.sleep(e_vars.sleep_len * random.uniform(0, 1))
                            # We don't want to cache all the calls into the individual listings, they'll never be repeated
                            with requests_cache.disabled():
                                source = adapter.get(orig_link).text
                            item_soup = BeautifulSoup(source, 'lxml')

                        if not item_datetime:
                            item_date_temp, item_datetime, days_before_date = ip_get_datetime(item_soup,
                                                                                              days_before_date)
                            if item_date_temp:
                                item_date = item_date_temp
                            if e_vars.debug or e_vars.verbose: print('Date-3:', item_date)
                            if e_vars.debug or e_vars.verbose: print('Datetime-3:', item_datetime)

                        seller, seller_fb, store = ip_get_seller(item_soup)
                        if e_vars.debug or e_vars.verbose: print('Seller:', seller)
                        if e_vars.debug or e_vars.verbose: print('Seller Feedback:', seller_fb)
                        if e_vars.debug or e_vars.verbose: print('Store:', store)

                        city, state, country_name = ip_get_loc_data(item_soup)
                        if e_vars.debug or e_vars.verbose: print('City:', city)
                        if e_vars.debug or e_vars.verbose: print('State:', state)
                        if e_vars.debug or e_vars.verbose: print('Country Name:', country_name)

                        # Sometimes the datetime isn't on the page for multilistings so we get the most recent sale
                        quantity_sold, multi_list, sold_list, sl_date, sl_datetime = ip_get_quant_hist(item_soup,
                                                                                                       sold_list)
                        if e_vars.debug or e_vars.verbose: print('multi_list:', multi_list)
                        if multi_list:
                            if e_vars.debug or e_vars.verbose: print('Quantity Sold:', quantity_sold)
                            if e_vars.debug or e_vars.verbose: print('sold_list:', sold_list)
                            if e_vars.debug or e_vars.verbose: print('sold_list_max_date:', sl_date)
                            if e_vars.debug or e_vars.verbose: print('sold_list_max_datetime:', sl_datetime)
                            if not item_date:
                                item_date_temp, item_datetime = sl_date, sl_datetime
                                days_before_date = min(sl_date, days_before_date)
                                if item_date_temp:
                                    item_date = item_date_temp
                                if e_vars.debug or e_vars.verbose: print('Date-4:', item_date)
                                if e_vars.debug or e_vars.verbose: print('Datetime-4:', item_datetime)

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

                    if not item_datetime and item_date:
                        item_datetime = item_date

                    if days_before_date < comp_date or min(item_date, days_before_date) < min_date:
                        time_break = True
                        break

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
                                   'Country'        : country_name, 'Sold Scrape Datetime': curr_time}

                        if not df[['Link', 'Sold Datetime']].isin(
                                {'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                                axis='columns').any() and item_tot > 0 and (quantity_sold - cap_sum) > 0:
                            if e_vars.verbose: print('non-multi', df__new)
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
                                       'Sold Datetime': sale[3], 'Link': item_link, 'Seller': seller,
                                       'Multi Listing': multi_list, 'Quantity': sale[1], 'Seller Feedback': seller_fb,
                                       'Ignore'       : ignor_val, 'Store': store, 'City': city, 'State': state,
                                       'Country'      : country_name, 'Sold Scrape Datetime': curr_time}

                            # There's a chance when we get to multiitem listings we'd be reinserting data, this is to prevent it
                            if not df[['Link', 'Sold Datetime']].isin(
                                    {'Link': [item_link], 'Sold Datetime': [sale[3]]}).all(
                                    axis='columns').any() and item_tot > 0:
                                if e_vars.verbose: print('multi', df__new)
                                df = df.append(df__new, ignore_index=True)

                        tot_sale_quant = np.sum(sold_list[:, 1])

                        if tot_sale_quant < quantity_sold:
                            # On some listings the offer list has scrolled off (only shows latest 100) despite some beint accepted
                            # In order to not lose the data I just shove everything into one entry, assuming the regular price
                            # Not perfect, but no great alternatives
                            # The main issue here of course is that now I'm assigning a bunch of sales to a semi-arbitrary date
                            df__new = {'Title'        : item_title, 'Brand': brand, 'Model': model,
                                       'description'  : item_desc, 'Price': item_price,
                                       'Shipping'     : item_shipping,
                                       'Total Price'  : item_tot, 'Sold Date': item_date,
                                       'Sold Datetime': item_datetime, 'Link': item_link, 'Seller': seller,
                                       'Quantity'     : quantity_sold - tot_sale_quant,
                                       'Multi Listing': multi_list, 'Seller Feedback': seller_fb, 'Ignore': 2,
                                       'Store'        : store, 'City': city, 'State': state,
                                       'Country'      : country_name, 'Sold Scrape Datetime': curr_time}
                            # There's a chance when we get to multiitem listings we'd be reinserting data, this is to prevent it
                            if not df[['Link', 'Sold Datetime', 'Quantity']].isin(
                                    {'Link'    : [item_link], 'Sold Datetime': [item_datetime],
                                     'Quantity': [quantity_sold - tot_sale_quant]}).all(
                                    axis='columns').any() and item_tot > 0:
                                if e_vars.verbose: print('multi-extra', df__new)
                                df = df.append(df__new, ignore_index=True)
        if e_vars.country == 'UK' and len(items) < 193:
            if e_vars.verbose: print('UK item break', len(items))
            break
        elif len(items) < 201:
            if e_vars.verbose: print('item break', len(items))
            break
        elif time_break:
            if e_vars.verbose: print('time_break', time_break, days_before_date, comp_date, min_date)
            break

    return df


def ebay_search(query: str,
                e_vars: EbayVariables,
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

    if e_vars.verbose: pd.set_option('display.max_rows', None)
    if e_vars.verbose: pd.set_option('display.max_columns', None)
    if e_vars.verbose: pd.set_option('display.width', None)
    if e_vars.verbose: pd.set_option('display.max_colwidth', -1)
    start = time.time()
    print(query)

    start_datetime = datetime.today().strftime("%Y%m%d%H%M%S")
    # https://realpython.com/caching-external-api-requests/
    curr_path = pathlib.Path(__file__).parent.absolute()

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

        # When saving the file, at times 0.000001 seconds might be added or subtracted from the Sold Datetime
        # This causes a mismatch when comparing datetimes, causing duplicates and wasting time rechecking listings
        # Testing on the 3060, adding this brought runtimes down from eight minutes to one minute.
        df['Sold Datetime'] = df['Sold Datetime'].dt.round('min')
        df['Sold Date'] = df['Sold Date'].dt.round('min')

    except Exception as e:
        # if file does not exist, create it
        dict = {'Title'      : [], 'Brand': [], 'Model': [], 'description': [], 'Price': [], 'Shipping': [],
                'Total Price': [], 'Sold Date': [], 'Sold Datetime': [], 'Quantity': [], 'Multi Listing': [],
                'Seller'     : [], 'Seller Feedback': [], 'Link': [], 'Store': [], 'Ignore': [], 'City': [],
                'State'      : [], 'Country': [], 'Sold Scrape Datetime': []}
        df = pd.DataFrame(dict)
        df = df.astype({'Brand': 'object'})
        df = df.astype({'Model': 'object'})
        if e_vars.verbose or e_vars.debug: print('ebay_search-df_load:', e)
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

            currentYear = datetime.now().year
            currentMonth = datetime.now().month

            # Get the last item on the page, if it's earlier than min_date or currentDate - days_before this break works
            # despite there being >800 items as the others are too old
            # For some reason the last item on the eBay search page sometimes has no date, perhaps a timing issue
            # Iterate through the items from bottom up to find the last date, if nothing found just assume it's far in
            # the past. This is just a means to improve performance but little harm in checking more listings
            last_item_date = datetime.now()
            found_date = False
            for item_date_search in reversed(items):
                try:
                    search_date, item_datetime, days_before_date = sp_get_datetime(item_date_search, datetime.now(),
                                                                                   e_vars, url)

                    if search_date:
                        last_item_date = last_item_date
                        found_date = True
                        break
                except Exception as e:
                    if e_vars.verbose: print('ebay_search-date_search', e)
                '''if found_date:
                    if e_vars.country == 'UK':
                        item_datetime = datetime.strptime(item_datetime, '%Y %d-%b %H:%M')
                    else:
                        item_datetime = datetime.strptime(item_datetime, '%Y %b-%d %H:%M')
                    break

            # When we run early in the year
            if currentMonth < 6 and item_datetime.month > 6:
                last_year = currentYear - 1
                item_datetime = item_datetime.replace(year=last_year)'''

            last_item_date = last_item_date.replace(hour=0, minute=0)
            days_before_date = datetime.now() - timedelta(days=e_vars.days_before)
            days_before_date = days_before_date.replace(hour=0, minute=0, second=0, microsecond=0)

            if e_vars.verbose: print(last_item_date)

            if days_before_date > last_item_date or (found_date and last_item_date > min_date):
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
