# Brand Fix

import pandas as pd

files = [

    'RTX 3060 -image -jpeg -img -picture -pic -jpg.xlsx',
    'RTX 3070 -image -jpeg -img -picture -pic -jpg.xlsx',
    'RTX 3080 -image -jpeg -img -picture -pic -jpg.xlsx',
    'RTX 3090 -image -jpeg -img -picture -pic -jpg.xlsx',

    'RX 6800 -XT -image -jpeg -img -picture -pic -jpg.xlsx',
    'RX 6800 XT -image -jpeg -img -picture -pic -jpg.xlsx',
    'RX 6900 -image -jpeg -img -picture -pic -jpg.xlsx',

    'RTX 3060 -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RTX 3070 -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RTX 3080 -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RTX 3090 -image -jpeg -img -picture -pic -jpg UK.xlsx',

    'RX 6800 -XT -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RX 6800 XT -image -jpeg -img -picture -pic -jpg UK.xlsx',
    'RX 6900 -image -jpeg -img -picture -pic -jpg UK.xlsx',

    'rtx 2060 -super.xlsx',
    'rtx 2060 super.xlsx',
    'rtx 2070 -super.xlsx',
    'rtx 2070 super.xlsx',
    'rtx 2080 -super -ti.xlsx',
    'rtx 2080 super -ti.xlsx',
    'rtx 2080 ti -super.xlsx',

    'rx 5500 xt.xlsx',
    'rx 5600 xt.xlsx',
    'rx 5700 -xt.xlsx',
    'rx 5700 xt.xlsx',

]

brand_list = ['FOUNDER', 'ASUS', 'MSI', 'EVGA', 'GIGABYTE', 'ZOTAC', 'XFX', 'PNY', 'SAPPHIRE', 'COLORFUL', 'ASROCK',
              'POWERCOLOR', 'INNO3D', 'PALIT', 'VISIONTEK', 'DELL']
model_list = [['XC3', 'EVGA'], ['TRINITY', 'ZOTAC'], ['FTW3', 'EVGA'], ['FOUNDER', 'FOUNDER'], ['STRIX', 'ASUS'],
              ['EKWB', 'ASUS'], ['TUF', 'ASUS'], ['SUPRIM', 'MSI'], ['VENTUS', 'MSI'], ['MECH', 'MSI'],
              ['EVOKE', 'MSI'], ['TRIO', 'MSI'], ['KINGPIN', 'EVGA'], ['K|NGP|N', 'EVGA'], ['AORUS', 'GIGABYTE'],
              ['WATERFORCE', 'GIGABYTE'], ['XTREME', 'GIGABYTE'], ['MASTER', 'GIGABYTE'], ['AMP', 'ZOTAC'],
              [' FE ', 'FOUNDER'], ['TWIN EDGE', 'ZOTAC'], ['POWER COLOR', 'POWERCOLOR'], ['ALIENWARE', 'DELL']]

for f in files:
    print(f)
    df = pd.read_excel('Spreadsheets/' + f, index_col=0, engine='openpyxl')
    for index, row in df.iterrows():
        for b in brand_list:
            if b.upper() in row['Title'].upper():
                df.loc[index, 'Brand'] = b
                break
        for m in model_list:
            if m[0].upper() in row['Title'].upper():
                df.loc[index, 'Model'] = m[0]
                df.loc[index, 'Brand'] = m[1]
                break

    df.to_excel('Spreadsheets/' + f, engine='openpyxl')
