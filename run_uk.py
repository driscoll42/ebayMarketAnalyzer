"""

"""

# Moving all the calls of the code out of the main.py to reduce confusion/overhead.

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
                       country='UK',
                       ccode='£',
                       days_before=30,
                       feedback=True,
                       quantity_hist=True,
                       debug=False,
                       verbose=False,
                       sacat=0,
                       tax_rate=0.0,
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

# ---------------------------------------------------------------------------------------------

# Zen 3 Data Scraping & Analysis
df_5950x = ebay_search('5950X', cpu_vars, query_exclusions, 750, 799, 2200)
df_5900x = ebay_search('5900X', cpu_vars, query_exclusions, 510, 549, 2050)
df_5800x = ebay_search('5800X', cpu_vars, query_exclusions, 420, 449, 1000)
df_5600x = ebay_search('5600X', cpu_vars, query_exclusions, 280, 299, 1000)

# Zen 3 Family Plotting
zen3_frames = [df_5600x, df_5800x, df_5900x, df_5950x]
median_plotting(zen3_frames, 'Zen 3 UK Median Pricing', e_vars=cpu_vars, roll=0)
median_plotting(zen3_frames, 'Zen 3 UK Median Pricing', e_vars=cpu_vars, roll=7)
ebay_seller_plot(zen3_frames, 'Zen 3', e_vars=cpu_vars)

# ---------------------------------------------------------------------------------------------

# Big Navi Analysis
df_6800 = ebay_search('RX 6800 -XT', gpu_vars, query_exclusions, 579, 579, 2500)
df_6800xt = ebay_search('RX 6800 XT', gpu_vars, query_exclusions, 649, 850, 2000)
df_6900 = ebay_search('RX 6900', gpu_vars, query_exclusions, 950, 950, 999999, min_date=datetime(2020, 12, 8))

# Big Navi Plotting
bignavi_frames = [df_6800, df_6800xt, df_6900]
median_plotting(bignavi_frames, 'Big Navi UK Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(bignavi_frames, 'Big Navi UK Median Pricing', e_vars=gpu_vars, roll=7)

ebay_seller_plot(bignavi_frames, 'Big NaviUK ', gpu_vars)

brand_plot(bignavi_frames, 'Big Navi UK AIB Comparison', e_vars=gpu_vars, roll=0)
brand_plot(bignavi_frames, 'Big Navi UK AIB Comparison', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# RTX 30 Series Analysis
df_3060 = ebay_search('RTX 3060 -Ti -3060ti', gpu_vars, query_exclusions, 299, 299, 2000,
                      min_date=datetime(2021, 2, 25))
df_3060ti = ebay_search('RTX (3060 Ti, 3060Ti)', gpu_vars, query_exclusions, 369, 369, 1300,
                        min_date=datetime(2020, 12, 1))
df_3070 = ebay_search('RTX 3070', gpu_vars, query_exclusions, 469, 469, 1300, min_date=datetime(2020, 10, 29))
df_3080 = ebay_search('RTX 3080', gpu_vars, query_exclusions, 649, 649, 10000, min_date=datetime(2020, 9, 17))
df_3090 = ebay_search('RTX 3090', gpu_vars, query_exclusions, 1399, 1399, 10000,
                      min_date=datetime(2020, 9, 17))

# RTX 30 Series/Ampere Plotting
df_3060ti = df_3060ti.assign(item='RTX 3060 Ti')
ampere_frames = [df_3060, df_3060ti, df_3070, df_3080, df_3090]

median_plotting(ampere_frames, 'RTX 30 Series UK Median Pricing', e_vars=gpu_vars, roll=0)
median_plotting(ampere_frames, 'RTX 30 Series UK Median Pricing', e_vars=gpu_vars, roll=7)

ebay_seller_plot(ampere_frames, 'RTX 30 Series-Ampere UK', gpu_vars)

brand_plot(ampere_frames, 'RTX 30 Series-Ampere UK AIB Comparison', e_vars=gpu_vars, roll=0)
brand_plot(ampere_frames, 'RTX 30 Series-Ampere UK AIB Comparison', e_vars=gpu_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# PS5 Analysis (All time)
df_ps5_digital = ebay_search('PS5 Digital', console_vars, ps5_digi_excludes, 360, 300, 11000,
                             min_date=datetime(2020, 9, 16))
df_ps5_disc = ebay_search('PS5 -digital', console_vars, query_exclusions, 450, 450, 11000,
                          min_date=datetime(2020, 9, 16))

# PS5 Plotting
df_ps5_disc = df_ps5_disc.assign(item='PS5 Disc')
ps5_frames = [df_ps5_digital, df_ps5_disc]

median_plotting(ps5_frames, 'PS5 Median UK Pricing', e_vars=console_vars, roll=0)
median_plotting(ps5_frames, 'PS5 Median UK Pricing', e_vars=console_vars, roll=7)

# ---------------------------------------------------------------------------------------------

# Xbox Analysis (All time)
df_xbox_s = ebay_search('Xbox Series S', console_vars, query_exclusions, 250, 250, 11000,
                        min_date=datetime(2020, 9, 22), )
df_xbox_x = ebay_search('Xbox Series X', console_vars, query_exclusions, 450, 350, 11000,
                        min_date=datetime(2020, 9, 22))

# Xbox Plotting
xbox_series_frames = [df_ps5_digital, df_ps5_disc]

ebay_seller_plot(xbox_series_frames, 'Xbox', console_vars)
median_plotting(xbox_series_frames, 'Xbox Median UK Pricing', e_vars=console_vars, roll=0)
median_plotting(xbox_series_frames, 'Xbox Median UK Pricing', e_vars=console_vars, roll=7)
