# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import time
import datetime
import matplotlib
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
import random
import requests_cache
import math
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


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


def ebay_scrape(base_url, df, adapter, min_date='', feedback=False, quantity_hist=False, sleep_len=0.4, brand_list=[],
                model_list=[], verbose=False, country='USA', debug=False, days_before=999):
    min_date = datetime.datetime.today()
    min_date = min_date.replace(hour=0, minute=0, second=0, microsecond=0)
    comp_date = min_date - datetime.timedelta(days=days_before)

    for x in range(1, 5):

        time.sleep(
                sleep_len * random.uniform(0,
                                           1))  # eBays servers will kill your connection if you hit them too frequently
        url = base_url + str(x)

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

                    orig_item_datetime = str(currentYear) + ' ' + item.find('span', class_='s-item__endedDate').text
                    if country == 'UK':
                        item_datetime = datetime.datetime.strptime(orig_item_datetime, '%Y %d-%b %H:%M')
                    else:
                        item_datetime = datetime.datetime.strptime(orig_item_datetime, '%Y %b-%d %H:%M')

                    # When we run early in the year
                    if currentMonth < 6 and item_datetime.month > 6:
                        last_year = currentYear - 1
                        item_datetime = item_datetime.replace(year=last_year)

                    item_date = item_datetime.replace(hour=0, minute=0)
                    min_date = min(item_date, min_date)

                except Exception as e:
                    if debug or verbose: print('ebay_scrape-orig_item_datetime', e, item_link)
                    try:
                        orig_item_datetime = item.find('span', class_='s-item__title--tagblock__COMPLETED').text
                        orig_item_datetime = orig_item_datetime.replace('Sold item', '').replace('Sold', '').strip()
                        item_datetime = orig_item_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

                        item_date = datetime.datetime.strptime(orig_item_datetime, '%d %b %Y')
                        item_date = item_date.replace(hour=0, minute=0, second=0, microsecond=0)
                        min_date = min(item_date, min_date)

                    except Exception as e:
                        item_datetime = 'None'
                        item_date = 'None'
                        if debug or verbose: print('ebay_scrape-item_datetime', e, item_link)

                if min_date < comp_date:
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
                                   'Ignore'         : ignor_val, 'Store': store}

                        if verbose: print(df__new)

                        if not df[['Link', 'Sold Datetime']].isin(
                                {'Link': [item_link], 'Sold Datetime': [item_datetime]}).all(
                                axis='columns').any() and item_tot > 0 and (quantity_sold - cap_sum) > 0:
                            df = df.append(df__new, ignore_index=True)
                            # Considered processing as went along, more efficient to just remove duplicates in postprocessing
                    else:
                        for sale in sold_list:
                            if sale[2] < datetime.datetime(2020, 9, 15):
                                ignor_val = 1
                            sale_price = item_price
                            if sale[0]:
                                sale_price = sale[0]
                            df__new = {'Title'        : item_title, 'Brand': brand, 'Model': model,
                                       'description'  : item_desc, 'Price': sale_price,
                                       'Shipping'     : item_shipping, 'Total Price': item_tot, 'Sold Date': sale[2],
                                       'Sold Datetime': sale[2], 'Link': item_link, 'Seller': seller,
                                       'Multi Listing': multi_list, 'Quantity': sale[1], 'Seller Feedback': seller_fb,
                                       'Ignore'       : ignor_val, 'Store': store}

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
                                       'Store'        : store}
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


def ebay_plot(query, msrp, df, extra_title_text=''):
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

    fig, ax1 = plt.subplots(figsize=(10, 8))
    color = 'tab:blue'
    plt.title(query.replace("+", " ").split('-', 1)[0].strip() + extra_title_text + ' eBay Sold Prices Over Time')
    ax1.scatter(df['Sold Date'], df['Total Price'], s=10, label='Sold Listing', color=color)
    estimated_shipping = 0

    if msrp > 0:
        # Replace these percentages as need be based on your projections
        estimated_shipping = df.loc[df['Shipping'] > 0]
        estimated_shipping = estimated_shipping['Shipping'].median()
        if math.isnan(estimated_shipping):
            estimated_shipping = 0
        est_tax = 0.0625

        pp_flat_fee = 0.30
        pp_fee_per = 0.029

        est_ebay_fee = 0.1
        min_be_ebay_fee = 0.036  # Basically the best ebay fee percentage possible
        msrp_discount = 0.05  # If drop scalpers are buying off of Amazon with an Amazon Prime account and credit card, they
        # can get 5% cash back, so effectively the MSRP is 5% lower

        est_break_even = round(
                (msrp * (1 + est_tax)) / (1 - est_ebay_fee - pp_fee_per) + pp_flat_fee + estimated_shipping)
        min_break_even = round((msrp * (1 - msrp_discount)) / (1 - min_be_ebay_fee - pp_fee_per) + pp_flat_fee)

        ax1.axhline(y=est_break_even, label='Est. Scalper Break Even - $' + str(int(est_break_even)), color=color,
                    dashes=[2, 2])
        ax1.axhline(y=min_break_even, label='Min Scalper Break Even - $' + str(int(min_break_even)), color=color,
                    dashes=[4, 1])

        # Estimated assuming 6.25% tax, $15 shipping, and the multiplier for ebay/Paypal fees determined by
        # https://www.ebayfeescalculator.com/usa-ebay-calculator/ where not an eBay store, seller is above standard, and
        # paying with PayPal with Item Category being Computers/Tablets & Networking

        ax1.axhline(y=msrp, label='MSRP - $' + str(msrp), color=color)
    ax1.plot(med_price, color='cyan', label='Median Price - $' + str(median_price))
    # plt.plot(sold_date, m * sold_date + b)
    ax1.set_ylabel("Sold Price", color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', rotation=30)
    formatter = ticker.FormatStrFormatter('$%1.0f')
    ax1.yaxis.set_major_formatter(formatter)
    ax1.set_xlabel("Sold Date")
    ax1.set_ylim(top=min(1.5 * max_med, max_max), bottom=min(min_min * 0.95, msrp * 0.95))

    color = 'tab:red'
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel("Quantity Sold", color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    tot_sold = int(df['Quantity'].sum())
    ax2.plot(count_sold[:-1], color=color, label='Total Sold - ' + str(tot_sold))

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
        ax3.plot(x, mymodel, dashes=[4, 1], label='Linear Trend Line')
    elif msrp > 0:
        ax3.plot(x, mymodel, dashes=[4, 1], label='Linear Trend Line - Est MSRP Date - ' + str(est_msrp))

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
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3)

    plt.savefig('Images/' + query + extra_title_text)
    plt.show()

    return median_price, est_break_even, min_break_even, tot_sold, estimated_shipping


def ebay_search(query, adapter, msrp=0, min_price=0, max_price=10000, min_date=datetime.datetime(2020, 1, 1),
                days_before=999,
                verbose=False, extra_title_text='', run_cached=False, feedback=False, quantity_hist=False,
                sleep_len=0.4, brand_list=[], model_list=[], sacat=0, country='USA', debug=False, store_rate=0.04,
                non_store_rate=0.1):
    start = time.time()
    requests_cache.clear()
    print(query)

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
                'Seller'     : [], 'Seller Feedback': [], 'Link': [], 'Store': []}
        df = pd.DataFrame(dict)
        df = df.astype({'Brand': 'object'})
        df = df.astype({'Model': 'object'})

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
            url = 'https://www.ebay.' + extension + '/sch/i.html?_from=R40&_nkw=' + str(
                    query.replace(" ", "+").replace(',', '%2C').replace('(', '%28').replace(')',
                                                                                            '%29')) + '&_sacat=' + str(
                    sacat) + '&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=' + str(
                    price_ranges[i]) + '&_udhi=' + str(
                    price_ranges[i + 1]) + '&rt=nc&_ipg=200&_dmd=1&_pgn=4'

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
            url = 'https://www.ebay.' + extension + '/sch/i.html?_from=R40&_nkw=' + str(
                    query.replace(" ", "+").replace(',', '%2C').replace('(', '%28').replace(')',
                                                                                            '%29')) + '&_sacat=' + str(
                    sacat) + '&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=' + str(
                    price_ranges[i]) + '&_udhi=' + str(
                    price_ranges[i + 1]) + '&rt=nc&_ipg=200&_pgn='
            if verbose: print(price_ranges[i], price_ranges[i + 1], url)

            df = ebay_scrape(url, df, adapter, min_date, feedback=feedback, quantity_hist=quantity_hist,
                             sleep_len=sleep_len,
                             brand_list=brand_list, model_list=model_list, verbose=verbose, country=country,
                             debug=debug, days_before=days_before)

            # Best to save semiregularly in case eBay kills the connection
            df = pd.DataFrame.drop_duplicates(df)
            df.to_excel('Spreadsheets/' + str(query) + extra_title_text + '.xlsx', engine='openpyxl')
            requests_cache.remove_expired_responses()

    df = df[df['Ignore'] == 0]
    if min_date:
        df = df[df['Sold Date'] >= min_date]

    median_price, est_break_even, min_break_even, tot_sold, estimated_shipping = ebay_plot(query, msrp, df,
                                                                                           extra_title_text)

    ebay_profit, pp_profit, scalp_profit = plot_profits(df, query.replace("+", " ").split('-', 1)[
        0].strip() + extra_title_text, msrp,
                                                        store_ebay_rate=store_rate, non_store_ebay_rate=non_store_rate)

    last_week = df.loc[
        df['Sold Date'] >= (datetime.datetime.now() - datetime.timedelta(days=7)).replace(hour=0, minute=0, second=0,
                                                                                          microsecond=0)]
    tot_sales = (df['Total Price'] * df['Quantity']).sum()
    tot_ini_sales = (df['Price'] * df['Quantity']).sum()

    print('Past Week Median Price: $' + str(last_week['Total Price'].median()))
    print('Median Price: $' + str(median_price))
    print('Past Week Average Price: $' + str(round(last_week['Total Price'].mean(), 2)))
    print('Average Price: $' + str(round(df['Total Price'].mean(), 2)))
    print('Total Sold: ' + str(tot_sold))
    print('Total Sales: $' + str(round(tot_sales, 2)))
    print('PayPal Profit: $' + str(int(pp_profit)))
    print('Est eBay Profit: $' + str(int(ebay_profit)))
    print('Est eBay + PayPal Profit: $' + str(int(ebay_profit + pp_profit)))
    if msrp > 0:
        total_scalp_val = round(tot_sales - tot_sold * (msrp * 1.0625 + estimated_shipping), 2)
        print('Total Scalpers/eBay Profit: $' + str(total_scalp_val))
        print('Estimated Scalper Profit: $' + str(round(scalp_profit)))
        print('Estimated Break Even Point for Scalpers: $' + str(est_break_even))
        print('Minimum Break Even Point for Scalpers: $' + str(min_break_even))
    elapsed = time.time() - start
    print("Runtime: %02d:%02d:%02d" % (elapsed // 3600, elapsed // 60 % 60, elapsed % 60))
    print('')
    return df


def median_plotting(dfs, names, title, roll=0, msrps=[], min_msrp=100):
    colors = ['#000000', '#7f0000', '#808000', '#008080', '#000080', '#ff8c00', '#2f4f4f', '#00ff00', '#0000ff',
              '#ff00ff', '#6495ed', '#ff1493', '#98fb98', '#ffdab9']
    plt.figure()  # In this example, all the plots will be in one figure.
    plt.ylabel("% of MSRP")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)
    if roll > 0:
        plt.title(title + ' ' + str(roll) + ' Rolling Average')
    else:
        plt.title(title)
    for i in range(len(dfs)):
        ci = i % (len(colors) - 1)

        dfs[i] = dfs[i][dfs[i]['Total Price'] > 0]
        dfs[i] = dfs[i][dfs[i]['Quantity'] > 0]
        dfs[i] = dfs[i].loc[dfs[i].index.repeat(dfs[i]['Quantity'])]
        dfs[i]['Quantity'] = 1

        med_price = dfs[i].groupby(['Sold Date'])['Total Price'].median() / msrps[i] * 100

        if roll > 0:
            med_price = med_price.rolling(roll, min_periods=1).mean()

        min_msrp = min(min_msrp, min(med_price))
        plt.plot(med_price, colors[ci], label=names[i])
    plt.ylim(bottom=min_msrp)
    plt.legend()
    plt.tight_layout()
    if roll > 0:
        plt.savefig("Images/" + title + ' ' + str(roll) + ' Rolling Average')
    else:
        plt.savefig("Images/" + title)
    plt.show()


# https://tylermarrs.com/posts/pareto-plot-with-matplotlib/
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
        plt.title(title + ' ' + str(roll) + ' Rolling Average')
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
        plt.savefig("Images/" + title + ' ' + str(roll) + ' Rolling Average')
    else:
        plt.savefig("Images/" + title)

    plt.show()


def plot_profits(df, title, msrp, store_ebay_rate=0.04, non_store_ebay_rate=0.09):
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
                                           - (msrp * 1.0625 + estimated_shipping) \
                                           - (df['Total Price'] * store_ebay_rate) \
                                           - (df['Total Price'] * 0.029 + 0.30)) + ((1 - df['Store']) * (
            df['Total Price'] \
            - (msrp * 1.0625 + estimated_shipping) \
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
    ax1.set_ylabel("Sales/Profits Dollars ($)")
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

    ax2.plot(df['Sold Date'], df['Total Price'], color='red', label='Total Sales ($)')
    ax2.plot(df['Sold Date'], df['Scalper Profits'], '-', color='darkred', label='Scalper Profits')

    ax2.tick_params(axis='y', colors='red')
    ax2.tick_params(axis='x', rotation=30)
    ax2.set_xlabel("Sold Date")
    ax2.set_ylabel("Sales/Profits Dollars ($)", color='r')

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


run_all_feedback = True
run_all_hist = True
run_cached = True
sleep_len = 10
country = 'USA'
debug = False
days_before = 4

comp_store_rate = 0.04
comp_non_store_rate = 0.1
vg_store_rate = 0.0915
vg_non_store_rate = 0.1

graphics_card_sacat = 27386
cpu_sacat = 164
mobo_sacat = 1244
psu_sacat = 42017
ssd_sacat = 175669
memory_sacat = 170083
comp_case_sacat = 42014
cpu_cooler_sacat = 131486

brand_list = ['FOUNDER', 'ASUS', 'MSI', 'EVGA', 'GIGABYTE', 'ZOTAC', 'XFX', 'PNY', 'SAPPHIRE', 'COLORFUL', 'ASROCK',
              'POWERCOLOR', 'INNO3D', 'PALIT', 'VISIONTEK', 'DELL']
model_list = [['XC3', 'EVGA'], ['TRINITY', 'ZOTAC'], ['FTW3', 'EVGA'], ['FOUNDER', 'FOUNDER'], ['STRIX', 'ASUS'],
              ['EKWB', 'ASUS'], ['TUF', 'ASUS'], ['SUPRIM', 'MSI'], ['VENTUS', 'MSI'], ['MECH', 'MSI'],
              ['EVOKE', 'MSI'], ['TRIO', 'MSI'], ['KINGPIN', 'EVGA'], ['K|NGP|N', 'EVGA'], ['AORUS', 'GIGABYTE'],
              ['WATERFORCE', 'GIGABYTE'], ['XTREME', 'GIGABYTE'], ['MASTER', 'GIGABYTE'], ['AMP', 'ZOTAC'],
              [' FE ', 'FOUNDER'], ['TWIN EDGE', 'ZOTAC'], ['POWER COLOR', 'POWERCOLOR'], ['ALIENWARE', 'DELL']]

requests_cache.install_cache('main_cache', backend='sqlite', expire_after=300)
retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504, 404],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1

)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)
# https://realpython.com/caching-external-api-requests/


df_darkhero = ebay_search('ASUS Dark Hero -image -jpeg -img -picture -pic -jpg', http, 399, 400, 1000,
                          run_cached=run_cached,
                          feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                          sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug,
                          sacat=mobo_sacat,
                          days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

# Zen 3 Analysis
df_5950x = ebay_search('5950X -image -jpeg -img -picture -pic -jpg', http, 799, 400, 2200, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       country=country, debug=debug, days_before=days_before, store_rate=comp_store_rate,
                       non_store_rate=comp_non_store_rate, sacat=cpu_sacat)
df_5900x = ebay_search('5900X -image -jpeg -img -picture -pic -jpg', http, 549, 499, 2050, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       country=country, debug=debug, days_before=days_before, store_rate=comp_store_rate,
                       non_store_rate=comp_non_store_rate, sacat=cpu_sacat)
df_5800x = ebay_search('5800X -image -jpeg -img -picture -pic -jpg', http, 449, 400, 1000, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       country=country, debug=debug, days_before=days_before, store_rate=comp_store_rate,
                       non_store_rate=comp_non_store_rate, sacat=cpu_sacat)
df_5600x = ebay_search('5600X -image -jpeg -img -picture -pic -jpg', http, 299, 250, 1000, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 11, 1),
                       sleep_len=sleep_len, country=country, extra_title_text='', debug=debug, days_before=days_before,
                       store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

# Zen 3 Plotting
median_plotting([df_5600x, df_5800x, df_5900x, df_5950x],
                ['5600X', '5800X', '5900X', '5950X'], 'Zen 3 Median Pricing', roll=0,
                msrps=[299, 449, 549, 799])

median_plotting([df_5600x, df_5800x, df_5900x, df_5950x],
                ['5600X', '5800X', '5900X', '5950X'], 'Zen 3 Median Pricing', roll=7,
                msrps=[299, 449, 549, 799])

df_5600X = df_5600x.assign(item='5600X')
df_5800X = df_5800x.assign(item='5800X')
df_5900X = df_5900x.assign(item='5900X')
df_5950X = df_5950x.assign(item='5950X')

frames = [df_5600X, df_5800X, df_5900X, df_5950X]
com_df = pd.concat(frames)
ebay_seller_plot('Zen 3', com_df, extra_title_text='')

# Big Navi Analysis
df_6800 = ebay_search('RX 6800 -XT -image -jpeg -img -picture -pic -jpg', http, 579, 400, 2500,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)
df_6800xt = ebay_search('RX 6800 XT -image -jpeg -img -picture -pic -jpg', http, 649, 850, 2000,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist,
                        extra_title_text='', sleep_len=sleep_len, brand_list=brand_list,
                        model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate,
                        non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)  # There are some $5000+, but screw with graphs
df_6900 = ebay_search('RX 6900 -image -jpeg -img -picture -pic -jpg', http, 999, 100, 999999, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 12, 8),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list,
                      model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)  # Not out until December 8

# Big Navi Plotting
median_plotting([df_6800, df_6800xt, df_6900], ['RX 6800', 'RX 6800 XT', 'RX 6900'], 'Big Navi Median Pricing', roll=0,
                msrps=[579, 649, 999])

df_6800 = df_6800.assign(item='6800')
df_6800xt = df_6800xt.assign(item='6800XT')
df_6900 = df_6900.assign(item='6900')

frames = [df_6800, df_6800xt, df_6900]
com_df = pd.concat(frames)
ebay_seller_plot('Big Navi', com_df, extra_title_text='')

brand_plot([df_6800, df_6800xt, df_6900], 'Big Navi AIB Comparison', brand_list, [579, 649, 999])

brand_plot([df_6800, df_6800xt, df_6900], 'Big Navi AIB Comparison', brand_list, [579, 649, 999], roll=7)


# RTX 30 Series Analysis
df_3060 = ebay_search('RTX 3060 -image -jpeg -img -picture -pic -jpg', http, 399, 200, 1300, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 12, 1),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)
df_3070 = ebay_search('RTX 3070 -image -jpeg -img -picture -pic -jpg', http, 499, 499, 1300, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 10, 29),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)
df_3080 = ebay_search('RTX 3080 -image -jpeg -img -picture -pic -jpg', http, 699, 550, 10000, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 17),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)
df_3090 = ebay_search('RTX 3090 -image -jpeg -img -picture -pic -jpg', http, 1499, 550, 10000,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 17),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)

# RTX 30 Series/Ampere Plotting
median_plotting([df_3060, df_3070, df_3080, df_3090], ['3060', '3070', '3080', '3090'], 'RTX 30 Series Median Pricing',
                roll=0,
                msrps=[399, 499, 699, 1499])

df_3060 = df_3060.assign(item='3060')
df_3070 = df_3070.assign(item='3070')
df_3080 = df_3080.assign(item='3080')
df_3090 = df_3090.assign(item='3090')

frames = [df_3060, df_3070, df_3080, df_3090]
com_df = pd.concat(frames)
ebay_seller_plot('RTX 30 Series-Ampere', com_df, extra_title_text='')

brand_plot([df_3060, df_3070, df_3080, df_3090], 'RTX 30 Series-Ampere AIB Comparison', brand_list,
           [399, 499, 699, 1499])
brand_plot([df_3060, df_3070, df_3080, df_3090], 'RTX 30 Series-Ampere AIB Comparison', brand_list,
           [399, 499, 699, 1499], roll=7)

# Pascal GPUs
df_titanxp = ebay_search('titan xp', http, 1200, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                         quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                         brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                         debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                         sacat=graphics_card_sacat)

df_1080ti = ebay_search('1080 Ti -image -jpeg -img -picture -pic -jpg', http, 699, 225, 1000, feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_1080 = ebay_search('gtx 1080 -Ti -image -jpeg -img -picture -pic -jpg -1080p', http, 599, 140, 1000,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1070 = ebay_search('gtx 1070 -Ti -image -jpeg -img -picture -pic -jpg', http, 379, 75, 600,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1070ti = ebay_search('gtx 1070 Ti -image -jpeg -img -picture -pic -jpg', http, 449, 130, 600,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_1060 = ebay_search('gtx 1060 -image -jpeg -img -picture -pic -jpg', http, 249, 130, 600, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

# Pascal Plotting
df_titanxp = df_titanxp.assign(item='Titan XP')
df_1080ti = df_1080ti.assign(item='1080Ti')
df_1080 = df_1080.assign(item='1080')
df_1070ti = df_1070ti.assign(item='1070Ti')
df_1070 = df_1070.assign(item='1070')
df_1060 = df_1060.assign(item='1060')

frames = [df_1060, df_1070ti, df_1070, df_1080, df_1080ti, df_titanxp]

median_plotting(frames, ['1060', '1070', '1070 Ti', '1080', '1080 Ti', 'Titan XP'],
                'Pascal (GTX 10) series Median Pricing', roll=0,
                msrps=[249, 599, 599, 599, 699, 1200])

# Turing 16 series
df_1650 = ebay_search('gtx 1650 -super -image -jpeg -img -picture -pic -jpg', http, 149, 50, 600,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1650S = ebay_search('gtx 1650 super -image -jpeg -img -picture -pic -jpg', http, 159, 50, 600,
                       feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_1660 = ebay_search('gtx 1660 -ti -super -image -jpeg -img -picture -pic -jpg', http, 219, 50, 600,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1660S = ebay_search('gtx 1660 Super -ti -image -jpeg -img -picture -pic -jpg', http, 229, 50, 600,
                       feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_1660Ti = ebay_search('gtx 1660 Ti -super -image -jpeg -img -picture -pic -jpg', http, 279, 50, 600,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_1650 = df_1650.assign(item='1650')
df_1650S = df_1650S.assign(item='1650S')
df_1660 = df_1660.assign(item='1660')
df_1660S = df_1660S.assign(item='1660S')
df_1660Ti = df_1660Ti.assign(item='1660Ti')

frames = [df_1650, df_1650S, df_1660, df_1660S, df_1660Ti]

median_plotting(frames, ['1650', '1650S', '1660', '1660S', '1660 Ti'], 'Turing (RTX 16) Series Median Pricing', roll=0,
                msrps=[149, 159, 249, 229, 279])

# Turing GPUs
df_2060 = ebay_search('rtx 2060 -super', http, 299, 100, 650, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_2060S = ebay_search('rtx 2060 super', http, 399, 79, 10008, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_2070 = ebay_search('rtx 2070 -super', http, 499, 79, 2800, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_2070S = ebay_search('rtx 2070 super', http, 499, 79, 1600, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_2080 = ebay_search('rtx 2080 -super -ti', http, 699, 250, 1300, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_2080S = ebay_search('rtx 2080 super -ti', http, 699, 299, 1600, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_2080Ti = ebay_search('rtx 2080 ti -super', http, 999, 400, 3800, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

# Turing (RTX 20) Series Plotting

df_2060 = df_2060.assign(item='2060')
df_2060S = df_2060S.assign(item='2060S')
df_2070 = df_2070.assign(item='2070')
df_2080 = df_2080.assign(item='2080')
df_2080S = df_2080S.assign(item='2080S')
df_2080Ti = df_2080Ti.assign(item='2080Ti')

frames = [df_2060, df_2060S, df_2070, df_2080, df_2080S, df_2080Ti]

median_plotting(frames,
                ['2060', '2060S', '2070', '2080', '2080S', '2080 Ti'],
                'Turing (RTX 20) Series Median Pricing', roll=0,
                msrps=[299, 399, 499, 499, 699, 699, 999])

# Vega and Radeon RX 5000 Series (not bothering to separate out 4 vs 8 GB models nor the 50th anniversary
df_5500XT = ebay_search('rx 5500 xt', http, 169, 80, 400, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_5600XT = ebay_search('rx 5600 xt', http, 279, 200, 750, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_5700 = ebay_search('rx 5700 -xt', http, 349, 250, 550, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_5700XT = ebay_search('rx 5700 xt', http, 499, 150, 850, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_vega56 = ebay_search('rx vega 56', http, 399, 0, 500, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_vega64 = ebay_search('rx vega 64', http, 499, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_radeonvii = ebay_search('Radeon VII', http, 699, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                           quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                           brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                           debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                           sacat=graphics_card_sacat)

# Vega and Radeon RX 5000 Series Plotting

df_5500XT = df_5500XT.assign(item='rx 5500 xt')
df_5600XT = df_5600XT.assign(item='rx 5600 xt')
df_5700 = df_5700.assign(item='rx 5700 -xt')
df_5700XT = df_5700XT.assign(item='rx 5700 xt')
df_vega56 = df_vega56.assign(item='rx vega 56')
df_vega64 = df_vega64.assign(item='rx vega 64')
df_radeonvii = df_radeonvii.assign(item='Radeon VII')

frames = [df_5500XT, df_5600XT, df_5700, df_5700XT, df_vega56, df_vega64, df_radeonvii]

median_plotting(frames,
                ['RX 5500 XT', 'RX 5600 XT', 'RX 5700', 'RX 5700 XT', 'RX Vega 56', 'RX Vega 64', 'Radeon VII'],
                'RX 5000 and Vega Series Median Pricing', roll=0,
                msrps=[169, 279, 349, 499, 399, 499, 699])

# Maxwell Series

df_titanx = ebay_search('titan x -xp', http, 1200, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_980Ti = ebay_search('980 Ti', http, 649, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_980 = ebay_search('980 -ti -optiplex', http, 549, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_970 = ebay_search('970', http, 329, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_960 = ebay_search('960 -optiplex', http, 199, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_950 = ebay_search('950 -950m', http, 159, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

# Maxwell Series Plotting

df_titanx = df_titanx.assign(item='Titan X')
df_980Ti = df_980Ti.assign(item='980 Ti')
df_980 = df_980.assign(item='980')
df_970 = df_970.assign(item='970')
df_960 = df_960.assign(item='960')
df_950 = df_950.assign(item='950')

frames = [df_950, df_960, df_970, df_980, df_980Ti, df_titanx]
median_plotting(frames, ['950', '960', '970', '980', '980 Ti', 'Titan X'], 'Maxwell (GTX 900) Series Median Pricing',
                roll=0,
                msrps=[159, 199, 329, 549, 649, 1200])

# Zen 2 data
df_3950X = ebay_search('3950X -image -jpeg -img -picture -pic -jpg', http, 749, 350, 1200, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=False, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3900X = ebay_search('3900X -combo -custom', http, 499, 230, 920, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3900XT = ebay_search('3900XT -combo -custom', http, 499, 200, 800, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3800XT = ebay_search('3800XT -combo -custom', http, 399, 60, 800, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3800X = ebay_search('3800X -combo -custom', http, 399, 60, 600, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3700X = ebay_search('3700X -combo -custom', http, 329, 100, 551, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3600XT = ebay_search('3600XT -combo -custom', http, 249, 149, 600, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3600X = ebay_search('3600X -combo -custom -roku', http, 249, 40, 520, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3600 = ebay_search('(AMD, Ryzen) 3600 -combo -custom -roku -3600x -3600xt', http, 249, 30, 361,
                      run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3300X = ebay_search('3300X -combo -custom', http, 120, 160, 250, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_3100 = ebay_search('(AMD, Ryzen) 3100 -combo -custom -radeon', http, 99, 79, 280, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

# Zen 2 Plotting

df_3950X = df_3950X.assign(item='3950X')
df_3900X = df_3900X.assign(item='3900X')
df_3900XT = df_3900XT.assign(item='3900XT')
df_3800XT = df_3800XT.assign(item='3800XT')
df_3800X = df_3800X.assign(item='3800X')
df_3700X = df_3700X.assign(item='3700X')
df_3600XT = df_3600XT.assign(item='3600XT')
df_3600X = df_3600X.assign(item='3600X')
df_3600 = df_3600.assign(item='3600')
df_3300X = df_3300X.assign(item='3300X')
df_3100 = df_3100.assign(item='3100')

frames = [df_3100, df_3300X, df_3600, df_3600X, df_3600XT, df_3700X, df_3800X, df_3800XT, df_3900XT, df_3900X, df_3950X]

com_df = pd.concat(frames)

median_plotting(frames,
                ['3100', '3300X', '3600', '3600X', '3600XT', '3700X', '3800X', '3800XT', '3900XT', '3900X', '3950X'],
                'Zen 2 Median Pricing', roll=0,
                msrps=[99, 120, 249, 249, 249, 329, 399, 399, 499, 499, 749]
                )

df_i9_10900k = ebay_search('i9 10900k', http, 0, 300, 1000, feedback=run_all_feedback,
                           run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                           brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                           debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i9_9900k = ebay_search('i9 9900k', http, 0, 100, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

# i9 Plotting

df_i9_10900k = df_i9_10900k.assign(item='i9 10900k')
df_i9_9900k = df_i9_9900k.assign(item='i9 9900k')

frames = [df_i9_9900k, df_i9_10900k]
com_df = pd.concat(frames)

median_plotting(frames,
                ['i9 9900k', 'i9 10900k'], 'i9 Median Pricing', roll=0,
                msrps=[488, 488])

# i7 Plotting
df_i7_10700k = ebay_search('i7 10700k', http, 374, 100, 1000, feedback=run_all_feedback,
                           run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                           brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                           debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_9700k = ebay_search('i7 9700k', http, 374, 100, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_8700k = ebay_search('i7 8700k', http, 359, 100, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_7700k = ebay_search('i7 7700k', http, 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_6700k = ebay_search('i7 6700k', http, 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_4790k = ebay_search('i7 4790k', http, 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_4770k = ebay_search('i7 4770k', http, 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_3770k = ebay_search('i7 3770k', http, 342, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_2700k = ebay_search('i7 (2600k, 2700k)', http, 332, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_970 = ebay_search('i7 (970, 980, 980X, 990X)', http, 583, 0, 1000, feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_i7_lynnfield = ebay_search('i7 (860, 970, 870k, 880)', http, 284, 0, 1000, feedback=run_all_feedback,
                              run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='',
                              sleep_len=sleep_len,
                              brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                              debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                              sacat=cpu_sacat)

df_i7_nehalem = ebay_search('i7 (920, 930, 940, 950, 960, 965, 975)', http, 284, 0, 1000, feedback=run_all_feedback,
                            run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                            brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                            debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                            sacat=cpu_sacat)

# i7 Plotting

df_i7_10700k = df_i7_10700k.assign(item='i7 10700k')
df_i7_9700k = df_i7_9700k.assign(item='i7 9700K')
df_i7_8700k = df_i7_8700k.assign(item='i7 8700k')
df_i7_7700k = df_i7_7700k.assign(item='i7 7700k')
df_i7_6700k = df_i7_6700k.assign(item='i7 6700k')
df_i7_4790k = df_i7_4790k.assign(item='i7 4790k')
df_i7_4770k = df_i7_4770k.assign(item='i7 4770k')
df_i7_3770k = df_i7_3770k.assign(item='i7 3770k')
df_i7_2700k = df_i7_2700k.assign(item='i7 2700k')
df_i7_970 = df_i7_970.assign(item='i7 970+')
df_i7_lynnfield = df_i7_lynnfield.assign(item='i7 Lynnfield')
df_i7_nehalem = df_i7_nehalem.assign(item='i7 Nehalem')

frames = [df_i7_nehalem, df_i7_lynnfield, df_i7_970, df_i7_2700k, df_i7_3770k, df_i7_4770k, df_i7_4790k, df_i7_6700k,
          df_i7_7700k, df_i7_8700k, df_i7_9700k, df_i7_10700k]

median_plotting(frames,
                ['i7 Nehalem', 'i7 Lynnfield', 'i7 970+', 'i7 2700k', 'i7 3770k', 'i7 4770k', 'i7 4790k', 'i7 6700k',
                 'i7 7700k', 'i7 8700k', 'i7 9700K', 'i7 10700k'],
                'i7 Median Pricing', roll=0,
                msrps=[284, 284, 583, 332, 342, 339, 339, 339, 339, 359, 374, 374])

#  Zen Series

df_1800X = ebay_search('(amd, ryzen) 1800X', http, 499, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1700X = ebay_search('(amd, ryzen) 1700X', http, 399, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1700 = ebay_search('(amd, ryzen) 1700 -1700X', http, 329, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1600X = ebay_search('(amd, ryzen) 1600X', http, 249, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1600 = ebay_search('(amd, ryzen) 1600', http, 219, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1500X = ebay_search('(amd, ryzen) 1500X', http, 189, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1400 = ebay_search('(amd, ryzen) 1400', http, 169, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1300X = ebay_search('(amd, ryzen) 1300X', http, 129, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1200 = ebay_search('(amd, ryzen) 1200 -intel', http, 109, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

# Zen Plotting

df_1200 = df_1200.assign(item='1200')
df_1300X = df_1300X.assign(item='1300X')
df_1400 = df_1400.assign(item='1400')
df_1500X = df_1500X.assign(item='1500X')
df_1600 = df_1600.assign(item='1600')
df_1600X = df_1600X.assign(item='1600X')
df_1700 = df_1700.assign(item='1700')
df_1700X = df_1700X.assign(item='1700X')
df_1800X = df_1800X.assign(item='1800X')

frames = [df_1200, df_1300X, df_1400, df_1500X, df_1600, df_1600X, df_1700, df_1700X, df_1800X]

com_df = pd.concat(frames)

median_plotting(frames,
                ['1200', '1300X', '1400', '1500X', '1600', '1600X', '1700', '1700X', '1800X'],
                'Zen Median Pricing', roll=0,
                msrps=[109, 129, 169, 189, 219, 249, 329, 399, 499])

#  Zen+ Series

df_2700X = ebay_search('(amd, ryzen) 2700X', http, 329, 100, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_2700 = ebay_search('(amd, ryzen) 2700 -2700X', http, 299, 50, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_2600X = ebay_search('(amd, ryzen) 2600X', http, 229, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_2600 = ebay_search('(amd, ryzen) 2600 -2600X', http, 199, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

df_1600af = ebay_search('(amd, ryzen) 1600 AF', http, 85, 0, 500, feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)

# df_1200af = ebay_search('(amd, ryzen) 1200 AF', http, 60, 0, 500, feedback=run_all_feedback,
#                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
#                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
#                        debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)


# Zen+ Plotting
df_1600af = df_1600af.assign(item='1600AF')
df_2600 = df_2600.assign(item='2600')
df_2600X = df_2600X.assign(item='2600X')
df_2700 = df_2700.assign(item='2700')
df_2700X = df_2700X.assign(item='2700X')

frames = [df_1600af, df_2600, df_2600X, df_2700, df_2700X]

com_df = pd.concat(frames)

median_plotting(frames,
                ['1600AF', '2600', '2600X', '2700', '2700X'],
                'Zen+ Median Pricing', roll=0,
                msrps=[85, 199, 229, 299, 329]
                )

# PS4 Analysis
df_ps4 = ebay_search('ps4 -pro -repair -box -broken -parts -bad', http, 399, 60, 5000, run_cached=run_cached,
                     feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     sacat=139971, country=country, days_before=days_before, debug=debug, store_rate=vg_store_rate,
                     non_store_rate=vg_non_store_rate)
df_ps4_pro = ebay_search('PS4 pro -repair -box -broken -parts -bad', http, 399, 60, 5000, run_cached=run_cached,
                         feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                         sleep_len=sleep_len, sacat=139971, country=country, days_before=days_before, debug=debug,
                         store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)

# PS4 Series Plotting

df_ps4 = df_ps4.assign(item='PS4')
df_ps4_pro = df_ps4_pro.assign(item='PS4 Pro')

frames = [df_ps4, df_ps4_pro]

median_plotting(frames, ['PS4', 'PS4 Pro'], 'PS4 Median Pricing', roll=0,
                msrps=[399, 399])

# Xbox One Analysis
df_xbox_one_s = ebay_search('xbox one s -pro -series -repair -box -broken -parts -bad', http, 299, 60, 11000,
                            run_cached=run_cached,
                            feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                            sleep_len=sleep_len, sacat=139971, country=country, days_before=days_before, debug=debug,
                            store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)
df_xbox_one_x = ebay_search('xbox one x -repair -series -box -broken -parts -bad', http, 499, 100, 11000,
                            run_cached=run_cached,
                            feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                            sleep_len=sleep_len, sacat=139971, country=country, days_before=days_before, debug=debug,
                            store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)

# Xbox One Series Plotting

df_xbox_one_s = df_xbox_one_s.assign(item='Xbox One S')
df_xbox_one_x = df_xbox_one_x.assign(item='Xbox One X')

frames = [df_xbox_one_s, df_xbox_one_x]

median_plotting(frames, ['Xbox One S', 'Xbox One X'], 'Xbox One Median Pricing', roll=0,
                msrps=[299, 499])

# PS5 Analysis (All time)
df_ps5_digital = ebay_search('PS5 Digital -image -jpeg -img -picture -pic -jpg', http, 399, 300, 11000,
                             run_cached=run_cached,
                             feedback=run_all_feedback, quantity_hist=run_all_hist,
                             min_date=datetime.datetime(2020, 9, 16), extra_title_text='', sleep_len=sleep_len,
                             sacat=139971, country=country, days_before=days_before, debug=debug,
                             store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)
df_ps5_disc = ebay_search('PS5 -digital -image -jpeg -img -picture -pic -jpg', http, 499, 450, 11000,
                          run_cached=run_cached,
                          feedback=run_all_feedback, quantity_hist=run_all_hist,
                          min_date=datetime.datetime(2020, 9, 16), extra_title_text='', sleep_len=sleep_len,
                          sacat=139971, country=country, days_before=days_before, debug=debug, store_rate=vg_store_rate,
                          non_store_rate=vg_non_store_rate)

# PS5 Plotting
median_plotting([df_ps5_digital, df_ps5_disc], ['PS5 Digital', 'PS5 Disc'], 'PS5 Median Pricing', roll=0,
                msrps=[299, 499])

df_ps5_digital = df_ps5_digital.assign(item='PS5 Digital')
df_ps5_disc = df_ps5_disc.assign(item='PS5 Disc')

frames = [df_ps5_digital, df_ps5_disc]
com_df = pd.concat(frames)
ebay_seller_plot('PS5', com_df, extra_title_text='')

# Xbox Analysis (All time)
df_xbox_s = ebay_search('Xbox Series S -image -jpeg -img -picture -pic -jpg', http, 299, 250, 11000,
                        run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 22),
                        extra_title_text='', sleep_len=sleep_len, sacat=139971, country=country,
                        days_before=days_before, debug=debug, store_rate=vg_store_rate,
                        non_store_rate=vg_non_store_rate)
df_xbox_x = ebay_search('Xbox Series X -image -jpeg -img -picture -pic -jpg', http, 499, 350, 11000,
                        run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 22),
                        extra_title_text='', sleep_len=sleep_len, sacat=139971, country=country,
                        days_before=days_before, debug=debug, store_rate=vg_store_rate,
                        non_store_rate=vg_non_store_rate)

# Xbox Plotting
median_plotting([df_xbox_s, df_xbox_x], ['Xbox Series S', 'Xbox Series X'], 'Xbox Median Pricing',
                roll=0, msrps=[299, 499])

df_xbox_s = df_xbox_s.assign(item='Xbox Series S')
df_xbox_x = df_xbox_x.assign(item='Xbox Series X')

frames = [df_xbox_s, df_xbox_x]
com_df = pd.concat(frames)
ebay_seller_plot('Xbox', com_df, extra_title_text='')

# Nintendo Switch
df_switch = ebay_search('nintendo switch -lite', http, 300, 0, 2800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, store_rate=vg_store_rate, non_store_rate=vg_non_store_rate,
                        sacat=139971)

df_switch_lite = ebay_search('nintendo switch lite', http, 200, 0, 2800, run_cached=run_cached,
                             feedback=run_all_feedback,
                             quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                             brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                             debug=debug, store_rate=vg_store_rate, non_store_rate=vg_non_store_rate,
                             sacat=139971)

# Nintendo Switch Plotting
median_plotting([df_switch_lite, df_switch], ['Lite', 'Standard'], 'Nintendo Switch Median Pricing', roll=0,
                msrps=[200, 300])

df_switch_lite = df_switch_lite.assign(item='Lite')
df_switch = df_switch.assign(item='Standard')

frames = [df_switch_lite, df_switch]
com_df = pd.concat(frames)
ebay_seller_plot('Nintendo Switch', com_df, extra_title_text='')




df_520 = ebay_search('(nvidia, gtx, geforce, gt) 520 -nvs -quadro', http, 59, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_530 = ebay_search('(nvidia, gtx, geforce, gt) 530 -nvs -quadro -tesla', http, 75, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_545 = ebay_search('(nvidia, gtx, geforce, gt) 545 -nvs -quadro', http, 109, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_550ti = ebay_search('(nvidia, gtx, geforce, gt) 550 ti -nvs -quadro', http, 149, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_560 = ebay_search('(nvidia, gtx, geforce, gt) 560 -ti -nvs -quadro', http, 199, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_570 = ebay_search('(nvidia, gtx, geforce, gt) 570 -nvs -quadro', http, 349, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_580 = ebay_search('(nvidia, gtx, geforce, gt) 580 -nvs -quadro', http, 499, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_590 = ebay_search('(nvidia, gtx, geforce, gt) 590 -nvs -quadro', http, 699, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_520 = df_520.assign(item='520')
df_530 = df_530.assign(item='530')
df_545 = df_545.assign(item='545')
df_550ti = df_550ti.assign(item='550 Ti')
df_560 = df_560.assign(item='560')
df_570 = df_570.assign(item='570')
df_580 = df_580.assign(item='580')
df_590 = df_590.assign(item='590')

frames = [df_520, df_530, df_545, df_550ti, df_560, df_570, df_580, df_590]
median_plotting(frames, ['520', '530', '545', '550 Ti', '560', '570', '580', '590'], 'Fermi (GTX 500) Series Median Pricing',
                roll=0, msrps=[59, 75, 109, 149, 199, 349, 499, 699])


df_605 = ebay_search('(nvidia, gtx, geforce, gt) 605 -nvs -quadro', http, 0, 0, 2000, run_cached=run_cached,
                       feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_610 = ebay_search('(nvidia, gtx, geforce, gt) 610 -nvs -quadro', http, 0, 0, 2000, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)


df_630 = ebay_search('(nvidia, gtx, geforce, gt) 630 -nvs -quadro', http, 0, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_640 = ebay_search('(nvidia, gtx, geforce, gt) 640 -nvs -quadro', http, 100, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_650 = ebay_search('(nvidia, gtx, geforce, gt) 650 -ti -nvs -quadro', http, 110, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_650ti = ebay_search('(nvidia, gtx, geforce, gt) 650 Ti -nvs -quadro', http, 150, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_660 = ebay_search('(nvidia, gtx, geforce, gt) 660 -ti -nvs -quadro', http, 230, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_660ti = ebay_search('(nvidia, gtx, geforce, gt) 660 Ti -nvs -quadro', http, 300, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_670 = ebay_search('(nvidia, gtx, geforce, gt) 670 -nvs -quadro', http, 400, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_680 = ebay_search('(nvidia, gtx, geforce, gt) 680 -nvs -quadro', http, 500, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_690 = ebay_search('(nvidia, gtx, geforce, gt) 690 -nvs -quadro', http, 1000, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_605 = df_605.assign(item='605')
df_610 = df_610.assign(item='610')
df_630 = df_630.assign(item='630')
df_640 = df_640.assign(item='640')
df_650 = df_650.assign(item='650')
df_650ti = df_650ti.assign(item='650 Ti')
df_660 = df_660.assign(item='660')
df_660ti = df_660ti.assign(item='660 Ti')
df_670 = df_670.assign(item='670')
df_680 = df_680.assign(item='680')
df_690 = df_690.assign(item='690')

frames = [df_605, df_610, df_630, df_640, df_650, df_650ti, df_660, df_660ti, df_670, df_680, df_690]
median_plotting(frames, ['605', '610', '630', '640', '650', '650 Ti', '660', '660 Ti', '670', '680', '690'],
                'Kepler (GTX 600) Series Median Pricing',
                roll=0, msrps=[40, 59, 75, 100, 110, 150, 230, 300, 400, 500, 1000])
median_plotting(frames, ['605', '610', '630', '640', '650', '650 Ti', '660', '660 Ti', '670', '680', '690'],
                'Kepler (GTX 600) Series Median Pricing',
                roll=7, msrps=[40, 59, 75, 100, 110, 150, 230, 300, 400, 500, 1000])

df_710 = ebay_search('(nvidia, gtx, geforce, gt) 710 -nvs -quadro', http, 40, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_720 = ebay_search('(nvidia, gtx, geforce, gt) 720 -nvs -quadro', http, 55, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_730 = ebay_search('(nvidia, gtx, geforce, gt) 730 -nvs -quadro', http, 75, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_740 = ebay_search('(nvidia, gtx, geforce, gt) 740 -nvs -quadro', http, 95, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_750 = ebay_search('(nvidia, gtx, geforce, gt) 750 -ti -nvs -quadro', http, 119, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_750ti = ebay_search('(nvidia, gtx, geforce, gt) 750 Ti -nvs -quadro', http, 149, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_760 = ebay_search('(nvidia, gtx, geforce, gt) 760 -nvs -quadro', http, 249, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_770 = ebay_search('(nvidia, gtx, geforce, gt) 770 -nvs -quadro', http, 399, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_780 = ebay_search('(nvidia, gtx, geforce, gt) 780 -ti -nvs -quadro', http, 649, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_780ti = ebay_search('(nvidia, gtx, geforce, gt) 780 ti -nvs -quadro', http, 699, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_titanblack = ebay_search('(nvidia, gtx, geforce, gt) titan black -nvs -quadro', http, 999, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_titanz = ebay_search('(nvidia, gtx, geforce, gt) titan Z -nvs -quadro', http, 2999, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)



df_710 = df_710.assign(item='710')
df_720 = df_720.assign(item='720')
df_730 = df_730.assign(item='730')
df_740 = df_740.assign(item='740')
df_750 = df_750.assign(item='750')
df_750ti = df_750ti.assign(item='750 Ti')
df_760 = df_760.assign(item='760')
df_770 = df_770.assign(item='770')
df_780 = df_780.assign(item='780')
df_780ti = df_780ti.assign(item='780 Ti')
df_titanblack = df_titanblack.assign(item='Titan Black')
df_titanz = df_titanz.assign(item='Titan Z')

frames = [df_710, df_720, df_730, df_740, df_750, df_750ti, df_760, df_770, df_780, df_780ti, df_titanblack, df_titanz]
median_plotting(frames, ['710', '720', '730', '740', '750', '750 Ti', '760', '770', '780', '780 Ti', 'Titan Black', 'Titan Z'],
                'Maxwell-Kepler (GTX 700) Series Median Pricing',
                roll=0, msrps=[40, 55, 75, 95, 119, 149, 249, 399, 649, 699, 999, 2999])
median_plotting(frames, ['710', '720', '730', '740', '750', '750 Ti', '760', '770', '780', '780 Ti', 'Titan Black', 'Titan Z'],
                'Maxwell-Kepler (GTX 700) Series Median Pricing',
                roll=7, msrps=[40, 55, 75, 95, 119, 149, 249, 399, 649, 699, 999, 2999])



'''df_b550 = ebay_search('b550', http, 0, 0, 600, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                      sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, sacat=mobo_sacat,
                      days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_X570 = ebay_search('x570', http, 0, 0, 2000, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                      sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, sacat=mobo_sacat,
                      days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_power = ebay_search('power', http, 0, 0, 2000, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                       sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, sacat=psu_sacat,
                       days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_ddr4 = ebay_search('ddr4 -laptop -rdimm -ecc -lrdimm -notebook', http, 0, 0, 2000, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                      sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug,
                      sacat=memory_sacat,
                      days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_cooler = ebay_search('cooler', http, 0, 0, 2000, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                        sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug,
                        sacat=cpu_cooler_sacat,
                        days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_ssd = ebay_search('ssd -portable -nas -external', http, 0, 0, 20000, run_cached=run_cached,
                     feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                     sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, sacat=ssd_sacat,
                     days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

# Xbox Analysis (Post Launch)
df_xbox_s_ld = ebay_search('Xbox Series S -image -jpeg -img -picture -pic -jpg', http, 299, 250, 11000,
                           min_date=datetime.datetime(2020, 11, 10), run_cached=True, extra_title_text=' (Post Launch)',
                           country=country, days_before=days_before, debug=debug, store_rate=vg_store_rate,
                           non_store_rate=vg_non_store_rate)
df_xbox_x_ld = ebay_search('Xbox Series X -image -jpeg -img -picture -pic -jpg', http, 499, 350, 11000,
                           min_date=datetime.datetime(2020, 11, 10), run_cached=True, extra_title_text=' (Post Launch)',
                           country=country, days_before=days_before, debug=debug, store_rate=vg_store_rate,
                           non_store_rate=vg_non_store_rate)
median_plotting([df_xbox_s_ld, df_xbox_x_ld], ['Xbox Series S', 'Xbox Series X'], 'Xbox Median Pricing (Post Launch)',
                [299, 499])

# PS5 Analysis (Post Launch)
df_ps5_digital_ld = ebay_search('PS5 Digital -image -jpeg -img -picture -pic -jpg', http, 399, 300, 11000,
                                min_date=datetime.datetime(2020, 11, 12), run_cached=True,
                                extra_title_text=' (Post Launch)', country=country, days_before=days_before,
                                debug=debug, store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)
df_ps5_disc_ld = ebay_search('PS5 -digital -image -jpeg -img -picture -pic -jpg', http, 499, 450, 11000,
                             min_date=datetime.datetime(2020, 11, 12), run_cached=True,
                             extra_title_text=' (Post Launch)', country=country, days_before=days_before, debug=debug,
                             store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)
median_plotting([df_ps5_disc_ld, df_ps5_digital_ld], ['PS5 Digital', 'PS5 Disc'], 'PS5 Median Pricing (Post Launch)',
                [299, 499])'''

# TODO: Model MSRP https://db.premiumbuilds.com/graphics-cards/
# TODO: Rerun multis, delete all first
# TODO: Get stockx listings (need to be manual)
# TODO: Count CL, FB, OfferUp listings
# TODO: Run all for UK
# TODO: Size dots at given price point

# TODO: Anonymize data

# TODO: "in 24 hours"

# TODO: Determine ebay "stock"
'''
Ways to predict future pricing:
1. Simple Moving Averages (SMA)
2. Weighted Moving Averages (WMA)
3. Exponential Moving Averages (EMA)
4. Moving Average Convergence Divergence (MACD)
5. Bollinger Bands

LSTM in Tensorflow
RNN
ARIMA type of model are all linear model

https://towardsdatascience.com/introduction-to-technical-indicators-and-its-implementation-using-python-155ae0fb51c9

https://docs.aws.amazon.com/sagemaker/latest/dg/deepar.html

Monte Carlo simulation


General ways to figure out how to analyze data:
https://www.edx.org/course/introduction-to-analytics-modeling
http://omscs.gatech.edu/isye-6501-intro-analytics-modeling


Other sources to scrape:
Consider scraping: https://stockx.com/amd-ryzen-9-5950x-processor
https://www.nowinstock.net/computers/videocards/nvidia/rtx3080/full_history.php
https://www.reddit.com/r/dataisbeautiful/comments/k93xt8/oc_ps5_online_availability_since_launch/
OfferUp
CL, FB, World of Mouth, DMs, twitter

Make visualizations in Tableau


I'm late to the party, but has scalping noticeably affected the market for games themselves & other related goods? E.g. 
4K TVs, VR sets, Series X games, Desktop power supplies
If scalping is inhibiting growth in other markets, that may be an important argument to make for anti scalping legislation
'''
