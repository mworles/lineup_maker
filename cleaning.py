from __future__ import division
import pandas as pd
import numpy as np

def num_from_string(x):
    s = x.replace(',', '')
    s = str(s)
    return int(s)

def get_relative_points(year, week):
    week = str(week)
    year = str(year)
    file = "".join(['fd_', year, '_', week, '.csv'])
    df = pd.read_csv('data/points/' + file, index_col=0)
    df = df[df['Salary'].notnull()]

    df['sal'] = df['Salary'].apply(num_from_string)

    pos_dict = {'Quarterbacks': 'QB', 
                'Running Backs': 'RB', 
                'Wide Receivers': 'WR',
                'Tight Ends': 'TE',
                'Kickers': 'K',
                'Defenses': 'DST'}

    df['pos'] = df['pos'].map(pos_dict)
    
    pos_vals = {}

    for p in df['pos'].unique():
        pos_vals[p] = {}
        pos_vals[p]['pts'] =  df.loc[df['pos'] == p, 'Points'].sum()
        pos_vals[p]['sal'] =  df.loc[df['pos'] == p, 'sal'].sum()

    # %%
    def compute_rpts(row, pos_vals):
        pos = row['pos']
        row_pct = row['sal'] / pos_vals[pos]['sal']
        rpts = row_pct * pos_vals[pos]['pts']
        return rpts
        
    df['rpts'] = df.apply(lambda x: compute_rpts(x, pos_vals), axis=1)

    """
    df['sal_pct'] = df['sal'] / df['sal'].sum()
    df['rpts'] = df['sal_pct'] * df['Points'].sum()
    """
    df = df.loc[:, ['name', 'Team', 'pos', 'sal', 'rpts', 'Points']]
    
    # add random noise to rpts
    rn = np.random.normal(0, .10, df.shape[0])
    df['rpts'] = df['rpts'] + rn
    
    return df

def clean_name(row):
    if row['pos'] != 'DST':
        ns = row['name'].split(' ')
        if len(ns) == 2:
            fn = ns[1]
            ln = ns[0]
        else:
            ns = row['name'].split(',')
            fn = ns[1]
            ln = ns[0]
            if len(ln) > 1:
                ln = ln[0]
            if len(fn) > 1:
                fn = fn[0]
        fn = fn.replace(' ', '')
        ln = ln.replace(' ', '')
        name = " ".join([fn, ln])
        name = name.replace(',', '')
    else:
        name = row['Team'].upper() + ' DST'
    return name

def clean_names(df):    
    df['name'] = df.apply(lambda x: clean_name(x), axis=1)
    return df
    
