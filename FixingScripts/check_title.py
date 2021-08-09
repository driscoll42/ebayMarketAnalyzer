import os

import pandas as pd

directory = r'C:\Users\mdriscoll6\Dropbox\PythonProjects\eBayScraper\Spreadsheets'

query_exclusions = ['image', 'jpeg', 'img', 'picture', ' pic ', 'jpg', 'charity', 'photo', 'humans', 'prints', 'framed',
                    'print', 'people', 'inkjet', 'pix', 'paper', 'digital', 'pics', 'alternative', 'drawn', 'photo',
                    'p n g']

psf_dig_qe = ['image', 'jpeg', 'img', 'picture', ' pic ', 'jpg', 'charity', 'photo', 'humans', 'prints', 'framed',
              'print', 'people', 'inkjet', 'pix', 'paper', 'digital', 'pics', 'alternative', 'drawn', 'photo', 'p n g']

for f in os.listdir(directory):
    print(f)
    if str(f).find('~') < 0 and 'xlsx' in str(f) and 'agent_list' not in str(f):
        df = pd.read_excel('../Spreadsheets/' + f, index_col=0, engine='openpyxl')
        dup_df = df.copy(deep=True)

        for index, row in dup_df.iterrows():
            title = row['Title'].lower()
            for qe in psf_dig_qe:
                if qe in title and row['Ignore'] == 0:
                    print(title)
