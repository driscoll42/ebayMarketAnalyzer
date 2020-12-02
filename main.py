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
                except Exception as e:
                    item_price = 'None'

                if verbose: print(item_price)

                try:
                    item_shipping = items.find('span', class_='s-item__shipping s-item__logisticsCost').text
                except Exception as e:
                    item_shipping = 'None'

                if verbose: print(item_shipping)

                try:
                    item_tot = float(float(item_price.replace('$', '').replace(',', '')))

                    if item_shipping.upper().find("FREE") == -1:
                        item_tot += float(item_shipping.replace('+$', '').replace(' shipping', ''))
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

                if 'None' not in str(item_tot) and 'None' not in str(item_date) and (item_date > min_date):
                    df = df.append(df__new, ignore_index=True)

    return df


def ebay_plot(query, msrp, df):
    # Make Linear Regression Trend Line
    # https://stackoverflow.com/questions/59723501/plotting-a-linear-regression-with-dates-in-matplotlib-pyplot
    # m, b = np.polyfit(sold_date, sold_price, 1)

    med_price = df.groupby(['Sold Date'])['Total Price'].median()
    max_price = df.groupby(['Sold Date'])['Total Price'].max()
    min_price = df.groupby(['Sold Date'])['Total Price'].min()
    max_med = max(med_price)
    max_max = max(max_price)
    min_min = min(min_price)
    median_price = int(df['Total Price'].median())
    count_sold = df.groupby(['Sold Date'])['Total Price'].count()

    fig, ax1 = plt.subplots(figsize=(10, 8))
    color = 'tab:blue'
    plt.title(query.replace("+", " ").split('-', 1)[0].strip() + ' eBay Sold Prices Over Time')
    ax1.scatter(df['Sold Date'], df['Total Price'], s=10, label='Sold Listing', color=color)
    est_break_even = round((msrp * 1.0625) * 1.1485 + 15)
    min_break_even = round(msrp * 1.125725)
    ax1.axhline(y=est_break_even, label='Est. Scalper Break Even - $' + str(est_break_even), color=color, dashes=[2, 2])
    ax1.axhline(y=min_break_even, label='Min Scalper Break Even - $' + str(min_break_even), color=color, dashes=[4, 1])

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
    ax1.set_ylim(top=min(1.5 * max_med, max_max), bottom=min(min_min - 5, msrp - 5))

    color = 'tab:red'
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel("Quantity Sold", color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.plot(count_sold, color=color, label='Total Sold - ' + str(len(df)))

    # Plotting Trendline
    y = df['Total Price']
    x = [i.toordinal() for i in df['Sold Date']]

    slope, intercept, r, p, std_err = stats.linregress(x, y)

    def myfunc(x):
        return slope * x + intercept

    mymodel = list(map(myfunc, x))

    ax3 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    est_msrp = datetime.datetime.fromordinal(int((msrp - intercept) / slope)).strftime("%y-%m-%d")

    if slope >= 0:
        ax3.plot(x, mymodel, dashes=[4, 1], label='Linear Trend Line')
    else:
        ax3.plot(x, mymodel, dashes=[4, 1], label='Linear Trend Line - Est MSRP Date - ' + str(est_msrp))

    ax3.set_ylim(top=min(1.5 * max_med, max_max), bottom=min(min_min - 5, msrp - 5))
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

    plt.savefig(query)
    plt.show()


def ebay_search(query, msrp, min_price, max_price, min_date=datetime.datetime(2020, 1, 1), verbose=False):
    print(query)
    dict = {'Title': [], 'description': [], 'Price': [], 'Shipping': [], 'Total Price': [], 'Sold Date': [], 'Link': []}
    df = pd.DataFrame(dict)
    price_ranges = [min_price, max_price]

    # source = requests.get(url).text
    # source = requests.get('https://www.ebay.com/sch/i.html?_from=R40&_nkw=5950x&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1').text
    # soup = BeautifulSoup(source, 'lxml')
    # items = soup.find_all('li', attrs={'class': 's-item'})
    # print(soup)

    # https://www.ebay.com/sch/i.html?_from=R40&_nkw=rtx+3090&_sacat=0&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=1000&_udhi=1562&rt=nc&_ipg=200&_pgn=4
    # https://www.ebay.com/sch/i.html?_from=R40&_nkw=rtx+3090&_sacat=0&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=1000&_udhi=1562&rt=nc&LH_TitleDesc=0
    # Determine price ranges to search with
    i = 0
    last_val = -1
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
        print(price_ranges, len(items), i, price_ranges[i], price_ranges[i + 1], last_val)

        if len(items) == 201 and price_ranges[i + 1] - price_ranges[i] > 0.01:
            # If there's only one cent difference between the two just increment, we can't split any finer
            midpoint = round((price_ranges[i] + price_ranges[i + 1]) / 2, 2)
            price_ranges = price_ranges[:i + 1] + [midpoint] + price_ranges[i + 1:]
        else:
            i += 1

    print(price_ranges)

    for i in range(len(price_ranges) - 1):
        url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' + str(
                query) + '&_sacat=0&LH_PrefLoc=1&LH_Sold=1&LH_Complete=1&_udlo=' + str(
                price_ranges[i]) + '&_udhi=' + str(
                price_ranges[i + 1]) + '&rt=nc&_ipg=200&_pgn='
        if verbose: print(price_ranges[i], price_ranges[i + 1], url)
        df = ebay_scrape(url, df, min_date, verbose)

    df = pd.DataFrame.drop_duplicates(df)

    df.to_excel(str(query) + '.xlsx')

    ebay_plot(query, msrp, df)

    return df

df_5950x = ebay_search('5950X', 799, 400, 2200)
df_5900x = ebay_search('5900X', 549, 499, 2050)
df_5800x = ebay_search('5800X', 449, 400, 1000)
df_5600x = ebay_search('5600X', 299, 250, 1000)

df_6800 = ebay_search('RX+6800+-XT', 579, 400, 2500)
df_6800xt = ebay_search('RX+6800+XT', 649, 850, 2000) # There are some $5000+, but screw with graphs
# df_6900 = ebay_search('RX 6900', 999, 100, 999999, min_date=datetime.datetime(2020, 12, 8)) # Not out until December 8

df_3070 = ebay_search('RTX+3070', 499, 499, 1300, min_date=datetime.datetime(2020, 10, 29))
df_3080 = ebay_search('RTX+3080', 699, 550, 10000, min_date=datetime.datetime(2020, 9, 17))
df_3090 = ebay_search('RTX+3090', 699, 550, 10000, min_date=datetime.datetime(2020, 9, 17))

df_ps5_digital = ebay_search('PS5 Digital', 299, 300, 11000, min_date=datetime.datetime(2020, 1, 12))
df_ps5_disc = ebay_search('PS5 -digital', 499, 450, 11000, min_date=datetime.datetime(2020, 1, 12))

df_xbox_x = ebay_search('Xbox Series S -one', 500, 300, 11000)
df_xbox_s = ebay_search('Xbox Series X -one', 300, 100, 11000)


# TODO: Get listings from Discord/Telegram to compare against
# TODO: Non-Linear Trendline and breakeven
