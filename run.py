# Moving all the calls of the code out of the main.py to reduce confusion/overhead.

import datetime

import pandas as pd

from main import brand_plot
from main import ebay_search
from main import ebay_seller_plot
from main import median_plotting

run_all_feedback = True
run_all_hist = True
run_cached = False
sleep_len = 5
country = 'USA'
debug = False
verbose = False
days_before = 5

comp_store_rate = 0.04
comp_non_store_rate = 0.1
vg_store_rate = 0.0915
vg_non_store_rate = 0.1
tax_rate = 0.0625

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


df_darkhero = ebay_search('ASUS Dark Hero -image -jpeg -img -picture -pic -jpg', 399, 400, 1000,
                          run_cached=run_cached,
                          feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                          sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug,
                          verbose=verbose,
                          sacat=mobo_sacat,
                          days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

# Zen 3 Analysis
df_5950x = ebay_search('5950X -image -jpeg -img -picture -pic -jpg', 799, 400, 2200, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       country=country, debug=debug, verbose=verbose, days_before=days_before,
                       store_rate=comp_store_rate,
                       non_store_rate=comp_non_store_rate, sacat=cpu_sacat)
df_5900x = ebay_search('5900X -image -jpeg -img -picture -pic -jpg', 549, 499, 2050, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       country=country, debug=debug, verbose=verbose, days_before=days_before,
                       store_rate=comp_store_rate,
                       non_store_rate=comp_non_store_rate, sacat=cpu_sacat)
df_5800x = ebay_search('5800X -image -jpeg -img -picture -pic -jpg', 449, 400, 1000, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       country=country, debug=debug, verbose=verbose, days_before=days_before,
                       store_rate=comp_store_rate,
                       non_store_rate=comp_non_store_rate, sacat=cpu_sacat)
df_5600x = ebay_search('5600X -image -jpeg -img -picture -pic -jpg', 299, 250, 1000, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 11, 1),
                       sleep_len=sleep_len, country=country, extra_title_text='', debug=debug, verbose=verbose,
                       days_before=days_before,
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
df_6800 = ebay_search('RX 6800 -XT -image -jpeg -img -picture -pic -jpg', 579, 400, 2500,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)
df_6800xt = ebay_search('RX 6800 XT -image -jpeg -img -picture -pic -jpg', 649, 850, 2000,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist,
                        extra_title_text='', sleep_len=sleep_len, brand_list=brand_list,
                        model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate,
                        non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)  # There are some $5000+, but screw with graphs
df_6900 = ebay_search('RX 6900 -image -jpeg -img -picture -pic -jpg', 999, 100, 999999, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 12, 8),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list,
                      model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)  # Not out until December 8

# Big Navi Plotting
median_plotting([df_6800, df_6800xt, df_6900], ['RX 6800', 'RX 6800 XT', 'RX 6900'], 'Big Navi Median Pricing', roll=0,
                msrps=[579, 649, 999])
median_plotting([df_6800, df_6800xt, df_6900], ['RX 6800', 'RX 6800 XT', 'RX 6900'], 'Big Navi Median Pricing', roll=7,
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
df_3060 = ebay_search('RTX 3060 -Ti -3060ti -image -jpeg -img -picture -pic -jpg', 329, 200, 2000,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2021, 2, 25),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, verbose=verbose,
                      store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)
df_3060ti = ebay_search('RTX (3060 Ti, 3060Ti) -image -jpeg -img -picture -pic -jpg', 399, 200, 1300,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 12, 1),
                        extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                        country=country, days_before=days_before, debug=debug, verbose=verbose,
                        store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)
df_3070 = ebay_search('RTX 3070 -image -jpeg -img -picture -pic -jpg', 499, 499, 1300, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 10, 29),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, verbose=verbose,
                      store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)
df_3080 = ebay_search('RTX 3080 -image -jpeg -img -picture -pic -jpg', 699, 550, 10000, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 17),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, verbose=verbose,
                      store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)
df_3090 = ebay_search('RTX 3090 -image -jpeg -img -picture -pic -jpg', 1499, 550, 10000,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 17),
                      extra_title_text='', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, days_before=days_before, debug=debug, verbose=verbose,
                      store_rate=comp_store_rate,
                      non_store_rate=comp_non_store_rate, sacat=graphics_card_sacat)

# RTX 30 Series/Ampere Plotting
median_plotting([df_3060, df_3060ti, df_3070, df_3080, df_3090], ['3060', '3060 Ti', '3070', '3080', '3090'],
                'RTX 30 Series Median Pricing',
                roll=0, msrps=[329, 399, 499, 699, 1499])
median_plotting([df_3060, df_3060ti, df_3070, df_3080, df_3090], ['3060', '3060 Ti', '3070', '3080', '3090'],
                'RTX 30 Series Median Pricing',
                roll=7, msrps=[329, 399, 499, 699, 1499])

df_3060 = df_3060.assign(item='3060')
df_3060ti = df_3060ti.assign(item='3060 Ti')
df_3070 = df_3070.assign(item='3070')
df_3080 = df_3080.assign(item='3080')
df_3090 = df_3090.assign(item='3090')

frames = [df_3060, df_3060ti, df_3070, df_3080, df_3090]
com_df = pd.concat(frames)
ebay_seller_plot('RTX 30 Series-Ampere', com_df, extra_title_text='')

brand_plot([df_3060, df_3060ti, df_3070, df_3080, df_3090], 'RTX 30 Series-Ampere AIB Comparison', brand_list,
           [329, 399, 499, 699, 1499])
brand_plot([df_3060, df_3060ti, df_3070, df_3080, df_3090], 'RTX 30 Series-Ampere AIB Comparison', brand_list,
           [329, 399, 499, 699, 1499], roll=7)

# Pascal GPUs
df_titanxp = ebay_search('titan xp', 1200, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                         quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                         brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                         debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                         sacat=graphics_card_sacat)

df_1080ti = ebay_search('1080 Ti -image -jpeg -img -picture -pic -jpg', 699, 225, 1000, feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_1080 = ebay_search('gtx 1080 -Ti -image -jpeg -img -picture -pic -jpg -1080p', 599, 140, 1000,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1070 = ebay_search('gtx 1070 -Ti -image -jpeg -img -picture -pic -jpg', 379, 75, 600,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1070ti = ebay_search('gtx 1070 Ti -image -jpeg -img -picture -pic -jpg', 449, 130, 600,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_1060 = ebay_search('gtx 1060 -image -jpeg -img -picture -pic -jpg', 249, 130, 600, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
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
median_plotting(frames, ['1060', '1070', '1070 Ti', '1080', '1080 Ti', 'Titan XP'],
                'Pascal (GTX 10) series Median Pricing', roll=7,
                msrps=[249, 599, 599, 599, 699, 1200])

# Turing 16 series
df_1650 = ebay_search('gtx 1650 -super -image -jpeg -img -picture -pic -jpg', 149, 50, 600,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1650S = ebay_search('gtx 1650 super -image -jpeg -img -picture -pic -jpg', 159, 50, 600,
                       feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_1660 = ebay_search('gtx 1660 -ti -super -image -jpeg -img -picture -pic -jpg', 219, 50, 600,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_1660S = ebay_search('gtx 1660 Super -ti -image -jpeg -img -picture -pic -jpg', 229, 50, 600,
                       feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_1660Ti = ebay_search('gtx 1660 Ti -super -image -jpeg -img -picture -pic -jpg', 279, 50, 600,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_1650 = df_1650.assign(item='1650')
df_1650S = df_1650S.assign(item='1650S')
df_1660 = df_1660.assign(item='1660')
df_1660S = df_1660S.assign(item='1660S')
df_1660Ti = df_1660Ti.assign(item='1660Ti')

frames = [df_1650, df_1650S, df_1660, df_1660S, df_1660Ti]

median_plotting(frames, ['1650', '1650S', '1660', '1660S', '1660 Ti'], 'Turing (RTX 16) Series Median Pricing', roll=0,
                msrps=[149, 159, 249, 229, 279])
median_plotting(frames, ['1650', '1650S', '1660', '1660S', '1660 Ti'], 'Turing (RTX 16) Series Median Pricing', roll=7,
                msrps=[149, 159, 249, 229, 279])

# Turing GPUs
df_2060 = ebay_search('rtx 2060 -super', 299, 100, 650, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_2060S = ebay_search('rtx 2060 super', 399, 79, 10008, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_2070 = ebay_search('rtx 2070 -super', 499, 79, 2800, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_2070S = ebay_search('rtx 2070 super', 499, 79, 1600, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_2080 = ebay_search('rtx 2080 -super -ti', 699, 250, 1300, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_2080S = ebay_search('rtx 2080 super -ti', 699, 299, 1600, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_2080Ti = ebay_search('rtx 2080 ti -super', 999, 400, 3800, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
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
median_plotting(frames,
                ['2060', '2060S', '2070', '2080', '2080S', '2080 Ti'],
                'Turing (RTX 20) Series Median Pricing', roll=7,
                msrps=[299, 399, 499, 499, 699, 699, 999])

# Vega and Radeon RX 5000 Series (not bothering to separate out 4 vs 8 GB models nor the 50th anniversary
df_5500XT = ebay_search('rx 5500 xt', 169, 80, 400, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_5600XT = ebay_search('rx 5600 xt', 279, 200, 750, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_5700 = ebay_search('rx 5700 -xt', 349, 250, 550, run_cached=run_cached, feedback=run_all_feedback,
                      quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=graphics_card_sacat)

df_5700XT = ebay_search('rx 5700 xt', 499, 150, 850, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_vega56 = ebay_search('rx vega 56', 399, 0, 500, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_vega64 = ebay_search('rx vega 64', 499, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_radeonvii = ebay_search('Radeon VII', 699, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                           quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                           brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                           debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
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
median_plotting(frames,
                ['RX 5500 XT', 'RX 5600 XT', 'RX 5700', 'RX 5700 XT', 'RX Vega 56', 'RX Vega 64', 'Radeon VII'],
                'RX 5000 and Vega Series Median Pricing', roll=7,
                msrps=[169, 279, 349, 499, 399, 499, 699])

# Maxwell Series

df_titanx = ebay_search('titan x -xp', 1200, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_980Ti = ebay_search('980 Ti', 649, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_980 = ebay_search('980 -ti -optiplex', 549, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_970 = ebay_search('970', 329, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_960 = ebay_search('960 -optiplex', 199, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_950 = ebay_search('950 -950m', 159, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
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
median_plotting(frames, ['950', '960', '970', '980', '980 Ti', 'Titan X'], 'Maxwell (GTX 900) Series Median Pricing',
                roll=7,
                msrps=[159, 199, 329, 549, 649, 1200])

# Zen 2 data
df_3950X = ebay_search('3950X -image -jpeg -img -picture -pic -jpg', 749, 350, 1200, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=False, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_3900X = ebay_search('3900X -combo -custom', 499, 230, 920, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_3900XT = ebay_search('3900XT -combo -custom', 499, 200, 800, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=cpu_sacat)

df_3800XT = ebay_search('3800XT -combo -custom', 399, 60, 800, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=cpu_sacat)

df_3800X = ebay_search('3800X -combo -custom', 399, 60, 600, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_3700X = ebay_search('3700X -combo -custom', 329, 100, 551, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_3600XT = ebay_search('3600XT -combo -custom', 249, 149, 600, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=cpu_sacat)

df_3600X = ebay_search('3600X -combo -custom -roku', 249, 40, 520, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_3600 = ebay_search('(AMD, Ryzen) 3600 -combo -custom -roku -3600x -3600xt', 249, 30, 361,
                      run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

df_3300X = ebay_search('3300X -combo -custom', 120, 160, 250, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_3100 = ebay_search('(AMD, Ryzen) 3100 -combo -custom -radeon', 99, 79, 280, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

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
median_plotting(frames,
                ['3100', '3300X', '3600', '3600X', '3600XT', '3700X', '3800X', '3800XT', '3900XT', '3900X', '3950X'],
                'Zen 2 Median Pricing', roll=7,
                msrps=[99, 120, 249, 249, 249, 329, 399, 399, 499, 499, 749]
                )

df_i9_10900k = ebay_search('i9 10900k', 0, 300, 1000, feedback=run_all_feedback,
                           run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                           brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                           debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                           sacat=cpu_sacat)

df_i9_9900k = ebay_search('i9 9900k', 0, 100, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

# i9 Plotting

df_i9_10900k = df_i9_10900k.assign(item='i9 10900k')
df_i9_9900k = df_i9_9900k.assign(item='i9 9900k')

frames = [df_i9_9900k, df_i9_10900k]
com_df = pd.concat(frames)

median_plotting(frames,
                ['i9 9900k', 'i9 10900k'], 'i9 Median Pricing', roll=0,
                msrps=[488, 488])

median_plotting(frames,
                ['i9 9900k', 'i9 10900k'], 'i9 Median Pricing', roll=7,
                msrps=[488, 488])
# i7 Plotting
df_i7_10700k = ebay_search('i7 10700k', 374, 100, 1000, feedback=run_all_feedback,
                           run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                           brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                           debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                           sacat=cpu_sacat)

df_i7_9700k = ebay_search('i7 9700k', 374, 100, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_8700k = ebay_search('i7 8700k', 359, 100, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_7700k = ebay_search('i7 7700k', 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_6700k = ebay_search('i7 6700k', 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_4790k = ebay_search('i7 4790k', 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_4770k = ebay_search('i7 4770k', 339, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_3770k = ebay_search('i7 3770k', 342, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_2700k = ebay_search('i7 (2600k, 2700k)', 332, 0, 1000, feedback=run_all_feedback,
                          run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                          brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                          debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                          sacat=cpu_sacat)

df_i7_970 = ebay_search('i7 (970, 980, 980X, 990X)', 583, 0, 1000, feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=cpu_sacat)

df_i7_lynnfield = ebay_search('i7 (860, 970, 870k, 880)', 284, 0, 1000, feedback=run_all_feedback,
                              run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='',
                              sleep_len=sleep_len,
                              brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                              debug=debug, verbose=verbose, store_rate=comp_store_rate,
                              non_store_rate=comp_non_store_rate,
                              sacat=cpu_sacat)

df_i7_nehalem = ebay_search('i7 (920, 930, 940, 950, 960, 965, 975)', 284, 0, 1000, feedback=run_all_feedback,
                            run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                            brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                            debug=debug, verbose=verbose, store_rate=comp_store_rate,
                            non_store_rate=comp_non_store_rate,
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
median_plotting(frames,
                ['i7 Nehalem', 'i7 Lynnfield', 'i7 970+', 'i7 2700k', 'i7 3770k', 'i7 4770k', 'i7 4790k', 'i7 6700k',
                 'i7 7700k', 'i7 8700k', 'i7 9700K', 'i7 10700k'],
                'i7 Median Pricing', roll=7,
                msrps=[284, 284, 583, 332, 342, 339, 339, 339, 339, 359, 374, 374])

#  Zen Series

df_1800X = ebay_search('(amd, ryzen) 1800X', 499, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_1700X = ebay_search('(amd, ryzen) 1700X', 399, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_1700 = ebay_search('(amd, ryzen) 1700 -1700X', 329, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

df_1600X = ebay_search('(amd, ryzen) 1600X', 249, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_1600 = ebay_search('(amd, ryzen) 1600', 219, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

df_1500X = ebay_search('(amd, ryzen) 1500X', 189, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_1400 = ebay_search('(amd, ryzen) 1400', 169, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

df_1300X = ebay_search('(amd, ryzen) 1300X', 129, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_1200 = ebay_search('(amd, ryzen) 1200 -intel', 109, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

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
median_plotting(frames,
                ['1200', '1300X', '1400', '1500X', '1600', '1600X', '1700', '1700X', '1800X'],
                'Zen Median Pricing', roll=7,
                msrps=[109, 129, 169, 189, 219, 249, 329, 399, 499])

#  Zen+ Series

df_2700X = ebay_search('(amd, ryzen) 2700X', 329, 100, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_2700 = ebay_search('(amd, ryzen) 2700 -2700X', 299, 50, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

df_2600X = ebay_search('(amd, ryzen) 2600X', 229, 0, 500, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=cpu_sacat)

df_2600 = ebay_search('(amd, ryzen) 2600 -2600X', 199, 0, 500, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                      debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                      sacat=cpu_sacat)

df_1600af = ebay_search('(amd, ryzen) 1600 AF', 85, 0, 500, feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=cpu_sacat)

# df_1200af = ebay_search('(amd, ryzen) 1200 AF', 60, 0, 500, feedback=run_all_feedback,
#                        run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
#                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
#                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate, sacat=cpu_sacat)


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
median_plotting(frames,
                ['1600AF', '2600', '2600X', '2700', '2700X'],
                'Zen+ Median Pricing', roll=7,
                msrps=[85, 199, 229, 299, 329]
                )

# PS4 Analysis
df_ps4 = ebay_search('ps4 -pro -repair -box -broken -parts -bad', 399, 60, 5000, run_cached=run_cached,
                     feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     sacat=139971, country=country, days_before=days_before, debug=debug, verbose=verbose,
                     store_rate=vg_store_rate,
                     non_store_rate=vg_non_store_rate)
df_ps4_pro = ebay_search('PS4 pro -repair -box -broken -parts -bad', 399, 60, 5000, run_cached=run_cached,
                         feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                         sleep_len=sleep_len, sacat=139971, country=country, days_before=days_before, debug=debug,
                         verbose=verbose,
                         store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)

# PS4 Series Plotting

df_ps4 = df_ps4.assign(item='PS4')
df_ps4_pro = df_ps4_pro.assign(item='PS4 Pro')

frames = [df_ps4, df_ps4_pro]

median_plotting(frames, ['PS4', 'PS4 Pro'], 'PS4 Median Pricing', roll=0,
                msrps=[399, 399])
median_plotting(frames, ['PS4', 'PS4 Pro'], 'PS4 Median Pricing', roll=7,
                msrps=[399, 399])

# Xbox One Analysis
df_xbox_one_s = ebay_search('xbox one s -pro -series -repair -box -broken -parts -bad', 299, 60, 11000,
                            run_cached=run_cached,
                            feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                            sleep_len=sleep_len, sacat=139971, country=country, days_before=days_before, debug=debug,
                            verbose=verbose,
                            store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)
df_xbox_one_x = ebay_search('xbox one x -repair -series -box -broken -parts -bad', 499, 100, 11000,
                            run_cached=run_cached,
                            feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                            sleep_len=sleep_len, sacat=139971, country=country, days_before=days_before, debug=debug,
                            verbose=verbose,
                            store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)

# Xbox One Series Plotting

df_xbox_one_s = df_xbox_one_s.assign(item='Xbox One S')
df_xbox_one_x = df_xbox_one_x.assign(item='Xbox One X')

frames = [df_xbox_one_s, df_xbox_one_x]

median_plotting(frames, ['Xbox One S', 'Xbox One X'], 'Xbox One Median Pricing', roll=0,
                msrps=[299, 499])
median_plotting(frames, ['Xbox One S', 'Xbox One X'], 'Xbox One Median Pricing', roll=7,
                msrps=[299, 499])

# PS5 Analysis (All time)
df_ps5_digital = ebay_search('PS5 Digital -image -jpeg -img -picture -pic -jpg', 399, 300, 11000,
                             run_cached=run_cached,
                             feedback=run_all_feedback, quantity_hist=run_all_hist,
                             min_date=datetime.datetime(2020, 9, 16), extra_title_text='', sleep_len=sleep_len,
                             sacat=139971, country=country, days_before=days_before, debug=debug, verbose=verbose,
                             store_rate=vg_store_rate, non_store_rate=vg_non_store_rate)
df_ps5_disc = ebay_search('PS5 -digital -image -jpeg -img -picture -pic -jpg', 499, 450, 11000,
                          run_cached=run_cached,
                          feedback=run_all_feedback, quantity_hist=run_all_hist,
                          min_date=datetime.datetime(2020, 9, 16), extra_title_text='', sleep_len=sleep_len,
                          sacat=139971, country=country, days_before=days_before, debug=debug, verbose=verbose,
                          store_rate=vg_store_rate,
                          non_store_rate=vg_non_store_rate)

# PS5 Plotting

df_ps5_digital = df_ps5_digital.assign(item='PS5 Digital')
df_ps5_disc = df_ps5_disc.assign(item='PS5 Disc')

frames = [df_ps5_digital, df_ps5_disc]
com_df = pd.concat(frames)
ebay_seller_plot('PS5', com_df, extra_title_text='')
median_plotting([df_ps5_digital, df_ps5_disc], ['PS5 Digital', 'PS5 Disc'], 'PS5 Median Pricing', roll=0,
                msrps=[299, 499])
median_plotting([df_ps5_digital, df_ps5_disc], ['PS5 Digital', 'PS5 Disc'], 'PS5 Median Pricing', roll=7,
                msrps=[299, 499])

# Xbox Analysis (All time)
df_xbox_s = ebay_search('Xbox Series S -image -jpeg -img -picture -pic -jpg', 299, 250, 11000,
                        run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 22),
                        extra_title_text='', sleep_len=sleep_len, sacat=139971, country=country,
                        days_before=days_before, debug=debug, verbose=verbose, store_rate=vg_store_rate,
                        non_store_rate=vg_non_store_rate)
df_xbox_x = ebay_search('Xbox Series X -image -jpeg -img -picture -pic -jpg', 499, 350, 11000,
                        run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 22),
                        extra_title_text='', sleep_len=sleep_len, sacat=139971, country=country,
                        days_before=days_before, debug=debug, verbose=verbose, store_rate=vg_store_rate,
                        non_store_rate=vg_non_store_rate)

# Xbox Plotting


df_xbox_s = df_xbox_s.assign(item='Xbox Series S')
df_xbox_x = df_xbox_x.assign(item='Xbox Series X')

frames = [df_xbox_s, df_xbox_x]
com_df = pd.concat(frames)
ebay_seller_plot('Xbox', com_df, extra_title_text='')
median_plotting([df_xbox_s, df_xbox_x], ['Xbox Series S', 'Xbox Series X'], 'Xbox Median Pricing',
                roll=0, msrps=[299, 499])
median_plotting([df_xbox_s, df_xbox_x], ['Xbox Series S', 'Xbox Series X'], 'Xbox Median Pricing',
                roll=7, msrps=[299, 499])

# Nintendo Switch
df_switch = ebay_search('nintendo switch -lite', 300, 0, 2800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=vg_store_rate, non_store_rate=vg_non_store_rate,
                        sacat=139971)

df_switch_lite = ebay_search('nintendo switch lite', 200, 0, 2800, run_cached=run_cached,
                             feedback=run_all_feedback,
                             quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                             brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                             debug=debug, verbose=verbose, store_rate=vg_store_rate, non_store_rate=vg_non_store_rate,
                             sacat=139971)

# Nintendo Switch Plotting


df_switch_lite = df_switch_lite.assign(item='Lite')
df_switch = df_switch.assign(item='Standard')

frames = [df_switch_lite, df_switch]
com_df = pd.concat(frames)
ebay_seller_plot('Nintendo Switch', com_df, extra_title_text='')
median_plotting([df_switch_lite, df_switch], ['Lite', 'Standard'], 'Nintendo Switch Median Pricing', roll=0,
                msrps=[200, 300])
median_plotting([df_switch_lite, df_switch], ['Lite', 'Standard'], 'Nintendo Switch Median Pricing', roll=7,
                msrps=[200, 300])

df_520 = ebay_search('(nvidia, gtx, geforce, gt) 520 -nvs -quadro', 59, 0, 2000, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_530 = ebay_search('(nvidia, gtx, geforce, gt) 530 -nvs -quadro -tesla', 75, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_545 = ebay_search('(nvidia, gtx, geforce, gt) 545 -nvs -quadro', 109, 0, 2000, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_550ti = ebay_search('(nvidia, gtx, geforce, gt) 550 ti -nvs -quadro', 149, 0, 400, run_cached=run_cached,
                       feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)
df_560 = ebay_search('(nvidia, gtx, geforce, gt) 560 -ti -nvs -quadro', 199, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_570 = ebay_search('(nvidia, gtx, geforce, gt) 570 -nvs -quadro', 349, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_580 = ebay_search('(nvidia, gtx, geforce, gt) 580 -nvs -quadro', 499, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_590 = ebay_search('(nvidia, gtx, geforce, gt) 590 -nvs -quadro', 699, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
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
median_plotting(frames, ['520', '530', '545', '550 Ti', '560', '570', '580', '590'],
                'Fermi (GTX 500) Series Median Pricing',
                roll=0, msrps=[59, 75, 109, 149, 199, 349, 499, 699])
median_plotting(frames, ['520', '530', '545', '550 Ti', '560', '570', '580', '590'],
                'Fermi (GTX 500) Series Median Pricing',
                roll=7, msrps=[59, 75, 109, 149, 199, 349, 499, 699])

df_605 = ebay_search('(nvidia, gtx, geforce, gt) 605 -nvs -quadro', 0, 0, 2000, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_610 = ebay_search('(nvidia, gtx, geforce, gt) 610 -nvs -quadro', 0, 0, 2000, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_630 = ebay_search('(nvidia, gtx, geforce, gt) 630 -nvs -quadro', 0, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_640 = ebay_search('(nvidia, gtx, geforce, gt) 640 -nvs -quadro', 100, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_650 = ebay_search('(nvidia, gtx, geforce, gt) 650 -ti -nvs -quadro', 110, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_650ti = ebay_search('(nvidia, gtx, geforce, gt) 650 Ti -nvs -quadro', 150, 0, 400, run_cached=run_cached,
                       feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)
df_660 = ebay_search('(nvidia, gtx, geforce, gt) 660 -ti -nvs -quadro', 230, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_660ti = ebay_search('(nvidia, gtx, geforce, gt) 660 Ti -nvs -quadro', 300, 0, 400, run_cached=run_cached,
                       feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)
df_670 = ebay_search('(nvidia, gtx, geforce, gt) 670 -nvs -quadro', 400, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_680 = ebay_search('(nvidia, gtx, geforce, gt) 680 -nvs -quadro', 500, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_690 = ebay_search('(nvidia, gtx, geforce, gt) 690 -nvs -quadro', 1000, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
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

df_710 = ebay_search('(nvidia, gtx, geforce, gt) 710 -nvs -quadro', 40, 0, 2000, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_720 = ebay_search('(nvidia, gtx, geforce, gt) 720 -nvs -quadro', 55, 0, 2000, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_730 = ebay_search('(nvidia, gtx, geforce, gt) 730 -nvs -quadro', 75, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_740 = ebay_search('(nvidia, gtx, geforce, gt) 740 -nvs -quadro', 95, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_750 = ebay_search('(nvidia, gtx, geforce, gt) 750 -ti -nvs -quadro', 119, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)

df_750ti = ebay_search('(nvidia, gtx, geforce, gt) 750 Ti -nvs -quadro', 149, 0, 400, run_cached=run_cached,
                       feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)
df_760 = ebay_search('(nvidia, gtx, geforce, gt) 760 -nvs -quadro', 249, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_770 = ebay_search('(nvidia, gtx, geforce, gt) 770 -nvs -quadro', 399, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_780 = ebay_search('(nvidia, gtx, geforce, gt) 780 -ti -nvs -quadro', 649, 0, 400, run_cached=run_cached,
                     feedback=run_all_feedback,
                     quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                     brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                     debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                     sacat=graphics_card_sacat)
df_780ti = ebay_search('(nvidia, gtx, geforce, gt) 780 ti -nvs -quadro', 699, 0, 400, run_cached=run_cached,
                       feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)
df_titanblack = ebay_search('(nvidia, gtx, geforce, gt) titan black -nvs -quadro', 999, 0, 400,
                            run_cached=run_cached, feedback=run_all_feedback,
                            quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                            brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                            debug=debug, verbose=verbose, store_rate=comp_store_rate,
                            non_store_rate=comp_non_store_rate,
                            sacat=graphics_card_sacat)

df_titanz = ebay_search('(nvidia, gtx, geforce, gt) titan Z -nvs -quadro', 2999, 0, 400, run_cached=run_cached,
                        feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
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
median_plotting(frames,
                ['710', '720', '730', '740', '750', '750 Ti', '760', '770', '780', '780 Ti', 'Titan Black', 'Titan Z'],
                'Maxwell-Kepler (GTX 700) Series Median Pricing',
                roll=0, msrps=[40, 55, 75, 95, 119, 149, 249, 399, 649, 699, 999, 2999])
median_plotting(frames,
                ['710', '720', '730', '740', '750', '750 Ti', '760', '770', '780', '780 Ti', 'Titan Black', 'Titan Z'],
                'Maxwell-Kepler (GTX 700) Series Median Pricing',
                roll=7, msrps=[40, 55, 75, 95, 119, 149, 249, 399, 649, 699, 999, 2999])

# RX 500 Series
df_RX550 = ebay_search('rx 550 -550x', 79, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX550X = ebay_search('rx 550x', 79, 0, 750, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_RX560 = ebay_search('rx 560', 99, 0, 550, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX570 = ebay_search('rx 570', 169, 0, 850, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX580 = ebay_search('rx 580', 199, 0, 500, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX590 = ebay_search('rx 590', 279, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX550 = df_RX550.assign(item='RX 550')
df_RX550X = df_RX550X.assign(item='RX 550X')
df_RX560 = df_RX560.assign(item='RX 560')
df_RX570 = df_RX570.assign(item='RX 570')
df_RX580 = df_RX580.assign(item='RX 580')
df_RX590 = df_RX590.assign(item='RX 590')

frames = [df_RX550, df_RX550X, df_RX560, df_RX570, df_RX580, df_RX590]

median_plotting(frames,
                ['RX 550', 'RX 550X', 'RX 560', 'RX 570', 'RX 580', 'RX 590'],
                'RX 500 Series Median Pricing', roll=0,
                msrps=[79, 79, 99, 169, 199, 279])

median_plotting(frames,
                ['RX 550', 'RX 550X', 'RX 560', 'RX 570', 'RX 580', 'RX 590'],
                'RX 500 Series Median Pricing', roll=7,
                msrps=[79, 79, 99, 169, 199, 279])

# R5/R7/R9 Series
df_R7350 = ebay_search('r7 350', 89, 0, 850, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_R7360 = ebay_search('r7 360', 109, 0, 500, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_R9370X = ebay_search('r9 370X', 179, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_R9380 = ebay_search('r9 380 -380X', 199, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_R9380X = ebay_search('r9 380X', 229, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_R9390 = ebay_search('r9 390', 329, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_R9390X = ebay_search('r9 390X', 429, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_R9FURY = ebay_search('r9 fury -X', 549, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_R9FURYX = ebay_search('r9 fury x', 649, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                         quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                         brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                         debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                         sacat=graphics_card_sacat)

df_R9NANO = ebay_search('r9 nano', 649, 0, 800, run_cached=run_cached, feedback=run_all_feedback,
                        quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                        brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                        debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                        sacat=graphics_card_sacat)

df_RADEONPRODUO = ebay_search('radeon pro duo', 1499, 0, 2000, run_cached=run_cached, feedback=run_all_feedback,
                              quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                              brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                              debug=debug, verbose=verbose, store_rate=comp_store_rate,
                              non_store_rate=comp_non_store_rate,
                              sacat=graphics_card_sacat)

df_R7350 = df_R7350.assign(item='R7 350')
df_R7360 = df_R7360.assign(item='R7 360')
df_R9370X = df_R9370X.assign(item='R9 370X')
df_R9380X = df_R9380X.assign(item='R9 380X')
df_R9390 = df_R9390.assign(item='R9 390')
df_R9390X = df_R9390X.assign(item='R9 390X')
df_R9FURY = df_R9FURY.assign(item='R9 Fury')
df_R9FURYX = df_R9FURYX.assign(item='R9 Fury X')
df_R9NANO = df_R9NANO.assign(item='R9 Nano')
df_RADEONPRODUO = df_RADEONPRODUO.assign(item='Radeon Pro Duo')

frames = [df_R7350, df_R7360, df_R9380X, df_R9390, df_R9390X, df_R9FURY, df_R9FURYX, df_R9NANO, df_RADEONPRODUO]

median_plotting(frames,
                ['R7 350', 'R7 360', 'R9 380X', 'R9 390', 'R9 380X', 'R9 Fury', 'R9 Fury X', 'R9 Nano',
                 'Radeon Pro Duo'],
                'R5-R7-R9 Series Median Pricing', roll=0,
                msrps=[89, 109, 199, 229, 329, 429, 549, 649, 649, 1499])

median_plotting(frames,
                ['R7 350', 'R7 360', 'R9 380X', 'R9 390', 'R9 380X', 'R9 Fury', 'R9 Fury X', 'R9 Nano',
                 'Radeon Pro Duo'],
                'R5-R7-R9 Series Median Pricing', roll=7,
                msrps=[89, 109, 199, 229, 329, 429, 549, 649, 649, 1499])

# RX 400 Series
df_RX460 = ebay_search('rx 460', 109, 0, 400, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX470 = ebay_search('rx 470', 179, 0, 750, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX480 = ebay_search('rx 480', 199, 0, 550, run_cached=run_cached, feedback=run_all_feedback,
                       quantity_hist=run_all_hist, extra_title_text='', sleep_len=sleep_len,
                       brand_list=brand_list, model_list=model_list, country=country, days_before=days_before,
                       debug=debug, verbose=verbose, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate,
                       sacat=graphics_card_sacat)

df_RX460 = df_RX460.assign(item='RX 460')
df_RX470 = df_RX470.assign(item='RX 470')
df_RX480 = df_RX480.assign(item='RX 480')

frames = [df_RX460, df_RX470, df_RX480]

median_plotting(frames,
                ['RX 460', 'RX 470', 'RX 480'],
                'RX 400 Series Median Pricing', roll=0,
                msrps=[109, 179, 199])

median_plotting(frames,
                ['RX 460', 'RX 470', 'RX 480'],
                'RX 400 Series Median Pricing', roll=7,
                msrps=[109, 179, 199])

'''df_b550 = ebay_search('b550', 0, 0, 600, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                      sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, verbose=verbose, sacat=mobo_sacat,
                      days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_X570 = ebay_search('x570', 0, 0, 2000, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                      sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, verbose=verbose, sacat=mobo_sacat,
                      days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_power = ebay_search('power', 0, 0, 2000, run_cached=run_cached,
                       feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                       sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, verbose=verbose, sacat=psu_sacat,
                       days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_ddr4 = ebay_search('ddr4 -laptop -rdimm -ecc -lrdimm -notebook', 0, 0, 2000, run_cached=run_cached,
                      feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                      sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, verbose=verbose,
                      sacat=memory_sacat,
                      days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_cooler = ebay_search('cooler', 0, 0, 2000, run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                        sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, verbose=verbose,
                        sacat=cpu_cooler_sacat,
                        days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)

df_ssd = ebay_search('ssd -portable -nas -external', 0, 0, 20000, run_cached=run_cached,
                     feedback=run_all_feedback, quantity_hist=run_all_hist, extra_title_text='',
                     sleep_len=sleep_len, brand_list=brand_list, model_list=model_list, debug=debug, verbose=verbose, sacat=ssd_sacat,
                     days_before=days_before, store_rate=comp_store_rate, non_store_rate=comp_non_store_rate)
'''

# TODO: Model MSRP https://db.premiumbuilds.com/graphics-cards/
# TODO: Get stockx listings (need to be manual)
# TODO: Count CL, FB, OfferUp listings
# TODO: Add License

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
