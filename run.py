"""

"""

# Moving all the calls of the code out of the main.py to reduce confusion/overhead.

import os
from copy import deepcopy
from datetime import datetime

from classes import EbayVariables
from main import ebay_search
from plotting import median_plotting, brand_plot, ebay_seller_plot

brand_list = ['FOUNDER', 'ASUS', 'MSI', 'EVGA', 'GIGABYTE', 'ZOTAC', 'XFX', 'PNY', 'SAPPHIRE', 'COLORFUL', 'ASROCK',
              'POWERCOLOR', 'INNO3D', 'PALIT', 'VISIONTEK', 'DELL']
model_list = [['XC3', 'EVGA'], ['TRINITY', 'ZOTAC'], ['FTW3', 'EVGA'], ['FOUNDER', 'FOUNDER'], ['STRIX', 'ASUS'],
              ['EKWB', 'ASUS'], ['TUF', 'ASUS'], ['SUPRIM', 'MSI'], ['VENTUS', 'MSI'], ['MECH', 'MSI'],
              ['EVOKE', 'MSI'], ['TRIO', 'MSI'], ['KINGPIN', 'EVGA'], ['K|NGP|N', 'EVGA'], ['AORUS', 'GIGABYTE'],
              ['WATERFORCE', 'GIGABYTE'], ['XTREME', 'GIGABYTE'], ['MASTER', 'GIGABYTE'], ['AMP', 'ZOTAC'],
              [' FE ', 'FOUNDER'], ['TWIN EDGE', 'ZOTAC'], ['POWER COLOR', 'POWERCOLOR'], ['ALIENWARE', 'DELL']]

query_exclusions = ['image', 'jpeg', 'img', 'picture', 'pic', 'jpg', 'charity', 'photo', 'humans', 'prints', 'framed',
                    'print', 'people', 'inkjet', 'pix', 'paper', 'digital', 'pics', 'alternative']

ignore_list = ['BENT PINS', 'BROKEN', 'PARTS ONLY']

ps5_digi_excludes = query_exclusions.copy()
ps5_digi_excludes.remove('digital')

# Set Class variables
e_vars = EbayVariables(run_cached=False,
                       sleep_len=4,
                       show_plots=True,
                       main_plot=True,
                       profit_plot=False,
                       trend_type='linear',
                       trend_param=[14],  # [Poly_Degree, Days_Out]
                       extra_title_text='',
                       country='USA',
                       ccode='$',
                       days_before=30,
                       feedback=False,
                       quantity_hist=False,
                       debug=False,
                       verbose=False,
                       sacat=0,
                       tax_rate=0.0625,
                       store_rate=0.04,  # The computer store rate
                       non_store_rate=0.1,  # The computer non-store rate
                       desc_ignore_list=ignore_list,
                       brand_list=[],
                       model_list=[]
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

df_3090 = ebay_search('RTX 3090', gpu_vars, query_exclusions, 1499, 1499, 10000,
                      min_date=datetime(2020, 9, 17))

df_darkhero = ebay_search('ASUS Dark Hero', mobo_vars, query_exclusions, 399, 400, 1000)

# ---------------------------------------------------------------------------------------------

# Zen 3 Data Scraping & Analysis
df_5950x = ebay_search('5950X', cpu_vars, query_exclusions, 799, 799, 2200)
df_5900x = ebay_search('5900X', cpu_vars, query_exclusions, 549, 549, 2050)
df_5800x = ebay_search('5800X', cpu_vars, query_exclusions, 449, 449, 1000)
df_5600x = ebay_search('5600X', cpu_vars, query_exclusions, 299, 299, 1000)

# Zen 3 Family Plotting
zen3_frames = [df_5600x, df_5800x, df_5900x, df_5950x]
median_plotting(zen3_frames, 'Zen 3 Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(zen3_frames, 'Zen 3 Median Pricing', e_vars=cpu_vars, roll=7)
ebay_seller_plot(zen3_frames, 'Zen 3', e_vars=cpu_vars)

# ---------------------------------------------------------------------------------------------

# Big Navi Analysis
df_6800 = ebay_search('RX 6800 -XT', gpu_vars, query_exclusions, 579, 579, 2500)
df_6800xt = ebay_search('RX 6800 XT', gpu_vars, query_exclusions, 649, 850, 2000)
df_6900 = ebay_search('RX 6900', gpu_vars, query_exclusions, 999, 999, 999999, min_date=datetime(2020, 12, 8))

# Big Navi Plotting
bignavi_frames = [df_6800, df_6800xt, df_6900]
median_plotting(bignavi_frames, 'Big Navi Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(bignavi_frames, 'Big Navi Median Pricing', e_vars=gpu_vars, roll=7)

ebay_seller_plot(bignavi_frames, 'Big Navi', gpu_vars)

brand_plot(bignavi_frames, 'Big Navi AIB Comparison', e_vars=gpu_vars, roll=0)
brand_plot(bignavi_frames, 'Big Navi AIB Comparison', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# RTX 30 Series Analysis
df_3060 = ebay_search('RTX 3060 -Ti -3060ti', gpu_vars, query_exclusions, 329, 329, 2000,
                      min_date=datetime(2021, 2, 25))
df_3060ti = ebay_search('RTX (3060 Ti, 3060Ti)', gpu_vars, query_exclusions, 399, 399, 1300,
                        min_date=datetime(2020, 12, 1))
df_3070 = ebay_search('RTX 3070', gpu_vars, query_exclusions, 499, 499, 1300, min_date=datetime(2020, 10, 29))
df_3080 = ebay_search('RTX 3080', gpu_vars, query_exclusions, 699, 699, 10000, min_date=datetime(2020, 9, 17))
df_3090 = ebay_search('RTX 3090', gpu_vars, query_exclusions, 1499, 1499, 10000,
                      min_date=datetime(2020, 9, 17))

# RTX 30 Series/Ampere Plotting
df_3060ti = df_3060ti.assign(item='RTX 3060 Ti')
ampere_frames = [df_3060, df_3060ti, df_3070, df_3080, df_3090]

median_plotting(ampere_frames, 'RTX 30 Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(ampere_frames, 'RTX 30 Series Median Pricing', e_vars=gpu_vars, roll=7)

ebay_seller_plot(ampere_frames, 'RTX 30 Series-Ampere', gpu_vars)

brand_plot(ampere_frames, 'RTX 30 Series-Ampere AIB Comparison', e_vars=gpu_vars, roll=0)
brand_plot(ampere_frames, 'RTX 30 Series-Ampere AIB Comparison', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Pascal GPUs
df_titanxp = ebay_search('Titan XP', gpu_vars, query_exclusions, 1200, 0, 2000)
df_1080ti = ebay_search('GTX 1080 Ti', gpu_vars, query_exclusions, 699, 225, 1000)
df_1080 = ebay_search('GTX 1080 -Ti -1080p', gpu_vars, query_exclusions, 599, 140, 1000)
df_1070 = ebay_search('GTX 1070 -Ti', gpu_vars, query_exclusions, 379, 75, 600)
df_1070ti = ebay_search('GTX 1070 Ti', gpu_vars, query_exclusions, 449, 130, 600)
df_1060 = ebay_search('GTX 1060', gpu_vars, query_exclusions, 249, 130, 600)

# Pascal Plotting
pascal_dfs = [df_1060, df_1070ti, df_1070, df_1080, df_1080ti, df_titanxp]
median_plotting(pascal_dfs, 'Pascal (GTX 10) series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(pascal_dfs, 'Pascal (GTX 10) series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Turing 16 series
df_1650 = ebay_search('GTX 1650 -Super', gpu_vars, query_exclusions, 149, 50, 600)
df_1650S = ebay_search('GTX 1650 Super', gpu_vars, query_exclusions, 159, 50, 600)
df_1660 = ebay_search('GTX 1660 -ti -Super', gpu_vars, query_exclusions, 219, 50, 600)
df_1660S = ebay_search('GTX 1660 Super -ti', gpu_vars, query_exclusions, 229, 50, 600)
df_1660Ti = ebay_search('GTX 1660 Ti -Super', gpu_vars, query_exclusions, 279, 50, 600)

# Turing 16 Plotting
tur16_frames = [df_1650, df_1650S, df_1660, df_1660S, df_1660Ti]
median_plotting(tur16_frames, 'Turing (RTX 16) Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(tur16_frames, 'Turing (RTX 16) Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Turing GPUs
df_2060 = ebay_search('RTX 2060 -Super', gpu_vars, query_exclusions, 299, 100, 650)
df_2060S = ebay_search('RTX 2060 Super', gpu_vars, query_exclusions, 399, 79, 10008)
df_2070 = ebay_search('RTX 2070 -Super', gpu_vars, query_exclusions, 499, 79, 2800)
df_2070S = ebay_search('RTX 2070 Super', gpu_vars, query_exclusions, 499, 79, 1600)
df_2080 = ebay_search('RTX 2080 -Super -ti', gpu_vars, query_exclusions, 699, 250, 1300)
df_2080S = ebay_search('RTX 2080 Super -ti', gpu_vars, query_exclusions, 699, 299, 1600)
df_2080Ti = ebay_search('RTX 2080 ti -Super', gpu_vars, query_exclusions, 999, 400, 3800)

# Turing (RTX 20) Series Plotting
tur20_frames = [df_2060, df_2060S, df_2070, df_2080, df_2080S, df_2080Ti]
median_plotting(tur20_frames, 'Turing (RTX 20) Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(tur20_frames, 'Turing (RTX 20) Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Vega and Radeon RX 5000 Series (not bothering to separate out 4 vs 8 GB models nor the 50th anniversary
df_5500XT = ebay_search('RX 5500 xt', gpu_vars, query_exclusions, 169, 80, 400)
df_5600XT = ebay_search('RX 5600 xt', gpu_vars, query_exclusions, 279, 200, 750)
df_5700 = ebay_search('RX 5700 -xt', gpu_vars, query_exclusions, 349, 250, 550)
df_5700XT = ebay_search('RX 5700 xt', gpu_vars, query_exclusions, 499, 150, 850)
df_vega56 = ebay_search('RX vega 56', gpu_vars, query_exclusions, 399, 0, 500)
df_vega64 = ebay_search('RX vega 64', gpu_vars, query_exclusions, 499, 0, 800)
df_radeonvii = ebay_search('Radeon VII', gpu_vars, query_exclusions, 699, 0, 2000)

# Vega and Radeon RX 5000 Series Plotting
rx5000_frames = [df_5500XT, df_5600XT, df_5700, df_5700XT, df_vega56, df_vega64, df_radeonvii]

median_plotting(rx5000_frames, 'RX 5000 and Vega Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(rx5000_frames, 'RX 5000 and Vega Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Maxwell Series
df_titanx = ebay_search('titan x -xp', gpu_vars, query_exclusions, 1200, 0, 2000)
df_980Ti = ebay_search('980 Ti', gpu_vars, query_exclusions, 649, 0, 2000)
df_980 = ebay_search('980 -ti -optiplex', gpu_vars, query_exclusions, 549, 0, 2000)
df_970 = ebay_search('970', gpu_vars, query_exclusions, 329, 0, 400)
df_960 = ebay_search('960 -optiplex', gpu_vars, query_exclusions, 199, 0, 400)
df_950 = ebay_search('950 -950m', gpu_vars, query_exclusions, 159, 0, 400)

# Maxwell Series Plotting
maxwell_frames = [df_950, df_960, df_970, df_980, df_980Ti, df_titanx]
median_plotting(maxwell_frames, 'Maxwell (GTX 900) Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(maxwell_frames, 'Maxwell (GTX 900) Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Zen 2 data
df_3950X = ebay_search('3950X', cpu_vars, query_exclusions, 749, 350, 1200)
df_3900X = ebay_search('3900X -combo -custom', cpu_vars, query_exclusions, 499, 230, 920)
df_3900XT = ebay_search('3900XT -combo -custom', cpu_vars, query_exclusions, 499, 200, 800)
df_3800XT = ebay_search('3800XT -combo -custom', cpu_vars, query_exclusions, 399, 60, 800)
df_3800X = ebay_search('3800X -combo -custom', cpu_vars, query_exclusions, 399, 60, 600)
df_3700X = ebay_search('3700X -combo -custom', cpu_vars, query_exclusions, 329, 100, 551)
df_3600XT = ebay_search('3600XT -combo -custom', cpu_vars, query_exclusions, 249, 149, 600)
df_3600X = ebay_search('3600X -combo -custom -roku', cpu_vars, query_exclusions, 249, 40, 520)
df_3600 = ebay_search('(AMD, Ryzen) 3600 -combo -custom -roku -3600x -3600xt', cpu_vars, query_exclusions, 249, 30, 361)
df_3300X = ebay_search('3300X -combo -custom', cpu_vars, query_exclusions, 120, 160, 250)
df_3100 = ebay_search('(AMD, Ryzen) 3100 -combo -custom -radeon', cpu_vars, query_exclusions, 99, 79, 280)

# Zen 2 Plotting
df_3600 = df_3600.assign(item='3600')
df_3100 = df_3100.assign(item='3100')

zen2_frames = [df_3100, df_3300X, df_3600, df_3600X, df_3600XT, df_3700X, df_3800X, df_3800XT, df_3900XT, df_3900X,
               df_3950X]

median_plotting(zen2_frames, 'Zen 2 Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(zen2_frames, 'Zen 2 Median Pricing', e_vars=cpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# i9 Data
df_i9_10900k = ebay_search('i9 10900k', cpu_vars, query_exclusions, 0, 300, 1000)
df_i9_9900k = ebay_search('i9 9900k', cpu_vars, query_exclusions, 0, 100, 1000)

# i9 Plotting
i9_dfs = [df_i9_9900k, df_i9_10900k]

median_plotting(i9_dfs, 'i9 Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(i9_dfs, 'i9 Median Pricing', e_vars=cpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# i7 Data
df_i7_10700k = ebay_search('i7 10700k', cpu_vars, query_exclusions, 374, 100, 1000)
df_i7_9700k = ebay_search('i7 9700k', cpu_vars, query_exclusions, 374, 100, 1000)
df_i7_8700k = ebay_search('i7 8700k', cpu_vars, query_exclusions, 359, 100, 1000)
df_i7_7700k = ebay_search('i7 7700k', cpu_vars, query_exclusions, 339, 0, 1000)
df_i7_6700k = ebay_search('i7 6700k', cpu_vars, query_exclusions, 339, 0, 1000)
df_i7_4790k = ebay_search('i7 4790k', cpu_vars, query_exclusions, 339, 0, 1000)
df_i7_4770k = ebay_search('i7 4770k', cpu_vars, query_exclusions, 339, 0, 1000)
df_i7_3770k = ebay_search('i7 3770k', cpu_vars, query_exclusions, 342, 0, 1000)
df_i7_2700k = ebay_search('i7 (2600k, 2700k)', cpu_vars, query_exclusions, 332, 0, 1000)
df_i7_970 = ebay_search('i7 (970, 980, 980X, 990X)', cpu_vars, query_exclusions, 583, 0, 1000)
df_i7_lynnfield = ebay_search('i7 (860, 970, 870k, 880)', cpu_vars, query_exclusions, 284, 0, 1000)
df_i7_nehalem = ebay_search('i7 (920, 930, 940, 950, 960, 965, 975)', cpu_vars, query_exclusions, 284, 0, 1000)

# i7 Plotting
df_i7_970 = df_i7_970.assign(item='i7 970+')
df_i7_lynnfield = df_i7_lynnfield.assign(item='i7 Lynnfield')
df_i7_nehalem = df_i7_nehalem.assign(item='i7 Nehalem')

i7_frames = [df_i7_nehalem, df_i7_lynnfield, df_i7_970, df_i7_2700k, df_i7_3770k, df_i7_4770k, df_i7_4790k, df_i7_6700k,
             df_i7_7700k, df_i7_8700k, df_i7_9700k, df_i7_10700k]

median_plotting(i7_frames, 'i7 Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(i7_frames, 'i7 Median Pricing', e_vars=cpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

#  Zen Series
df_1800X = ebay_search('(amd, ryzen) 1800X', cpu_vars, query_exclusions, 499, 0, 500)
df_1700X = ebay_search('(amd, ryzen) 1700X', cpu_vars, query_exclusions, 399, 0, 500)
df_1700 = ebay_search('(amd, ryzen) 1700 -1700X', cpu_vars, query_exclusions, 329, 0, 500)
df_1600X = ebay_search('(amd, ryzen) 1600X', cpu_vars, query_exclusions, 249, 0, 500)
df_1600 = ebay_search('(amd, ryzen) 1600', cpu_vars, query_exclusions, 219, 0, 500)
df_1500X = ebay_search('(amd, ryzen) 1500X', cpu_vars, query_exclusions, 189, 0, 500)
df_1400 = ebay_search('(amd, ryzen) 1400', cpu_vars, query_exclusions, 169, 0, 500)
df_1300X = ebay_search('(amd, ryzen) 1300X', cpu_vars, query_exclusions, 129, 0, 500)
df_1200 = ebay_search('(amd, ryzen) 1200 -intel', cpu_vars, query_exclusions, 109, 0, 500)

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

zen_frames = [df_1200, df_1300X, df_1400, df_1500X, df_1600, df_1600X, df_1700, df_1700X, df_1800X]

median_plotting(zen_frames, 'Zen Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(zen_frames, 'Zen Median Pricing', e_vars=cpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

#  Zen+ Series
df_2700X = ebay_search('(amd, ryzen) 2700X', cpu_vars, query_exclusions, 329, 100, 500)
df_2700 = ebay_search('(amd, ryzen) 2700 -2700X', cpu_vars, query_exclusions, 299, 50, 500)
df_2600X = ebay_search('(amd, ryzen) 2600X', cpu_vars, query_exclusions, 229, 0, 500)
df_2600 = ebay_search('(amd, ryzen) 2600 -2600X', cpu_vars, query_exclusions, 199, 0, 500)
df_1600af = ebay_search('(amd, ryzen) 1600 AF', cpu_vars, query_exclusions, 85, 0, 500)
# df_1200af = ebay_search('(amd, ryzen) 1200 AF', cpu_vars, query_exclusions, 85, 0, 500)

# Zen+ Plotting
df_1600af = df_1600af.assign(item='1600AF')
df_2600 = df_2600.assign(item='2600')
df_2600X = df_2600X.assign(item='2600X')
df_2700 = df_2700.assign(item='2700')
df_2700X = df_2700X.assign(item='2700X')

zenplus_frames = [df_1600af, df_2600, df_2600X, df_2700, df_2700X]

median_plotting(zenplus_frames, 'Zen+ Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(zenplus_frames, 'Zen+ Median Pricing', e_vars=cpu_vars, roll=0)

# ---------------------------------------------------------------------------------------------

# PS4 Analysis
df_ps4 = ebay_search('PS4 -pro -repair -box -broken -parts -bad', console_vars, query_exclusions, 399, 60, 5000)
df_ps4_pro = ebay_search('PS4 pro -repair -box -broken -parts -bad', console_vars, query_exclusions, 399, 60, 5000)

# PS4 Series Plotting
ps4_frames = [df_ps4, df_ps4_pro]
median_plotting(ps4_frames, 'PS4 Median Pricing', e_vars=console_vars, roll=0)
median_plotting(ps4_frames, 'PS4 Median Pricing', e_vars=console_vars, roll=7)

# ---------------------------------------------------------------------------------------------


# Xbox One Analysis
df_xbox_one_s = ebay_search('Xbox One S -pro -series -repair -box -broken -parts -bad', console_vars, query_exclusions,
                            299, 60, 11000)
df_xbox_one_x = ebay_search('Xbox One X -repair -series -box -broken -parts -bad', console_vars, query_exclusions, 499,
                            100, 11000)

# Xbox One Series Plotting
xbox_one_frames = [df_xbox_one_s, df_xbox_one_x]
median_plotting(xbox_one_frames, 'Xbox One Median Pricing', e_vars=console_vars, roll=0)
median_plotting(xbox_one_frames, 'Xbox One Median Pricing', e_vars=console_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# PS5 Analysis (All time)
df_ps5_digital = ebay_search('PS5 Digital', console_vars, ps5_digi_excludes, 399, 300, 11000,
                             min_date=datetime(2020, 9, 16))
df_ps5_disc = ebay_search('PS5 -digital', console_vars, query_exclusions, 499, 450, 11000,
                          min_date=datetime(2020, 9, 16))

# PS5 Plotting
df_ps5_disc = df_ps5_disc.assign(item='PS5 Disc')
ps5_frames = [df_ps5_digital, df_ps5_disc]

median_plotting(ps5_frames, 'PS5 Median Pricing', e_vars=console_vars, roll=0)
median_plotting(ps5_frames, 'PS5 Median Pricing', e_vars=console_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Xbox Analysis (All time)
df_xbox_s = ebay_search('Xbox Series S', console_vars, query_exclusions, 299, 250, 11000,
                        min_date=datetime(2020, 9, 22), )
df_xbox_x = ebay_search('Xbox Series X', console_vars, query_exclusions, 499, 350, 11000,
                        min_date=datetime(2020, 9, 22))

# Xbox Plotting
xbox_series_frames = [df_ps5_digital, df_ps5_disc]

ebay_seller_plot(xbox_series_frames, 'Xbox', console_vars)
median_plotting(xbox_series_frames, 'Xbox Median Pricing', e_vars=console_vars, roll=0)
median_plotting(xbox_series_frames, 'Xbox Median Pricing', e_vars=console_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Nintendo Switch
df_switch = ebay_search('Nintendo Switch -lite', console_vars, query_exclusions, 300, 0, 2800)
df_switch_lite = ebay_search('Nintendo Switch Lite', console_vars, query_exclusions, 200, 0, 2800)

# Nintendo Switch Plotting
switch_frames = [df_switch_lite, df_switch]

ebay_seller_plot(switch_frames, 'Nintendo Switch', console_vars)
median_plotting(switch_frames, 'Nintendo Switch Median Pricing', e_vars=console_vars, roll=0)
median_plotting(switch_frames, 'Nintendo Switch Median Pricing', e_vars=console_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Fermi Series
df_520 = ebay_search('(nvidia, GTX, geforce, gt) 520 -nvs -quadro', gpu_vars, query_exclusions, 59, 0, 2000)
df_530 = ebay_search('(nvidia, GTX, geforce, gt) 530 -nvs -quadro -tesla', gpu_vars, query_exclusions, 75, 0, 400)
df_545 = ebay_search('(nvidia, GTX, geforce, gt) 545 -nvs -quadro', gpu_vars, query_exclusions, 109, 0, 2000)
df_550ti = ebay_search('(nvidia, GTX, geforce, gt) 550 ti -nvs -quadro', gpu_vars, query_exclusions, 149, 0, 400)
df_560 = ebay_search('(nvidia, GTX, geforce, gt) 560 -ti -nvs -quadro', gpu_vars, query_exclusions, 199, 0, 400)
df_570 = ebay_search('(nvidia, GTX, geforce, gt) 570 -nvs -quadro', gpu_vars, query_exclusions, 349, 0, 400)
df_580 = ebay_search('(nvidia, GTX, geforce, gt) 580 -nvs -quadro', gpu_vars, query_exclusions, 499, 0, 400)
df_590 = ebay_search('(nvidia, GTX, geforce, gt) 590 -nvs -quadro', gpu_vars, query_exclusions, 699, 0, 400)

df_520 = df_520.assign(item='520')
df_530 = df_530.assign(item='530')
df_545 = df_545.assign(item='545')
df_550ti = df_550ti.assign(item='550 Ti')
df_560 = df_560.assign(item='560')
df_570 = df_570.assign(item='570')
df_580 = df_580.assign(item='580')
df_590 = df_590.assign(item='590')

fermi_frames = [df_520, df_530, df_545, df_550ti, df_560, df_570, df_580, df_590]
median_plotting(fermi_frames, 'Fermi (GTX 500) Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(fermi_frames, 'Fermi (GTX 500) Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

df_605 = ebay_search('(nvidia, GTX, geforce, gt) 605 -nvs -quadro', gpu_vars, query_exclusions, 0, 0, 2000, )
df_610 = ebay_search('(nvidia, GTX, geforce, gt) 610 -nvs -quadro', gpu_vars, query_exclusions, 0, 0, 2000, )
df_630 = ebay_search('(nvidia, GTX, geforce, gt) 630 -nvs -quadro', gpu_vars, query_exclusions, 0, 0, 400, )
df_640 = ebay_search('(nvidia, GTX, geforce, gt) 640 -nvs -quadro', gpu_vars, query_exclusions, 100, 0, 400)
df_650 = ebay_search('(nvidia, GTX, geforce, gt) 650 -ti -nvs -quadro', gpu_vars, query_exclusions, 110, 0, 400)
df_650ti = ebay_search('(nvidia, GTX, geforce, gt) 650 Ti -nvs -quadro', gpu_vars, query_exclusions, 150, 0, 400)
df_660 = ebay_search('(nvidia, GTX, geforce, gt) 660 -ti -nvs -quadro', gpu_vars, query_exclusions, 230, 0, 400)
df_660ti = ebay_search('(nvidia, GTX, geforce, gt) 660 Ti -nvs -quadro', gpu_vars, query_exclusions, 300, 0, 400)
df_670 = ebay_search('(nvidia, GTX, geforce, gt) 670 -nvs -quadro', gpu_vars, query_exclusions, 400, 0, 400)
df_680 = ebay_search('(nvidia, GTX, geforce, gt) 680 -nvs -quadro', gpu_vars, query_exclusions, 500, 0, 400)
df_690 = ebay_search('(nvidia, GTX, geforce, gt) 690 -nvs -quadro', gpu_vars, query_exclusions, 1000, 0, 400)

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

kepler_frames = [df_605, df_610, df_630, df_640, df_650, df_650ti, df_660, df_660ti, df_670, df_680, df_690]
median_plotting(kepler_frames, 'Kepler (GTX 600) Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(kepler_frames, 'Kepler (GTX 600) Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

df_710 = ebay_search('(nvidia, GTX, geforce, gt) 710 -nvs -quadro', gpu_vars, query_exclusions, 40, 0, 2000)
df_720 = ebay_search('(nvidia, GTX, geforce, gt) 720 -nvs -quadro', gpu_vars, query_exclusions, 55, 0, 2000)
df_730 = ebay_search('(nvidia, GTX, geforce, gt) 730 -nvs -quadro', gpu_vars, query_exclusions, 75, 0, 400)
df_740 = ebay_search('(nvidia, GTX, geforce, gt) 740 -nvs -quadro', gpu_vars, query_exclusions, 5, 0, 400)
df_750 = ebay_search('(nvidia, GTX, geforce, gt) 750 -ti -nvs -quadro', gpu_vars, query_exclusions, 119, 0, 400)
df_750ti = ebay_search('(nvidia, GTX, geforce, gt) 750 Ti -nvs -quadro', gpu_vars, query_exclusions, 149, 0, 400)
df_760 = ebay_search('(nvidia, GTX, geforce, gt) 760 -nvs -quadro', gpu_vars, query_exclusions, 249, 0, 400)
df_770 = ebay_search('(nvidia, GTX, geforce, gt) 770 -nvs -quadro', gpu_vars, query_exclusions, 399, 0, 400)
df_780 = ebay_search('(nvidia, GTX, geforce, gt) 780 -ti -nvs -quadro', gpu_vars, query_exclusions, 649, 0, 400)
df_780ti = ebay_search('(nvidia, GTX, geforce, gt) 780 ti -nvs -quadro', gpu_vars, query_exclusions, 699, 0, 400)
df_titanblack = ebay_search('(nvidia, GTX, geforce, gt) titan black -nvs -quadro', gpu_vars, query_exclusions, 999, 0,
                            400)
df_titanz = ebay_search('(nvidia, GTX, geforce, gt) titan Z -nvs -quadro', gpu_vars, query_exclusions, 2999, 0, 400)

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

maxwell_kepler_frames = [df_710, df_720, df_730, df_740, df_750, df_750ti, df_760, df_770, df_780, df_780ti,
                         df_titanblack, df_titanz]
median_plotting(maxwell_kepler_frames, 'Maxwell-Kepler (GTX 700) Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(maxwell_kepler_frames, 'Maxwell-Kepler (GTX 700) Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# RX 500 Series
df_RX550 = ebay_search('RX 550 -550x', gpu_vars, query_exclusions, 79, 0, 400)
df_RX550X = ebay_search('RX 550x', gpu_vars, query_exclusions, 79, 0, 750)
df_RX560 = ebay_search('RX 560', gpu_vars, query_exclusions, 99, 0, 550)
df_RX570 = ebay_search('RX 570', gpu_vars, query_exclusions, 169, 0, 850)
df_RX580 = ebay_search('RX 580', gpu_vars, query_exclusions, 199, 0, 500)
df_RX590 = ebay_search('RX 590', gpu_vars, query_exclusions, 279, 0, 800)

rx_500_frames = [df_RX550, df_RX550X, df_RX560, df_RX570, df_RX580, df_RX590]
median_plotting(rx_500_frames, 'RX 500 Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(rx_500_frames, 'RX 500 Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# R5/R7/R9 Series
df_R7350 = ebay_search('R7 350', gpu_vars, query_exclusions, 89, 0, 850)
df_R7360 = ebay_search('R7 360', gpu_vars, query_exclusions, 109, 0, 500)
df_R9370X = ebay_search('R9 370X', gpu_vars, query_exclusions, 179, 0, 800)
df_R9380 = ebay_search('R9 380 -380X', gpu_vars, query_exclusions, 199, 0, 800)
df_R9380X = ebay_search('R9 380X', gpu_vars, query_exclusions, 229, 0, 800)
df_R9390 = ebay_search('R9 390', gpu_vars, query_exclusions, 329, 0, 800)
df_R9390X = ebay_search('R9 390X', gpu_vars, query_exclusions, 429, 0, 800)
df_R9FURY = ebay_search('R9 Fury -X', gpu_vars, query_exclusions, 549, 0, 800)
df_R9FURYX = ebay_search('R9 Fury x', gpu_vars, query_exclusions, 649, 0, 800)
df_R9NANO = ebay_search('R9 Nano', gpu_vars, query_exclusions, 649, 0, 800)
df_RADEONPRODUO = ebay_search('Radeon Pro Duo', gpu_vars, query_exclusions, 1499, 0, 2000)

r5_frames = [df_R7350, df_R7360, df_R9380X, df_R9390, df_R9390X, df_R9FURY, df_R9FURYX, df_R9NANO, df_RADEONPRODUO]
median_plotting(r5_frames, 'R5-R7-R9 Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(r5_frames, 'R5-R7-R9 Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# RX 400 Series
df_RX460 = ebay_search('RX 460', gpu_vars, query_exclusions, 109, 0, 400)
df_RX470 = ebay_search('RX 470', gpu_vars, query_exclusions, 179, 0, 750)
df_RX480 = ebay_search('RX 480', gpu_vars, query_exclusions, 199, 0, 550)

rx_400_frames = [df_RX460, df_RX470, df_RX480]
median_plotting(rx_400_frames, 'RX 400 Series Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(rx_400_frames, 'RX 400 Series Median Pricing', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------
