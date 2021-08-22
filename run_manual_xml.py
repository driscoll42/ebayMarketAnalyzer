"""

"""

# Moving all the calls of the code out of the main.py to reduce confusion/overhead.

import os
from copy import deepcopy
from datetime import datetime

import pandas as pd

from classes import EbayVariables
from main_manual_xml import ebay_search
from plotting import median_plotting, brand_plot, ebay_seller_plot, mean_plotting

brand_list = ['FOUNDER', 'ASUS', 'MSI', 'EVGA', 'GIGABYTE', 'ZOTAC', 'XFX', 'PNY', 'SAPPHIRE', 'COLORFUL', 'ASROCK',
              'POWERCOLOR', 'INNO3D', 'PALIT', 'VISIONTEK', 'DELL']
model_list = [['XC3', 'EVGA'], ['TRINITY', 'ZOTAC'], ['FTW3', 'EVGA'], ['FOUNDER', 'FOUNDER'], ['STRIX', 'ASUS'],
              ['EKWB', 'ASUS'], ['TUF', 'ASUS'], ['SUPRIM', 'MSI'], ['VENTUS', 'MSI'], ['MECH', 'MSI'],
              ['EVOKE', 'MSI'], ['TRIO', 'MSI'], ['KINGPIN', 'EVGA'], ['K|NGP|N', 'EVGA'], ['AORUS', 'GIGABYTE'],
              ['WATERFORCE', 'GIGABYTE'], ['XTREME', 'GIGABYTE'], ['MASTER', 'GIGABYTE'], ['AMP', 'ZOTAC'],
              [' FE ', 'FOUNDER'], ['TWIN EDGE', 'ZOTAC'], ['POWER COLOR', 'POWERCOLOR'], ['ALIENWARE', 'DELL']]

query_exclusions = []

ignore_list = ['BENT PINS', 'BROKEN', 'PARTS ONLY']

ps5_digi_excludes = query_exclusions.copy()

# Set Class variables
e_vars = EbayVariables(run_cached=True,
                       sleep_len=8,
                       show_plots=True,
                       main_plot=True,
                       profit_plot=True,
                       trend_type='None',
                       trend_param=[1, 14],  # [Poly_Degree, Days_Out]
                       extra_title_text='',
                       country='USA',
                       ccode='$',
                       days_before=365,
                       feedback=True,
                       quantity_hist=True,
                       debug=False,
                       verbose=True,
                       sacat=0,
                       tax_rate=0.0625,
                       store_rate=0.04,  # The computer store rate
                       non_store_rate=0.1,  # The computer non-store rate
                       desc_ignore_list=ignore_list,
                       brand_list=[],
                       model_list=[],
                       agent_list=pd.DataFrame()
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
gpu_vars.brand_list = brand_list
gpu_vars.model_list = model_list

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

# If you terminate a run of the program before it completes, it leaves orphan sqlite files. Best to just delete them
for x in os.listdir():
    if x.endswith(".sqlite"):
        os.remove(x)

# df_darkhero = ebay_search('ASUS Dark Hero', mobo_vars, 399, 400, 1000)

# Zen 3 Data Scraping & Analysis
'''df_5300g = ebay_search('5300G', cpu_vars, 150, 100, 2250)
df_5600g = ebay_search('5600G', cpu_vars, 259, 200, 2250)
df_5700g = ebay_search('5700G', cpu_vars, 359, 300, 2250)
df_5950x = ebay_search('5950X', cpu_vars, 799, 700, 2250)
df_5900x = ebay_search('5900X', cpu_vars, 549, 400, 2050)
df_5800x = ebay_search('5800X', cpu_vars, 449, 350, 1000)
df_5600x = ebay_search('5600X', cpu_vars, 299, 200, 1000)  # Make sure to minus 5600g

# Zen 3 Family Plotting
zen3_frames = [df_5300g, df_5600g, df_5700g, df_5600x, df_5800x, df_5900x, df_5950x]
median_plotting(zen3_frames, 'Zen 3 Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(zen3_frames, 'Zen 3 Median Pricing', e_vars=cpu_vars, roll=7)
ebay_seller_plot(zen3_frames, 'Zen 3', e_vars=cpu_vars)
'''

# Big Navi Analysis
df_6600 = ebay_search('RX 6600', gpu_vars, 379, 379, 2500)
df_6700 = ebay_search('RX 6700', gpu_vars, 479, 479, 2500)
df_6800 = ebay_search('RX 6800', gpu_vars, 579, 579, 2500)
df_6800xt = ebay_search('RX 6800 XT', gpu_vars, 649, 850, 2000)
df_6900 = ebay_search('RX 6900', gpu_vars, 999, 999, 999999, min_date=datetime(2020, 12, 8))

# Big Navi Plotting
bignavi_frames = [df_6600, df_6700, df_6800, df_6800xt, df_6900]
bignavi_colors = ['red', 'purple', 'green', 'cyan', 'lime', 'black', 'white']

median_plotting(bignavi_frames, 'Big Navi Median Pricing', colors=bignavi_colors, e_vars=gpu_vars, roll=0)
median_plotting(bignavi_frames, 'Big Navi Median Pricing', colors=bignavi_colors, e_vars=gpu_vars, roll=7)

mean_plotting(bignavi_frames, 'Big Navi Mean Pricing', e_vars=gpu_vars, roll=0, stdev_plot=True)
mean_plotting(bignavi_frames, 'Big Navi Mean Pricing', e_vars=gpu_vars, roll=7, stdev_plot=True)

ebay_seller_plot(bignavi_frames, 'Big Navi', gpu_vars)

brand_plot(bignavi_frames, 'Big Navi AIB Comparison', e_vars=gpu_vars, roll=0)
brand_plot(bignavi_frames, 'Big Navi AIB Comparison', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------
# RTX 30 Series Analysis
df_3060 = ebay_search('RTX 3060', gpu_vars, 329, 329, 2000, min_date=datetime(2021, 2, 25))
# Remember to search ebay with -Ti
df_3060ti = ebay_search('RTX 3060 Ti', gpu_vars, 399, 399, 5000, min_date=datetime(2020, 12, 1))
df_3070 = ebay_search('RTX 3070', gpu_vars, 499, 499, 10000, min_date=datetime(2020, 10, 29))
# Remember to search ebay with -Ti
df_3070ti = ebay_search('RTX 3070 Ti', gpu_vars, 599, 599, 10000, min_date=datetime(2020, 6, 10))
df_3080 = ebay_search('RTX 3080', gpu_vars, 699, 699, 10000, min_date=datetime(2020, 9, 17))
df_3080ti = ebay_search('RTX 3080 Ti', gpu_vars, 1199, 1199, 10000, min_date=datetime(2021, 6, 3))
df_3090 = ebay_search('RTX 3090', gpu_vars, 1499, 1499, 10000, min_date=datetime(2020, 9, 17))

# RTX 30 Series/Ampere Plotting
df_3060ti = df_3060ti.assign(item='RTX 3060 Ti')
ampere_frames = [df_3060, df_3060ti, df_3070, df_3070ti, df_3080, df_3090]
ampere_colors = ['#0B6623', '#708238', '#39FF14', '#00A86B', '#043927', '#01796F', '#4F7942']
ampere_colors = ['red', 'purple', 'green', 'cyan', 'lime', 'black', 'white']

median_plotting(ampere_frames, 'RTX 30 Series Median Pricing', colors=ampere_colors, e_vars=gpu_vars, roll=0)
median_plotting(ampere_frames, 'RTX 30 Series Median Pricing', colors=ampere_colors, e_vars=gpu_vars, roll=7)

mean_plotting(ampere_frames, 'RTX 30 Series Average Pricing', e_vars=gpu_vars, roll=0, stdev_plot=True)
mean_plotting(ampere_frames, 'RTX 30 Series Average Pricing', e_vars=gpu_vars, roll=7, stdev_plot=True)

ebay_seller_plot(ampere_frames, 'RTX 30 Series-Ampere', gpu_vars)

brand_plot(ampere_frames, 'RTX 30 Series-Ampere AIB Comparison', e_vars=gpu_vars, roll=0)
brand_plot(ampere_frames, 'RTX 30 Series-Ampere AIB Comparison', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------
'''
# PS5 Analysis (All time)
df_ps5_digital = ebay_search('PS5 Digital', console_vars, 399, 300, 11000, min_date=datetime(2020, 9, 16))
df_ps5_disc = ebay_search('PS5', console_vars, 499, 450, 11000, min_date=datetime(2020, 9, 16))
# Remember when generating XMLs need the -digital

# PS5 Plotting
df_ps5_disc = df_ps5_disc.assign(item='PS5 Disc')
ps5_frames = [df_ps5_digital, df_ps5_disc]
ps5_colors = ['darkblue', '#006fcd']
ebay_seller_plot(ps5_frames, 'PS5', console_vars)

median_plotting(ps5_frames, 'PS5 Median Pricing', colors=ps5_colors, e_vars=console_vars, roll=0)
median_plotting(ps5_frames, 'PS5 Median Pricing', colors=ps5_colors, e_vars=console_vars, roll=7)

# ---------------------------------------------------------------------------------------------
# Xbox Analysis (All time)
df_xbox_s = ebay_search('Xbox Series S', console_vars, 299, 250, 11000, min_date=datetime(2020, 9, 22), )
df_xbox_x = ebay_search('Xbox Series X', console_vars, 499, 350, 11000, min_date=datetime(2020, 9, 22))

# Xbox Plotting
xbox_series_frames = [df_xbox_s, df_xbox_x]
xbox_colors = ['limegreen', '#0e7a0d']

ebay_seller_plot(xbox_series_frames, 'Xbox', console_vars)
median_plotting(xbox_series_frames, 'Xbox Median Pricing', colors=xbox_colors, e_vars=console_vars, roll=0)
median_plotting(xbox_series_frames, 'Xbox Median Pricing', colors=xbox_colors, e_vars=console_vars, roll=7)

console_frames = [df_ps5_digital, df_ps5_disc, df_xbox_s, df_xbox_x]
console_colors = ['darkblue', '#006fcd', 'limegreen', '#0e7a0d']

median_plotting(console_frames, 'PS5 & Xbox Median Pricing', colors=console_colors, e_vars=console_vars, roll=0)
median_plotting(console_frames, 'PS5 & Xbox Median Pricing', colors=console_colors, e_vars=console_vars, roll=7)

ebay_seller_plot(console_frames, 'PS5 & Xbox', console_vars)
'''
