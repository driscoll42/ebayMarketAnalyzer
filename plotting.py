"""
plotting.py

Contains all the functions for creating various plots/graphs

Current functions:
    ebay_plot - Creates a scatterplot of sales with a line connecting the median sale each date, the MSRP, scalper
                    profit cutoffs, and trend lines
    plot_profits -
    median_plotting -
    crpyto_comp_plotting -
    pareto_plot -
    ebay_seller_plot -
    brand_plot -
"""

import math
import warnings
from copy import deepcopy
from datetime import timedelta, datetime
from typing import List, Tuple

import matplotlib.ticker as ticker
import numpy.polynomial.polynomial as poly
import pandas as pd
from fastquant import get_crypto_data
from matplotlib import pyplot as plt
from sklearn.metrics import r2_score

from classes import EbayVariables
from util import prep_df


# pylint: disable=line-too-long
# pylint: disable=multiple-statements

def ebay_plot(query: str,
              msrp: float,
              df: pd.DataFrame,
              e_vars: EbayVariables,
              plot_msrp: bool = True,
              plot_scalp: bool = True) -> Tuple[int, float, float, int, float]:
    """

    Parameters
    ----------
    query :
    msrp :
    df :
    e_vars :
    plot_msrp :
    plot_scalp :

    Returns
    -------

    """

    # Make Linear Regression Trend Line
    # https://stackoverflow.com/questions/59723501/plotting-a-linear-regression-with-dates-in-matplotlib-pyplot
    df_calc = prep_df(df)

    median_prices = df_calc.groupby(['Sold Date'])['Total Price'].median()
    max_price = df_calc.groupby(['Sold Date'])['Total Price'].max()
    min_price = df_calc.groupby(['Sold Date'])['Total Price'].min()
    max_med = max(median_prices)
    max_max = max(max_price)
    min_min = min(min_price)
    median_price = int(df_calc['Total Price'].median())

    est_break_even = 0
    min_break_even = 0

    plt.style.use('ggplot')

    fig, ax1 = plt.subplots(figsize=(10, 8))

    color = 'tab:blue'
    plt.title(
            query.replace("+", " ").split('-', 1)[0].strip() + e_vars.extra_title_text + ' eBay Sold Prices Over Time',
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
        msrp_discount = 0.05  # If drop scalpers are buying off of Amazon with an Amazon Prime account and credit card,
        # they can get 5% cash back, so effectively the MSRP is 5% lower

        est_break_even = round(
                (msrp * (1 + e_vars.tax_rate)) / (1 - est_ebay_fee - pp_fee_per) + pp_flat_fee + estimated_shipping)
        min_break_even = round((msrp * (1 - msrp_discount)) / (1 - min_be_ebay_fee - pp_fee_per) + pp_flat_fee)

        if plot_scalp:
            ax1.axhline(y=est_break_even, label=f'Est. Scalper Break Even - {e_vars.ccode}{int(est_break_even)}',
                        color=color, linestyle='dashed', dashes=[2, 2])
            ax1.axhline(y=min_break_even, label=f'Min Scalper Break Even - {e_vars.ccode}{int(min_break_even)}',
                        color=color, linestyle='dashed', dashes=[4, 1])

        # Estimated assuming 6.25% tax, $15 shipping, and the multiplier for ebay/Paypal fees determined by
        # https://www.ebayfeescalculator.com/usa-ebay-calculator/ where not an eBay store, seller is above standard, and
        # paying with PayPal with Item Category being Computers/Tablets & Networking

        if plot_msrp:
            ax1.axhline(y=msrp, label=f'MSRP - {e_vars.ccode}{msrp}', color=color)
    ax1.plot(median_prices, linewidth=3, color='dimgray', label=f'Median Price - {e_vars.ccode}{median_price}',
             zorder=999)
    # plt.plot(sold_date, m * sold_date + b)
    ax1.set_ylabel("Sold Price", color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', rotation=30)
    formatter = ticker.FormatStrFormatter(f'{e_vars.ccode}%1.0f')
    ax1.yaxis.set_major_formatter(formatter)
    ax1.set_xlabel("Sold Date")
    ax1.set_ylim(top=min(1.5 * max_med, max_max), bottom=min(min_min * 0.95, msrp * 0.95))
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, bbox_to_anchor=(0, -0.325, 1, 0), loc="lower left",
               mode="expand", ncol=2)

    # color = 'tab:red'
    # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    # ax2.set_ylabel("Quantity Sold", color=color)
    # ax2.tick_params(axis='y', labelcolor=color)
    tot_sold = int(df['Quantity'].sum())
    # ax2.plot(count_sold[:-1], color=color, label=f'Total Sold - {tot_sold}')

    # Poly Trendline
    if e_vars.trend_type == 'poly' or e_vars.trend_type == 'linear' or e_vars.trend_type == 'roll':
        ax2 = ax1.twinx()
        ax2.set_ylim(top=min(1.5 * max_med, max_max), bottom=min(min_min * 0.95, msrp * 0.95))
        ax2.grid(False)
        ax2.tick_params(right=False)  # remove the ticks
        ax2.set(ylabel=None)  # remove the y-axis label
        ax2.set(yticklabels=[])

        if e_vars.trend_type == 'poly' or e_vars.trend_type == 'linear':
            if e_vars.trend_type == 'linear':
                degree = 1
                project_date = e_vars.trend_param[0]
            else:
                degree = e_vars.trend_param[0]
                project_date = e_vars.trend_param[1]

            # Plotting Trendline
            x_orig = median_prices.index.tolist()
            x_orig = [i.toordinal() for i in x_orig]
            x_orig = [i - df_calc['Sold Date'].min().toordinal() for i in x_orig]

            max_date = df_calc['Sold Date'].max() + timedelta(project_date)
            date_diff = (df_calc['Sold Date'].max() - df_calc['Sold Date'].min()).days + project_date
            date_list = [max_date - timedelta(days=x) for x in range(date_diff)]
            date_list.sort()

            with warnings.catch_warnings(record=True) as caught_warnings:
                coefs = poly.polyfit(x_orig, median_prices, degree)
                if e_vars.verbose: print('Polynomial Coefficients: ', coefs)
                for warn in caught_warnings:
                    print('WARNING: Polynomial may be overfit, try a lower order polynomial')

            max_x_poly = max(x_orig) - min(x_orig) + 1
            x_poly = [*range(1, max_x_poly + project_date, 1)]
            ffit = poly.polyval(x_poly, coefs)

            ax2.plot(date_list, ffit)
            ffit = poly.polyval(x_orig, coefs)

            print('R Squared:', r2_score(ffit, median_prices))

        elif e_vars.trend_type == 'roll':
            med_roll = median_prices.rolling(e_vars.trend_param[0], min_periods=1).mean()
            ax2.plot(med_roll)

        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, bbox_to_anchor=(0, -0.325, 1, 0), loc="lower left",
                   mode="expand", ncol=2)

    plt.subplots_adjust(bottom=0.225)

    plt.savefig('Images/' + query + e_vars.extra_title_text)
    if e_vars.show_plots and e_vars.main_plot: plt.show()

    return median_price, est_break_even, min_break_even, tot_sold, estimated_shipping


def plot_profits(df: pd.DataFrame,
                 title: str,
                 msrp: float,
                 e_vars: EbayVariables) -> Tuple[float, float, float]:
    """

    Parameters
    ----------
    df :
    title :
    msrp :
    e_vars :

    Returns
    -------

    """
    df = prep_df(deepcopy(df))

    med_price = df.groupby(['Sold Date'])['Total Price'].median() / msrp * 100

    estimated_shipping = df.loc[df['Shipping'] > 0]
    estimated_shipping = estimated_shipping['Shipping'].median()
    if math.isnan(estimated_shipping):
        estimated_shipping = 0

    # Very useful site for determining all this: https://www.ebayfeescalculator.com/usa-ebay-calculator/
    df['eBay Profits'] = df['Total Price'] * e_vars.non_store_rate * (1 - df['Store']) \
                         + df['Total Price'] * e_vars.store_rate * df['Store']

    df['PayPal Profits'] = df['Total Price'] * 0.029 + 0.30

    df['Scalper Profits'] = df['Store'] * (df['Total Price']
                                           - (msrp * (1.0 + e_vars.tax_rate) + estimated_shipping)
                                           - (df['Total Price'] * e_vars.store_rate)
                                           - (df['Total Price'] * 0.029 + 0.30)) + ((1 - df['Store']) * (
            df['Total Price'] \
            - (msrp * (1.0 + e_vars.tax_rate) + estimated_shipping) \
            - (df['Total Price'] * e_vars.non_store_rate) \
            - (df['Total Price'] * 0.029 + 0.30)))

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
    ax1.set_ylabel(f"Sales/Profits ({e_vars.ccode})")
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

    ax2.plot(df['Sold Date'], df['Total Price'], color='red', label=f'Total Sales ({e_vars.ccode})')
    ax2.plot(df['Sold Date'], df['Scalper Profits'], '-', color='darkred', label='Scalper Profits')

    ax2.tick_params(axis='y', colors='red')
    ax2.tick_params(axis='x', rotation=30)
    ax2.set_xlabel("Sold Date")
    ax2.set_ylabel(f"Sales/Profits ({e_vars.ccode})", color='r')

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

    if e_vars.show_plots and e_vars.profit_plot: plt.show()

    return df['Cum eBay'].iloc[-1], df['Cum PayPal'].iloc[-1], df['Cum Scalper'].iloc[-1]


def median_plotting(dfs: List[pd.DataFrame],
                    title: str,
                    e_vars: EbayVariables,
                    roll: int = 0,
                    min_msrp: int = 100) -> None:
    """

    Parameters
    ----------
    dfs :
    title :
    e_vars :
    roll :
    min_msrp :

    Returns
    -------

    """
    dfs = deepcopy(dfs)
    colors = ['#000000', '#7f0000', '#808000', '#008080', '#000080', '#ff8c00', '#2f4f4f', '#00ff00', '#0000ff',
              '#ff00ff', '#6495ed', '#ff1493', '#98fb98', '#ffdab9']
    plt.figure()  # In this example, all the plots will be in one figure.
    plt.ylabel("% of MSRP")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)

    for i, df in enumerate(dfs):
        color = i % (len(colors) - 1)

        df = prep_df(df)

        med_price_scaled = df.groupby(['Sold Date'])['Total Price'].median() / df['msrp'].iloc[0] * 100
        # med_mad = robust.mad(df.groupby(['Sold Date'])['Total Price']/ msrps[i] * 100)

        if roll > 0:
            med_price_scaled = med_price_scaled.rolling(roll, min_periods=1).mean()

        min_msrp = min(min_msrp, min(med_price_scaled))
        plt.plot(med_price_scaled, colors[color], label=df['item'].iloc[0])
        # plt.fill_between(med_price_scaled, med_price_scaled - med_mad, med_price_scaled + med_mad, color=colors[ci])

    plt.ylim(bottom=min_msrp)
    plt.legend()
    plt.tight_layout()

    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average - % MSRP")
        plt.savefig(f"Images/{title} {roll} Day Rolling Average - % MSRP")
    else:
        plt.title(f"{title} - % MSRP")
        plt.savefig(f"Images/{title} - % MSRP")

    if e_vars.show_plots: plt.show()

    # Plotting the non-scaled graph
    plt.figure()  # In this example, all the plots will be in one figure.
    fig, ax1 = plt.subplots()
    plt.ylabel(f"Median Sale Price ({e_vars.ccode})")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)

    for i, df in enumerate(dfs):
        color = i % (len(colors) - 1)

        med_price = df.groupby(['Sold Date'])['Total Price'].median()

        if roll > 0:
            med_price = med_price.rolling(roll, min_periods=1).mean()

        min_msrp = min(min_msrp, min(med_price))
        plt.plot(med_price, colors[color], label=df['item'].iloc[0])

    plt.ylim(bottom=min_msrp)
    formatter = ticker.FormatStrFormatter(f'{e_vars.ccode}%1.0f')
    ax1.yaxis.set_major_formatter(formatter)
    plt.legend()
    plt.tight_layout()

    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average - {e_vars.ccode}")
        plt.savefig(f"Images/{title} {roll} Day Rolling Average - {e_vars.ccode}")
    else:
        plt.title(f"{title} - {e_vars.ccode}")
        plt.savefig(f"Images/{title} - {e_vars.ccode}")
    if e_vars.show_plots: plt.show()


def crpyto_comp_plotting(dfs: List[pd.DataFrame],
                         title: str,
                         e_vars: EbayVariables,
                         roll: int = 0,
                         min_msrp: int = 100) -> None:
    """

    Parameters
    ----------
    dfs :
    title :
    e_vars :
    roll :
    min_msrp :

    Returns
    -------

    """
    dfs = deepcopy(dfs)

    min_date = datetime.now()
    max_date = datetime.now() - timedelta(365)
    for df in dfs:
        df_min = df['Sold Date'].min()
        df_max = df['Sold Date'].max()
        if df_min < min_date:
            min_date = df_min
        if df_max > max_date:
            max_date = df_max

    min_date = str(min_date).split(' ')[0]
    max_date = str(max_date).split(' ')[0]

    # Etherium Pricing
    eth_crypto = get_crypto_data("ETH/USDT", min_date, max_date)
    eth_prices = eth_crypto.close
    eth_prices = eth_prices.div(eth_prices.min())
    eth_prices = eth_prices.mul(100)

    # Bitcoin Pricing
    btc_crypto = get_crypto_data("BTC/USDT", min_date, max_date)
    btc_prices = btc_crypto.close
    btc_prices = btc_prices.div(btc_prices.min())
    btc_prices = btc_prices.mul(100)

    colors = ['#000000', '#7f0000', '#808000', '#008080', '#000080', '#ff8c00', '#2f4f4f', '#00ff00', '#0000ff',
              '#ff00ff', '#6495ed', '#ff1493', '#98fb98', '#ffdab9']
    plt.figure()  # In this example, all the plots will be in one figure.
    plt.ylabel("% of MSRP")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)

    for i, df in enumerate(dfs):
        color = i % (len(colors) - 1)

        df = prep_df(df)

        med_price_scaled = df.groupby(['Sold Date'])['Total Price'].median() / df['msrp'].iloc[0] * 100

        # med_mad = robust.mad(df.groupby(['Sold Date'])['Total Price']/ msrps[i] * 100)
        # print(med_mad)

        if roll > 0:
            med_price_scaled = med_price_scaled.rolling(roll, min_periods=1).mean()

        min_msrp = min(min_msrp, min(med_price_scaled))
        plt.plot(med_price_scaled, colors[color], label=df['item'].iloc[0])
        # plt.fill_between(med_price_scaled, med_price_scaled - med_mad, med_price_scaled + med_mad, color=colors[ci])

    plt.plot(eth_prices, label='Etherium')
    plt.plot(btc_prices, label='Bitcoin')
    plt.ylim(bottom=min_msrp)
    plt.legend()
    plt.tight_layout()

    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average - % MSRP")
        plt.savefig(f"Images/{title} {roll} Day Rolling Average - % MSRP")
    else:
        plt.title(f"{title} - % MSRP")
        plt.savefig(f"Images/{title} - % MSRP")
    if e_vars.show_plots: plt.show()

    # Plotting the non-scaled graph
    plt.figure()  # In this example, all the plots will be in one figure.
    fig, ax1 = plt.subplots()
    plt.ylabel(f"Median Sale Price ({e_vars.ccode})")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)
    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average - {e_vars.ccode}")
    else:
        plt.title(f"{title} - {e_vars.ccode}")
    for i, df in enumerate(dfs):
        color = i % (len(colors) - 1)

        med_price = df.groupby(['Sold Date'])['Total Price'].median()

        if roll > 0:
            med_price = med_price.rolling(roll, min_periods=1).mean()

        min_msrp = min(min_msrp, min(med_price))
        plt.plot(med_price, colors[color], label=df['item'].iloc[0])
    plt.ylim(bottom=min_msrp)
    formatter = ticker.FormatStrFormatter(f'{e_vars.ccode}%1.0f')
    ax1.yaxis.set_major_formatter(formatter)
    plt.legend()
    plt.tight_layout()
    # plt.savefig(f"Images/{title} - {e_vars.ccode}")
    # if e_vars.show_plots: plt.show()
    plt.show()


# https://tylermarrs.com/posts/pareto-plot-with-matplotlib/
def pareto_plot(df: pd.DataFrame,
                df2: pd.DataFrame,
                df3: pd.DataFrame,
                e_vars: EbayVariables,
                df_name: str = '',
                df2_name: str = '',
                x_label: str = '',
                y_label: str = '',
                title: str = '') -> None:
    """

    Parameters
    ----------
    df :
    df2 :
    df3 :
    e_vars :
    df_name :
    df2_name :
    x_label :
    y_label :
    title :

    Returns
    -------

    """
    weights = df3[y_label] / df3[y_label].sum()
    cumsum = weights.cumsum()

    plt.figure(figsize=(8, 8))

    fig, ax1 = plt.subplots()

    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label)
    ax1.tick_params(axis='x', rotation=30)
    ax1.legend(loc='center right')

    ax1.bar(df[x_label], df[y_label], label=df_name)
    if df2.size > 0:
        ax1.bar(df2[x_label], df2[y_label], bottom=df[y_label], label=df2_name)

    ax2 = ax1.twinx()
    ax2.set_ylabel('', color='r')
    ax2.tick_params('y', colors='r')
    ax2.set_ylim(bottom=0)
    ax2.plot(df3[x_label], cumsum, '-ro', alpha=0.5)

    vals = ax2.get_yticks()
    ax2.set_yticklabels(['{:,.2%}'.format(x) for x in vals])

    formatted_weights = ['{0:.0%}'.format(x) for x in cumsum]
    for i, txt in enumerate(formatted_weights):
        ax2.annotate(txt, (df[x_label][i], cumsum[i]), fontweight='heavy')

    plt.title(title)
    fig.tight_layout()
    plt.legend()

    plt.savefig('Images/' + title)
    if e_vars.show_plots: plt.show()


def ebay_seller_plot(dfs: List[pd.DataFrame],
                     title_text: str,
                     e_vars: EbayVariables) -> None:
    """

    Parameters
    ----------
    dfs :
    title_text :
    e_vars :

    Returns
    -------

    """
    df = pd.concat(dfs)
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
                              green_star, shooting_star]})
        return df_fb

    df_store_fb = split_data(df_stores)
    df_nostores_fb = split_data(df_nostores)
    df_all = split_data(df_sell)

    title = title_text.replace("+", " ").split('-', 1)[
                0].strip() + e_vars.extra_title_text + ' eBay Seller Feedback vs Quantity Sold'

    pareto_plot(df_nostores_fb, df_store_fb, df_all, e_vars=e_vars, df_name='Non-Store', df2_name='Store',
                x_label='Star Category', y_label='Quantity Sold', title=title)

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
                                twen_fifty, fifty_plus]})
        return df_fb

    title = title_text.replace("+", " ").split('-', 1)[
                0].strip() + e_vars.extra_title_text + ' eBay Seller Sales vs Total Sold'

    df_store_fb = split_data_again(df_stores)
    df_nostore_fb = split_data_again(df_nostores)
    df_all = split_data_again(df_quant)

    pareto_plot(df_nostore_fb, df_store_fb, df_all, e_vars=e_vars, df_name='Non-Store', df2_name='Store',
                x_label='Number of Sales', y_label='Quantity Sold', title=title)


def brand_plot(dfs: List[pd.DataFrame],
               title: str,
               e_vars: EbayVariables,
               roll: int = 0) -> None:
    """

    Parameters
    ----------
    dfs :
    title :
    e_vars :
    roll :

    Returns
    -------

    """
    dfs = deepcopy(dfs)
    pd.set_option('display.max_columns', None)

    for i, df in enumerate(dfs):
        df = prep_df(df)
        df['Total Price'] /= df['msrp'].iloc[0]

    df = pd.concat(dfs)

    brand_dict = {}
    for brand in e_vars.brand_list:
        brand_dict[brand] = df[(df['Brand'] == brand) & (df['Ignore'] == 0) & (df['Total Price'] <= 3000)]

    # Picked using this https://mokole.com/palette.html
    colors = ['#000000', '#7f0000', '#808000', '#008080', '#000080', '#ff8c00', '#2f4f4f', '#00ff00', '#0000ff',
              '#ff00ff', '#6495ed', '#ff1493', '#98fb98', '#ffdab9']
    min_msrp = 100
    max_msrp = 300
    plt.figure(figsize=(12, 8))  # In this example, all the plots will be in one figure.
    plt.ylabel("% of MSRP")
    plt.xlabel("Sale Date")
    plt.tick_params(axis='y')
    plt.tick_params(axis='x', rotation=30)

    if roll > 0:
        plt.title(f"{title} {roll} Day Rolling Average")
    else:
        plt.title(title)

    for i, brand in enumerate(e_vars.brand_list):
        color = i % (len(colors) - 1)

        if len(brand_dict[brand]) > 10:
            print(brand, len(brand_dict[brand]))

            brand_dict[brand] = brand_dict[brand][brand_dict[brand]['Total Price'] > 0]
            brand_dict[brand] = brand_dict[brand].loc[brand_dict[brand].index.repeat(brand_dict[brand]['Quantity'])]
            brand_dict[brand]['Quantity'] = 1

            med_price = brand_dict[brand].groupby(['Sold Date'])['Total Price'].median() * 100
            if roll > 0:
                med_price = med_price.rolling(roll, min_periods=1).mean()

            min_msrp = min(100, min(med_price))
            max_msrp = min(300, max(med_price))
            plt.plot(med_price, colors[color], label=e_vars.brand_list[i])
    plt.ylim(bottom=min_msrp, top=max_msrp)
    plt.legend()
    plt.tight_layout()
    if roll > 0:
        plt.savefig(f"Images/{title} {roll} Day Rolling Average")
    else:
        plt.savefig(f"Images/{title}")

    if e_vars.show_plots: plt.show()
