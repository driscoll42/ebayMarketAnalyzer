# Moving all the calls of the code out of the main.py to reduce confusion/overhead.

import datetime

from main import ebay_search
from main import median_plotting

run_all_feedback = True
run_all_hist = True
run_cached = True
sleep_len = 5
country = 'UK'
ccode = '£'
debug = False
days_before = 5

comp_store_rate = 0.04
comp_non_store_rate = 0.1
vg_store_rate = 0.0915
vg_non_store_rate = 0.1
tax_rate = 0.0

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

df_3070 = ebay_search('RTX 3070 -image -jpeg -img -picture -pic -jpg', 499, 499, 1300, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 10, 29),
                      extra_title_text=' UK', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, ccode=ccode, debug=debug)

# Zen 3 Analysis
df_5950x = ebay_search('5950X -image -jpeg -img -picture -pic -jpg', 799, 400, 2200, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text=' UK', sleep_len=sleep_len,
                       country=country, ccode=ccode)
df_5900x = ebay_search('5900X -image -jpeg -img -picture -pic -jpg', 549, 499, 2050, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text=' UK', sleep_len=sleep_len,
                       country=country, ccode=ccode)
df_5800x = ebay_search('5800X -image -jpeg -img -picture -pic -jpg', 449, 400, 1000, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text=' UK', sleep_len=sleep_len,
                       country=country, ccode=ccode)
df_5600x = ebay_search('5600X -image -jpeg -img -picture -pic -jpg', 299, 250, 1000, feedback=run_all_feedback,
                       run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 11, 1),
                       sleep_len=sleep_len, country=country, ccode=ccode, extra_title_text=' UK')

median_plotting([df_5600x, df_5800x, df_5900x, df_5950x],
                ['5600X', '5800X', '5900X', '5950X'], 'Zen 3 UK Median Pricing', roll=0,
                msrps=[299, 449, 549, 799], ccode=ccode)

median_plotting([df_5600x, df_5800x, df_5900x, df_5950x],
                ['5600X', '5800X', '5900X', '5950X'], 'Zen 3 UK Median Pricing', roll=7,
                msrps=[299, 449, 549, 799], ccode=ccode)

# Big Navi Analysis
df_6800 = ebay_search('RX 6800 -XT -image -jpeg -img -picture -pic -jpg', 579, 400, 2500,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, extra_title_text=' UK', sleep_len=sleep_len,
                      brand_list=brand_list, model_list=model_list, country=country, ccode=ccode)
df_6800xt = ebay_search('RX 6800 XT -image -jpeg -img -picture -pic -jpg', 649, 850, 2000,
                        feedback=run_all_feedback,
                        run_cached=run_cached, quantity_hist=run_all_hist,
                        extra_title_text=' UK', sleep_len=sleep_len, brand_list=brand_list,
                        model_list=model_list, country=country,
                        ccode=ccode)  # There are some $5000+, but screw with graphs
df_6900 = ebay_search('RX 6900 -image -jpeg -img -picture -pic -jpg', 999, 100, 999999, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 12, 8),
                      extra_title_text=' UK', sleep_len=sleep_len, brand_list=brand_list,
                      model_list=model_list, country=country, ccode=ccode)  # Not out until December 8

median_plotting([df_6800, df_6800xt, df_6900], ['RX 6800', 'RX 6800 XT', 'RX 6900'], 'Big Navi UK Median Pricing',
                roll=0,
                msrps=[579, 649, 999], ccode=ccode)
median_plotting([df_6800, df_6800xt, df_6900], ['RX 6800', 'RX 6800 XT', 'RX 6900'], 'Big Navi UK Median Pricing',
                roll=7,
                msrps=[579, 649, 999], ccode=ccode)

# RTX 30 Series Analysis
df_3060 = ebay_search('RTX 3060 -image -jpeg -img -picture -pic -jpg', 399, 200, 1300, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 12, 1),
                      extra_title_text=' UK', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, ccode=ccode)

df_3080 = ebay_search('RTX 3080 -image -jpeg -img -picture -pic -jpg', 699, 550, 10000, feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 17),
                      extra_title_text=' UK', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, ccode=ccode)
df_3090 = ebay_search('RTX 3090 -image -jpeg -img -picture -pic -jpg', 1499, 550, 10000,
                      feedback=run_all_feedback,
                      run_cached=run_cached, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 17),
                      extra_title_text=' UK', sleep_len=sleep_len, brand_list=brand_list, model_list=model_list,
                      country=country, ccode=ccode)

median_plotting([df_3060, df_3070, df_3080, df_3090], ['3060', '3070', '3080', '3090'],
                'RTX 30 UK Series Median Pricing', roll=0,
                msrps=[399, 499, 699, 1499], ccode=ccode)
median_plotting([df_3060, df_3070, df_3080, df_3090], ['3060', '3070', '3080', '3090'],
                'RTX 30 UK Series Median Pricing', roll=7,
                msrps=[399, 499, 699, 1499], ccode=ccode)

# PS5 Analysis (All time)
df_ps5_digital = ebay_search('PS5 Digital -image -jpeg -img -picture -pic -jpg', 399, 300, 11000,
                             run_cached=run_cached,
                             feedback=run_all_feedback, quantity_hist=run_all_hist,
                             min_date=datetime.datetime(2020, 9, 16), extra_title_text=' UK', sleep_len=sleep_len,
                             sacat=139971, country=country, ccode=ccode)
df_ps5_disc = ebay_search('PS5 -digital -image -jpeg -img -picture -pic -jpg', 499, 450, 11000,
                          run_cached=run_cached,
                          feedback=run_all_feedback, quantity_hist=run_all_hist,
                          min_date=datetime.datetime(2020, 9, 16), extra_title_text=' UK', sleep_len=sleep_len,
                          sacat=139971, country=country, ccode=ccode)
median_plotting([df_ps5_digital, df_ps5_disc], ['PS5 Digital', 'PS5 Disc'], 'PS5 UK Median Pricing', roll=0,
                msrps=[299, 499], ccode=ccode)
median_plotting([df_ps5_digital, df_ps5_disc], ['PS5 Digital', 'PS5 Disc'], 'PS5 UK Median Pricing', roll=7,
                msrps=[299, 499], ccode=ccode)

# Xbox Analysis (All time)
df_xbox_s = ebay_search('Xbox Series S -image -jpeg -img -picture -pic -jpg', 299, 250, 11000,
                        run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 22),
                        extra_title_text=' UK', sleep_len=sleep_len, sacat=139971, country=country, ccode=ccode)
df_xbox_x = ebay_search('Xbox Series X -image -jpeg -img -picture -pic -jpg', 499, 350, 11000,
                        run_cached=run_cached,
                        feedback=run_all_feedback, quantity_hist=run_all_hist, min_date=datetime.datetime(2020, 9, 22),
                        extra_title_text=' UK', sleep_len=sleep_len, sacat=139971, country=country, ccode=ccode)
median_plotting([df_xbox_s, df_xbox_x], ['Xbox Series S', 'Xbox Series X'], 'Xbox UK Median Pricing', roll=0,
                msrps=[299, 499], ccode=ccode)
median_plotting([df_xbox_s, df_xbox_x], ['Xbox Series S', 'Xbox Series X'], 'Xbox UK Median Pricing', roll=7,
                msrps=[299, 499], ccode=ccode)
