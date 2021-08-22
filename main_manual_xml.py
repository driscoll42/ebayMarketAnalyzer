"""
This requires one to manually download XMLs. See ReadMe for details
"""
# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import os
import pathlib
import random
import re
import time
from datetime import datetime, timedelta
from typing import List, Union, Any, Tuple

import numpy as np
import pandas as pd
import requests
import requests_cache
from bs4 import BeautifulSoup
from dateutil import parser
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from classes import EbayVariables
from plotting import ebay_plot, plot_profits
from util_request import load_agents, request_link


# pylint: disable=line-too-long
# pylint: disable=multiple-statements

def validate_inputs(query: str,
                    e_vars: EbayVariables,
                    msrp: float = 0,
                    min_price: float = 0,
                    max_price: float = 10000,
                    min_date: datetime = datetime.now() - timedelta(days=90)) -> bool:
    """
    Validates the inputs of the ebay_search function and if any are

    Parameters
    ----------
    query : The main query to search on eBay
    e_vars : An instance of EbayVariables
    msrp : The msrp of the item being searched
    min_price : The minimum price to search for
    max_price : The maximum price to search for
    min_date : The earliest eBay sale to scrape, anything before this is discarded

    Returns
    -------
        A boolean value if inputs are valid or not.
    """
    validation_success = True
    if not isinstance(query, str):
        print('query is not a string!')
        validation_success = False

    if not isinstance(msrp, float) and not isinstance(msrp, int):
        print('msrp is not a float or int!')
        validation_success = False

    if not isinstance(min_price, float) and not isinstance(min_price, int):
        print('min_price is not a float or int!')
        validation_success = False

    if not isinstance(max_price, float) and not isinstance(max_price, int):
        print('max_price is not a float or int!')
        validation_success = False

    if not isinstance(min_date, datetime):
        print('min_date is not a Datetime!')
        validation_success = False

    if not isinstance(e_vars.run_cached, bool):
        print('EbayVariables class variable run_cached is not a bool!')
        validation_success = False

    if not isinstance(e_vars.sleep_len, float) and not isinstance(e_vars.sleep_len, int):
        print('EbayVariables class variable sleep_len is not a bool!')
        validation_success = False

    if not isinstance(e_vars.show_plots, bool):
        print('EbayVariables class variable show_plots is not a bool!')
        validation_success = False

    if not isinstance(e_vars.profit_plot, bool):
        print('EbayVariables class variable profit_plot is not a bool!')
        validation_success = False

    if not isinstance(e_vars.main_plot, bool):
        print('EbayVariables class variable main_plot is not a bool!')
        validation_success = False

    if not isinstance(e_vars.trend_type, str):
        print('EbayVariables class variable trend_type is not a string!')
        validation_success = False

    if e_vars.trend_type != 'none' and e_vars.trend_type != 'linear' and e_vars.trend_type != 'poly' and \
            e_vars.trend_type != 'roll':
        print(
                'EbayVariables class variable trend_type is not a valid! Must be one of "poly", "linear", "roll" or "none"')
        validation_success = False

    if not isinstance(e_vars.trend_param, list):
        print('EbayVariables class variable trend_param is not an int!')
        validation_success = False
    elif e_vars.trend_type == 'linear' and (len(e_vars.trend_param) != 1 or not isinstance(e_vars.trend_param[0], int)):
        print('EbayVariables class variable trend_type must be a list with a single integer when trend_type = linear!')
        validation_success = False
    elif e_vars.trend_type == 'roll' and (len(e_vars.trend_param) != 1 or not isinstance(e_vars.trend_param[0], int)):
        print('EbayVariables class variable trend_type must be a list with a single integer when trend_type = roll!')
        validation_success = False
    elif e_vars.trend_type == 'poly' and (
            len(e_vars.trend_param) != 2 or not isinstance(e_vars.trend_param[0], int) or not isinstance(
            e_vars.trend_param[1], int)):
        print('EbayVariables class variable trend_type must be a list with of two integers when trend_type = poly!')
        validation_success = False

    if not isinstance(e_vars.sacat, int):
        print('EbayVariables class variable sacat is not an int!')
        validation_success = False

    if not isinstance(e_vars.tax_rate, float) and isinstance(e_vars.tax_rate, int):
        print('EbayVariables class variable tax_rate is not a float or int!')
        validation_success = False
    elif e_vars.tax_rate >= 1 or e_vars.tax_rate < 0:
        print('EbayVariables class variable tax_rate must be between 0 and 1!')
        validation_success = False

    if not isinstance(e_vars.store_rate, float) and not isinstance(e_vars.store_rate, int):
        print('EbayVariables class variable store_rate is not a float or int!')
        validation_success = False
    elif e_vars.store_rate >= 1 or e_vars.store_rate < 0:
        print('EbayVariables class variable store_rate must be between 0 and 1!')
        validation_success = False

    if not isinstance(e_vars.non_store_rate, float) and not isinstance(e_vars.non_store_rate, int):
        print('EbayVariables class variable non_store_rate is not a float or int!')
        validation_success = False
    elif e_vars.non_store_rate >= 1 or e_vars.non_store_rate < 0:
        print('EbayVariables class variable non_store_rate must be between 0 and 1!')
        validation_success = False

    if not isinstance(e_vars.country, str):
        print('EbayVariables class variable country is not a string!')
        validation_success = False
    elif e_vars.country != 'USA' and e_vars.country != 'UK':
        print('EbayVariables class variable country must be "USA" or "UK"!')
        validation_success = False

    if not isinstance(e_vars.ccode, str):
        print('EbayVariables class variable ccode is not a string!')
        validation_success = False

    if not isinstance(e_vars.days_before, int):
        print('EbayVariables class variable days_before is not a int!')
        validation_success = False

    elif e_vars.days_before < 1:
        print('EbayVariables class variable days_before must be >= 1!')
        validation_success = False

    if not isinstance(e_vars.feedback, bool):
        print('EbayVariables class variable feedback is not a bool!')
        validation_success = False

    if not isinstance(e_vars.quantity_hist, bool):
        print('EbayVariables class variable quantity_hist is not a bool!')
        validation_success = False

    if not isinstance(e_vars.desc_ignore_list, list):
        print('EbayVariables class variable desc_ignore_list is not a list!')
        validation_success = False

    if not isinstance(e_vars.extra_title_text, str):
        print('EbayVariables class variable extra_title_text is not a string!')
        validation_success = False

    if not isinstance(e_vars.brand_list, list):
        print('EbayVariables class variable brand_list is not a list!')
        validation_success = False

    if not isinstance(e_vars.model_list, list):
        print('EbayVariables class variable model_list is not a list!')
        validation_success = False

    if not isinstance(e_vars.debug, bool):
        print('EbayVariables class variable debug is not a bool!')
        validation_success = False

    if not isinstance(e_vars.verbose, bool):
        print('EbayVariables class variable verbose is not a bool!')
        validation_success = False
    return validation_success


def get_purchase_hist(trs, e_vars: EbayVariables, sold_list: List[Union[float, int, datetime, datetime]],
                      sold_hist_url: str) -> Tuple[
    List[Union[float, int, datetime]], Union[Union[str, datetime], Any], Union[str, Any]]:
    """

    Parameters
    ----------
    trs :
    e_vars :
    sold_list :
    sold_hist_url :

    Returns
    -------

    """
    bin_date, bin_datetime = '', ''
    # Typically these are true
    price_col = 2
    date_col = 4
    quant_col = 3
    trs = trs.find('table', "app-table__table").find_all('tr')
    for tr in trs:
        ths = tr.find_all('th')

        for i, th in enumerate(ths):
            if 'PRICE' in th.text.upper():
                price_col = i
            elif 'QUANT' in th.text.upper():
                quant_col = i
            elif 'DATE' in th.text.upper():
                date_col = i

        tds = tr.find_all('td')
        spec_offer = False
        if len(tds) > 1:
            # buyer = tds[1].text
            try:
                if 'SPECIAL OFFER' in tds[price_col].text.upper():
                    price = ''
                    spec_offer = True
                else:
                    price = float(re.sub(r'[^\d.]+', '', tds[price_col].text))
            except Exception as e:
                if e_vars.verbose: print('get_purchase_hist-price', tds[price_col].text, e, sold_hist_url)
                price = ''

            if price or spec_offer:
                quantity = int(tds[quant_col].text)

                sold_datetime = parser.parse(tds[date_col].text)
                sold_date = sold_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

                if not bin_date:
                    bin_date, bin_datetime = sold_date, sold_datetime
                bin_date, bin_datetime = max(bin_date, sold_date), max(bin_datetime, sold_datetime)

                if e_vars.verbose: print('get_purchase_hist', price, quantity, sold_datetime)

                if sold_date > datetime.now() - timedelta(e_vars.days_before):
                    sold_list.append([price, quantity, sold_date, sold_datetime])

    return sold_list, bin_date, bin_datetime


def get_offer_hist(trs, e_vars: EbayVariables, sold_list: List[Union[float, int, datetime, datetime]],
                   sold_hist_url: str) -> Tuple[
    List[Union[float, int, datetime]], Union[Union[str, datetime], Any], Union[str, Any]]:
    """

    Parameters
    ----------
    trs :
    e_vars :
    sold_list :
    sold_hist_url :

    Returns
    -------

    """
    off_date, off_datetime = '', ''
    offer_col = 1
    quant_col = 2
    date_col = 3
    trs = trs.find('table', "app-table__table").find_all('tr')

    for tr in trs:
        ths = tr.find_all('th')

        for i, th in enumerate(ths):
            if 'QUANT' in th.text.upper():
                quant_col = i
            elif 'DATE' in th.text.upper():
                date_col = i
            elif 'STATUS' in th.text.upper():
                offer_col = i

        tds = tr.find_all('td', )
        # if e_vars.verbose: print('get_offer_hist-tds', tds)
        if len(tds) > 1:
            try:
                quantity = int(tds[quant_col].text)
            except Exception as e:
                quantity = ''
                if e_vars.verbose: print('get_offer_hist-trs', e, sold_hist_url)

            if quantity:
                # buyer = tds[0].text
                offer_status = tds[offer_col].text
                sold_datetime = parser.parse(tds[date_col].text)
                sold_date = sold_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

                if not off_date:
                    off_date, off_datetime = sold_date, sold_datetime
                off_date, off_datetime = max(off_date, sold_date), max(off_datetime, sold_datetime)

                if e_vars.verbose: print('get_offer_hist', offer_status, quantity, sold_datetime)

                if offer_status == 'Accepted':
                    if sold_date > datetime.now() - timedelta(e_vars.days_before):
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

    # eBays servers will kill your connection if you hit them too frequently
    time.sleep(e_vars.sleep_len * random.uniform(0, 1))

    try:
        # We don't want to cache all the calls into the individual listings, they'll never be repeated
        source = request_link(sold_hist_url, adapter, cache=False, e_vars=e_vars, page_type='Quant_Hist')

        soup = BeautifulSoup(source, 'lxml')
        # items = soup.find_all('tr')

        fixed_price_table = soup.find('div', attrs={'class': 'app-table fixed-price'})
        offer_table = soup.find('div', attrs={'class': 'app-table offer'})

        # eBay has a number of possible tables in the purchase history, Offer History, Offer Retraction History,
        # Purchase History, listings don't have to have all of them so just need to check
        bin_date, off_date = '', ''
        bin_datetime, off_datetime = '', ''

        if fixed_price_table:
            sold_list, bin_date, bin_datetime = get_purchase_hist(fixed_price_table, e_vars, sold_list, sold_hist_url)
        if offer_table:
            sold_list, off_date, off_datetime = get_offer_hist(offer_table, e_vars, sold_list, sold_hist_url)

        if not bin_date and off_date:
            sl_date, sl_datetime = off_date, off_datetime
        elif not off_date and bin_date:
            sl_date, sl_datetime = bin_date, bin_datetime
        elif off_date and bin_date:
            sl_date, sl_datetime = max(bin_date, off_date), max(bin_datetime, off_datetime)

    except Exception as e:
        if e_vars.verbose: print('get_quantity_hist', e, sold_hist_url)
    return sold_list, sl_date, sl_datetime


def sp_get_datetime(item, days_before_date, e_vars, sp_link):
    """

    Parameters
    ----------
    item :
    days_before_date :
    e_vars :
    sp_link :

    Returns
    -------

    """
    item_date, item_datetime = '', ''
    try:
        date_time = item.find('span', attrs={'class': 'POSITIVE'}).text

        if 'Sold' in date_time:
            date_txt = date_time.replace('Sold', '').replace(',', '').strip()
            if e_vars.country == 'UK':
                item_date = datetime.strptime(date_txt, "%d %b %Y")
            else:
                item_date = datetime.strptime(date_txt, "%b %d %Y")
        days_before_date = min(item_date, days_before_date)

    except Exception as e:
        if e_vars.verbose: print('sp_get_datetime-1', e, sp_link)

        try:
            current_year = datetime.now().year
            current_month = datetime.now().month

            orig_item_datetime = f"{current_year} {item.find('span', class_='s-item__endedDate').text}"
            if e_vars.country == 'UK':
                item_datetime = datetime.strptime(orig_item_datetime, '%Y %d-%b %H:%M')
            else:
                item_datetime = datetime.strptime(orig_item_datetime, '%Y %b-%d %H:%M')

            # When we run early in the year
            if current_month < 6 < item_datetime.month:
                last_year = current_year - 1
                item_datetime = item_datetime.replace(year=last_year)

            item_date = item_datetime.replace(hour=0, minute=0)
            days_before_date = min(item_date, days_before_date)

        except Exception as e:
            if e_vars.verbose: print('sp_get_datetime-2', e, sp_link)
            try:
                orig_item_datetime = item.find('span', class_='s-item__title--tagblock__COMPLETED').text
                orig_item_datetime = orig_item_datetime.replace('Sold item', '').replace('Sold', '').strip()
                item_datetime = orig_item_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

                if e_vars.country == 'UK':
                    item_date = datetime.strptime(orig_item_datetime, '%b %d %Y')
                else:
                    item_date = datetime.strptime(orig_item_datetime, '%d %b %Y')
                item_date = item_date.replace(hour=0, minute=0, second=0, microsecond=0)
                days_before_date = min(item_date, days_before_date)

            except Exception as e:
                if e_vars.verbose: print('sp_get_datetime-3', e, sp_link)
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
                            if e_vars.country == 'UK':
                                item_date = datetime.strptime(date_txt, "%d %b %Y")
                            else:
                                item_date = datetime.strptime(date_txt, "%b %d %Y")
                    days_before_date = min(item_date, days_before_date)

                except Exception as e:
                    if e_vars.verbose: print('sp_get_datetime-4', e, sp_link)

    return item_date, item_datetime, days_before_date


def ebay_scrape(xml_file,
                xml_file_name: str,
                query: str,
                df: pd.DataFrame,
                adapter: requests,
                e_vars: EbayVariables,
                min_date: datetime = datetime(2020, 1, 1),
                max_date: datetime = datetime(2020, 1, 1)) -> pd.DataFrame:
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
            item_link = ''
            if e_vars.verbose: print('sp_get_item_link', e)
        return item_link

    def sp_get_domestic(item):
        try:
            item_domestic = str(item.find('span', class_='s-item__location').text).startswith("From ") == False
        except Exception as e:
            # failed to find item location, meaning the item is domestic
            item_domestic = True
            if e_vars.verbose: print('sp_get_domestic', e)
        return item_domestic

    def sp_get_title(item):
        try:
            item_title = item.find('h3', class_='s-item__title').text
        except Exception as e:
            item_title = ''
            if e_vars.verbose: print('sp_get_title', e, item_link)
        return item_title

    def sp_get_desc(item):
        try:
            item_desc = item.find('div', class_='s-item__subtitle').text
        except Exception as e:
            item_desc = ''
            if e_vars.verbose: print('sp_get_desc', e, item_link)
        return item_desc

    def sp_get_price(item):
        try:
            item_price = item.find('span', class_='s-item__price').text
            item_price = float(re.sub(r'[^\d.]+', '', item_price))
        except Exception as e:
            item_price = -1
            if e_vars.verbose: print('sp_get_price', e, item_link)
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
            if e_vars.verbose: print('sp_get_shipping', e, item_link)
        return item_shipping

    def ip_get_datetime(item_soup, days_before_date):
        item_date, item_datetime = '', ''
        try:
            date_one = item_soup.find('div', attrs={'class': 'u-flL vi-bboxrev-posabs vi-bboxrev-dsplinline'})
            date_one = date_one.find('span', attrs={'id': 'bb_tlft'})
            date_one = date_one.text.replace("\n", " ").replace(",", "").strip().split()

            try:
                # Normally eBay stores the date as a 12 hour time, but at times it's 24 hour
                if e_vars.country == 'UK':
                    item_datetime = datetime.strptime(f"{date_one[0]} {date_one[1]} {date_one[2]} {date_one[3]}",
                                                      "%d %b %Y %I:%M:%S")
                else:
                    item_datetime = datetime.strptime(f"{date_one[0]} {date_one[1]} {date_one[2]} {date_one[3]}",
                                                      "%b %d %Y %I:%M:%S")
            except Exception as e:
                if e_vars.country == 'UK':
                    item_datetime = datetime.strptime(f"{date_one[0]} {date_one[1]} {date_one[2]} {date_one[3]}",
                                                      "%d %b %Y %H:%M:%S")
                else:
                    item_datetime = datetime.strptime(f"{date_one[0]} {date_one[1]} {date_one[2]} {date_one[3]}",
                                                      "%b %d %Y %H:%M:%S")
            item_datetime = item_datetime.replace(second=0, microsecond=0)
            item_date = item_datetime.replace(hour=0, minute=0)
            days_before_date = min(item_date, days_before_date)

        except Exception as e:
            if e_vars.verbose: print('ip_get_datetime', e, item_link)
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
            if e_vars.verbose: print('ip_get_loc_data-1', e, item_link)
            try:
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
            except Exception as e:
                if e_vars.verbose: print('ip_get_loc_data-2', e, item_link)
        return city, state, country_name

    def ip_get_seller(item_soup):
        seller, seller_fb, store = '', '', False
        try:
            seller_text = item_soup.find_all('span', attrs={'class': 'mbg-nw'})
            seller = seller_text[0].text

            seller_fb_text = item_soup.find_all('span', attrs={'class': 'mbg-l'})
            seller_fb = int(seller_fb_text[0].find('a').text)

            store_id = item_soup.find_all('div', attrs={'id': 'storeSeller'})

            if len(store_id[0].text) > 0:
                store = True
        except Exception as e:
            if e_vars.verbose: print('ip_get_seller', e, item_link)
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
            if e_vars.verbose: print('ip_get_datetime_card', e,
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
                if e_vars.verbose: print('sold_hist_url', sold_hist_url)
                sold_list, sl_date, sl_datetime = get_quantity_hist(sold_hist_url, sold_list, adapter=adapter,
                                                                    e_vars=e_vars)

        except Exception as e:
            if e_vars.verbose: print('ip_get_quant_hist', e, item_link)
        return quantity_sold, multi_list, sold_list, sl_date, sl_datetime

    days_before_date = datetime.today()
    days_before_date = days_before_date.replace(hour=0, minute=0, second=0, microsecond=0)
    comp_date = days_before_date - timedelta(days=e_vars.days_before)

    soup = BeautifulSoup(xml_file, 'lxml')
    items = soup.find_all('li', attrs={'class': 's-item'})

    for n, item in enumerate(items):
        if e_vars.debug or e_vars.verbose: print('----------------------------')
        curr_time = datetime.now()
        if e_vars.verbose: print(curr_time)

        if n > 0 and all(x in sp_get_title(item).upper() for x in query.upper().split()):

            item_link = sp_get_item_link(item)
            if e_vars.debug or e_vars.verbose: print('URL:', item_link)

            item_date, item_datetime, days_before_date = sp_get_datetime(item, days_before_date, e_vars, xml_file_name)
            if e_vars.debug or e_vars.verbose: print('Date-1:', item_date)
            if e_vars.debug or e_vars.verbose: print('Datetime-1:', item_datetime)

            if days_before_date < comp_date or days_before_date < min_date:
                time_break = True
                break

            # Only need to add new records
            line_datetime_found = df[['Link', 'Sold Datetime']].isin(
                    {'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                    axis='columns').any()
            nonmulti_date_line_found = (df[['Link', 'Sold Date', 'Multi Listing']].isin(
                    {'Link': [item_link], 'Sold Date': [item_date], 'Multi Listing': [0]}).all(
                    axis='columns').any())

            # Issue #58 on GitHub
            multi_date_found = (df[['Link', 'Sold Date', 'Multi Listing']].isin(
                    {'Link': [item_link], 'Sold Date': [item_date], 'Multi Listing': [1]}).all(
                    axis='columns').any() and item_date < (max_date - timedelta(2)))

            if e_vars.verbose: print('line_datetime_found', line_datetime_found)
            if e_vars.verbose: print('nonmulti_date_line_found', nonmulti_date_line_found)
            if e_vars.verbose: print('multi_date_found', multi_date_found)

            if not line_datetime_found and not nonmulti_date_line_found and not multi_date_found:

                item_domestic = sp_get_domestic(item)
                if e_vars.debug or e_vars.verbose: print('Domestic:', item_domestic)

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
                    isource = request_link(item_link, adapter, cache=False, e_vars=e_vars, page_type='Item')

                    item_soup = BeautifulSoup(isource, 'lxml')

                    # Check if this is the original item, or eBay trying to sell another item and having a redirect
                    oitems = item_soup.find_all('div', attrs={'class': 'nodestar-item-card-details__title'})

                    if len(oitems) > 0:
                        if e_vars.debug or e_vars.verbose: print(
                                'Search Link goes to similar item, finding original')
                        try:
                            oitems = item_soup.find_all('a', attrs={'class': 'nodestar-item-card-details__view-link'})
                            orig_link = oitems[0]['href']
                        except Exception as e:
                            print('Getting other kind of card')
                            items = item_soup.find_all('script')
                            orig_link = re.search('{"_type":"Action","URL":"(.*?)"', items[-1].contents[0]).group(1)

                        if not item_datetime:
                            item_date_temp, item_datetime, days_before_date = ip_get_datetime_card(item_soup,
                                                                                                   days_before_date)
                            if item_date_temp:
                                item_date = item_date_temp
                            if e_vars.debug or e_vars.verbose: print('Date-2:', item_date)
                            if e_vars.debug or e_vars.verbose: print('Datetime-2:', item_datetime)

                        time.sleep(e_vars.sleep_len * random.uniform(0, 1))
                        # We don't want to cache all the calls into the individual listings, they'll never be repeated
                        source = request_link(orig_link, adapter, cache=False, e_vars=e_vars, page_type='Item')

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

                for brand_val in e_vars.brand_list:
                    if brand_val.upper() in title.upper():
                        brand_val = brand_val.replace(' ', '')
                        brand = brand_val

                model = ''
                for model_val in e_vars.model_list:
                    if model_val[0].upper() in title.upper():
                        model = model_val[0].replace(' ', '')
                        brand = model_val[1].replace(' ', '')
                if e_vars.verbose: print('Brand', brand)
                if e_vars.verbose: print('Model', model)

                sold_list = np.array(sold_list)

                ignor_val = 0

                if e_vars.domestic_only and item_domestic == False:
                    ignor_val = 1

                for di in e_vars.desc_ignore_list:
                    if item_desc.upper().find(di.upper()) >= 0:
                        ignor_val = 1
                        break

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
    return df


def ebay_search(query: str,
                e_vars: EbayVariables,
                msrp: float = 0,
                min_price: float = 0,
                max_price: float = 10000,
                min_date: datetime = datetime.now() - timedelta(days=365)) -> pd.DataFrame:
    """
    The main function of the project which searches eBay for a query, gathering all sold listings and outputting a
    dataframe of the search query and generates basic plots on the data.

    Parameters
    ----------
    query : The main query to search on eBay
    e_vars : An instance of EbayVariables
    msrp : The msrp of the item being searched
    min_price : The minimum price to search for
    max_price : The maximum price to search for
    min_date : The earliest eBay sale to scrape, anything before this is discarded

    Returns
    -------
        A dataframe containing the sales history of the search query
    """

    if e_vars.verbose: pd.set_option('display.max_rows', None)
    if e_vars.verbose: pd.set_option('display.max_columns', None)
    if e_vars.verbose: pd.set_option('display.width', None)
    if e_vars.verbose: pd.set_option('display.max_colwidth', None)
    start = time.time()
    print(query)

    start_datetime = datetime.today().strftime("%Y%m%d%H%M%S")
    # https://realpython.com/caching-external-api-requests/
    curr_path = pathlib.Path(__file__).parent.absolute()

    if not os.path.exists('Spreadsheets'):
        os.makedirs('Spreadsheets')

    if not os.path.exists('Images'):
        os.makedirs('Images')

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
        df_dict = {'Title'      : [], 'Brand': [], 'Model': [], 'description': [], 'Price': [], 'Shipping': [],
                   'Total Price': [], 'Sold Date': [], 'Sold Datetime': [], 'Quantity': [], 'Multi Listing': [],
                   'Seller'     : [], 'Seller Feedback': [], 'Link': [], 'Store': [], 'Ignore': [], 'City': [],
                   'State'      : [], 'Country': [], 'Sold Scrape Datetime': []}
        df = pd.DataFrame(df_dict)

        if e_vars.verbose or e_vars.debug: print('ebay_search-df_load:', e)
        if e_vars.run_cached:
            print(
                    f'WARNING: Cannot find "{filename}". In order to use run_cached = True an extract must already exists. Try setting run_cached=False first and rerunning.')
            return None

    try:
        df_sum = pd.read_excel('summary.xlsx', index_col=0, engine='openpyxl')

    except Exception as e:
        if e_vars.verbose: print('Creating summary.xlsx file')
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

    # Load known good/bad user agents
    load_agents('agent_list.xlsx', e_vars)

    start_datetime = datetime.now()

    if not e_vars.run_cached:
        i = 0
        if e_vars.country == 'UK':
            extension = 'co.uk'
            num_check = 193
        else:
            extension = 'com'
            num_check = 201

        if len(df) > 0:
            temp_df = df[df['Ignore'] == 0]
            temp_df = temp_df[temp_df['Total Price'] > 0]
            temp_df = temp_df[temp_df['Multi Listing'] == 0]
            max_date = temp_df['Sold Date'].max()
            if e_vars.verbose: print('max_date:', max_date)
        else:
            max_date = datetime(2020, 1, 1)

        directory = os.getcwd() + '\XMLs\\' + query

        for xml_file in os.listdir(directory):
            if e_vars.verbose: print(xml_file, os.path.isfile(os.path.join(directory, xml_file)))
            if os.path.isfile(os.path.join(directory, xml_file)):
                with open(directory + '\\' + xml_file, 'r', encoding='cp850') as xmlFile:
                    xmlData = xmlFile.read()

                df = ebay_scrape(xmlData, xml_file, query, df, adapter, e_vars=e_vars, min_date=min_date,
                                 max_date=max_date)

                # Best to save semi-regularly in case eBay kills the connection
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
    if not e_vars.run_cached:
        try:
            os.remove(f"{cache_name}.sqlite")
        except Exception as e:
            print(e)
    return df
