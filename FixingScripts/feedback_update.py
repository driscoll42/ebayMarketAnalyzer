import os

import pandas as pd

directory = r'C:\Users\mdriscoll6\Dropbox\PythonProjects\eBayScraper\Spreadsheets'

fb_dict = {}

for f in os.listdir(directory):
    print(f)
    if str(f).find('~') < 0 and 'xlsx' in str(f) and 'agent' not in str(f) and 'Medians' not in str(f):
        df = pd.read_excel('../Spreadsheets/' + f, index_col=0, engine='openpyxl')
        dup_df = df.copy(deep=True)

        for index, row in dup_df.iterrows():
            seller = row['Seller']
            sell_fb = row['Seller Feedback']

            if sell_fb == 'None':
                sell_fb = -1

            if seller in fb_dict.keys():
                fb_dict[seller] = max(sell_fb, fb_dict[seller])
            else:
                fb_dict[seller] = sell_fb

        print(len(fb_dict))
num_updates = 0

for f in os.listdir(directory):
    print(f)
    if str(f).find('~') < 0 and 'xlsx' in str(f) and 'agent' not in str(f) and 'Medians' not in str(f):
        create = False
        df = pd.read_excel('../Spreadsheets/' + f, index_col=0, engine='openpyxl')
        dup_df = df.copy(deep=True)

        for index, row in dup_df.iterrows():
            seller = row['Seller']
            sell_fb = row['Seller Feedback']
            if sell_fb == 'None':
                sell_fb = -1

            max_fb = fb_dict[seller]

            if sell_fb < max_fb:
                create = True
                num_updates += 1
                dup_df.loc[dup_df['Seller'] == seller, 'Seller Feedback'] = max_fb

        print(num_updates)
        if create:
            dup_df.to_excel('../temp/' + f, engine='openpyxl')

print('--------------------------')

for f in os.listdir(directory):
    print(f)
    if str(f).find('~') < 0 and 'xlsx' in str(f) and 'agent' not in str(f) and 'Medians' not in str(f):
        create = False
        df = pd.read_excel('../Spreadsheets/' + f, index_col=0, engine='openpyxl')
        dup_df = df.copy(deep=True)

        for index, row in dup_df.iterrows():
            seller = row['Seller']
            sell_fb = row['Seller Feedback']
            if sell_fb == 'None':
                sell_fb = -1

            max_fb = fb_dict[seller]

            if sell_fb < max_fb:
                create = True
                num_updates += 1
                dup_df.loc[dup_df['Seller'] == seller, 'Seller Feedback'] = max_fb

        dup_df.loc[dup_df['Seller Feedback'] == 'None', 'Seller Feedback'] = -1
        dup_df.loc[dup_df['Seller Feedback'] <= 5, 'Ignore'] = 1
        dup_df = dup_df.sort_values(by='Sold Date')

        if create:
            dup_df.to_excel('../temp/' + f, engine='openpyxl')
