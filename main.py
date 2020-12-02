# Initial Code: https://oaref.blogspot.com/2019/01/web-scraping-using-python-part-2.html

import matplotlib
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import numpy as np
import datetime
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats


def ebay_scrape(base_url, df, min_date='', verbose=False):
    for x in range(1, 5):
        time.sleep(0.1)
        url = base_url + str(x)
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        items = soup.find_all('li', attrs={'class': 's-item'})

        if verbose: print(x, len(items), url)

        for n, items in enumerate(items):
            if n > 0:
                try:
                    item_title = items.find('h3', class_='s-item__title').text
                except Exception as e:
                    item_title = 'None'

                if verbose: print(item_title)

                try:
                    item_date = '2020 ' + items.find('span', class_='s-item__endedDate').text
                    item_date = datetime.datetime.strptime(item_date, '%Y %b-%d %H:%M')
                    item_date = item_date.replace(hour=0, minute=0, second=0, microsecond=0)

                except Exception as e:
                    item_date = 'None'

                if verbose: print(item_date)

                try:
                    item_desc = items.find('div', class_='s-item__subtitle').text
                except Exception as e:
                    item_desc = 'None'

                if verbose: print(item_desc)

                try:
                    item_price = items.find('span', class_='s-item__price').text
                    item_price = float(float(item_price.replace('$', '').replace(',', '')))
                except Exception as e:
                    item_price = 'None'

                if verbose: print(item_price)

                try:
                    item_shipping = items.find('span', class_='s-item__shipping s-item__logisticsCost').text
                    if item_shipping.upper().find("FREE") == -1:
                        item_shipping = float(item_shipping.replace('+$', '').replace(' shipping', ''))
                    else:
                        item_shipping = 0
                except Exception as e:
                    item_shipping = 'None'

                if verbose: print(item_shipping)

                try:
                    item_tot = item_price + item_shipping
                except Exception as e:
                    item_tot = 'None'

                if verbose: print(item_shipping)

                try:
                    item_link = items.find('a', class_='s-item__link')['href']
                except Exception as e:
                    item_link = 'None'

                if verbose: print(item_link)
                if verbose: print()

                df__new = {'Title'   : item_title, 'description': item_desc, 'Price': item_price,
                           'Shipping': item_shipping, 'Total Price': item_tot, 'Sold Date': item_date,
                           'Link'    : item_link}

                if 'None' not in str(item_tot) and 'None' not in str(item_date) and (item_date >= min_date):
                    df = df.append(df__new, ignore_index=True)

    return df


def ebay_plot(query, msrp, df):
    # Make Linear Regression Trend Line
    # https://stackoverflow.com/questions/59723501/plotting-a-linear-regression-with-dates-in-matplotlib-pyplot

    med_price = df.groupby(['Sold Date'])['Total Price'].median()
    max_price = df.groupby(['Sold Date'])['Total Price'].max()
    min_price = df.groupby(['Sold Date'])['Total Price'].min()
    max_med = max(med_price)
    max_max = max(max_price)
    min_min = min(min_price)
    median_price = int(df['Total Price'].median())
    count_sold = df.groupby(['Sold Date'])['Total Price'].count()
    est_break_even = 0
    min_break_even = 0

    fig, ax1 = plt.subplots(figsize=(10, 8))
    color = 'tab:blue'
    plt.title(query.replace("+", " ").split('-', 1)[0].strip() + ' eBay Sold Prices Over Time')
    ax1.scatter(df['Sold Date'], df['Total Price'], s=10, label='Sold Listing', color=color)

    if msrp > 0:
        # Replace these percentages as need be based on your projections
        estimated_shipping = df.loc[df['Shipping'] > 0]
        estimated_shipping = estimated_shipping['Shipping'].median()

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
    tot_sold = len(df)
    ax2.plot(count_sold, color=color, label='Total Sold - ' + str(tot_sold))

    # Plotting Trendline
    y = df['Total Price']
    x = [i.toordinal() for i in df['Sold Date']]

    slope, intercept, r, p, std_err = stats.linregress(x, y)

    def myfunc(x):
        return slope * x + intercept

    mymodel = list(map(myfunc, x))

    ax3 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    if msrp > 0:
        est_msrp = datetime.datetime.fromordinal(int((msrp - intercept) / slope)).strftime("%y-%m-%d")

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

    plt.savefig('Images/' + query)
    plt.show()

    return median_price, est_break_even, min_break_even, tot_sold


def ebay_search(query, msrp=0, min_price=0, max_price=10000, min_date=datetime.datetime(2020, 1, 1), verbose=False):
    print(query)

    dict = {'Title': [], 'description': [], 'Price': [], 'Shipping': [], 'Total Price': [], 'Sold Date': [], 'Link': []}
    df = pd.DataFrame(dict)
    price_ranges = [min_price, max_price]

    # Determine price ranges to search with
    i = 0
    while i != len(price_ranges) - 1:
        time.sleep(0.1)
        url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' + str(
                query.replace(" ", "+")) + '&_sacat=0&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=' + str(
                price_ranges[i]) + '&_udhi=' + str(
                price_ranges[i + 1]) + '&rt=nc&_ipg=200&_pgn=4'

        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        items = soup.find_all('li', attrs={'class': 's-item'})
        if verbose: print(price_ranges, len(items), i, price_ranges[i], price_ranges[i + 1], url)

        if len(items) == 201 and round(price_ranges[i + 1] - price_ranges[i], 2) > 0.01:
            # If there's only one cent difference between the two just increment, we need to do some special logic below
            midpoint = round((price_ranges[i] + price_ranges[i + 1]) / 2, 2)
            price_ranges = price_ranges[:i + 1] + [midpoint] + price_ranges[i + 1:]
        elif len(items) == 201 and round(price_ranges[i + 1] - price_ranges[i], 2) == 0.01:
            # If there is a one cent difference between the two, we can have eBay just return that specific price to get a little bit finer detail
            price_ranges = price_ranges[:i + 1] + [price_ranges[i]] + [price_ranges[i + 1]] + price_ranges[i + 1:]
            i += 2
        else:
            i += 1

    # https://www.ebay.com/sch/i.html?_from=R40&_nkw=xbox+series+x+-one&_sacat=0&LH_TitleDesc=0&LH_Sold=1&LH_Complete=1&_udlo=100&_udhi=1100&rt=nc&LH_PrefLoc=1
    # https://www.ebay.com/sch/i.html?_from=R40&_nkw=Xbox+Series+X+-one&_sacat=0&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=100&_udhi=10000&rt=nc&_ipg=200&_pgn=4

    for i in range(len(price_ranges) - 1):
        url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' + str(
                query.replace(" ", "+")) + '&_sacat=0&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=' + str(
                price_ranges[i]) + '&_udhi=' + str(
                price_ranges[i + 1]) + '&rt=nc&_ipg=200&_pgn='
        if verbose: print(price_ranges[i], price_ranges[i + 1], url)
        df = ebay_scrape(url, df, min_date, verbose)

    df = pd.DataFrame.drop_duplicates(df)

    df.to_excel('Spreadsheets/' + str(query) + '.xlsx')

    median_price, est_break_even, min_break_even, tot_sold = ebay_plot(query, msrp, df)

    last_week = df.loc[
        df['Sold Date'] >= (datetime.datetime.now() - datetime.timedelta(days=7)).replace(hour=0, minute=0, second=0,
                                                                                          microsecond=0)]
    tot_sales = df['Total Price'].sum()
    tot_ini_sales = df['Price'].sum()

    ebay_profit = float(tot_sales) * 0.08
    # Estimate, eBay can take up to 10% for a fairly "new" seller and as little as 3.6% for a top selling store
    # I assume most scalpers are "new" sellers so 8% seems fair

    pp_profit = float(tot_sold) * 0.30 + float(tot_ini_sales) * 0.029

    print('Past Week Median Price: $' + str(last_week['Total Price'].median()))
    print('Median Price: $' + str(median_price))
    print('Past Week Average Price: $' + str(round(last_week['Total Price'].mean(), 2)))
    print('Average Price: $' + str(round(df['Total Price'].mean(), 2)))
    print('Total Sold: ' + str(tot_sold))
    print('Total Sales: $' + str(tot_sales))
    print('PayPal Profit: $' + str(int(pp_profit)))
    print('Est eBay Profit: $' + str(int(ebay_profit)))
    if msrp > 0:
        total_scalp_val = round(df['Total Price'].sum() - tot_sold * msrp, 2)
        print('Total Scalpers/eBay Profit: $' + str(total_scalp_val))
        print('Estimated Break Even Point for Scalpers: $' + str(est_break_even))
        print('Minimum Break Even Point for Scalpers: $' + str(min_break_even))
    print('')
    return df


df_3060 = ebay_search('RTX 3060', 399, 200, 1300, min_date=datetime.datetime(2020, 12, 1))


df_ps5_digital = ebay_search('PS5 Digital', 299, 300, 11000, min_date=datetime.datetime(2020, 9, 12))
df_ps5_disc = ebay_search('PS5 -digital', 499, 450, 11000, min_date=datetime.datetime(2020, 9, 12))

# Launch Date
df_xbox_x_ld = ebay_search('Xbox Series S', 299, 250, 11000, min_date=datetime.datetime(2020, 11, 10))
df_xbox_s_ld = ebay_search('Xbox Series X', 499, 350, 11000, min_date=datetime.datetime(2020, 11, 10))

df_ps5_digital_ld = ebay_search('PS5 Digital', 299, 300, 11000, min_date=datetime.datetime(2020, 11, 12))
df_ps5_disc_ld = ebay_search('PS5 -digital', 499, 450, 11000, min_date=datetime.datetime(2020, 11, 12))

df_3080 = ebay_search('RTX+3080', 699, 550, 10000, min_date=datetime.datetime(2020, 9, 17))

df_5950x = ebay_search('5950X', 799, 400, 2200)
df_5900x = ebay_search('5900X', 549, 499, 2050)
df_5800x = ebay_search('5800X', 449, 400, 1000)
df_5600x = ebay_search('5600X', 299, 250, 1000)

df_6800 = ebay_search('RX 6800 -XT', 579, 400, 2500)
df_6800xt = ebay_search('RX 6800 XT', 649, 850, 2000)  # There are some $5000+, but screw with graphs
# df_6900 = ebay_search('RX 6900', 999, 100, 999999, min_date=datetime.datetime(2020, 12, 8)) # Not out until December 8

df_3060 = ebay_search('RTX 3060', 399, 200, 1300, min_date=datetime.datetime(2020, 12, 1))
df_3070 = ebay_search('RTX 3070', 499, 499, 1300, min_date=datetime.datetime(2020, 10, 29))
df_3080 = ebay_search('RTX 3080', 699, 550, 10000, min_date=datetime.datetime(2020, 9, 17))
df_3090 = ebay_search('RTX 3090', 1499, 550, 10000, min_date=datetime.datetime(2020, 9, 17))

df_xbox_x = ebay_search('Xbox Series S', 299, 250, 11000, min_date=datetime.datetime(2020, 9, 22))
df_xbox_s = ebay_search('Xbox Series X', 499, 350, 11000, min_date=datetime.datetime(2020, 9, 22))

df_ps5_digital = ebay_search('PS5 Digital', 299, 300, 11000, min_date=datetime.datetime(2020, 9, 12))
df_ps5_disc = ebay_search('PS5 -digital', 499, 450, 11000, min_date=datetime.datetime(2020, 9, 12))

# Launch Date
df_xbox_x_ld = ebay_search('Xbox Series S', 299, 250, 11000, min_date=datetime.datetime(2020, 11, 10))
df_xbox_s_ld = ebay_search('Xbox Series X', 499, 350, 11000, min_date=datetime.datetime(2020, 11, 10))

df_ps5_digital_ld = ebay_search('PS5 Digital', 299, 300, 11000, min_date=datetime.datetime(2020, 11, 12))
df_ps5_disc_ld = ebay_search('PS5 -digital', 499, 450, 11000, min_date=datetime.datetime(2020, 11, 12))

df_3080 = ebay_search('RTX+3080', 699, 550, 10000, min_date=datetime.datetime(2020, 9, 17))


# TODO: Non-Linear Trendline and breakeven
