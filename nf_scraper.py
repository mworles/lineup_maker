import pandas as pd
import numpy as np
from urllib import urlopen
from bs4 import BeautifulSoup
import time
import os

url = 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections'
urls = [url, url + '/d']

data_files = []

def scrape():
    for u in urls:
        html = urlopen(u)
        print 'scraping ' + u
        soup = BeautifulSoup(html.read(), "lxml")
        tables = soup.find_all('table')
        tab0 = tables[0]
        header = tab0.find('th', {'title': 'Player'}).get_text().strip()
        tab0tds = tab0.tbody.find_all('td', {'class': 'player'})
        cells = tab0.tbody.find_all('span', {'class': 'full'})

        if '/d' in u:
            tab0c1 = [x.get_text().lower().split(' D/ST')[0] for x in cells]
        else:
            tab0c1 = [x.get_text().lower() for x in cells]
        tab0c2 = [x.get_text().lower().split('(')[1].split(',')[0] for x in tab0tds]
        tab0c3 = [x.get_text().lower().split('(')[1].split(',')[1].strip().replace(')', '') for x in tab0tds]

        tab1 = tables[1]
        headers = tab1.thead.find_all('tr')[1].find_all('th')
        cols = [x.get_text().lower().strip() for x in headers]
        rows = tab1.tbody.find_all('tr')
        data_rows = [[td.get_text().strip().lower() for td in row.find_all('td')] for row in rows]

        df = pd.DataFrame(data_rows, columns=cols)
        df = df.rename(columns={'team': 'opponent'})

        df['name'] = pd.Series(tab0c1).values
        df['pos'] = pd.Series(tab0c2).values
        df['team'] = pd.Series(tab0c3).values

        if '/d' in u:
            sfx = 'dst'
        else:
            sfx = 'off'

        f = 'data/numberfire_' + sfx + '.csv'
        print 'writing ' + f
        df.to_csv(f, index=False)
        data_files.append(f)
        time.sleep(1)

    # dict to rename columns
    ctor_dict = {'fp.1': 'fp_fd', 'cost': 'cst_fd',
                 'value': 'val_fd', 'fp.2': 'fp_dk',
                 'cost.1': 'cst_dk', 'value.1': 'val_dk',
                 'fp.3': 'fp_yh', 'cost.2': 'cst_yh',
                 'value.2': 'val_yh'}


    
    # import projection data
    data_frames = [pd.read_csv(f) for f in data_files]

    df = pd.concat(data_frames, sort=False)
    df['pos'] = df['pos'].str.upper()
    df['pos'] = df['pos'].replace({'D': 'DST'})
    df = df.rename(columns=ctor_dict)
    

    keep_cols = ['name', 'pos', 'team', 'fp_fd', 'fp_dk', 'cst_fd', 'cst_dk',
                 'val_dk', 'val_fd']
    df = df.loc[:, keep_cols]
    
    # format cost column data
    cst_cols = [c for c in df.columns if 'cst_' in c]
    for c in cst_cols:
        df[c] = df[c].str.replace('$', '').astype(float)    
    
    # drop 'd/st' from defense names
    def fix_name(row):
        if row['pos'] != 'DST':
            return row['name']
        else:
            name = row['name'].split('D/ST')[0].strip()
            return name

    df['name'] = df.apply(fix_name, axis=1)
    
    
    f = 'data/nf_projections.csv'
    print 'writing ' + f
    df.to_csv(f, index=False)
    [os.remove(f) for f in data_files]
