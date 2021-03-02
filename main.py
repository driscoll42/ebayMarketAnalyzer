# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import datetime
import math
import os
import random
import re
import time

import matplotlib
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import requests
import requests_cache
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from scipy import stats


# XML Formatter: https://jsonformatter.org/xml-formatter

def get_quantity_hist(sold_hist_url, sold_list, adapter, sleep_len=0.4, verbose=False, debug=False):
    time.sleep(
            sleep_len * random.uniform(0, 1))  # eBays servers will kill your connection if you hit them too frequently
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


def ebay_scrape(base_url, df, adapter, days_before=999, min_date='', feedback=False, quantity_hist=False, sleep_len=0.4,
                brand_list=[], model_list=[], country='USA', debug=False, verbose=False):
    days_before_date = datetime.datetime.today()
    days_before_date = days_before_date.replace(hour=0, minute=0, second=0, microsecond=0)
    comp_date = days_before_date - datetime.timedelta(days=days_before)

    for x in range(1, 5):

        time.sleep(
                sleep_len * random.uniform(0,
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

        if verbose: print(x, len(items), url)

        for n, item in enumerate(items):
            if n > 0:
                try:
                    item_link = item.find('a', class_='s-item__link')['href']
                except Exception as e:
                    item_link = 'None'
                    if debug or verbose: print('ebay_scrape-item_link', e)

                if verbose: print('URL:', item_link)

                try:
                    currentYear = datetime.datetime.now().year
                    currentMonth = datetime.datetime.now().month

                    orig_item_datetime = f"{currentYear} {item.find('span', class_='s-item__endedDate').text}"
                    if country == 'UK':
                        item_datetime = datetime.datetime.strptime(orig_item_datetime, '%Y %d-%b %H:%M')
                    else:
                        item_datetime = datetime.datetime.strptime(orig_item_datetime, '%Y %b-%d %H:%M')

                    # When we run early in the year
                    if currentMonth < 6 and item_datetime.month > 6:
                        last_year = currentYear - 1
                        item_datetime = item_datetime.replace(year=last_year)

                    item_date = item_datetime.replace(hour=0, minute=0)
                    days_before_date = min(item_date, days_before_date)

                except Exception as e:
                    if debug or verbose: print('ebay_scrape-orig_item_datetime', e, item_link)
                    try:
                        orig_item_datetime = item.find('span', class_='s-item__title--tagblock__COMPLETED').text
                        orig_item_datetime = orig_item_datetime.replace('Sold item', '').replace('Sold', '').strip()
                        item_datetime = orig_item_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

                        item_date = datetime.datetime.strptime(orig_item_datetime, '%d %b %Y')
                        item_date = item_date.replace(hour=0, minute=0, second=0, microsecond=0)
                        days_before_date = min(item_date, days_before_date)

                    except Exception as e:
                        item_datetime = 'None'
                        item_date = 'None'
                        if debug or verbose: print('ebay_scrape-item_datetime', e, item_link)

                if days_before_date < comp_date or days_before_date < min_date:
                    time_break = True
                    break

                if verbose: print('Date:', item_date)
                if verbose: print('Datetime:', item_datetime)

                # Only need to add new records
                if not df[['Link', 'Sold Datetime']].isin({'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                        axis='columns').any():

                    try:
                        item_title = item.find('h3', class_='s-item__title').text
                    except Exception as e:
                        item_title = 'None'
                        if debug or verbose: print('ebay_scrape-item_title', e, item_link)

                    if verbose: print('Title:', item_title)

                    try:
                        item_desc = item.find('div', class_='s-item__subtitle').text
                    except Exception as e:
                        item_desc = 'None'
                        if debug or verbose: print('ebay_scrape-item_desc', e, item_link)
                    if verbose: print('Desc: ', item_desc)

                    try:
                        item_price = item.find('span', class_='s-item__price').text
                        item_price = float(re.sub(r'[^\d.]+', '', item_price))
                    except Exception as e:
                        item_price = -1
                        if debug or verbose: print('ebay_scrape-item_price', e, item_link)
                    if verbose: print('Price:', item_price)

                    try:
                        item_shipping = item.find('span', class_='s-item__shipping s-item__logisticsCost').text
                        if item_shipping.upper().find("FREE") == -1:
                            item_shipping = float(re.sub(r'[^\d.]+', '', item_shipping))
                        else:
                            item_shipping = 0
                    except Exception as e:
                        item_shipping = 0
                        if debug or verbose: print('ebay_scrape-item_shipping', e, item_link)

                    if verbose: print('Shipping:', item_shipping)

                    try:
                        item_tot = item_price + item_shipping
                    except Exception as e:
                        item_tot = -1
                        if debug or verbose: print('ebay_scrape-item_tot', e, item_link)

                    if verbose: print('Total:', item_tot)

                    quantity_sold = 1
                    sold_list = []
                    multi_list = False
                    store = False
                    city, state, country_name = '', '', ''

                    if feedback or quantity_hist:
                        try:
                            time.sleep(sleep_len * random.uniform(0, 1))
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
                                    if debug or verbose: print('ebay_scrape-seller-1', e, item_link)
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

                                    if quantity_hist:
                                        sold_hist_url = iitem[0]['href']
                                        sold_list = get_quantity_hist(sold_hist_url, sold_list, adapter=adapter,
                                                                      sleep_len=sleep_len,
                                                                      verbose=verbose)

                                except Exception as e:
                                    sold_hist_url = ''
                                    if debug or verbose: print('ebay_scrape-iitem', e, item_link)

                            except Exception as e:
                                if debug or verbose: print('ebay_scrape-seller-1', e, item_link)
                                try:
                                    oitems = soup.find_all('a',
                                                           attrs={'class': 'nodestar-item-card-details__view-link'})
                                    orig_link = oitems[0]['href']

                                    time.sleep(sleep_len * random.uniform(0, 1))
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
                                        if debug or verbose: print('ebay_scrape-vi-wp', e, item_link)
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

                                        if quantity_hist and quantity_sold > 1:
                                            sold_hist_url = nnitems[0]['href']
                                            sold_list = get_quantity_hist(sold_hist_url, sold_list, adapter=adapter,
                                                                          sleep_len=sleep_len,
                                                                          verbose=verbose)

                                    except Exception as e:
                                        sold_hist_url = ''
                                        if debug or verbose: print('ebay_scrape-nnitems', e, item_link)
                                except Exception as e:
                                    # print(url)
                                    # print(e)
                                    seller = 'None'
                                    seller_fb = 'None'
                                    if debug or verbose: print('ebay_scrape-oitems-2', e, item_link)
                        except Exception as e:
                            seller = 'None'
                            seller_fb = 'None'
                            if debug or verbose: print('ebay_scrape-oitems-1', e, item_link)
                    else:
                        seller = 'None'
                        seller_fb = 'None'

                    if verbose: print('Seller: ', seller)
                    if verbose: print('Seller Feedback: ', seller_fb)
                    if verbose: print('Quantity Sold: ', quantity_sold)
                    if verbose: print()

                    brand = ''
                    title = item_title

                    for b in brand_list:
                        if b.upper() in title.upper():
                            b = b.replace(' ', '')
                            brand = b

                    model = ''
                    for m in model_list:
                        if m[0].upper() in title.upper():
                            m[0] = m[0].replace(' ', '')
                            model = m[0]
                            brand = m[1]
                    if verbose: print('Brand', brand)
                    if verbose: print('Model', model)

                    sold_list = np.array(sold_list)

                    ignor_val = 0
                    if item_desc.upper().find("PARTS ONLY") >= 0 or item_desc.upper().find("BENT PIN") >= 0:
                        ignor_val = 1

                    if sold_list.size == 0:
                        try:
                            cap_sum = df[(df['Link'] == item_link)]['Quantity'].sum()
                        except Exception as e:
                            cap_sum = 0
                            if debug or verbose: print('ebay_scrape-cap_sum', e, item_link)

                        df__new = {'Title'          : item_title, 'Brand': brand, 'Model': model,
                                   'description'    : item_desc, 'Price': item_price,
                                   'Shipping'       : item_shipping, 'Total Price': item_tot, 'Sold Date': item_date,
                                   'Sold Datetime'  : item_datetime, 'Link': item_link, 'Seller': seller,
                                   'Multi Listing'  : multi_list, 'Quantity': quantity_sold - cap_sum,
                                   'Seller Feedback': seller_fb,
                                   'Ignore'         : ignor_val, 'Store': store, 'City': city, 'State': state,
                                   'Country'        : country_name}

                        if verbose: print(df__new)

                        if not df[['Link', 'Sold Datetime']].isin(
                                {'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                                axis='columns').any() and item_tot > 0 and (quantity_sold - cap_sum) > 0:
                            df = df.append(df__new, ignore_index=True)
                            # Considered processing as went along, more efficient to just remove duplicates in postprocessing
                    else:
                        for sale in sold_list:
                            # When scraping multilistings they can go back months, years even which really throws off graphs
                            # Generally best to just ignore values far in the past
                            if sale[2] < datetime.datetime.now() - datetime.timedelta(days=90):
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
        if country == 'UK' and len(items) < 193:
            break
        elif len(items) < 201:
            break
        elif time_break:
            break

    return df


def ebay_plot(query, msrp, df, extra_title_text='', est_tax=0.0625, ccode='$'):
    # Make Linear Regression Trend Line
    # https://stackoverflow.com/questions/59723501/plotting-a-linear-regression-with-dates-in-matplotlib-pyplot
    df_calc = df[df['Total Price'] > 0]
    df_calc = df_calc[df_calc['Quantity'] > 0]

    df_temp = df_calc.loc[df_calc.index.repeat(df_calc['Quantity'])]

    med_price = df_temp.groupby(['Sold Date'])['Total Price'].median()
    max_price = df_calc.groupby(['Sold Date'])['Total Price'].max()
    min_price = df_calc.groupby(['Sold Date'])['Total Price'].min()
    max_med = max(med_price)
    max_max = max(max_price)
    min_min = min(min_price)
    median_price = int(df_calc['Total Price'].median())
    count_sold = df.groupby(['Sold Date'])['Quantity'].sum()
    est_break_even = 0
    min_break_even = 0
    plt.style.use('ggplot')


    fig, ax1 = plt.subplots(figsize=(10, 8))

    color = 'tab:blue'
    plt.title(query.replace("+", " ").split('-', 1)[0].strip() + extra_title_text + ' eBay Sold Prices Over Time',
              size=20)

    ax1.scatter(df['Sold Date'], df['Total Price'], alpha=0.5, s=10, label='Sold Listing', color=color)
    estimated_shipping = 0

    if msrp > 0:
        # Replace these percentages as need be based on your projections
        estimated_shipping = df.loc[df['Shipping'] > 0]
        estimated_shipping = estimated_shipping['Shipping'].median()
        if math.isnan(estimated_shipping):
            estimated_shipping = 0

        pp_flat_fee = 0.30
        pp_fee_per = 0.029

        est_ebay_fee = 0.1
        min_be_ebay_fee = 0.036  # Basically the best ebay fee percentage possible
        msrp_discount = 0.05  # If drop scalpers are buying off of Amazon with an Amazon Prime account and credit card, they
        # can get 5% cash back, so effectively the MSRP is 5% lower

        est_break_even = round(
                (msrp * (1 + est_tax)) / (1 - est_ebay_fee - pp_fee_per) + pp_flat_fee + estimated_shipping)
        min_break_even = round((msrp * (1 - msrp_discount)) / (1 - min_be_ebay_fee - pp_fee_per) + pp_flat_fee)

        ax1.axhline(y=est_break_even, label=f'Est. Scalper Break Even - {ccode}{int(est_break_even)}', color=color,
                    linestyle='dashed',
                    dashes=[2, 2])
        ax1.axhline(y=min_break_even, label=f'Min Scalper Break Even - {ccode}{int(min_break_even)}', color=color,
                    linestyle='dashed',
                    dashes=[4, 1])

        # Estimated assuming 6.25% tax, $15 shipping, and the multiplier for ebay/Paypal fees determined by
        # https://www.ebayfeescalculator.com/usa-ebay-calculator/ where not an eBay store, seller is above standard, and
        # paying with PayPal with Item Category being Computers/Tablets & Networking

        ax1.axhline(y=msrp, label=f'MSRP - {ccode}{msrp}', color=color)
    ax1.plot(med_price, linewidth=3, color='dimgray', label=f'Median Price - {ccode}{median_price}', zorder=999)
    # plt.plot(sold_date, m * sold_date + b)
    ax1.set_ylabel("Sold Price", color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', rotation=30)
    formatter = ticker.FormatStrFormatter(f'{ccode}%1.0f')
    ax1.yaxis.set_major_formatter(formatter)
    ax1.set_xlabel("Sold Date")
    ax1.set_ylim(top=min(1.5 * max_med, max_max), bottom=min(min_min * 0.95, msrp * 0.95))

    color = 'tab:red'
    #ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    #ax2.set_ylabel("Quantity Sold", color=color)
    #ax2.tick_params(axis='y', labelcolor=color)
    tot_sold = int(df['Quantity'].sum())
    # ax2.plot(count_sold[:-1], color=color, label=f'Total Sold - {tot_sold}')

    # Plotting Trendline
    y = df['Total Price']
    x = [i.toordinal() for i in df['Sold Date']]

    slope, intercept, r, p, std_err = stats.linregress(x, y)

    def myfunc(x):
        return slope * x + intercept

    mymodel = list(map(myfunc, x))

    ax3 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    if msrp > 0:
        try:
            est_msrp = datetime.datetime.fromordinal(int((msrp - intercept) / slope)).strftime("%y-%m-%d")
        except Exception as e:
            msrp = 0

    if slope >= 0:
        ax3.plot(df['Sold Date'], mymodel, label='Linear Trend Line', color='blue')
    elif msrp > 0:
        ax3.plot(df['Sold Date'], mymodel,  color='red',                 label=f'Linear Trend Line - Est MSRP Date - {est_msrp}')

        #med_price = med_price.rolling(7, min_periods=1).mean()

        #ax3.plot(med_price, color='red')

    ax3.set_ylim(top=min(1.5 * max_med, max_max), bottom=min(min_min * 0.95, msrp * 0.95))
    ax3.set(yticklabels=[])
    ax3.set(ylabel=None)
    ax3.tick_params(left=False, right=False)

    # instruct matplotlib on how to convert the numbers back into dates for the x-axis
    l = matplotlib.dates.AutoDateLocator()
    f = matplotlib.dates.AutoDateFormatter(l)

    ax3.xaxis.set_major_locator(l)
    ax3.xaxis.set_major_formatter(f)

    lines, labels = ax1.get_legend_handles_labels()
    #lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    plt.subplots_adjust(bottom=0.225)

    ax1.legend(lines + lines3, labels + labels3, bbox_to_anchor=(0, -0.325, 1, 0), loc="lower left",
               mode="expand", ncol=2)

    #ax2.grid(False)
    ax3.grid(False)
    #ax1.set_ylim(top=min(1.5 * max_med, max_max), bottom=0)
    #ax3.set_ylim(top=min(1.5 * max_med, max_max), bottom=0)

    plt.savefig('Images/' + query + extra_title_text)
    plt.show()

    return median_price, est_break_even, min_break_even, tot_sold, estimated_shipping


def ebay_search(query, msrp=0, min_price=0, max_price=10000, min_date=datetime.datetime(2020, 1, 1),
                days_before=999,
                verbose=False, extra_title_text='', run_cached=False, feedback=False, quantity_hist=False,
                sleep_len=0.4, brand_list=[], model_list=[], sacat=0, country='USA', debug=False, store_rate=0.04,
                non_store_rate=0.1, tax_rate=0.0625, ccode='$'):
    start = time.time()
    print(query)

    start_datetime = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    # https://realpython.com/caching-external-api-requests/
    cache_name = f"cache_{start_datetime}"

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
    try:
        df = pd.read_excel('Spreadsheets/' + query + extra_title_text + '.xlsx', index_col=0, engine='openpyxl')
        df = df.astype({'Brand': 'object'})
        df = df.astype({'Model': 'object'})

    except:
        # if file does not exist, create it
        dict = {'Title'      : [], 'Brand': [], 'Model': [], 'description': [], 'Price': [], 'Shipping': [],
                'Total Price': [],
                'Sold Date'  : [], 'Sold Datetime': [], 'Quantity': [], 'Multi Listing': [],
                'Seller'     : [], 'Seller Feedback': [], 'Link': [], 'Store': [], 'Ignore': [],
                'City'       : [], 'State': [], 'Country': []}
        df = pd.DataFrame(dict)
        df = df.astype({'Brand': 'object'})
        df = df.astype({'Model': 'object'})
        if run_cached:
            print(
                    'WARNING: In order to use run_cached = True an extract must already exists. Try setting run_cached=False first and rerunning.')
            return

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

    start_datetime = datetime.datetime.now()

    if not run_cached:
        price_ranges = [min_price, max_price]

        # Determine price ranges to search with
        i = 0
        if country == 'UK':
            extension = 'co.uk'
            num_check = 193
        else:
            extension = 'com'
            num_check = 201

        while i != len(price_ranges) - 1:
            time.sleep(
                    sleep_len * random.uniform(0,
                                               1))  # eBays servers will kill your connection if you hit them too frequently
            fomatted_query = query.replace(' ', '+').replace(',', '%2C').replace('(', '%28').replace(')', '%29')
            url = f"https://www.ebay.{extension}/sch/i.html?_from=R40&_nkw={fomatted_query}&_sacat={sacat}&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo={price_ranges[i]}&_udhi={price_ranges[i + 1]}&rt=nc&_ipg=200&_pgn=4"

            source = adapter.get(url, timeout=10).text
            soup = BeautifulSoup(source, 'lxml')
            items = soup.find_all('li', attrs={'class': 's-item'})
            if verbose: print(price_ranges, len(items), i, price_ranges[i], price_ranges[i + 1], url)

            if len(items) >= num_check and round(price_ranges[i + 1] - price_ranges[i], 2) > 0.01:
                # If there's only one cent difference between the two just increment, we need to do some special logic below
                midpoint = round((price_ranges[i] + price_ranges[i + 1]) / 2, 2)
                price_ranges = price_ranges[:i + 1] + [midpoint] + price_ranges[i + 1:]
            elif len(items) >= num_check and round(price_ranges[i + 1] - price_ranges[i], 2) == 0.01:
                # If there is a one cent difference between the two, we can have eBay just return that specific price to get a little bit finer detail
                price_ranges = price_ranges[:i + 1] + [price_ranges[i]] + [price_ranges[i + 1]] + price_ranges[i + 1:]
                i += 2
            else:
                i += 1

        for i in range(len(price_ranges) - 1):
            fomatted_query = query.replace(' ', '+').replace(',', '%2C').replace('(', '%28').replace(')', '%29')
            url = f"https://www.ebay.{extension}/sch/i.html?_from=R40&_nkw={fomatted_query}&_sacat={sacat}&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo={price_ranges[i]}&_udhi={price_ranges[i + 1]}&rt=nc&_ipg=200&_pgn="

            if verbose: print(price_ranges[i], price_ranges[i + 1], url)

            df = ebay_scrape(url, df, adapter, min_date=min_date, feedback=feedback, quantity_hist=quantity_hist,
                             sleep_len=sleep_len,
                             brand_list=brand_list, model_list=model_list, verbose=verbose, country=country,
                             debug=debug, days_before=days_before)

            # Best to save semiregularly in case eBay kills the connection
            df = pd.DataFrame.drop_duplicates(df)
            df.to_excel(f"Spreadsheets/{query}{extra_title_text}.xlsx", engine='openpyxl')
            requests_cache.remove_expired_responses()

    df = df[df['Ignore'] == 0]
    if min_date:
        df = df[df['Sold Date'] >= min_date]

    median_price, est_break_even, min_break_even, tot_sold, estimated_shipping = ebay_plot(query, msrp, df,
                                                                                           extra_title_text,
                                                                                           est_tax=tax_rate,
                                                                                           ccode=ccode)

    ebay_profit, pp_profit, scalp_profit = plot_profits(df, query.replace("+", " ").split('-', 1)[
        0].strip() + extra_title_text, msrp,
                                                        store_ebay_rate=store_rate, non_store_ebay_rate=non_store_rate,
                                                        tax_rate=tax_rate, ccode=ccode)

    last_week = df.loc[
        df['Sold Date'] >= (datetime.datetime.now() - datetime.timedelta(days=7)).replace(hour=0, minute=0, second=0,
                                                                                          microsecond=0)]
    tot_sales = (df['Total Price'] * df['Quantity']).sum()
    tot_ini_sales = (df['Price'] * df['Quantity']).sum()

    print(f"Past Week Median Price: {ccode}{last_week['Total Price'].median()}")
    print(f"Median Price: {ccode}{median_price}")
    print(f"Past Week Average Price: {ccode}{round(last_week['Total Price'].mean(), 2)}")
    print(f"Average Price: {ccode}{round(df['Total Price'].mean(), 2)}")
    print(f"Total Sold: {tot_sold}")
    print(f"Total Sales: {ccode}{round(tot_sales, 2)}")
    print(f"PayPal Profit: {ccode}{int(pp_profit)}")
    print(f"Est eBay Profit: {ccode}{int(ebay_profit)}")
    print(f"Est eBay + PayPal Profit: {ccode}{int(ebay_profit + pp_profit)}")
    if msrp > 0:
        total_scalp_val = round(tot_sales - tot_sold * (msrp * (1.0 + tax_rate) + estimated_shipping), 2)
        print(f"Total Scalpers/eBay Profit: {ccode}{total_scalp_val}")
        print(f"Estimated Scalper Profit: {ccode}{round(scalp_profit)}")
        print(f"Estimated Break Even Point for Scalpers: {ccode}{est_break_even}")
        print(f"Minimum Break Even Point for Scalpers: {ccode}{min_break_even}")
    elapsed = time.time() - start
    print("Runtime: %02d:%02d:%02d" % (elapsed // 3600, elapsed // 60 % 60, elapsed % 60))
    print('')

    if msrp > 0:
        dict_sum_new = {'Run Datetime'                           : start_datetime,
                        'Country'                                : country,
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
                        'Country'                                : country, 'MSRP': msrp,
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
    df_sum = df_sum.append(dict_sum_new, ignore_index=True)

    df_sum.to_excel('summary.xlsx', engine='openpyxl')
    os.remove(f"{cache_name}.sqlite")
    return df


def median_plotting(dfs, names, title, roll=0, msrps=[], min_msrp=100, ccode='$'):
    colors = ['#000000', '#7f0000', '#808000', '#008080', '#000080', '#ff8c00', '#2f4f4f', '#00ff00', '#0000ff',
              '#ff00ff', '#6495ed', '#ff1493', '#98fb98', '#ffdab9']
    plt.figure()  # In this example, all the plots will be in one figure.
    plt.ylabel("% of MSRP")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)
    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average - % MSRP")
    else:
        plt.title(f"{title} - % MSRP")
    for i in range(len(dfs)):
        ci = i % (len(colors) - 1)

        dfs[i] = dfs[i][dfs[i]['Total Price'] > 0]
        dfs[i] = dfs[i][dfs[i]['Quantity'] > 0]
        dfs[i] = dfs[i].loc[dfs[i].index.repeat(dfs[i]['Quantity'])]
        dfs[i]['Quantity'] = 1

        med_price_scaled = dfs[i].groupby(['Sold Date'])['Total Price'].median() / msrps[i] * 100

        # med_mad = robust.mad(dfs[i].groupby(['Sold Date'])['Total Price']/ msrps[i] * 100)
        # print(med_mad)

        if roll > 0:
            med_price_scaled = med_price_scaled.rolling(roll, min_periods=1).mean()

        min_msrp = min(min_msrp, min(med_price_scaled))
        plt.plot(med_price_scaled, colors[ci], label=names[i])
        # plt.fill_between(med_price_scaled, med_price_scaled - med_mad, med_price_scaled + med_mad, color=colors[ci])
    plt.ylim(bottom=min_msrp)
    plt.legend()
    plt.tight_layout()
    if roll > 0:
        plt.savefig(f"Images/{title} {roll} Day Rolling Average - % MSRP")
    else:
        plt.savefig(f"Images/{title} - % MSRP")
    plt.show()

    # Plotting the non-scaled graph
    plt.figure()  # In this example, all the plots will be in one figure.
    fig, ax = plt.subplots()
    plt.ylabel(f"Median Sale Price ({ccode})")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)
    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average - {ccode}")
    else:
        plt.title(f"{title} - {ccode}")
    for i in range(len(dfs)):
        ci = i % (len(colors) - 1)

        med_price = dfs[i].groupby(['Sold Date'])['Total Price'].median()

        if roll > 0:
            med_price = med_price.rolling(roll, min_periods=1).mean()

        min_msrp = min(min_msrp, min(med_price))
        plt.plot(med_price, colors[ci], label=names[i])
    plt.ylim(bottom=min_msrp)
    formatter = ticker.FormatStrFormatter(f'{ccode}%1.0f')
    ax.yaxis.set_major_formatter(formatter)
    plt.legend()
    plt.tight_layout()
    if roll > 0:
        plt.savefig(f"Images/{title} {roll} Day Rolling Average - {ccode}")
    else:
        plt.savefig(f"Images/{title} - {ccode}")
    plt.show()


# https://tylermarrs.com/posts/pareto-plot-with-matplotlib/
def pareto_plot(df, df2, df3, df_name='', df2_name='', x=None, y=None, title=None, show_pct_y=False,
                pct_format='{0:.0%}'):
    xlabel = x
    ylabel = y

    weights = df3[y] / df3[y].sum()
    cumsum = weights.cumsum()

    plt.figure(figsize=(8, 8))

    fig, ax1 = plt.subplots()

    ax1.bar(df[x], df[y], label=df_name)
    if df2.size > 0:
        ax1.bar(df2[x], df2[y], bottom=df[y], label=df2_name)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.tick_params(axis='x', rotation=30)
    ax1.legend(loc='center right')

    ax2 = ax1.twinx()
    ax2.plot(df3[x], cumsum, '-ro', alpha=0.5)
    ax2.set_ylabel('', color='r')
    ax2.tick_params('y', colors='r')
    ax2.set_ylim(bottom=0)

    vals = ax2.get_yticks()
    ax2.set_yticklabels(['{:,.2%}'.format(x) for x in vals])

    # hide y-labels on right side
    if not show_pct_y:
        ax2.set_yticks([])

    formatted_weights = [pct_format.format(x) for x in cumsum]
    for i, txt in enumerate(formatted_weights):
        ax2.annotate(txt, (df[x][i], cumsum[i]), fontweight='heavy')

    if title:
        plt.title(title)
    fig.tight_layout()
    plt.legend()

    plt.savefig('Images/' + title)
    plt.show()


def ebay_seller_plot(query, df, extra_title_text=''):
    # eBay Seller Feedback vs Quantity Sold

    df_sell = df[df['Seller'] != 'None']
    df_sell = df_sell[df_sell['Seller Feedback'] != 'None']

    df_sell['Seller Feedback'] = pd.to_numeric(df_sell['Seller Feedback'])

    df_stores = df_sell[df_sell['Store'] == 1]
    df_nostores = df_sell[df_sell['Store'] == 0]

    def split_data(df_sell):
        # https://blog.edesk.com/resources/ebay-star-ratings/
        zero_fb = df_sell[df_sell['Seller Feedback'] == 0]['Quantity'].sum()
        no_star = df_sell[(df_sell['Seller Feedback'] > 0) & (df_sell['Seller Feedback'] < 10)]['Quantity'].sum()
        yellow_star = df_sell[(df_sell['Seller Feedback'] >= 10) & (df_sell['Seller Feedback'] < 50)]['Quantity'].sum()
        blue_star = df_sell[(df_sell['Seller Feedback'] >= 50) & (df_sell['Seller Feedback'] < 100)]['Quantity'].sum()
        turquoise_star = df_sell[(df_sell['Seller Feedback'] >= 100) & (df_sell['Seller Feedback'] < 500)][
            'Quantity'].sum()
        purple_star = df_sell[(df_sell['Seller Feedback'] >= 500) & (df_sell['Seller Feedback'] < 1000)][
            'Quantity'].sum()
        red_star = df_sell[(df_sell['Seller Feedback'] >= 1000) & (df_sell['Seller Feedback'] < 5000)]['Quantity'].sum()
        green_star = df_sell[(df_sell['Seller Feedback'] >= 5000) & (df_sell['Seller Feedback'] < 10000)][
            'Quantity'].sum()
        shooting_star = df_sell[(df_sell['Seller Feedback'] >= 10000)]['Quantity'].sum()

        df_fb = pd.DataFrame({
            'Star Category': ['Zero FB', '1 - 9', '10 - 49', '50 - 99', '100 - 499', '500 - 999', '1000 - 4999',
                              '5000 - 9999', '10000+'],
            'Quantity Sold': [zero_fb, no_star, yellow_star, blue_star, turquoise_star, purple_star, red_star,
                              green_star,
                              shooting_star]
        })
        return df_fb

    df_store_fb = split_data(df_stores)
    df_nostores_fb = split_data(df_nostores)
    df_all = split_data(df_sell)

    title = query.replace("+", " ").split('-', 1)[
                0].strip() + extra_title_text + ' eBay Seller Feedback vs Quantity Sold'

    pareto_plot(df_nostores_fb, df_store_fb, df_all, df_name='Non-Store', df2_name='Store', x='Star Category',
                y='Quantity Sold', title=title)

    # eBay Seller Sales vs Total Sold

    df_quant = df[df['Seller'] != 'None']

    df_stores = df_quant[df_sell['Store'] == 1]
    df_nostores = df_quant[df_sell['Store'] == 0]

    def split_data_again(df_quant):
        df_quant = df_quant.groupby(['Seller'])['Quantity'].sum().reset_index()

        one_sale = df_quant[df_quant['Quantity'] == 1]['Quantity'].sum()
        two_sales = df_quant[(df_quant['Quantity'] == 2)]['Quantity'].sum()
        three_sales = df_quant[(df_quant['Quantity'] == 3)]['Quantity'].sum()
        four_sales = df_quant[(df_quant['Quantity'] == 4)]['Quantity'].sum()
        five_sales = df_quant[(df_quant['Quantity'] == 5)]['Quantity'].sum()
        five_ten = df_quant[(df_quant['Quantity'] >= 6) & (df_quant['Quantity'] < 10)]['Quantity'].sum()
        eleven_twenty = df_quant[(df_quant['Quantity'] >= 11) & (df_quant['Quantity'] < 20)]['Quantity'].sum()
        twen_fifty = df_quant[(df_quant['Quantity'] >= 21) & (df_quant['Quantity'] < 50)]['Quantity'].sum()
        fifty_plus = df_quant[(df_quant['Quantity'] >= 50)]['Quantity'].sum()

        df_fb = pd.DataFrame({
            'Number of Sales': ['1', '2', '3', '4', '5', '5 - 10', '11 - 20', '21 - 50', '50 +'],
            'Quantity Sold'  : [one_sale, two_sales, three_sales, four_sales, five_sales, five_ten, eleven_twenty,
                                twen_fifty,
                                fifty_plus]
        })
        return df_fb

    title = query.replace("+", " ").split('-', 1)[0].strip() + extra_title_text + ' eBay Seller Sales vs Total Sold'

    df_store_fb = split_data_again(df_stores)
    df_nostore_fb = split_data_again(df_nostores)
    df_all = split_data_again(df_quant)

    pareto_plot(df_nostore_fb, df_store_fb, df_all, df_name='Non-Store', df2_name='Store', x='Number of Sales',
                y='Quantity Sold', title=title)


def brand_plot(dfs, title, brand_list, msrp, roll=0):
    pd.set_option('display.max_columns', None)

    for i, df in enumerate(dfs):
        dfs[i] = dfs[i][dfs[i]['Total Price'] > 0]
        dfs[i] = dfs[i][dfs[i]['Quantity'] > 0]
        dfs[i] = dfs[i].loc[dfs[i].index.repeat(dfs[i]['Quantity'])]
        dfs[i]['Quantity'] = 1

        for b in brand_list:
            # Get average price by
            print(df['item'].iloc[0], b, round(
                    df[(df['Brand'] == b) & (df['Ignore'] == 0) & (df['Total Price'] <= 3000)]['Total Price'].mean(),
                    2),
                  round(
                          df[(df['Brand'] == b) & (df['Ignore'] == 0) & (df['Total Price'] <= 3000)]['Quantity'].sum(),
                          2))
        dfs[i]['Total Price'] /= msrp[i]

    df = pd.concat(dfs)

    brand_dict = {}
    for b in brand_list:
        brand_dict[b] = df[(df['Brand'] == b) & (df['Ignore'] == 0) & (df['Total Price'] <= 3000)]

    # Picked using this https://mokole.com/palette.html
    colors = ['#000000', '#7f0000', '#808000', '#008080', '#000080', '#ff8c00', '#2f4f4f', '#00ff00', '#0000ff',
              '#ff00ff', '#6495ed', '#ff1493', '#98fb98', '#ffdab9']
    min_msrp = 100
    plt.figure(figsize=(12, 8))  # In this example, all the plots will be in one figure.
    plt.ylabel("% of MSRP")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)

    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average")
    else:
        plt.title(title)

    for i, b in enumerate(brand_list):
        ci = i % (len(colors) - 1)
        if len(brand_dict[b]) > 10:
            print(b, len(brand_dict[b]))

            brand_dict[b] = brand_dict[b][brand_dict[b]['Total Price'] > 0]
            brand_dict[b] = brand_dict[b].loc[brand_dict[b].index.repeat(brand_dict[b]['Quantity'])]
            brand_dict[b]['Quantity'] = 1

            med_price = brand_dict[b].groupby(['Sold Date'])['Total Price'].median() * 100
            if roll > 0:
                med_price = med_price.rolling(roll, min_periods=1).mean()

            min_msrp = min(100, min(med_price))
            max_msrp = min(300, max(med_price))
            plt.plot(med_price, colors[ci], label=brand_list[i])
    plt.ylim(bottom=min_msrp, top=max_msrp)
    plt.legend()
    plt.tight_layout()
    if roll > 0:
        plt.savefig(f"Images/{title} {roll} Day Rolling Average")
    else:
        plt.savefig(f"Images/{title}")

    plt.show()


def plot_profits(df, title, msrp, store_ebay_rate=0.04, non_store_ebay_rate=0.09, tax_rate=0.0625, ccode='$'):
    df = df.copy()

    df = df[df['Ignore'] == 0]
    df = df[df['Total Price'] > 0]
    df = df[df['Quantity'] > 0]
    df = df.sort_values(by=['Sold Date'])

    # Repeat each row quantity times, need for accurate median plotting
    df = df.loc[df.index.repeat(df['Quantity'])]
    df['Quantity'] = 1
    med_price = df.groupby(['Sold Date'])['Total Price'].median() / msrp * 100

    df['Profits'] = 0
    df['eBay Profits'] = 0
    df['Scalper Profits'] = 0
    df['PayPal Profits'] = 0

    estimated_shipping = df.loc[df['Shipping'] > 0]
    estimated_shipping = estimated_shipping['Shipping'].median()
    if math.isnan(estimated_shipping):
        estimated_shipping = 0

    df['eBay Profits'] = df['Total Price'] * non_store_ebay_rate * (1 - df['Store']) \
                         + df['Total Price'] * store_ebay_rate * df['Store']

    df['PayPal Profits'] = df['Total Price'] * 0.029 + 0.30

    df['Scalper Profits'] = df['Store'] * (df['Total Price'] \
                                           - (msrp * (1.0 + tax_rate) + estimated_shipping) \
                                           - (df['Total Price'] * store_ebay_rate) \
                                           - (df['Total Price'] * 0.029 + 0.30)) + ((1 - df['Store']) * (
            df['Total Price'] \
            - (msrp * (1.0 + tax_rate) + estimated_shipping) \
            - (df['Total Price'] * non_store_ebay_rate) \
            - (df['Total Price'] * 0.029 + 0.30)))

    df['Total Sales'] = df['Total Price']

    df = df.groupby(['Sold Date']).agg(
            {'Total Price'    : 'sum', 'Quantity': 'sum', 'eBay Profits': 'sum', 'PayPal Profits': 'sum',
             'Scalper Profits': 'sum'})

    df['Sold Date'] = df.index

    df['Cum Sales'] = df['Total Price'].cumsum()
    df['Cum Quantity'] = df['Quantity'].cumsum()
    df['Cum eBay'] = df['eBay Profits'].cumsum()
    df['Cum PayPal'] = df['PayPal Profits'].cumsum()
    df['Cum Scalper'] = df['Scalper Profits'].cumsum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), tight_layout=True)

    ax1.plot(df['Sold Date'], df['Cum Sales'], color='red', label='Cumulative Sales')
    ax1.plot(df['Sold Date'], df['Cum Scalper'], color='purple', label='Cumulative Scalper Profits')
    ax1.plot(df['Sold Date'], df['Cum eBay'], color='crimson', label='Cumulative eBay Profits')
    ax1.plot(df['Sold Date'], df['Cum PayPal'], color='deeppink', label='Cumulative PayPal Profits')

    ax1.set_ylabel('', color='r')
    ax1.tick_params('y', colors='r')
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y')
    ax1.set_ylabel(f"Sales/Profits ({ccode})")
    ax1.tick_params(axis='x', rotation=30)
    ax1.set_xlabel("Sold Date")

    ax1_2 = ax1.twinx()
    ax1_2.plot(df['Sold Date'], df['Cum Quantity'], color='blue', label='Cumulative Quantity')
    ax1_2.set_ylabel('Quantity Sold', color='blue')
    ax1_2.tick_params('y', colors='b')
    ax1_2.set_ylim(bottom=0)
    ax1_2.set_ylabel("Quantity")

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2)

    ax2.plot(df['Sold Date'], df['Total Price'], color='red', label=f'Total Sales ({ccode})')
    ax2.plot(df['Sold Date'], df['Scalper Profits'], '-', color='darkred', label='Scalper Profits')

    ax2.tick_params(axis='y', colors='red')
    ax2.tick_params(axis='x', rotation=30)
    ax2.set_xlabel("Sold Date")
    ax2.set_ylabel(f"Sales/Profits ({ccode})", color='r')

    ax2_2 = ax2.twinx()
    ax2_2.plot(med_price, color='black', label='Median % of MSRP')
    ax2_2.set_ylabel("Median % of MSRP")
    ax2_2.set_ylim(bottom=100)

    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2)

    fig.tight_layout()
    fig.suptitle(title + ' Cumulative Sales/Profits and Profits over time')
    plt.subplots_adjust(top=0.45)
    plt.savefig('Images/' + title + ' Cumulative Plots')

    plt.show()

    return df['Cum eBay'].iloc[-1], df['Cum PayPal'].iloc[-1], df['Cum Scalper'].iloc[-1]
