"""
util.py

Various functions that get reused and don't belong in any other specific file

Current functions:
    prep_df - Cleanses a dataframe to prepare it for analysis
"""

import pandas as pd


def prep_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['Ignore'] == 0]
    df = df[df['Total Price'] > 0]
    df = df[df['Quantity'] > 0]
    df = df[df['Seller Feedback'] >= 5]
    df = df.sort_values(by='Sold Date')
    df = df.loc[df.index.repeat(df['Quantity'])]
    df['Quantity'] = 1
    return df
